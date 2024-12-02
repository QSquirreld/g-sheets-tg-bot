import re

from datetime import datetime
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto

import fsms as fsm
import keyboards as kb
import google_table as gtab
import google_drive as gdrive

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Хотите отправить данные?', reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Бот предназначен для отправки данных о покупках.',
                         reply_markup=kb.restart)


@router.message(F.text == 'Начать сначала')
async def beginning(message: Message, state: fsm.FSMContext):
    await state.clear()
    await cmd_start(message)


@router.message(F.text == 'Помощь')
async def txt_help(message: Message):
    await message.answer('Бот предназначен для отправки данных о покупках.',
                         reply_markup=kb.restart)


@router.message(F.text == 'Отправить данные')
async def first_step_data_collect(message: Message, state: fsm.FSMContext):
    await state.set_state(fsm.Data_Collect.project_name)
    await message.answer('Введите название проекта', reply_markup=kb.restart)


@router.message(fsm.Data_Collect.project_name)
async def select_project_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if not (1 <= len(message.text)):
            raise ValueError('Поле не может быть пустым')
        if not (len(message.text) <= 40):
            raise ValueError('Длина не может превышать 40 сиволов')

        await state.update_data(project_name=message.text)
        await state.set_state(fsm.Data_Collect.responsible)
        await message.answer('Введите ответственного:', reply_markup=kb.restart)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.restart)


@router.message(fsm.Data_Collect.responsible)
async def responsible_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if not re.match('^[A-Za-zА-Яа-яЁё .-]+$', message.text):
            raise ValueError('Поле может содержать буквы, пробелы, - и .')
        if not (len(message.text) <= 40):
            raise ValueError('Длина не может превышать 40 сиволов')
        if not (2 <= len(message.text)):
            raise ValueError('Введите хотя бы 2 символа')
        if not re.match('^[A-Za-zА-Яа-яЁё .-]+$', message.text) or not (2 <= len(message.text) <= 40):
            raise ValueError('Поле может содержать буквы, пробелы, - и .'
                             '\nПоле может содержать не более 40 символов'
                             '\nПоле должно содержать минимум 2 символа')

        await state.update_data(responsible=message.text)
        await state.set_state(fsm.Data_Collect.payment_status)
        await message.answer('Выберите тип операции', reply_markup=kb.status)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.restart)


@router.message(fsm.Data_Collect.payment_status)
async def payment_status_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if (message.text != 'Расход') and (message.text != 'Возврат') and (message.text != 'Начать сначала'):
            raise ValueError('Пожалуйста используйте кнопки')

        await state.update_data(payment_status=message.text)
        await state.set_state(fsm.Data_Collect.item_name)
        await message.answer('Введите название покупки:', reply_markup=kb.restart)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.status)


@router.message(fsm.Data_Collect.item_name)
async def item_name_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if not (1 <= len(message.text)):
            raise ValueError('Поле не может быть пустым')

        await state.update_data(item_name=message.text)
        await state.set_state(fsm.Data_Collect.item_photo)
        await message.answer('Прикрепите фото "предмета" (или отправьте "пропустить")', reply_markup=kb.skip)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.restart)


# Дополнить исключения
@router.message(fsm.Data_Collect.item_photo)
async def item_photo_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if message.photo:
            await state.update_data(item_photo=message.photo[-1].file_id)
        elif message.text and message.text.capitalize() == 'Пропустить':
            await state.update_data(item_photo='Отсутствует')
        else:
            raise ValueError('Пожалуйста, прикрепите фото(сжатое) или отправьте "пропустить"')

        await state.set_state(fsm.Data_Collect.payment_type)
        await message.answer('Выберите способ оплаты или впишите свой:', reply_markup=kb.payment)
    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.skip)


@router.message(fsm.Data_Collect.payment_type)
async def payment_type_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if ((message.text != 'Карта') and (message.text != 'Перевод') and (message.text != 'Наличные')
                and (message.text != 'Юр. Лицо') and (message.text != 'Начать сначала')):
            raise ValueError('Пожалуйста используйте кнопки')

        await state.update_data(payment_type=message.text)
        await state.set_state(fsm.Data_Collect.payment_comment)
        await message.answer('Можете добавить информацию об оплате (например номер карты или имя держателя):',
                             reply_markup=kb.skip)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.payment)


@router.message(fsm.Data_Collect.payment_comment)
async def payment_comment_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if not (len(message.text) <= 40):
            raise ValueError('Длина не может превышать 40 сиволов')

        if message.text and message.text.capitalize() == 'Пропустить':
            await state.update_data(payment_comment='Отсутствует')
        else:
            await state.update_data(payment_comment=message.text)

        await state.set_state(fsm.Data_Collect.item_price)
        await message.answer('Введите цену в рублях:', reply_markup=kb.restart)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.skip)


