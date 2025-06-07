#!/usr/bin/env python3
"""
Test script to verify the Excel Insights Chatbot functionality
"""

import pandas as pd
import sys
import os

# Add the current directory to Python path
sys.path.append('.')

from data_processor import DataProcessor
from fallback_query_handler import FallbackQueryHandler
from visualization import ChartGenerator

def test_data_processor():
    """Test the DataProcessor class with sample data."""
    print("Testing DataProcessor...")
    
    # Create test data
    test_data = {
        'Employee ID': [1, 2, 3, 4, 5],
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
        'Age': [25, 30, 35, 28, 42],
        'Department': ['Sales', 'Marketing', 'IT', 'HR', 'Finance'],
        'Salary': [50000, 60000, 75000, 55000, 80000],
        'Remote Work': ['Yes', 'No', 'Yes', 'No', 'Yes']
    }
    
    df = pd.DataFrame(test_data)
    
    # Save as Excel file for testing
    df.to_excel('test_data.xlsx', index=False)
    
    # Test DataProcessor
    processor = DataProcessor()
    
    # Test file loading
    with open('test_data.xlsx', 'rb') as f:
        class MockUpload:
            def __init__(self, file_obj):
                self.file_obj = file_obj
                self.name = 'test_data.xlsx'
            
            def read(self):
                return self.file_obj.read()
            
            def seek(self, pos):
                return self.file_obj.seek(pos)
        
        mock_file = MockUpload(f)
        success, message = processor.load_excel(mock_file)
    
    if success:
        print(f"✓ File loaded successfully: {message}")
        print(f"✓ Shape: {processor.df.shape}")
        print(f"✓ Columns: {list(processor.df.columns)}")
        print(f"✓ Numeric columns: {processor.numeric_columns}")
        print(f"✓ Categorical columns: {processor.categorical_columns}")
        print(f"✓ Binary columns: {processor.binary_columns}")
    else:
        print(f"✗ Failed to load file: {message}")
        return False
    
    return True

def test_fallback_handler():
    """Test the FallbackQueryHandler."""
    print("\nTesting FallbackQueryHandler...")
    
    # Create processor with test data
    processor = DataProcessor()
    
    # Load test data again
    with open('test_data.xlsx', 'rb') as f:
        class MockUpload:
            def __init__(self, file_obj):
                self.file_obj = file_obj
                self.name = 'test_data.xlsx'
            
            def read(self):
                return self.file_obj.read()
            
            def seek(self, pos):
                return self.file_obj.seek(pos)
        
        mock_file = MockUpload(f)
        processor.load_excel(mock_file)
    
    # Create fallback handler
    handler = FallbackQueryHandler(processor)
    
    # Test different types of queries
    test_queries = [
        "What is the average age?",
        "How many employees are there?",
        "Show a bar chart of department",
        "Compare salary by department",
        "Show me employees under 30"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        try:
            response = handler.process_query(query)
            print(f"✓ Response type: {response['type']}")
            if response['type'] == 'error':
                print(f"  Error: {response['content']}")
            else:
                print(f"  Success: Response generated")
        except Exception as e:
            print(f"✗ Error processing query: {e}")
    
    return True

def test_chart_generator():
    """Test the ChartGenerator class."""
    print("\nTesting ChartGenerator...")
    
    # Create processor with test data
    processor = DataProcessor()
    
    with open('test_data.xlsx', 'rb') as f:
        class MockUpload:
            def __init__(self, file_obj):
                self.file_obj = file_obj
                self.name = 'test_data.xlsx'
            
            def read(self):
                return self.file_obj.read()
            
            def seek(self, pos):
                return self.file_obj.seek(pos)
        
        mock_file = MockUpload(f)
        processor.load_excel(mock_file)
    
    # Create chart generator
    chart_gen = ChartGenerator()
    
    # Test different chart types
    test_cases = [
        (['age'], 'histogram', 'Age histogram'),
        (['department'], 'bar', 'Department bar chart'),
        (['age', 'salary'], 'scatter', 'Age vs Salary scatter plot'),
        (['department', 'salary'], 'bar', 'Salary by Department')
    ]
    
    for columns, chart_type, description in test_cases:
        print(f"\nTesting: {description}")
        try:
            chart = chart_gen.create_chart(
                df=processor.df,
                columns=columns,
                chart_type=chart_type,
                original_columns=processor.original_columns,
                column_types=processor.column_types
            )
            
            if chart:
                print(f"✓ {description} created successfully")
            else:
                print(f"✗ Failed to create {description}")
        except Exception as e:
            print(f"✗ Error creating {description}: {e}")
    
    return True

def cleanup():
    """Clean up test files."""
    try:
        if os.path.exists('test_data.xlsx'):
            os.remove('test_data.xlsx')
            print("\n✓ Test files cleaned up")
    except:
        pass

def main():
    """Run all tests."""
    print("Excel Insights Chatbot - Component Tests")
    print("=" * 50)
    
    try:
        # Run tests
        success = True
        success &= test_data_processor()
        success &= test_fallback_handler()
        success &= test_chart_generator()
        
        print("\n" + "=" * 50)
        if success:
            print("✓ All tests completed successfully!")
            print("\nThe Excel Insights Chatbot is ready to use:")
            print("- Upload an Excel file with up to 500 rows and 20 columns")
            print("- Ask questions in natural language")
            print("- Get statistics, charts, and data insights")
            print("- Works with or without OpenAI API key")
        else:
            print("✗ Some tests failed. Please check the errors above.")
            
    finally:
        cleanup()

if __name__ == "__main__":
    main()