"""
client.py
---------
Low-level Binance Futures Testnet REST client.

Responsibilities:
  - HMAC-SHA256 request signing
  - HTTP session management
  - Raw API call with structured logging
  - Raising typed exceptions on HTTP / network errors
"""

import hashlib
import hmac
import os
import time
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logging

logger = setup_logging()

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
ORDER_ENDPOINT = "/fapi/v1/order"
REQUEST_TIMEOUT_S = 10


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx HTTP response."""

    def __init__(self, message: str, code: int | None = None):
        self.code = code
        super().__init__(f"Binance API Error (code={code}): {message}")


class NetworkError(Exception):
    """Raised on connection / timeout failures."""


class BinanceFuturesClient:
    """
    Thin wrapper around the Binance Futures Testnet REST API.

    API credentials are read from environment variables:
        BINANCE_API_KEY
        BINANCE_API_SECRET
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("BINANCE_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            raise EnvironmentError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set as "
                "environment variables (or passed explicitly)."
            )

        self._session = requests.Session()
        self._session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def place_order(self, params: dict) -> dict:
        """
        POST /fapi/v1/order with HMAC signing.

        Args:
            params: Order parameters (symbol, side, type, quantity, …).

        Returns:
            Parsed JSON response dict from Binance.

        Raises:
            BinanceAPIError: Non-2xx Binance response.
            NetworkError:    Connection / timeout failure.
        """
        url = TESTNET_BASE_URL + ORDER_ENDPOINT
        signed = self._sign(params.copy())

        logger.info("REQUEST  | POST %s | params=%s", url, self._redact(signed))

        try:
            response = self._session.post(
                url,
                data=signed,
                timeout=REQUEST_TIMEOUT_S,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as exc:
            error_body: dict = {}
            try:
                error_body = exc.response.json()
            except Exception:
                pass
            logger.error(
                "HTTP ERROR | status=%s | body=%s",
                exc.response.status_code,
                error_body,
            )
            raise BinanceAPIError(
                error_body.get("msg", str(exc)),
                error_body.get("code"),
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            logger.error("NETWORK ERROR | %s", exc)
            raise NetworkError(
                f"Unable to reach Binance Testnet ({TESTNET_BASE_URL}). "
                "Check your internet connection."
            ) from exc

        except requests.exceptions.Timeout as exc:
            logger.error("TIMEOUT | %s", exc)
            raise NetworkError(
                f"Request timed out after {REQUEST_TIMEOUT_S}s."
            ) from exc

        data: dict = response.json()
        logger.info(
            "RESPONSE | status=%s | body=%s", response.status_code, data
        )
        return data

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append timestamp + HMAC-SHA256 signature to params dict."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    @staticmethod
    def _redact(params: dict) -> dict:
        """Return a copy of params with the signature partially masked."""
        p = params.copy()
        if "signature" in p:
            p["signature"] = p["signature"][:8] + "…"
        return p
