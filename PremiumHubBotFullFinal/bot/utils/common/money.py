"""Money utilities: integer scaling and display formatting for balances."""

from decimal import Decimal

SCALE = 100  # 1 olmos = 100 cents (2 decimal places of precision)


def to_scaled(amount: Decimal) -> int:
    """Convert Decimal olmos amount to scaled integer (cents)."""
    return int(amount * SCALE)


def from_scaled(scaled: int) -> Decimal:
    """Convert scaled integer (cents) back to Decimal olmos amount."""
    return Decimal(scaled) / SCALE


def format_balance(balance: Decimal) -> str:
    """Format balance for Telegram message display."""
    if balance == int(balance):
        return f"{int(balance):,}💎"
    return f"{balance:,.2f}💎"
