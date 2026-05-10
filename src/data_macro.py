from __future__ import annotations

from pathlib import Path
from typing import Any
import time

import pandas as pd
import requests


WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"


INDICATORS = {
    "inflation": "FP.CPI.TOTL.ZG",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "current_account_gdp": "BN.CAB.XOKA.GD.ZS",
    "government_debt_gdp": "GC.DOD.TOTL.GD.ZS",
    "external_debt_gni": "DT.DOD.DECT.GN.ZS",
    "total_reserves_usd": "FI.RES.TOTL.CD",
    "gdp_current_usd": "NY.GDP.MKTP.CD",
}


def fetch_world_bank_indicator(
    iso3: str,
    indicator_code: str,
    start_year: int = 2015,
    end_year: int = 2025,
) -> pd.DataFrame:
    """
    Fetch a single World Bank indicator for one country with retry logic.

    Returns a dataframe with columns:
    iso3, year, indicator_code, value
    """
    url = f"{WORLD_BANK_BASE_URL}/country/{iso3}/indicator/{indicator_code}"

    params = {
        "format": "json",
        "per_page": 20000,
        "date": f"{start_year}:{end_year}",
    }

    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=180)
            response.raise_for_status()
            
            payload: list[Any] = response.json()

            if len(payload) < 2 or payload[1] is None:
                return pd.DataFrame(
                    columns=["iso3", "year", "indicator_code", "value"]
                )

            rows = []

            for item in payload[1]:
                rows.append(
                    {
                        "iso3": iso3,
                        "year": int(item["date"]),
                        "indicator_code": indicator_code,
                        "value": item["value"],
                    }
                )

            df = pd.DataFrame(rows)
            df = df.dropna(subset=["value"])
            
            return df
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"  Timeout on attempt {attempt + 1}, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"  Failed after {max_retries} attempts, returning empty...")
                return pd.DataFrame(
                    columns=["iso3", "year", "indicator_code", "value"]
                )
        except requests.exceptions.RequestException as e:
            print(f"  Error: {e}")
            return pd.DataFrame(
                columns=["iso3", "year", "indicator_code", "value"]
            )


def latest_available_value(series: pd.DataFrame) -> tuple:
    """
    Return the latest non-null value and year from a World Bank indicator series.
    """
    if series.empty:
        return None, None

    clean = series.dropna(subset=["value"]).sort_values("year", ascending=False)

    if clean.empty:
        return None, None

    latest = clean.iloc[0]
    return float(latest["value"]), int(latest["year"])


def build_world_bank_macro_dataset(
    countries: pd.DataFrame,
    start_year: int = 2015,
    end_year: int = 2025,
) -> pd.DataFrame:
    """
    Build a latest-available macro dataset for selected countries.

    countries must contain:
    country, iso3, ccy
    """
    output_rows = []

    for idx, (_, country_row) in enumerate(countries.iterrows()):
        country_name = country_row["country"]
        iso3 = country_row["iso3"]
        ccy = country_row["ccy"]

        print(f"[{idx+1}/{len(countries)}] Fetching World Bank data for {country_name} ({iso3})...")
        
        # Be respectful to the API - wait between requests
        if idx > 0:
            time.sleep(1)

        row = {
            "country": country_name,
            "iso3": iso3,
            "ccy": ccy,
        }

        raw_series = {}

        for clean_name, indicator_code in INDICATORS.items():
            series = fetch_world_bank_indicator(
                iso3=iso3,
                indicator_code=indicator_code,
                start_year=start_year,
                end_year=end_year,
            )

            raw_series[clean_name] = series

            value, year = latest_available_value(series)

            row[clean_name] = value
            row[f"{clean_name}_year"] = year

        # Calculate reserves as % of GDP using the latest year where both exist.
        reserves = raw_series["total_reserves_usd"].rename(
            columns={"value": "total_reserves_usd"}
        )
        gdp = raw_series["gdp_current_usd"].rename(
            columns={"value": "gdp_current_usd"}
        )

        if not reserves.empty and not gdp.empty:
            merged = reserves[["year", "total_reserves_usd"]].merge(
                gdp[["year", "gdp_current_usd"]],
                on="year",
                how="inner",
            )
            merged = merged.dropna()

            if not merged.empty:
                merged["reserves_gdp"] = (
                    merged["total_reserves_usd"] / merged["gdp_current_usd"] * 100
                )
                latest_reserves = merged.sort_values(
                    "year",
                    ascending=False,
                ).iloc[0]

                row["reserves_gdp"] = float(latest_reserves["reserves_gdp"])
                row["reserves_gdp_year"] = int(latest_reserves["year"])
            else:
                row["reserves_gdp"] = None
                row["reserves_gdp_year"] = None
        else:
            row["reserves_gdp"] = None
            row["reserves_gdp_year"] = None

        output_rows.append(row)

    return pd.DataFrame(output_rows)


def save_macro_data(df: pd.DataFrame, path) -> None:
    """
    Save macro dataset to CSV.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)