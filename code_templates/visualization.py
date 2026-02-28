"""Template: visualization examples"""

import seaborn as sns
import matplotlib.pyplot as plt


def plot_feature_distributions(df):
    num_cols = df.select_dtypes(include='number').columns
    for col in num_cols:
        sns.histplot(df[col], kde=True)
        plt.title(col)
        plt.show()


def plot_correlation_heatmap(df):
    corr = df.corr()
    sns.heatmap(corr, annot=True, fmt='.2f')
    plt.show()
