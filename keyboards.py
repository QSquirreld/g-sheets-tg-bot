from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

remove = ReplyKeyboardRemove()

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить данные'), KeyboardButton(text='Помощь')]],
                           resize_keyboard=True,
                           input_field_placeholder='Нажмите кнопку или напишите "Отправить данные" в поле для ввода')

restart = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Начать сначала')]], resize_keyboard=True)

status = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Расход'), KeyboardButton(text='Возврат'), KeyboardButton(text='Начать сначала')]],
                             resize_keyboard=True,
                             input_field_placeholder='Выберите тип операции:')

skip = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Пропустить'), KeyboardButton(text='Начать сначала')]],
                            resize_keyboard=True,
                            input_field_placeholder='Этот шаг можно пропустить')

payment = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Карта'), KeyboardButton(text='Перевод')],
                                        [KeyboardButton(text='Наличные'), KeyboardButton(text='Юр. Лицо')],
                                        [KeyboardButton(text='Начать сначала')]],
                              resize_keyboard=True,
                              input_field_placeholder='Нажмите кнопку или впишите свой вариант')

choice = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]],
                             resize_keyboard=True,
                             input_field_placeholder='Пожалуйста, проверьте корректность внесённых данных. (Да/Нет)')
