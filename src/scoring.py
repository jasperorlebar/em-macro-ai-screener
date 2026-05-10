import pandas as pd


def min_max_scale(series: pd.Series) -> pd.Series:
    """
    Scale a series from 0 to 100.

    Higher values become closer to 100.
    Lower values become closer to 0.
    """
    if series.max() == series.min():
        return series * 0

    return 100 * (series - series.min()) / (series.max() - series.min())


def calculate_structural_vulnerability(country_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate a transparent structural vulnerability score for EM countries.

    Higher score = more vulnerable.

    This is a heuristic score, not a trained return-prediction model.
    Incorporates real World Bank macro variables for EM-relevant assessment.
    """
    output = country_data.copy()

    output["inflation_score"] = min_max_scale(output["inflation"])
    output["debt_score"] = min_max_scale(output["government_debt_gdp"])
    output["current_account_score"] = min_max_scale(-output["current_account_gdp"])
    output["external_debt_score"] = min_max_scale(output["external_debt_gni"])
    output["reserves_weakness_score"] = min_max_scale(-output["reserves_gdp"])
    output["oil_importer_score_scaled"] = min_max_scale(output["oil_importer_score"])
    output["china_exposure_score_scaled"] = min_max_scale(output["china_exposure_score"])

    output["structural_vulnerability_score"] = (
        0.20 * output["inflation_score"]
        + 0.20 * output["debt_score"]
        + 0.20 * output["current_account_score"]
        + 0.15 * output["external_debt_score"]
        + 0.10 * output["reserves_weakness_score"]
        + 0.075 * output["oil_importer_score_scaled"]
        + 0.075 * output["china_exposure_score_scaled"]
    )

    return output

def calculate_regime_adjusted_vulnerability(
    country_data: pd.DataFrame,
    current_regime: str,
) -> pd.DataFrame:
    """
    Adjust structural vulnerability scores depending on the current market regime.

    This connects the market regime model with the EM country screener.
    """
    output = country_data.copy()

    output["regime_adjustment"] = 0.0
    output["regime_rationale"] = ""

    if current_regime == "Dollar squeeze":
        output["regime_adjustment"] += (
            0.15 * output["current_account_score"]
            + 0.10 * output["china_exposure_score_scaled"]
        )
        output["regime_rationale"] = (
            "Dollar squeeze: penalises external deficits and high-beta exposures."
        )

    elif current_regime == "Commodity rally":
        output["regime_adjustment"] -= 10 * output["commodity_score"]
        output["regime_adjustment"] += 5 * output["oil_importer_score_scaled"] / 100
        output["regime_rationale"] = (
            "Commodity rally: supports commodity exporters but can hurt oil importers."
        )

    elif current_regime == "Growth scare":
        output["regime_adjustment"] += (
            0.15 * output["china_exposure_score_scaled"]
            + 0.10 * output["current_account_score"]
        )
        output["regime_rationale"] = (
            "Growth scare: penalises China-sensitive and externally vulnerable countries."
        )

    elif current_regime == "Risk-on carry":
        output["regime_adjustment"] -= 0.10 * output["structural_vulnerability_score"]
        output["regime_rationale"] = (
            "Risk-on carry: reduces pressure on vulnerable EM currencies as risk appetite improves."
        )

    elif current_regime == "Inflation shock":
        output["regime_adjustment"] += (
            0.15 * output["inflation_score"]
            + 0.10 * output["oil_importer_score_scaled"]
        )
        output["regime_rationale"] = (
            "Inflation shock: penalises high-inflation countries and oil importers."
        )

    else:
        output["regime_rationale"] = (
            "Placeholder regime: no specific macro adjustment applied."
        )

    output["final_vulnerability_score"] = (
        output["structural_vulnerability_score"] + output["regime_adjustment"]
    )

    output["final_vulnerability_score"] = output["final_vulnerability_score"].clip(
        lower=0,
        upper=100,
    )

    return output.sort_values("final_vulnerability_score", ascending=False)


def incorporate_news_risk(
    scored: pd.DataFrame,
    news_scores: pd.DataFrame,
    news_weight: float = 0.15,
) -> pd.DataFrame:
    """
    Incorporate news risk scores into the final vulnerability score.

    final_vulnerability_score = (1 - news_weight) * current_score + news_weight * news_risk_score

    This makes the screener dynamic: countries become more vulnerable not only from
    static macro data, but from deteriorating news flow.
    """
    output = scored.copy()

    # Merge news scores on country/ccy
    output = output.merge(
        news_scores[["country", "ccy", "news_risk_score"]],
        on=["country", "ccy"],
        how="left",
    )

    # Fill missing news scores with 0 (neutral news)
    output["news_risk_score"] = output["news_risk_score"].fillna(0.0)

    # Normalize news_risk_score to 0-100 scale if needed
    if output["news_risk_score"].max() > 100:
        output["news_risk_score"] = min_max_scale(output["news_risk_score"])

    # Calculate blended score
    output["final_vulnerability_score"] = (
        (1 - news_weight) * output["final_vulnerability_score"]
        + news_weight * output["news_risk_score"]
    )

    output["final_vulnerability_score"] = output["final_vulnerability_score"].clip(
        lower=0,
        upper=100,
    )

    return output.sort_values("final_vulnerability_score", ascending=False)


def generate_relative_value_ideas(scored: pd.DataFrame, n_ideas: int = 3) -> pd.DataFrame:
    """
    Generate relative-value trade ideas based on vulnerability scores.
    
    Long the least vulnerable (lowest scores), short the most vulnerable (highest scores).
    """
    scored_sorted = scored.sort_values("final_vulnerability_score")
    
    ideas = []
    
    # Long ideas (least vulnerable)
    for idx, (_, row) in enumerate(scored_sorted.head(n_ideas).iterrows()):
        ideas.append({
            "idea_type": "LONG",
            "rank": idx + 1,
            "country": row["country"],
            "ccy": row["ccy"],
            "vulnerability_score": row["final_vulnerability_score"],
            "rationale": f"Low vulnerability ({row['final_vulnerability_score']:.1f}). {row.get('regime_rationale', 'Neutral regime adjustment.')}",
        })
    
    # Short ideas (most vulnerable)
    for idx, (_, row) in enumerate(scored_sorted.tail(n_ideas).iloc[::-1].iterrows()):
        ideas.append({
            "idea_type": "SHORT",
            "rank": idx + 1,
            "country": row["country"],
            "ccy": row["ccy"],
            "vulnerability_score": row["final_vulnerability_score"],
            "rationale": f"High vulnerability ({row['final_vulnerability_score']:.1f}). {row.get('regime_rationale', 'Neutral regime adjustment.')}",
        })
    
    return pd.DataFrame(ideas)