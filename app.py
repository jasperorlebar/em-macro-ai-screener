"""
EM Macro Regime & Vulnerability Screener
A prototype systematic EM macro research tool combining market regime detection
and country clustering by macro vulnerability.
"""

from pathlib import Path
import pandas as pd
import streamlit as st


# Page configuration
st.set_page_config(
    page_title="EM Macro AI Screener",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Data paths
MARKET_DATA_PATH = Path("data/raw/market_data.csv")
REGIME_DATA_PATH = Path("data/processed/regime_data.csv")
COUNTRY_CLUSTERS_PATH = Path("data/processed/country_clusters.csv")


st.title("🌍 EM Macro Regime & Vulnerability Screener")

st.markdown(
    """
    A prototype systematic EM macro research tool that combines:
    - **Cross-asset market data** (equities, commodities, FX, volatility)
    - **Unsupervised market regime detection** (clustering market environments)
    - **EM country macro clustering** (organizing the EM universe by vulnerability)
    
    The goal is to create a structured, interpretable research framework—not a black-box predictor.
    """
)

# Check for required data files
missing_files = []
if not MARKET_DATA_PATH.exists():
    missing_files.append("Market data (run: `python scripts/01_download_market_data.py`)")
if not REGIME_DATA_PATH.exists():
    missing_files.append("Regime data (run: `python scripts/02_regime_detection.py`)")
if not COUNTRY_CLUSTERS_PATH.exists():
    missing_files.append("Country clusters (run: `python scripts/03_country_clustering.py`)")

if missing_files:
    st.error("❌ Missing required data files:")
    for f in missing_files:
        st.write(f"  • {f}")
    st.stop()

# Load data
try:
    market_data = pd.read_csv(MARKET_DATA_PATH, index_col=0, parse_dates=True)
    regime_data = pd.read_csv(REGIME_DATA_PATH, index_col=0, parse_dates=True)
    country_clusters = pd.read_csv(COUNTRY_CLUSTERS_PATH)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Get latest regime
try:
    latest_regime = regime_data[["regime", "regime_name"]].iloc[-1]
except Exception as e:
    st.error(f"❌ Error reading regime data: {e}")
    st.stop()


st.header("1️⃣ Current Market Regime")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Regime", int(latest_regime["regime"]), delta=None)

with col2:
    st.metric("Regime Label", latest_regime["regime_name"])

with col3:
    st.metric("Data Points", len(regime_data))

st.divider()


st.header("2️⃣ Global Macro Market Data")

try:
    chart_cols = ["S&P 500", "VIX", "Oil", "Copper", "Gold"]
    available_cols = [col for col in chart_cols if col in market_data.columns]
    
    if available_cols:
        st.line_chart(market_data[available_cols], width='stretch')
    else:
        st.warning("⚠️ Required market data columns not found")
except Exception as e:
    st.error(f"❌ Error displaying chart: {e}")

st.divider()


st.header("3️⃣ EM Country Clusters")

try:
    cluster_display_cols = [
        "country",
        "ccy",
        "cluster",
        "inflation",
        "current_account_gdp",
        "government_debt_gdp",
        "gdp_growth",
        "commodity_score",
        "oil_importer_score",
        "china_exposure_score",
    ]
    
    # Only show columns that exist
    existing_cols = [col for col in cluster_display_cols if col in country_clusters.columns]
    
    st.dataframe(
        country_clusters[existing_cols],
        width='stretch',
        hide_index=True,
    )
except Exception as e:
    st.error(f"❌ Error displaying country clusters: {e}")

st.divider()


st.header("4️⃣ Latest Regime Detection Data")

try:
    st.dataframe(
        regime_data.tail(20),
        width='stretch',
    )
except Exception as e:
    st.error(f"❌ Error displaying regime data: {e}")

st.divider()


st.header("5️⃣ Interpretation Guide")

st.markdown(
    """
    The regime model uses cross-asset data to group market environments into clusters.
    These clusters currently have placeholder labels and should be manually interpreted
    using their average behaviour.

    The country clustering model groups EM currencies by macro vulnerability indicators.
    This helps organise the EM universe into economically meaningful groups, such as
    commodity-sensitive currencies, oil importers, higher-beta currencies, or more
    externally vulnerable economies.
    """
)