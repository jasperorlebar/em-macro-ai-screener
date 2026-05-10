from pathlib import Path

import pandas as pd

from src.data_macro import build_world_bank_macro_dataset, save_macro_data


EXPOSURE_INPUT_PATH = Path("data/inputs/country_exposure_scores.csv")
MACRO_OUTPUT_PATH = Path("data/processed/country_macro_real.csv")


def main() -> None:
    print("Loading country list and exposure scores...")
    print(f"Looking for file: {EXPOSURE_INPUT_PATH}")

    countries = pd.read_csv(EXPOSURE_INPUT_PATH)
    print(f"Loaded {len(countries)} countries")

    required_cols = {"country", "iso3", "ccy"}

    missing_cols = required_cols - set(countries.columns)

    if missing_cols:
        raise ValueError(
            f"Missing required columns in {EXPOSURE_INPUT_PATH}: {missing_cols}"
        )

    print("Downloading real macro data from World Bank...")
    print("This may take 1-2 minutes...")

    macro_data = build_world_bank_macro_dataset(
        countries=countries[["country", "iso3", "ccy"]],
        start_year=2015,
        end_year=2025,
    )

    print(f"Downloaded data for {len(macro_data)} countries")
    print("Merging real macro data with manual exposure scores...")

    exposure_cols = [
        "country",
        "iso3",
        "ccy",
        "commodity_score",
        "oil_importer_score",
        "china_exposure_score",
    ]

    final = macro_data.merge(
        countries[exposure_cols],
        on=["country", "iso3", "ccy"],
        how="left",
    )

    save_macro_data(final, MACRO_OUTPUT_PATH)

    print(f"Saved real macro dataset to {MACRO_OUTPUT_PATH}")

    display_cols = [
        "country",
        "ccy",
        "inflation",
        "gdp_growth",
        "current_account_gdp",
        "government_debt_gdp",
        "external_debt_gni",
        "reserves_gdp",
        "commodity_score",
        "oil_importer_score",
        "china_exposure_score",
    ]

    print(final[display_cols])


if __name__ == "__main__":
    main()