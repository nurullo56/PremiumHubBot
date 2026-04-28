"""Channel management FSM states."""

from aiogram.fsm.state import State, StatesGroup


class ChannelStates(StatesGroup):
    waiting_for_channel_input = State()
