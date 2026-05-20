"""
orders.py
---------
Business-logic layer for order placement.

Bridges the CLI ↔ client layers:
  1. Validates user inputs (delegates to validators.py)
  2. Builds the Binance-compliant parameter dict
  3. Calls the client and returns the raw response
"""

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging
from bot.validators import validate_inputs

logger = setup_logging()


def build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
) -> dict:
    """
    Construct and validate the parameter dict for a Binance Futures order.

    Args:
        symbol:     Trading pair, e.g. "BTCUSDT".
        side:       "BUY" or "SELL".
        order_type: "MARKET" or "LIMIT".
        quantity:   Positive float.
        price:      Required for LIMIT orders; ignored for MARKET.

    Returns:
        Dict ready to be signed and POSTed.

    Raises:
        ValidationError: If any argument fails validation.
    """
    symbol, side, order_type = validate_inputs(
        symbol, side, order_type, quantity, price
    )

    params: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"  # Good-Till-Cancelled

    logger.debug("ORDER PARAMS | %s", params)
    return params


def place_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
) -> dict:
    """
    Validate inputs, build params, and submit the order to Binance Testnet.

    Returns:
        Parsed Binance API response dict.

    Raises:
        ValidationError:  Bad input.
        BinanceAPIError:  Binance rejected the request.
        NetworkError:     Connection / timeout failure.
        EnvironmentError: Missing API credentials.
    """
    params = build_order_params(symbol, side, order_type, quantity, price)
    client = BinanceFuturesClient()
    return client.place_order(params)
