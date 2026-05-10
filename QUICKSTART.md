# Quick Start Guide

## Setup (First Time Only)

```bash
# Clone repository
git clone https://github.com/jasperorlebar/em-macro-ai-screener.git
cd em-macro-ai-screener

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Project

### Option 1: Full Pipeline + Dashboard

```bash
source .venv/bin/activate

# Run all 6 pipeline steps (5-10 minutes)
python scripts/run_pipeline.py

# Launch dashboard
streamlit run app.py
```

Then open: **http://localhost:8501**

### Option 2: Individual Scripts

```bash
# Download market data (11 years)
python scripts/01_download_market_data.py

# Detect market regimes
python scripts/02_regime_detection.py

# Download World Bank macro data (slow: 3-5 min)
python scripts/00_download_macro_data.py

# Cluster countries by vulnerability
python scripts/03_country_clustering.py

# Calculate vulnerability scores
python scripts/04_vulnerability_scoring.py

# Classify news headlines
python scripts/05_news_classification.py
```

## Dashboard Tabs

| Tab | Purpose |
|-----|---------|
| **Overview** | Key metrics: latest regime, top vulnerable currency, top trade idea |
| **Market Regime** | Timeline of detected regimes + cross-asset chart |
| **Country Clusters** | PCA visualization of 12 countries with macro data |
| **Vulnerability Screener** | Ranked table with macro scores + trade ideas (LONG/SHORT) |
| **News Risk** | Classified headlines + country news risk scores |
| **Methodology** | Explanation of all 6 pipeline steps |
| **Limitations** | Known constraints + planned upgrades |

## Key Output Files

```
data/processed/
├── market_data.csv              # Cross-asset data (2,958 rows)
├── regime_data.csv              # Detected regimes (2,786 rows)
├── country_clusters.csv         # Clustered countries (12 rows)
├── vulnerability_scores.csv     # Final scores (12 rows)
├── trade_ideas.csv              # 3 LONG + 3 SHORT ideas
├── classified_news.csv          # Headlines with themes (24 rows)
└── news_risk_scores.csv         # Country news risk (12 rows)
```

## Architecture

### Vulnerability Score Formula

```
final_score = 0.85 * (structural + regime) + 0.15 * news_risk

Where:
- structural = min-max scaled macro variables (0-100)
- regime = market environment adjustment (-40 to +25)
- news_risk = headline sentiment aggregated to country (-30 to +90)
```

### News Themes & Risk Weights

| Theme | Risk | Keywords |
|-------|------|----------|
| Sovereign Risk | 90 | imf, default, downgrade, credit rating |
| Fiscal Stress | 80 | debt, deficit, budget, fiscal concerns |
| Political Risk | 75 | election, protest, coalition, corruption |
| Commodity Shock | 55 | oil, copper, commodity, supply |
| China Concerns | 50 | china stimulus, china slowdown, property |
| Hawkish CB | 45 | rate hike, higher for longer, inflation |
| Dovish CB | 40 | rate cut, easing, slowdown |
| Positive Macro | -30 | reform, investment, growth, upgrade |

## Example Usage

### View Latest Vulnerability Scores

```bash
python -c "
import pandas as pd
scores = pd.read_csv('data/processed/vulnerability_scores.csv')
print(scores[['country', 'ccy', 'final_vulnerability_score']].head(5))
"
```

### View News Scores

```bash
python -c "
import pandas as pd
news = pd.read_csv('data/processed/news_risk_scores.csv')
print(news[['country', 'ccy', 'news_risk_score', 'dominant_theme']])
"
```

### View Trade Ideas

```bash
python -c "
import pandas as pd
ideas = pd.read_csv('data/processed/trade_ideas.csv')
print(ideas)
"
```

## Development Notes

### Adding Custom News Headlines

Edit `data/inputs/news_headlines_sample.csv`:

```csv
date,country,ccy,headline
2026-05-10,Turkey,TRY,Turkish central bank raises rates amid inflation surge
2026-05-10,Brazil,BRL,Brazil faces fiscal concerns over budget deficit
...
```

Then rerun:
```bash
python scripts/05_news_classification.py
python scripts/04_vulnerability_scoring.py
```

### Upgrading News Classifier

The current classifier is keyword-based (in `src/news_classifier.py`). To upgrade:

1. **Replace GDELT for live news** instead of sample CSV
2. **Use Hugging Face zero-shot**: `pipeline("zero-shot-classification")`
3. **Fine-tune a custom classifier** on labelled macro news dataset

The integration point is `incorporate_news_risk()` in `src/scoring.py`.

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

Ensure you're running from the project root with `PYTHONPATH` set:

```bash
cd /Users/jasperorlebar/em-macro-ai-screener
PYTHONPATH=. python scripts/01_download_market_data.py
```

Or use the pipeline runner which handles this:

```bash
python scripts/run_pipeline.py
```

### "World Bank API timeout"

The macro data download can be slow. The script has retry logic with exponential backoff (max 3 attempts, 180s timeout). If it fails:

```bash
# Try again - it will continue from where it left off
python scripts/00_download_macro_data.py
```

### "Streamlit not found"

Ensure you activated the virtual environment:

```bash
source .venv/bin/activate
pip install streamlit
```

## Git Commits

```bash
# View recent changes
git log --oneline -5

# Show changes since last commit
git diff

# Commit your changes
git add .
git commit -m "Your message"
git push
```

## Contact & Questions

See README.md for full documentation.
See reports/project_summary.md for architecture details.

---

**Last Updated**: May 10, 2026
