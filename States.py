from aiogram.dispatcher.filters.state import StatesGroup, State

class States(StatesGroup):
    Mail = State()

    Code = State()

    City = State()

    Phone = State()

    EnterPhone = State()

    GetToken = State()