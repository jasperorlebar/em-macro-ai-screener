from pathlib import Path

import pandas as pd

from src.news_classifier import classify_news, calculate_country_news_scores


REAL_NEWS_INPUT_PATH = Path("data/processed/news_headlines_real.csv")
SAMPLE_NEWS_INPUT_PATH = Path("data/inputs/news_headlines_sample.csv")

CLASSIFIED_NEWS_OUTPUT_PATH = Path("data/processed/classified_news.csv")
NEWS_SCORES_OUTPUT_PATH = Path("data/processed/news_risk_scores.csv")


def main() -> None:
    if REAL_NEWS_INPUT_PATH.exists():
        news_input_path = REAL_NEWS_INPUT_PATH
        print(f"Using real news input: {news_input_path}")
    else:
        news_input_path = SAMPLE_NEWS_INPUT_PATH
        print(f"Using sample news input: {news_input_path}")

    print("Loading news headlines...")

    news = pd.read_csv(news_input_path)

    required_cols = {"country", "ccy", "date", "headline"}
    missing_cols = required_cols - set(news.columns)

    if missing_cols:
        raise ValueError(f"Missing required columns in news input: {missing_cols}")

    print("Classifying headlines...")

    classified_news = classify_news(news)
    news_scores = calculate_country_news_scores(classified_news)

    CLASSIFIED_NEWS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    classified_news.to_csv(CLASSIFIED_NEWS_OUTPUT_PATH, index=False)
    news_scores.to_csv(NEWS_SCORES_OUTPUT_PATH, index=False)

    print(f"Saved classified news to {CLASSIFIED_NEWS_OUTPUT_PATH}")
    print(f"Saved news risk scores to {NEWS_SCORES_OUTPUT_PATH}")

    print("\nCountry news risk scores:")
    print(news_scores)


if __name__ == "__main__":
    main()