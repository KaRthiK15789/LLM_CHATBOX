import pytest
import pandas as pd
from visualization import ChartGenerator
from utils import DataUtils

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=3),
        'Product': ['Laptop', 'Phone', 'Monitor'],
        'Price': [1000, 800, 300],
        'Quantity': [5, 10, 8]
    })

def test_pie_chart_generation(sample_data):
    chart_gen = ChartGenerator()
    fig = chart_gen.create_chart(
        df=sample_data,
        query="pie chart of revenue by product",
        columns=['Product', 'Price', 'Quantity']
    )
    assert fig is not None
    assert fig.layout.title.text == 'Revenue Share by Product'

def test_invalid_chart_request(sample_data):
    chart_gen = ChartGenerator()
    fig = chart_gen.create_chart(
        df=sample_data,
        query="invalid chart request",
        columns=['Date']
    )
    assert fig is None

def test_empty_data_handling():
    chart_gen = ChartGenerator()
    with pytest.raises(ValueError):
        chart_gen.create_chart(
            df=pd.DataFrame(),
            query="bar chart",
            columns=[]
        )
