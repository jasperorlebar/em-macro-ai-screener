from pathlib import Path

import pandas as pd
import yfinance as yf


DEFAULT_TICKERS = {
    "S&P 500": "^GSPC",
    "VIX": "^VIX",
    "Oil": "CL=F",
    "Copper": "HG=F",
    "Gold": "GC=F",
    "USD/MXN": "MXN=X",
    "USD/ZAR": "ZAR=X",
    "USD/BRL": "BRL=X",
    "USD/INR": "INR=X",
    "USD/TRY": "TRY=X",
}


def download_market_data(
    tickers: dict[str, str] = DEFAULT_TICKERS,
    start: str = "2015-01-01",
) -> pd.DataFrame:
    """
    Download cross-asset market data using yfinance.

    Returns a dataframe of adjusted close prices with clean column names.
    """
    data = yf.download(
        list(tickers.values()),
        start=start,
        auto_adjust=True,
        progress=False,
    )

    close = data["Close"]
    close.columns = list(tickers.keys())
    close = close.dropna(how="all")

    return close


def save_market_data(df: pd.DataFrame, path) -> None:
    """
    Save market data to CSV.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)