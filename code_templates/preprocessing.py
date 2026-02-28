"""Template: data cleaning and preprocessing"""

import pandas as pd


def clean_missing(df: pd.DataFrame) -> pd.DataFrame:
    # drop columns with too many missing values
    thresh = len(df) * 0.5
    df = df.dropna(axis=1, thresh=thresh)
    # fill numeric with median
    num_cols = df.select_dtypes(include='number').columns
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    return df


def encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    cat_cols = df.select_dtypes(include='object').columns
    return pd.get_dummies(df, columns=cat_cols, drop_first=True)
