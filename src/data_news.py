from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests


GDELT_DOC_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


COUNTRY_QUERY_TERMS = {
    "Brazil": "Brazil OR Brasil",
    "Mexico": "Mexico",
    "South Africa": "\"South Africa\" OR rand",
    "India": "India",
    "Turkey": "Turkey OR Turkiye",
    "Chile": "Chile",
    "Colombia": "Colombia",
    "Indonesia": "Indonesia",
    "Poland": "Poland",
    "Hungary": "Hungary",
}


MACRO_QUERY_TERMS = (
    "inflation OR central bank OR interest rates OR fiscal OR debt OR deficit "
    "OR currency OR FX OR election OR protest OR commodity OR oil OR copper "
    "OR IMF OR downgrade OR growth OR recession"
)


def build_gdelt_query(country: str) -> str:
    """
    Build a GDELT query for country-specific macro/market news.
    """
    country_terms = COUNTRY_QUERY_TERMS.get(country, country)
    return f"({country_terms}) ({MACRO_QUERY_TERMS})"


def fetch_gdelt_articles(
    query: str,
    country: str,
    ccy: str,
    timespan: str = "7d",
    max_records: int = 50,
) -> pd.DataFrame:
    """
    Fetch recent GDELT article headlines for a given query.

    Parameters
    ----------
    query:
        GDELT search query.
    country:
        Country name used in project.
    ccy:
        Currency code used in project.
    timespan:
        GDELT relative time window, e.g. '1d', '7d', '30d'.
    max_records:
        Number of article records to request.

    Returns
    -------
    pd.DataFrame
        Article headline dataset.
    """
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "timespan": timespan,
        "maxrecords": max_records,
        "sort": "hybridrel",
    }

    response = requests.get(
        GDELT_DOC_API_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()
    articles = payload.get("articles", [])

    rows = []

    for article in articles:
        rows.append(
            {
                "country": country,
                "ccy": ccy,
                "date": article.get("seendate"),
                "headline": article.get("title"),
                "url": article.get("url"),
                "domain": article.get("domain"),
                "language": article.get("language"),
                "source_country": article.get("sourcecountry"),
            }
        )

    return pd.DataFrame(rows)


def fetch_news_for_countries(
    countries: pd.DataFrame,
    timespan: str = "7d",
    max_records_per_country: int = 50,
    pause_seconds: float = 1.0,
) -> pd.DataFrame:
    """
    Fetch GDELT macro headlines for each country in the project universe.

    countries must contain:
    country, ccy
    """
    all_results = []

    for _, row in countries.iterrows():
        country = row["country"]
        ccy = row["ccy"]

        query = build_gdelt_query(country)

        print(f"Fetching news for {country} ({ccy})...")
        print(f"Query: {query}")

        try:
            country_news = fetch_gdelt_articles(
                query=query,
                country=country,
                ccy=ccy,
                timespan=timespan,
                max_records=max_records_per_country,
            )

            all_results.append(country_news)

        except requests.HTTPError as exc:
            print(f"HTTP error fetching news for {country}: {exc}")

        except requests.RequestException as exc:
            print(f"Request error fetching news for {country}: {exc}")

        except ValueError as exc:
            print(f"Could not parse response for {country}: {exc}")

        time.sleep(pause_seconds)

    if not all_results:
        return pd.DataFrame(
            columns=[
                "country",
                "ccy",
                "date",
                "headline",
                "url",
                "domain",
                "language",
                "source_country",
            ]
        )

    news = pd.concat(all_results, ignore_index=True)

    news = news.dropna(subset=["headline"])
    news = news.drop_duplicates(subset=["country", "headline"])

    return news


def save_news_data(df: pd.DataFrame, path) -> None:
    """
    Save news dataset to CSV.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)