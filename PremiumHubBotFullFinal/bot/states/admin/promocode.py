"""Promocode admin FSM states."""

from aiogram.fsm.state import State, StatesGroup


class PromocodeStates(StatesGroup):
    waiting_for_promocode_data = State()
    waiting_for_delete_code = State()
