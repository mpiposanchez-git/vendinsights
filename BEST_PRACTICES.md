# Data Science & Machine Learning Best Practices

## Overview

This guide outlines best practices for developing data science and machine learning projects, specifically tailored for credit risk analysis. Follow these practices to ensure reproducibility, maintainability, and reliability of your models.

## Project Structure

```
project/
├── data/
│   ├── raw/                 # Original, immutable data
│   ├── processed/           # Cleaned, transformed data
│   └── external/            # External data sources
├── notebooks/               # Jupyter notebooks for EDA and experiments
├── hola/                    # Main package code
│   ├── data/               # Data loading and preprocessing
│   ├── features/           # Feature engineering
│   ├── models/             # Model definitions and training
│   ├── evaluation/         # Evaluation metrics and visualization
│   └── utils/              # Helper functions
├── models/                 # Saved trained models
├── results/                # Outputs, predictions, reports
├── tests/                  # Unit tests
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
└── .gitignore              # Git ignore file
```

## Key Principles

### 1. Data Management

- **Raw Data is Sacred**: Never modify raw data. Always create a copy in `data/processed/`
- **Version Control**: Use meaningful file names with timestamps: `processed_data_v1_2024-01-15.csv`
- **Documentation**: Document data sources, transformations, and assumptions
- **Data Cleaning**: Keep data cleaning logic in `hola/data/` module, not in notebooks

### 2. Code Organization

- **Modularity**: Break code into small, reusable functions
- **Single Responsibility**: Each function should do one thing well
- **Type Hints**: Use Python type hints for clarity
- **Documentation**: Write docstrings for all functions
- **DRY**: Don't Repeat Yourself - abstract common patterns into utilities

### 3. Reproducibility

- **Random Seeds**: Set random seeds for numpy, scikit-learn, and xgboost
- **Requirements**: Keep `pyproject.toml` updated with exact versions
- **Configuration**: Use configuration files (not hardcoded values)
- **Notebooks**: Document steps and assumptions clearly

### 4. Model Development

#### Experimentation Phase (Notebooks)
```python
# notebooks/01_eda.ipynb - Exploratory Data Analysis
# notebooks/02_feature_engineering.ipynb - Feature creation
# notebooks/03_model_comparison.ipynb - Model selection
# notebooks/04_hyperparameter_tuning.ipynb - Optimization
```

#### Production Phase (Code)
- Move validated code to `hola/` modules
- Create proper classes and functions
- Add error handling and logging
- Write unit tests

### 5. Feature Engineering

- **Feature Store**: Document all features in a central location
- **Validation**: Check feature distributions and missing values
- **Encoding**: Use consistent encoding for categorical variables
- **Scaling**: Document which features need scaling
- **Feature Importance**: Track and document feature importance

### 6. Model Evaluation

For Credit Risk Analysis specifically:

```python
from sklearn.metrics import (
    roc_auc_score,      # Overall model performance
    precision_score,    # False positive rate (cost of lending)
    recall_score,       # False negative rate (risk of default)
    confusion_matrix,   # Type I and II errors
    roc_curve,          # Threshold selection
)
```

Key metrics:
- **AUC-ROC**: Overall discrimination ability
- **Precision**: Of predicted defaults, how many are correct?
- **Recall**: Of actual defaults, how many do we catch?
- **Threshold Selection**: Balance between precision and recall

### 7. Handling Imbalanced Data

Credit risk datasets are typically imbalanced (few defaults vs many non-defaults):

```python
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

# Create balanced training set
balancer = Pipeline([
    ('over', SMOTE(random_state=42)),
    ('under', RandomUnderSampler(random_state=42))
])
X_balanced, y_balanced = balancer.fit_resample(X_train, y_train)
```

### 8. Model Interpretability

Use SHAP values to explain model decisions:

```python
import shap

# Create explainer
explainer = shap.Explainer(model)
shap_values = explainer(X_test)

# Plot summary
shap.summary_plot(shap_values, X_test)

# Individual predictions
shap.force_plot(explainer.expected_value, shap_values[0], X_test[0])
```

