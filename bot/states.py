"""aiogram FSM holatlari."""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    name = State()
    phone = State()
    instagram = State()
    agree = State()          # qoidalarni qabul qilish


class SubmitVideo(StatesGroup):
    link = State()
    views = State()
    screenshot = State()
    confirm = State()


class UpdateViews(StatesGroup):
    views = State()
    screenshot = State()


class ExpoCreate(StatesGroup):
    title = State()
    desc = State()
    rules = State()
    prizes = State()
    start = State()
    end = State()
    confirm = State()


class BroadcastFlow(StatesGroup):
    choose_target = State()
    single_user = State()
    message = State()
    preview = State()
