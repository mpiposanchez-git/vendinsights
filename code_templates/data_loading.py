"""Template: data loading and basic inspection"""

import pandas as pd
from pathlib import Path


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(df.head())
    print(df.info())
    return df


def load_parquet(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def example_usage():
    df = load_csv('data/raw/sample.csv')
    # further processing
