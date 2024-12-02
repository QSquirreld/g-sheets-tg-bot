from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class Data_Collect(StatesGroup):
    project_name = State()
    responsible = State()
    payment_status = State()
    item_name = State()
    item_photo = State()
    payment_type = State()
    payment_comment = State()
    item_price = State()
    payment_date = State()
    payment_photo = State()

    confirmation = State()