### 9. Hyperparameter Tuning

Use Optuna for efficient hyperparameter optimization:

```python
import optuna

def objective(trial):
    params = {
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
    }
    # Train and evaluate model
    return auc_score

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)
```

### 10. Testing

Write tests for data and model components:

```python
# tests/test_data.py
def test_load_data_shape():
    df = load_data('test_data.csv')
    assert df.shape[0] > 0
    assert df.shape[1] > 0

# tests/test_models.py
def test_model_predictions():
    model = create_xgboost_model()
    predictions = model.predict(X_test)
    assert predictions.shape[0] == X_test.shape[0]
```

### 11. Documentation

- **README.md**: Project overview, setup instructions, usage examples
- **Docstrings**: Explain what, why, and how for each function
- **Comments**: Explain complex logic (not obvious code)
- **Notebooks**: Use markdown cells to explain analysis steps
- **Parameter Documentation**: Document model parameters and ranges

### 12. Git Workflow

```bash
# Keep commits focused and meaningful
git add <specific files>
git commit -m "Add SHAP interpretability to model evaluation"

# Use branches for features
git checkout -b feature/lgbm-model

# Merge when complete
git checkout main
git merge feature/lgbm-model
```

## Workflow Example

### Phase 1: Exploration
```
notebooks/01_eda.ipynb
├── Load data
├── Basic statistics
├── Missing value analysis
└── Distribution plots
```

### Phase 2: Feature Engineering
```
notebooks/02_features.ipynb
├── Create new features
├── Feature importance
└── Feature correlation
```

### Phase 3: Model Development
```
notebooks/03_models.ipynb
├── Train baseline models
├── Hyperparameter tuning (Optuna)
├── Cross-validation
└── Model comparison
```

### Phase 4: Productionization
```
hola/
├── data/loader.py
├── features/engineering.py
├── models/credit_risk.py
└── evaluation/metrics.py
```

### Phase 5: Testing & Validation
```
tests/
├── test_data.py
├── test_features.py
└── test_models.py
```

## Tools & Libraries

- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **ML Algorithms**: scikit-learn, XGBoost, LightGBM
- **Imbalanced Data**: imbalanced-learn
- **Hyperparameter Optimization**: optuna
- **Model Interpretability**: SHAP
- **Statistical Modeling**: statsmodels
- **Testing**: pytest
- **Code Quality**: black, flake8, mypy
- **Notebooks**: Jupyter, JupyterLab

## Quick Start

1. **Setup environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
   ```

2. **Start exploration**:
   ```bash
   jupyter lab notebooks/
   ```

3. **Run tests**:
   ```bash
   pytest tests/ -v --cov=hola
   ```

4. **Check code quality**:
   ```bash
   black hola/
   flake8 hola/
   mypy hola/
   ```

## Common Pitfalls to Avoid

1. ❌ **Data Leakage**: Don't use test data information in training
2. ❌ **Hardcoded Values**: Use configuration files instead
3. ❌ **Skipping Train/Test Split**: Always validate on unseen data
4. ❌ **Imbalanced Metrics**: Use appropriate metrics for imbalanced data
5. ❌ **No Random Seed**: Always set seeds for reproducibility
6. ❌ **Overfitting**: Use cross-validation and regularization
7. ❌ **Poor Documentation**: Document assumptions and decisions
8. ❌ **Inconsistent Preprocessing**: Apply same transformations to test data

## Credit Risk Specific Considerations

- **Class Imbalance**: Use SMOTE or class weights
- **Cost Sensitivity**: False negatives (missed defaults) are costly
- **Business Context**: Understand the business impact of predictions
- **Regulatory Requirements**: Consider model explainability requirements
- **Model Monitoring**: Monitor model performance over time (model drift)
- **Feature Selection**: Avoid features with data availability issues

## Resources

- [scikit-learn Best Practices](https://scikit-learn.org/stable/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)

---

Last updated: February 2026
