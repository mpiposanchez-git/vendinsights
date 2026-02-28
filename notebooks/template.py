"""Example notebook template for exploratory data analysis."""

# This is a template for Jupyter notebooks
# Copy this and rename as: 01_eda.ipynb, 02_features.ipynb, etc.

# %% [markdown]
# # Exploratory Data Analysis
# 
# This notebook performs initial data exploration for credit risk analysis.

# %% [markdown]
# ## 1. Load Libraries

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# %% [markdown]
# ## 2. Load Data

# %%
# Load your data
# df = pd.read_csv('data/raw/credit_risk_data.csv')

# %% [markdown]
# ## 3. Basic Information

# %%
# print(df.shape)
# print(df.head())
# print(df.info())
# print(df.describe())

# %% [markdown]
# ## 4. Missing Values

# %%
# missing_values = df.isnull().sum()
# print(missing_values[missing_values > 0])

# %% [markdown]
# ## 5. Target Distribution

# %%
# if 'target' in df.columns:
#     df['target'].value_counts().plot(kind='bar')
#     plt.title('Target Distribution')
#     plt.show()

# %% [markdown]
# ## 6. Feature Analysis

# %%
# Analyze distributions and relationships

print("Template notebook - modify for your data")
