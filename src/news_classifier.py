import pandas as pd


THEME_KEYWORDS = {
    "fiscal_stress": [
        "debt",
        "deficit",
        "budget",
        "downgrade",
        "fiscal",
        "default",
    ],
    "political_instability": [
        "election",
        "protest",
        "coalition",
        "corruption",
        "unrest",
    ],
    "hawkish_central_bank": [
        "rate hike",
        "higher for longer",
        "tightening",
        "inflation",
        "hawkish",
    ],
    "dovish_central_bank": [
        "rate cut",
        "easing",
        "slowdown",
        "dovish",
    ],
    "commodity_shock": [
        "oil",
        "copper",
        "commodity",
        "supply",
        "exports",
    ],
    "china_weakness": [
        "china slowdown",
        "china weakness",
        "property crisis",
        "stimulus hopes",
    ],
    "sovereign_risk": [
        "imf",
        "default",
        "restructuring",
        "bond spread",
        "credit rating",
    ],
    "positive_reform": [
        "reform",
        "investment",
        "upgrade",
        "growth",
        "stability",
    ],
}


THEME_RISK_WEIGHTS = {
    "fiscal_stress": 80,
    "political_instability": 75,
    "hawkish_central_bank": 45,
    "dovish_central_bank": 50,
    "commodity_shock": 55,
    "china_weakness": 70,
    "sovereign_risk": 90,
    "positive_reform": -30,
    "unclassified": 0,
}


def classify_headline(headline: str) -> str:
    """
    Classify a headline into a macro news theme using simple keyword matching.
    """
    text = headline.lower()

    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return theme

    return "unclassified"


def classify_news(news_data: pd.DataFrame) -> pd.DataFrame:
    """
    Add news theme and risk score columns to a headline dataset.
    """
    output = news_data.copy()

    output["news_theme"] = output["headline"].apply(classify_headline)
    output["headline_risk_score"] = output["news_theme"].map(THEME_RISK_WEIGHTS)

    return output


def calculate_country_news_scores(classified_news: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate classified headlines into a country-level news risk score.
    """
    grouped = (
        classified_news.groupby(["country", "ccy"])
        .agg(
            headline_count=("headline", "count"),
            news_risk_score=("headline_risk_score", "mean"),
            dominant_theme=("news_theme", lambda x: x.value_counts().index[0]),
        )
        .reset_index()
    )

    return grouped.sort_values("news_risk_score", ascending=False)
