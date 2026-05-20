#!/usr/bin/env python3
"""
cli.py
------
Command-line interface for the Binance Futures Testnet Trading Bot.

Usage examples
--------------
# Market buy
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit sell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
"""

import argparse
import sys
from dotenv import load_dotenv
from bot.client import BinanceAPIError, NetworkError
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import ValidationError

load_dotenv()
logger = setup_logging()

# ── ANSI colours (degrade gracefully on Windows cmd) ──────────────────────────
_GREEN = "\033[92m"
_RED = "\033[91m"
_CYAN = "\033[96m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


# ── Presentation helpers ───────────────────────────────────────────────────────

def _print_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
) -> None:
    print(f"\n{_BOLD}{_CYAN}{'─' * 38}{_RESET}")
    print(f"{_BOLD}  Order Request Summary{_RESET}")
    print(f"{_CYAN}{'─' * 38}{_RESET}")
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    print(f"{_CYAN}{'─' * 38}{_RESET}\n")


def _print_response(response: dict) -> None:
    avg_price = response.get("avgPrice") or response.get("price", "N/A")
    print(f"{_BOLD}  Order Response{_RESET}")
    print(f"{_CYAN}{'─' * 38}{_RESET}")
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
    print(f"  Avg Price    : {avg_price}")
    print(f"{_CYAN}{'─' * 38}{_RESET}\n")


# ── Argument parser ────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot — places MARKET and LIMIT orders.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.001\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.001 --price 95000\n"
        ),
    )
    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol (e.g. BTCUSDT, ETHUSDT)",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        metavar="SIDE",
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        metavar="TYPE",
        help="Order type: MARKET or LIMIT",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        metavar="QTY",
        help="Order quantity (positive float, e.g. 0.001)",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        metavar="PRICE",
        help="Limit price — required for LIMIT orders, ignored for MARKET",
    )
    return parser


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    symbol: str = args.symbol.upper().strip()
    side: str = args.side.upper().strip()
    order_type: str = args.order_type.upper().strip()
    quantity: float = args.quantity
    price: float | None = args.price

    _print_summary(symbol, side, order_type, quantity, price)
    logger.info(
        "CLI INPUT | symbol=%s side=%s type=%s quantity=%s price=%s",
        symbol, side, order_type, quantity, price,
    )

    try:
        response = place_order(symbol, side, order_type, quantity, price)
    except ValidationError as exc:
        print(f"{_RED}❌ Validation Error:{_RESET} {exc}\n")
        logger.error("VALIDATION ERROR | %s", exc)
        sys.exit(1)
    except EnvironmentError as exc:
        print(f"{_RED}❌ Configuration Error:{_RESET} {exc}\n")
        logger.error("CONFIG ERROR | %s", exc)
        sys.exit(1)
    except BinanceAPIError as exc:
        print(f"{_RED}❌ API Error:{_RESET} {exc}\n")
        logger.error("API ERROR | %s", exc)
        sys.exit(1)
    except NetworkError as exc:
        print(f"{_RED}❌ Network Error:{_RESET} {exc}\n")
        logger.error("NETWORK ERROR | %s", exc)
        sys.exit(1)
    except Exception as exc:
        print(f"{_RED}❌ Unexpected Error:{_RESET} {exc}\n")
        logger.exception("UNEXPECTED ERROR | %s", exc)
        sys.exit(1)

    _print_response(response)
    print(f"{_GREEN}{_BOLD}✅ Order placed successfully!{_RESET}\n")
    logger.info(
        "ORDER SUCCESS | orderId=%s status=%s",
        response.get("orderId"),
        response.get("status"),
    )


if __name__ == "__main__":
    main()
