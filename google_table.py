import gspread

gc = gspread.service_account(filename='creds.json')
wks1 = gc.open('bot-table').sheet1  # открытие таблицы и выбор листа в таблице


def head_setter():
    headers_wks1 = [
        'Название проекта', 'Дата', 'Ответственный', 'Название покупки', 'Статус', 'Способ оплаты', 'Комментарий к оплате',
        'Цена', 'Фото товара', 'Дата по чеку', 'Фото чека', '', 'user_id', 'username', 'user_first_name'
    ]

    current_headers_wks1 = wks1.row_values(1)
    if current_headers_wks1 != headers_wks1:
        wks1.delete_rows(1)
        wks1.insert_row(headers_wks1, index=1)
        print("Заголовки первого листа обновлены.")


def send_data_bot_to_sheets(data: dict):
    row = [
        str(data["project_name"]).capitalize(),
        data["date"],
        data["responsible"],
        data["item_name"],
        data["payment_status"],
        data["payment_type"],
        data["payment_comment"],
        data["item_price"],
        data.get("item_photo_link", "Нет фото предмета"),
        # ссылка на фото предмета, если есть |исп. get(), потому что он вернёт None, |
        data["payment_date"],
        data.get("payment_photo_link", "Нет фото чека"),
        # ссылка на фото чека, если есть  |если в словаре будут остутствовать ключ|
        '',
        data["user_id"],
        data["user_name"],
        data["user_personal_name"]
    ]

    max_retries = 3

    for attempt in range(max_retries):
        next_row = len(wks1.get_all_values()) + 1
        range_to_update = f'A{next_row}:O{next_row}'
        try:
            wks1.update(range_to_update, [row])
            print("Данные успешно отправлены в Google Sheets")

            last_row_values = wks1.row_values(next_row)  # проверка записанных и отправленных данных

            if [str(item) for item in last_row_values] == [str(item) for item in
                                                           row]:  # тут оказалось, что типы данных в таблице и в словаре могут отличаться, поэтому так некрасиво
                return True
            else:
                print('Ошибка несовпадения записанных и отправленных данных')
                raise ValueError('Записанные данные и отправленные - не совпадают')

        except Exception as e:
            print(f'Попытка {attempt + 1} не удалась: {e}')
            if attempt == max_retries - 1:
                print('Максимальное количество попыток достигнуто, данные не записаны')
                raise e
    return False