@router.message(fsm.Data_Collect.item_price)
async def item_price_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if not re.match(r'^\d+(\.\d{1,2})?$', message.text):
            raise ValueError('Пожалуйста введите целое или вещественное число(исп. ".")')
        price = float(message.text)
        if price < 0:
            raise ValueError('Значение не может быть отрицательным')
        form_price = f'{price:.2f}'

        await state.update_data(item_price=form_price)
        await state.set_state(fsm.Data_Collect.payment_date)
        await message.answer('Введите дату по чеку "д/м":', reply_markup=kb.restart)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.restart)


# добавить исключение по формату
@router.message(fsm.Data_Collect.payment_date)
async def payment_date_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if not re.match('^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])$', message.text):
            raise ValueError('Пожалуйста введите дату согласно формату "д/м"')

        await state.update_data(payment_date=message.text)
        await state.set_state(fsm.Data_Collect.payment_photo)
        await message.answer('Прикрепите фото "чека" (или отправьте "пропустить")', reply_markup=kb.skip)

    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.restart)


@router.message(fsm.Data_Collect.payment_photo)
async def payment_photo_step_data_collect(message: Message, state: fsm.FSMContext):
    try:
        if message.photo:
            await state.update_data(payment_photo=message.photo[-1].file_id)
        elif message.text and message.text.capitalize() == 'Пропустить':
            await state.update_data(payment_photo='Отсутствует')
        else:
            raise ValueError('Пожалуйста, прикрепите фото(сжатое) или отправьте "пропустить"')

        await state.update_data(date=datetime.now().strftime('%d-%m-%Y %H:%M'), user_id=message.from_user.id,
                                user_name=f'@{message.from_user.username}',
                                user_personal_name=message.from_user.first_name)
        data = await state.get_data()
        await state.set_state(fsm.Data_Collect.confirmation)
        await message.answer('Данные записаны.', reply_markup=kb.remove)
        await message.answer(f'Пожалуйста, проверьте корректность внесённых данных.'
                             f'\n\nПроект: {str(data["project_name"]).capitalize()}'
                             f'\nОтветственный: {data["responsible"]}'
                             f'\nТип операции: {data["payment_status"]}'
                             f'\nНазвание покупки: {data["item_name"]}'
                             f'\nСпособ оплаты: {data["payment_type"]}'
                             f'\nКомментарий к оплате: {data["payment_comment"]}'
                             f'\nДата по чеку: {data["payment_date"]}'
                             f'\nЦена: {data["item_price"]}₽')

        if data['item_photo'] == 'Отсутствует' and data['payment_photo'] == 'Отсутствует':
            await message.answer('Прикреплённые фото отсутствуют')
        else:
            media_group = []
            if data['item_photo'] != 'Отсутствует':
                media_group.append(InputMediaPhoto(media=data['item_photo'], caption='Фото предмета:'))
            else:
                await message.answer('Фото чека: Отстутствует')
            if data['payment_photo'] != 'Отсутствует':
                media_group.append(InputMediaPhoto(media=data['payment_photo'], caption='Фото чека:'))
            else:
                await message.answer('Фото покупки: Отстутствует')
            await message.answer_media_group(media_group)

        await message.answer(f'Всё верно - Да\nЗаполнить заново - Нет', reply_markup=kb.choice)
    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.skip)


@router.message(fsm.Data_Collect.confirmation)
async def confirm_data(message: Message, state: fsm.FSMContext):
    data = await state.get_data()

    if message.text.lower() == 'да':
        try:
            if data['item_photo'] != 'Отсутствует':
                item_photo_path = await gdrive.download_photo(data['item_photo'])
                print(f'item path {item_photo_path}')
                item_photo_drive_id, item_photo_link = gdrive.upload_and_cleanup(item_photo_path,
                                                                                 f'item_photo_{data["date"]}.jpg')
                data['item_photo_drive_id'] = item_photo_drive_id
                data['item_photo_link'] = item_photo_link
                print(item_photo_drive_id)
                print(item_photo_link)

            if data['payment_photo'] != 'Отсутствует':
                payment_photo_path = await gdrive.download_photo(data['payment_photo'])
                print(f'payment path {payment_photo_path}')
                payment_photo_drive_id, payment_photo_link = gdrive.upload_and_cleanup(payment_photo_path,
                                                                                       f'payment_photo_{data["date"]}.jpg')
                data['payment_photo_drive_id'] = payment_photo_drive_id
                data['payment_photo_link'] = payment_photo_link
                print(payment_photo_drive_id)
                print(payment_photo_link)

            if data['payment_comment'] == 'Отсутствует':
                data['payment_comment'] = ''

            success_data_transfer = gtab.send_data_bot_to_sheets(data)
            if success_data_transfer:
                await message.answer('Данные успешно отправлены', reply_markup=kb.remove)
            else:
                await message.answer('Ошибка записи данных, попробуйте снова:', reply_markup=kb.remove)
        except Exception as e:
            await message.answer(f'{str(e)}. Попробуйте снова', reply_markup=kb.remove)

        await state.clear()
        await cmd_start(message)

    elif message.text.lower() == 'нет':
        await message.answer('Заполняем заново', reply_markup=kb.remove)
        await state.clear()
        await first_step_data_collect(message, state)
    else:
        await message.answer('Выберите "Да" или "Нет"')
