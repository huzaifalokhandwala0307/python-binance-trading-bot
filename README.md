# Binance Futures Testnet Trading Bot

A Python-based CLI trading bot for Binance Futures Testnet (USDT-M) that supports **MARKET** and **LIMIT** orders with BUY/SELL functionality.  
The project is built with clean architecture, input validation, logging, and robust error handling.

---

## Folder Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance Futures REST client (signing, HTTP, errors)
│   ├── orders.py            # Order-placement business logic
│   ├── validators.py        # Input validation rules
│   └── logging_config.py   # Rotating file + console logger
├── logs/
│   └── sample_trading_bot.log   # Example log output (committed for reference)
|   └── trading_bot.log  # original logs
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # Credential template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Prerequisites

- Python **3.10+** (uses `X | Y` union type hints)
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

### 2. Get Testnet API Credentials

1. Go to <https://testnet.binancefuture.com> and log in (GitHub OAuth).
2. Click **API Key** in the top-right → **Generate API keys**.
3. Copy the **API Key** and **Secret Key** — they are shown only once.

### 3. Clone / Download the Project

```bash
git clone https://github.com/your-username/trading_bot.git
```

### 4. Create a Virtual Environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (cmd)
.venv\Scripts\activate.bat
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure API Credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

Then export them into your shell:

```bash
# macOS / Linux
export $(grep -v '^#' .env | xargs)

# Windows PowerShell
Get-Content .env | Where-Object { $_ -notmatch '^#' } | ForEach-Object {
    $name, $value = $_ -split '=', 2
    [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
}
```

---

## Run Examples

### MARKET BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Output:**

```
──────────────────────────────────────
  Order Request Summary
──────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
──────────────────────────────────────

  Order Response
──────────────────────────────────────
  Order ID     : 3851920471
  Status       : FILLED
  Executed Qty : 0.001
  Avg Price    : 57823.40
──────────────────────────────────────

✅ Order placed successfully!
```

---

### LIMIT SELL

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
```

**Output:**

```
──────────────────────────────────────
  Order Request Summary
──────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : SELL
  Type       : LIMIT
  Quantity   : 0.001
  Price      : 95000.0
──────────────────────────────────────

  Order Response
──────────────────────────────────────
  Order ID     : 3851924882
  Status       : NEW
  Executed Qty : 0.000
  Avg Price    : 95000.00
──────────────────────────────────────

✅ Order placed successfully!
```

---

### MARKET SELL

```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

---

### Help / All Options

```bash
python cli.py --help
```

---

## Logging

All requests, responses, and errors are written to `logs/trading_bot.log` (rotating, max 5 MB × 3 backups).

Only `WARNING`-level messages and above appear on the console to keep output clean.

A representative sample is committed at `logs/sample_trading_bot.log`.

---

## Assumptions

| # | Assumption |
|---|------------|
| 1 | **Testnet only.** All orders are sent to `https://testnet.binancefuture.com`. No mainnet keys are ever used. |
| 2 | **USDT-M perpetual futures.** The bot targets the `/fapi/v1/order` endpoint (USDT-margined contracts). |
| 3 | **LIMIT orders use GTC (Good-Till-Cancelled)** time-in-force. This is the most common default and requires no additional CLI flag. |
| 4 | **Credentials via environment variables.** `BINANCE_API_KEY` and `BINANCE_API_SECRET` must be exported before running. The `.env` file is never committed. |
| 5 | **No persistence.** The bot is stateless; it places one order per invocation and exits. |
| 6 | **Python 3.10+** is required for `X | Y` union type syntax. On older Python 3.x, replace `float | None` with `Optional[float]` from `typing`. |
| 7 | **Quantity precision** is the caller's responsibility. Binance enforces per-symbol lot-size filters; an invalid quantity will return a Binance API error, which is caught and displayed. |
| 8 | **Single dependency** (`requests`). No Binance SDK is used — direct REST calls keep the project dependency-minimal and avoid SDK version drift. |

---

## Error Handling Summary

| Scenario | Behaviour |
|---|---|
| Missing `--price` for LIMIT | `ValidationError` → printed + logged, exit 1 |
| Invalid side / type | `ValidationError` → printed + logged, exit 1 |
| Non-positive quantity or price | `ValidationError` → printed + logged, exit 1 |
| Invalid symbol (Binance rejects) | `BinanceAPIError` with Binance code/msg → printed + logged, exit 1 |
| Network unreachable / timeout | `NetworkError` → printed + logged, exit 1 |
| Missing API credentials | `EnvironmentError` → printed + logged, exit 1 |
