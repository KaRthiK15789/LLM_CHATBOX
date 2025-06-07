import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_sample_excel_files():
    """Create sample Excel files for testing the chatbot."""
    
    # Sample 1: Employee Data
    np.random.seed(42)
    
    employees_data = {
        'Employee ID': range(1, 101),
        'Name': [f'Employee_{i}' for i in range(1, 101)],
        'Age': np.random.randint(22, 65, 100),
        'Department': np.random.choice(['Sales', 'Marketing', 'IT', 'HR', 'Finance'], 100),
        'Salary': np.random.randint(30000, 120000, 100),
        'Years Experience': np.random.randint(0, 25, 100),
        'Gender': np.random.choice(['Male', 'Female'], 100),
        'Remote Work': np.random.choice(['Yes', 'No'], 100),
        'Performance Rating': np.random.choice([1, 2, 3, 4, 5], 100),
        'Bonus Eligible': np.random.choice([True, False], 100)
    }
    
    df_employees = pd.DataFrame(employees_data)
    df_employees.to_excel('sample_employee_data.xlsx', index=False)
    
    # Sample 2: Sales Data
    sales_data = {
        'Transaction ID': range(1, 201),
        'Customer Age': np.random.randint(18, 80, 200),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 200),
        'Product Category': np.random.choice(['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books'], 200),
        'Sale Amount': np.random.uniform(10, 1000, 200).round(2),
        'Customer Type': np.random.choice(['New', 'Returning'], 200),
        'Payment Method': np.random.choice(['Credit Card', 'Cash', 'Debit Card', 'Online'], 200),
        'Satisfaction Score': np.random.randint(1, 10, 200),
        'Discount Applied': np.random.choice(['Yes', 'No'], 200),
        'Delivery Required': np.random.choice([1, 0], 200)
    }
    
    df_sales = pd.DataFrame(sales_data)
    df_sales.to_excel('sample_sales_data.xlsx', index=False)
    
    # Sample 3: Customer Survey Data
    survey_data = {
        'Response ID': range(1, 151),
        'Customer ID': np.random.randint(1000, 9999, 150),
        'Age Group': np.random.choice(['18-25', '26-35', '36-45', '46-55', '55+'], 150),
        'Income Level': np.random.choice(['Low', 'Medium', 'High'], 150),
        'Product Rating': np.random.randint(1, 5, 150),
        'Service Rating': np.random.randint(1, 5, 150),
        'Overall Satisfaction': np.random.randint(1, 10, 150),
        'Recommend to Friend': np.random.choice(['Yes', 'No', 'Maybe'], 150),
        'Previous Customer': np.random.choice(['Y', 'N'], 150),
        'Monthly Spending': np.random.uniform(50, 500, 150).round(2)
    }
    
    df_survey = pd.DataFrame(survey_data)
    df_survey.to_excel('sample_survey_data.xlsx', index=False)
    
    print("Sample Excel files created:")
    print("- sample_employee_data.xlsx (100 rows, 10 columns)")
    print("- sample_sales_data.xlsx (200 rows, 10 columns)")
    print("- sample_survey_data.xlsx (150 rows, 10 columns)")

if __name__ == "__main__":
    create_sample_excel_files()