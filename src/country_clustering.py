from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def fit_country_clustering(
    macro_data: pd.DataFrame,
    features: list[str],
    n_clusters: int = 3,
) -> pd.DataFrame:
    """
    Cluster EM countries by macro vulnerability indicators.
    """
    output = macro_data.copy()

    X = output[features].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    coords = pca.fit_transform(X_scaled)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto",
    )

    clusters = model.fit_predict(X_scaled)

    output.loc[X.index, "cluster"] = clusters
    output.loc[X.index, "pca_1"] = coords[:, 0]
    output.loc[X.index, "pca_2"] = coords[:, 1]

    return output


def save_country_clusters(df: pd.DataFrame, path) -> None:
    """
    Save country clustering output to CSV.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)