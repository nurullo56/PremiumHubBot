"""Broadcast FSM states."""

from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_target = State()
    waiting_for_confirm = State()
