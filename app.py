#!/usr/bin/env python3
"""
Market Data Analysis Script
Downloads and analyzes global macro market variables
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def download_market_data():
    """Download market data from Yahoo Finance"""
    
    tickers = {
        "S&P 500": "^GSPC",
        "VIX": "^VIX",
        "Oil": "CL=F",
        "Copper": "HG=F",
        "Gold": "GC=F",
        "USD/MXN": "MXN=X",
        "USD/ZAR": "ZAR=X",
        "USD/BRL": "BRL=X",
        "USD/INR": "INR=X",
        "USD/TRY": "TRY=X"
    }
    
    print("Downloading market data...")
    raw = yf.download(
        list(tickers.values()),
        start="2015-01-01",
        auto_adjust=True
    )["Close"]
    
    raw.columns = tickers.keys()
    raw = raw.dropna(how="all")
    
    print("\nLast 5 rows of data:")
    print(raw.tail())
    
    # Save to CSV
    raw.to_csv("data/raw/market_data.csv")
    print("\nData saved to data/raw/market_data.csv")
    
    # Create plot
    raw[["S&P 500", "VIX", "Oil", "Copper", "Gold"]].plot(figsize=(12, 6))
    plt.title("Global Macro Market Variables")
    plt.savefig("reports/figures/market_data_plot.png")
    print("Plot saved to reports/figures/market_data_plot.png")
    plt.show()
    
    return raw

if __name__ == "__main__":
    download_market_data()
