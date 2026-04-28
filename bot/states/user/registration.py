"""User registration FSM states."""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_captcha = State()
    waiting_for_gender = State()
    waiting_for_phone = State()
    waiting_for_subscription = State()
