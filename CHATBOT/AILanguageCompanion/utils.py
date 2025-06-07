import pandas as pd
import re
from typing import Union, Dict, List, Optional
from datetime import datetime

class DataUtils:
    """Utility functions for data processing and query parsing"""
    
    @staticmethod
    def normalize_column_name(query: str, columns: List[str]) -> Optional[str]:
        """Match query terms to actual column names"""
        query = query.lower()
        col_mapping = {
            'sales': 'Revenue',
            'income': 'Price',
            'amount': 'Quantity',
            'region': 'Region',
            'date': 'Date',
            'product': 'Product'
        }
        
        # Check direct matches first
        for col in columns:
            if col.lower() in query:
                return col
        
        # Check common synonyms
        for term, col in col_mapping.items():
            if term in query and col in columns:
                return col
        
        return None

    @staticmethod
    def detect_date_columns(df: pd.DataFrame) -> List[str]:
        """Identify potential date columns"""
        date_cols = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols.append(col)
            elif 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_cols.append(col)
                except:
                    continue
        return date_cols

    @staticmethod
    def calculate_revenue(df: pd.DataFrame) -> pd.DataFrame:
        """Add revenue column if Price and Quantity exist"""
        if 'Price' in df.columns and 'Quantity' in df.columns:
            df['Revenue'] = df['Price'] * df['Quantity']
        return df

    @staticmethod
    def parse_date_range(query: str) -> Optional[Dict[str, datetime]]:
        """Extract date ranges from queries"""
        date_patterns = [
            r'from (\w+ \d{1,2},? \d{4}) to (\w+ \d{1,2},? \d{4})',
            r'between (\w+ \d{1,2},? \d{4}) and (\w+ \d{1,2},? \d{4})',
            r'(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    return {
                        'start': pd.to_datetime(match.group(1)),
                        'end': pd.to_datetime(match.group(2))
                    }
                except:
                    continue
        return None

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> bool:
        """Check if DataFrame meets requirements"""
        if df.empty:
            return False
        if len(df.columns) < 2:
            return False
        return True

    @staticmethod
    def get_column_stats(df: pd.DataFrame, column: str) -> Dict[str, Union[str, float]]:
        """Generate statistics for a specific column"""
        stats = {
            'name': column,
            'type': str(df[column].dtype),
            'missing': df[column].isna().sum()
        }
        
        if pd.api.types.is_numeric_dtype(df[column]):
            stats.update({
                'mean': df[column].mean(),
                'min': df[column].min(),
                'max': df[column].max(),
                'median': df[column].median()
            })
        else:
            stats['unique'] = df[column].nunique()
            stats['sample_values'] = df[column].dropna().unique()[:5].tolist()
        
        return stats
