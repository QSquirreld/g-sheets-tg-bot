from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import aiohttp
import os

try:
    # Загрузка учетных данных из файла
    creds = Credentials.from_service_account_file('creds.json')
    service = build('drive', 'v3', credentials=creds)
except Exception as e:
    print(f'Ошибка при загрузке учетных данных или создании сервиса: {e}')
    service = None


async def download_photo(file_id):
    token = os.getenv("TOKEN")
    if not token:
        raise Exception("TOKEN не установлен в переменных окружения")

    url = f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    file_info = await response.json()
                    file_path = file_info['result']['file_path']
                    download_url = f'https://api.telegram.org/file/bot{token}/{file_path}'
                    async with session.get(download_url) as file_response:
                        if file_response.status == 200:
                            file_data = await file_response.read()
                            # Ensure /tmp/ directory exists
                            tmp_dir = '/tmp'
                            if not os.path.exists(tmp_dir):
                                os.makedirs(tmp_dir)
                            local_path = f'{tmp_dir}/{file_id}.jpg'
                            with open(local_path, 'wb') as f:
                                f.write(file_data)
                            print(f'Файл загружен и сохранен по пути: {local_path}')
                            return local_path
                        else:
                            print(f'Не удалось загрузить файл из Telegram: {file_response.status}')
                            return None
                else:
                    print(f'Не удалось получить информацию о файле из Telegram: {response.status}')
                    return None
    except Exception as e:
        print(f'Ошибка при загрузке фото: {e}')
        return None


def generate_file_link(file_id):
    try:
        # Создание общего доступа к файлу
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()

        # Возвращаем публичную ссылку
        return f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
    except Exception as e:
        print(f'Ошибка при создании ссылки на файл: {e}')
        return None


def upload_to_drive(local_path, drive_file_name):
    if not service:
        raise Exception("Сервис Google Drive не инициализирован")

    file_metadata = {
        'name': drive_file_name,
        'parents': [os.getenv('GDRIVE_FOLDER')]  # Указание родительской папки
    }
    media = MediaFileUpload(local_path, mimetype='image/jpeg')
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id, parents').execute()
        print(f'Загруженный файл: {file}')
        return file
    except Exception as e:
        print(f'Ошибка при загрузке файла в Google Drive: {e}')
        return None


def check_file_in_drive(file_id):
    try:
        service.files().get(fileId=file_id).execute()
        return True
    except Exception as e:
        print(f'Файл не найден в GoogleDrive: {e}')
        return False


def upload_and_cleanup(local_path, drive_file_name):
    try:
        file = upload_to_drive(local_path, drive_file_name)
        if file:
            file_id = file.get('id')
            file_link = generate_file_link(file_id)
            parents = file.get('parents')
            print(f'Файл загружен в Google Drive с ID: {file_id}')
            if parents:  # метаданные, а конкретно содержит данные о папках
                parent_id = parents[0]
                parent_info = service.files().get(fileId=parent_id, fields='name').execute()
                parent_name = parent_info.get('name')
                print(f'Файл загружен в папку: {parent_name} (ID: {parent_id})')
            if not check_file_in_drive(file_id):
                print(f'{drive_file_name} не найден в Google Drive.')
            return file_id, file_link
        else:
            print(f'Ошибка при загрузке файла {drive_file_name} в Google Drive.')
            return None
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
            print(f'Локальный файл {local_path} удалён.')
