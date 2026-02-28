"""Template: feature engineering"""

import pandas as pd


def create_ratio_feature(df: pd.DataFrame, num: str, denom: str, new_name: str):
    df[new_name] = df[num] / (df[denom] + 1e-8)
    return df


def bin_numeric(df: pd.DataFrame, col: str, bins: int):
    df[col + '_bin'] = pd.qcut(df[col], bins, duplicates='drop')
    return df
