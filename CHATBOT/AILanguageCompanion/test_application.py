#!/usr/bin/env python3
"""
Modernized test script for Excel Insights Chatbot
"""

import pytest
import pandas as pd
import os
from datetime import datetime
from data_processor import DataProcessor
from query_handler import QueryHandler
from visualization import ChartGenerator

@pytest.fixture
def sample_data(tmp_path):
    """Generate test data fixture"""
    data = {
        'Date': pd.date_range('2024-01-01', periods=3),
        'Product': ['Laptop', 'Phone', 'Monitor'],
        'Price': [1000, 800, 300],
        'Quantity': [5, 10, 8],
        'Region': ['East', 'West', 'East']
    }
    df = pd.DataFrame(data)
    test_file = tmp_path / "test_data.xlsx"
    df.to_excel(test_file, index=False)
    return test_file

def test_data_processor(sample_data):
    """Test DataProcessor with modern checks"""
    print("\nTesting DataProcessor...")
    
    processor = DataProcessor()
    success, msg = processor.load_excel(sample_data)
    
    assert success, f"Failed to load file: {msg}"
    assert processor.df.shape == (3, 5)
    assert 'Revenue' in processor.df.columns  # Verify auto-calculation
    print("✓ All data processing tests passed")

@pytest.mark.parametrize("query,expected_type", [
    ("show laptops", "dataframe"),
    ("total revenue", "text"),
    ("plot price by region", "chart"),
    ("invalid query 123", "error")
])
def test_query_handler(sample_data, query, expected_type):
    """Test query handling scenarios"""
    processor = DataProcessor()
    processor.load_excel(sample_data)
    handler = QueryHandler(processor)
    
    response = handler.process_query(query)
    assert response['type'] == expected_type
    print(f"✓ Query '{query}' handled correctly")

def test_visualization(sample_data):
    """Test chart generation"""
    print("\nTesting Visualization...")
    
    processor = DataProcessor()
    processor.load_excel(sample_data)
    chart_gen = ChartGenerator()
    
    # Test all chart types
    charts = [
        chart_gen.create_chart(processor.df, "pie revenue by product", ['Product']),
        chart_gen.create_chart(processor.df, "bar quantity by region", ['Region']),
        chart_gen.create_chart(processor.df, "plot price over time", ['Date'])
    ]
    
    assert all(chart is not None for chart in charts)
    print("✓ All chart types generated successfully")

def test_error_handling():
    """Test error scenarios"""
    print("\nTesting Error Handling...")
    
    # Test empty processor
    empty_processor = DataProcessor()
    handler = QueryHandler(empty_processor)
    response = handler.process_query("any query")
    assert response['type'] == 'error'
    print("✓ Empty processor handled")

if __name__ == "__main__":
    pytest.main(["-v", "--tb=line", __file__])
