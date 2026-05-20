"""
validators.py
-------------
Pure validation functions — no I/O, no side-effects.
Raises ValidationError with a human-readable message on failure.
"""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(Exception):
    """Raised when CLI input fails business-rule validation."""


def validate_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
) -> tuple[str, str, str]:
    """
    Validate and normalise trading inputs.

    Returns:
        (symbol, side, order_type) — all upper-cased and stripped.

    Raises:
        ValidationError: on any rule violation.
    """
    # --- Symbol ---
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol cannot be empty.")
    symbol = symbol.strip().upper()

    # --- Side ---
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Allowed values: {', '.join(sorted(VALID_SIDES))}."
        )

    # --- Order type ---
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. "
            f"Allowed values: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    # --- Quantity ---
    if quantity is None:
        raise ValidationError("Quantity is required.")
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        raise ValidationError(
            f"Quantity must be a positive number, got '{quantity}'."
        )

    # --- Price (LIMIT only) ---
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValidationError(
                f"Price must be a positive number, got '{price}'."
            )

    return symbol, side, order_type
