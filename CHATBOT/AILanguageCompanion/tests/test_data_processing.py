import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from data_processor import DataProcessor
from utils import DataUtils

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', None],
        'Product': ['Laptop', 'Phone', 'Monitor'],
        'Price': [1000, 800, 300],
        'Quantity': [5, 10, None]
    })

def test_load_excel_valid(sample_data, tmp_path):
    # Create test Excel file
    test_file = tmp_path / "test.xlsx"
    sample_data.to_excel(test_file, index=False)
    
    processor = DataProcessor()
    success, _ = processor.load_excel(test_file)
    assert success is True
    assert processor.df.shape == (3, 4)

def test_load_excel_invalid(tmp_path):
    # Create empty file
    test_file = tmp_path / "empty.xlsx"
    test_file.write_text("")
    
    processor = DataProcessor()
    success, message = processor.load_excel(test_file)
    assert success is False
    assert "Invalid Excel file" in message

def test_date_detection(sample_data):
    date_cols = DataUtils.detect_date_columns(sample_data)
    assert 'Date' in date_cols

def test_revenue_calculation(sample_data):
    df = DataUtils.calculate_revenue(sample_data)
    assert 'Revenue' in df.columns
    assert df['Revenue'].iloc[0] == 5000

def test_column_normalization():
    columns = ['Revenue', 'Price', 'Quantity']
    assert DataUtils.normalize_column_name("total sales", columns) == 'Revenue'
    assert DataUtils.normalize_column_name("average price", columns) == 'Price'
    assert DataUtils.normalize_column_name("unknown", columns) is None
