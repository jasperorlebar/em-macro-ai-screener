from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


MARKET_DATA_PATH = Path("data/raw/market_data.csv")
REGIME_DATA_PATH = Path("data/processed/regime_data.csv")
COUNTRY_CLUSTERS_PATH = Path("data/processed/country_clusters.csv")
VULNERABILITY_SCORES_PATH = Path("data/processed/vulnerability_scores.csv")
TRADE_IDEAS_PATH = Path("data/processed/trade_ideas.csv")


st.set_page_config(
    page_title="EM Macro AI Screener",
    layout="wide",
)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load generated project datasets.
    """
    missing_files = []

    for path in [
        MARKET_DATA_PATH,
        REGIME_DATA_PATH,
        COUNTRY_CLUSTERS_PATH,
        VULNERABILITY_SCORES_PATH,
        TRADE_IDEAS_PATH,
    ]:
        if not path.exists():
            missing_files.append(str(path))

    if missing_files:
        st.error("Some required data files are missing.")
        st.code(
            "python scripts/run_pipeline.py\nstreamlit run app.py",
            language="bash",
        )
        st.write("Missing files:")
        for file in missing_files:
            st.write(f"- {file}")
        st.stop()

    market_data = pd.read_csv(MARKET_DATA_PATH, index_col=0, parse_dates=True)
    regime_data = pd.read_csv(REGIME_DATA_PATH, index_col=0, parse_dates=True)
    country_clusters = pd.read_csv(COUNTRY_CLUSTERS_PATH)
    vulnerability_scores = pd.read_csv(VULNERABILITY_SCORES_PATH)
    trade_ideas = pd.read_csv(TRADE_IDEAS_PATH)

    return market_data, regime_data, country_clusters, vulnerability_scores, trade_ideas


def index_to_100(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rebase series to 100 for easier visual comparison.
    """
    clean = df.dropna()
    return clean / clean.iloc[0] * 100


market_data, regime_data, country_clusters, vulnerability_scores, trade_ideas = load_data()

latest_regime = regime_data[["regime", "regime_name"]].iloc[-1]


st.title("EM Macro Regime & Vulnerability Screener")

st.markdown(
    """
    A prototype systematic EM macro research tool combining market regime detection,
    country-level macro clustering, and eventually AI-based news classification.

    The aim is **not** to build a black-box FX predictor. The aim is to organise
    noisy macro and market information into an interpretable research framework.
    """
)


overview_tab, regime_tab, country_tab, screener_tab, methodology_tab, limitations_tab = st.tabs(
    [
        "Overview",
        "Market Regime",
        "Country Clusters",
        "Vulnerability Screener",
        "Methodology",
        "Limitations",
    ]
)


with overview_tab:
    st.header("Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Latest Detected Regime", int(latest_regime["regime"]))

    with col2:
        st.metric("Regime Label", latest_regime["regime_name"])

    with col3:
        st.metric("EM Countries Covered", len(country_clusters))

    st.subheader("Latest Country Clusters")

    st.dataframe(
        country_clusters[
            [
                "country",
                "ccy",
                "cluster",
                "inflation",
                "current_account_gdp",
                "government_debt_gdp",
                "gdp_growth",
            ]
        ],
        use_container_width=True,
    )

    st.info(
        "Current country macro data is toy/placeholder data used to test the project pipeline. "
        "A later version will replace this with sourced World Bank/IMF data."
    )


