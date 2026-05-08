from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def calculate_returns(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert price data into daily percentage returns.
    """
    return price_data.pct_change().dropna()


def calculate_rolling_z_scores(
    returns: pd.DataFrame,
    window: int = 60,
) -> pd.DataFrame:
    """
    Calculate rolling z-scores of returns.

    This helps put variables like FX, equities, commodities and volatility
    onto a comparable scale.
    """
    z_scores = (returns - returns.rolling(window).mean()) / returns.rolling(window).std()
    return z_scores.dropna()


def fit_regime_model(
    z_scores: pd.DataFrame,
    features: list[str],
    n_clusters: int = 5,
) -> pd.DataFrame:
    """
    Fit a k-means model to classify market regimes.
    """
    model_data = z_scores[features].dropna().copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(model_data)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto",
    )

    model_data["regime"] = model.fit_predict(X_scaled)

    return model_data


def save_regime_data(df: pd.DataFrame, path) -> None:
    """
    Save regime classification output to CSV.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)