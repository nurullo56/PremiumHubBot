"""Admin user management states."""

from aiogram.fsm.state import State, StatesGroup


class UserManagementStates(StatesGroup):
    """User management FSM states."""

    waiting_for_balance_amount = State()
    waiting_for_premium_duration = State()
    waiting_for_ref_user_id = State()