with regime_tab:
    st.header("Market Regime Detection")

    st.markdown(
        """
        The regime model uses cross-asset market data and k-means clustering to group
        similar market environments. Regime labels are currently placeholders and should
        be manually interpreted using the cluster summary.
        """
    )

    chart_cols = ["S&P 500", "VIX", "Oil", "Copper", "Gold"]

    st.subheader("Global Macro Variables Indexed to 100")

    indexed_market_data = index_to_100(market_data[chart_cols])
    st.line_chart(indexed_market_data)

    st.subheader("Regime Timeline")

    regime_plot = regime_data.copy()
    regime_plot["date"] = regime_plot.index
    regime_plot["s_and_p_500"] = market_data.loc[regime_plot.index, "S&P 500"]

    fig = px.scatter(
        regime_plot,
        x="date",
        y="s_and_p_500",
        color="regime_name",
        title="Unsupervised Market Regime Classification",
        labels={
            "date": "Date",
            "s_and_p_500": "S&P 500",
            "regime_name": "Regime",
        },
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Latest Regime Data")
    st.dataframe(regime_data.tail(20), use_container_width=True)


with country_tab:
    st.header("EM Country Clustering")

    st.markdown(
        """
        The country model uses macro vulnerability indicators to group EM countries.
        The current version uses toy data, but the structure is designed so that real
        sourced macro data can replace it later.
        """
    )

    fig = px.scatter(
        country_clusters,
        x="pca_1",
        y="pca_2",
        color=country_clusters["cluster"].astype(str),
        text="ccy",
        hover_data=[
            "country",
            "inflation",
            "current_account_gdp",
            "government_debt_gdp",
            "gdp_growth",
            "commodity_score",
            "oil_importer_score",
            "china_exposure_score",
        ],
        title="EM Country Clustering by Macro Vulnerability",
        labels={
            "pca_1": "PCA 1",
            "pca_2": "PCA 2",
            "color": "Cluster",
        },
    )

    fig.update_traces(textposition="top center")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Country Macro Dataset")

    st.dataframe(country_clusters, use_container_width=True)


with screener_tab:
    st.header("EM Vulnerability Screener")

    st.markdown(
        """
        This section ranks EM currencies by a transparent vulnerability score.

        The score combines structural macro indicators with a regime-aware adjustment.
        It is not a trading recommendation; it is a research tool for identifying
        currencies that may deserve further investigation.
        """
    )

    col1, col2 = st.columns(2)

    most_vulnerable = vulnerability_scores.iloc[0]
    least_vulnerable = vulnerability_scores.iloc[-1]

    with col1:
        st.metric(
            "Most Vulnerable Currency",
            most_vulnerable["ccy"],
            f"{most_vulnerable['final_vulnerability_score']:.1f}",
        )

    with col2:
        st.metric(
            "Most Resilient Currency",
            least_vulnerable["ccy"],
            f"{least_vulnerable['final_vulnerability_score']:.1f}",
        )

    st.subheader("Vulnerability Ranking")

    ranking_cols = [
        "country",
        "ccy",
        "cluster",
        "structural_vulnerability_score",
        "regime_adjustment",
        "final_vulnerability_score",
        "regime_rationale",
    ]

    st.dataframe(
        vulnerability_scores[ranking_cols],
        use_container_width=True,
    )

    st.subheader("Final Vulnerability Scores")

    score_chart = vulnerability_scores.sort_values(
        "final_vulnerability_score",
        ascending=True,
    )

    st.bar_chart(
        score_chart.set_index("ccy")["final_vulnerability_score"]
    )

    st.subheader("Screened Relative-Value Ideas")

    st.markdown(
        """
        These are not trade recommendations. They are automatically generated research
        prompts based on the gap between relatively resilient and vulnerable currencies.
        """
    )

    st.dataframe(
        trade_ideas,
        use_container_width=True,
    )


with methodology_tab:
    st.header("Methodology")

    st.subheader("1. Market Data Pipeline")

    st.markdown(
        """
        The first script downloads cross-asset market data, including equities,
        volatility, commodities, gold and selected EM FX pairs.
        """
    )

    st.code("python scripts/01_download_market_data.py", language="bash")

    st.subheader("2. Regime Detection")

    st.markdown(
        """
        The regime model converts market prices into returns, calculates rolling
        z-scores, and then applies k-means clustering. This produces unsupervised
        market regimes.
        """
    )

    st.code("python scripts/02_regime_detection.py", language="bash")

    st.subheader("3. Country Clustering")

    st.markdown(
        """
        The country model uses PCA and k-means clustering to group EM countries by
        macro vulnerability indicators.
        """
    )

    st.code("python scripts/03_country_clustering.py", language="bash")


with limitations_tab:
    st.header("Limitations and Next Steps")

    st.subheader("Current Limitations")

    st.markdown(
        """
        - Country macro data is currently toy/placeholder data.
        - Free market data is not institutional quality.
        - Regime labels currently require manual interpretation.
        - No transaction cost or liquidity modelling is included.
        - No positioning data is included.
        - This is a research screener, not an automated trading system.
        """
    )

    st.subheader("Next Steps")

    st.markdown(
        """
        - Replace toy country data with World Bank/IMF indicators.
        - Add vulnerability scoring.
        - Add NLP-based news classification.
        - Add a trade idea screener.
        - Add simple backtesting by regime.
        """
    )