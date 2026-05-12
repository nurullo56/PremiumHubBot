"""User promocode FSM states."""

from aiogram.fsm.state import State, StatesGroup


class UserPromocodeStates(StatesGroup):
    waiting_for_code = State()
