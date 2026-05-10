from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.country_clustering import fit_country_clustering, save_country_clusters


INPUT_PATH = Path("data/processed/country_macro_real.csv")
OUTPUT_PATH = Path("data/processed/country_clusters.csv")
FIGURE_PATH = Path("reports/figures/country_clusters.png")


FEATURES = [
    "inflation",
    "current_account_gdp",
    "government_debt_gdp",
    "gdp_growth",
    "external_debt_gni",
    "reserves_gdp",
    "commodity_score",
    "oil_importer_score",
    "china_exposure_score",
]


def main() -> None:
    print("Loading country macro data...")

    macro_data = pd.read_csv(INPUT_PATH)

    print("\nMissing values before imputation:")
    print(macro_data[FEATURES].isna().sum())

    for col in FEATURES:
        macro_data[col] = pd.to_numeric(macro_data[col], errors="coerce")

    macro_data[FEATURES] = macro_data[FEATURES].fillna(
        macro_data[FEATURES].median()
    )

    print("\nMissing values after imputation:")
    print(macro_data[FEATURES].isna().sum())

    print("Fitting country clustering model...")

    clustered = fit_country_clustering(
        macro_data=macro_data,
        features=FEATURES,
        n_clusters=3,
    )

    save_country_clusters(clustered, OUTPUT_PATH)

    print(f"Saved country clusters to {OUTPUT_PATH}")
    print("\nClustered countries:")
    print(clustered[["country", "ccy", "cluster", "pca_1", "pca_2"]])

    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 7))

    for _, row in clustered.iterrows():
        plt.scatter(
            row["pca_1"],
            row["pca_2"],
            c=f"C{int(row['cluster'])}",
            s=90,
        )
        plt.text(
            row["pca_1"] + 0.03,
            row["pca_2"] + 0.03,
            row["ccy"],
        )

    plt.axhline(0, linewidth=0.5)
    plt.axvline(0, linewidth=0.5)
    plt.title("EM Country Clustering by Macro Vulnerability")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.tight_layout()
    plt.savefig(FIGURE_PATH, dpi=200)
    plt.close()

    print(f"Saved figure to {FIGURE_PATH}")


if __name__ == "__main__":
    main()