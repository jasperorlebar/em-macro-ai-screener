# EM Macro AI Screener

## Overview

This project builds a prototype systematic EM macro research tool. It combines cross-asset market data, unsupervised market regime detection, country-level macro clustering, and eventually AI-based news classification to screen EM FX vulnerability.

The aim is not to build a black-box FX predictor. Instead, the project explores how AI and machine learning can organise noisy macro information into structured, interpretable trade hypotheses.

## Current Status

Day 1 prototype completed:

- Market data download script
- Market regime detection script
- EM country clustering script
- Initial Streamlit dashboard

Day 2 improvements:

- Cleaner project structure
- Toy input data separated from downloaded raw data
- Pipeline runner script
- Tabbed Streamlit dashboard
- Improved project documentation

## Project Modules

### 1. Market Data Pipeline

Downloads cross-asset market data including:

- S&P 500
- VIX
- Oil
- Copper
- Gold
- Selected EM FX pairs

### 2. Market Regime Detection

Uses rolling z-scores and k-means clustering to classify market environments into unsupervised regimes.

The model is designed to detect patterns such as:

- risk-on carry
- dollar squeeze
- commodity rally
- growth scare
- inflation shock

Current regime labels are placeholders and require manual interpretation.

### 3. EM Country Clustering

Clusters EM countries using macro vulnerability indicators such as:

- inflation
- current account balance
- government debt
- GDP growth
- commodity exposure
- oil importer exposure
- China exposure

The current version uses toy data to validate the project pipeline.

### 4. Dashboard

A Streamlit dashboard displays:

- latest detected regime
- market data
- regime timeline
- country clustering map
- methodology
- limitations and next steps

## Vulnerability Scoring

The project now includes a transparent EM vulnerability scoring framework.

The baseline score combines:

- inflation risk
- government debt burden
- current-account vulnerability
- oil-importer exposure
- China exposure

A regime-aware adjustment is then applied depending on the current market environment.

For example:

- in a dollar squeeze, countries with weaker external balances are penalised;
- in a commodity rally, commodity exporters receive a relative benefit;
- in a growth scare, China-sensitive countries receive a higher vulnerability adjustment;
- in an inflation shock, high-inflation countries and oil importers are penalised.

The output is a ranked EM FX vulnerability table and a set of relative-value trade research prompts.

This is a heuristic research framework, not a return-prediction model or trading recommendation.

## Real Macro Data

The project now replaces the toy country macro dataset with real World Bank macro indicators.

The sourced variables include:

- inflation: `FP.CPI.TOTL.ZG`
- GDP growth: `NY.GDP.MKTP.KD.ZG`
- current account balance, % of GDP: `BN.CAB.XOKA.GD.ZS`
- central government debt, % of GDP: `GC.DOD.TOTL.GD.ZS`
- external debt stocks, % of GNI: `DT.DOD.DECT.GN.ZS`
- total reserves, current USD: `FI.RES.TOTL.CD`
- GDP, current USD: `NY.GDP.MKTP.CD`

The project calculates `reserves_gdp` as:

```text
total reserves / GDP * 100
```

## News Risk Classification

The project now includes a prototype news classification layer that converts unstructured headlines into structured macro risk themes.

### How It Works

1. **Headline Classification**: Headlines are classified into macro themes using a transparent keyword-based classifier.
2. **Risk Scoring**: Each theme receives a risk weight (ranging from -30 for positive macro news to +90 for sovereign risk).
3. **Country Aggregation**: Scores are aggregated to the country level to produce a country news risk score.
4. **Integration**: News risk is blended into the final vulnerability score at 15% weight.

### Macro Themes

The current classifier recognizes 8 macro news themes:

- **fiscal_stress**: Debt, budget, deficit, funding concerns (risk: 80)
- **political_instability**: Elections, protests, corruption (risk: 75)
- **hawkish_central_bank**: Rate hikes, inflation concerns (risk: 45)
- **dovish_central_bank**: Rate cuts, easing expectations (risk: 40)
- **commodity_shock**: Oil, copper, commodity price movements (risk: 55)
- **china_growth**: China stimulus, slowdown, property concerns (risk: 50)
- **sovereign_risk**: IMF programs, defaults, credit rating downgrades (risk: 90)
- **positive_macro**: Reform, investment, economic upgrades (risk: -30)

### Integration with Vulnerability Scoring

The final vulnerability score combines three components:

```
final_vulnerability_score = 0.85 * (structural + regime) + 0.15 * news_risk
```

This makes the screener **dynamic**: countries become more vulnerable not only from static macro data, but from deteriorating news flow.

### Current Implementation

- Input: `data/inputs/news_headlines_sample.csv` (sample headlines)
- Classifier: `src/news_classifier.py` (keyword-based theme classification)
- Outputs: 
  - `data/processed/classified_news.csv` (headlines with themes and risk scores)
  - `data/processed/news_risk_scores.csv` (country-level aggregated scores)
- Dashboard: **News Risk Classification** tab showing scores and classified headlines

### Future Upgrades

The current keyword-based classifier is designed as a prototype. Future versions can:

- Replace sample headlines with live news from GDELT or similar sources
- Upgrade to zero-shot NLP classification (e.g., using Hugging Face transformers)
- Fine-tune a text classifier on labelled macro news datasets
- Add sentiment analysis and topic modeling

## How to Run

Activate the virtual environment:

```bash
source .venv/bin/activate