import os
import subprocess
import sys


PIPELINE_STEPS = [
    "scripts/01_download_market_data.py",
    "scripts/02_regime_detection.py",
    "scripts/00_download_macro_data.py",
    "scripts/03_country_clustering.py",
    "scripts/04_vulnerability_scoring.py",
    "scripts/05_news_classification.py",
]


def run_step(script_path: str) -> None:
    """
    Run a pipeline script and stop the pipeline if it fails.
    """
    print(f"\nRunning {script_path}...")
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    result = subprocess.run([sys.executable, script_path], env=env, check=False)

    if result.returncode != 0:
        raise RuntimeError(f"Pipeline failed at: {script_path}")


def main() -> None:
    print("Starting EM macro screener pipeline...")

    for step in PIPELINE_STEPS:
        run_step(step)

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()