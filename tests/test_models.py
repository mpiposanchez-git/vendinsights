# Test for models module
import pytest
from mps_package.models import create_xgboost_model, create_lightgbm_model


def test_create_xgboost_model():
    """Test XGBoost model creation."""
    model = create_xgboost_model()
    assert model is not None


def test_create_lightgbm_model():
    """Test LightGBM model creation."""
    model = create_lightgbm_model()
    assert model is not None
