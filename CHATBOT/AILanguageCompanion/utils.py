import pandas as pd
import re
from typing import Tuple, Optional, Dict, Any

class DataUtils:
    @staticmethod
    def extract_product_name(query: str, products: list) -> str:
        """Extract product name from natural language query."""
        query = query.lower()
        for product in products:
            if product.lower() in query:
                return product
        raise ValueError(f"Product not found in query. Available products: {', '.join(products)}")

    @staticmethod
    def detect_columns(query: str, available_columns: list) -> list:
        """Identify which columns are being referenced in a query."""
        detected = []
        query = query.lower()
        for col in available_columns:
            if col.lower() in query:
                detected.append(col)
        return detected

    @staticmethod
    def calculate_revenue(df: pd.DataFrame) -> pd.DataFrame:
        """Add revenue column if Price and Quantity exist."""
        if 'Price' in df.columns and 'Quantity' in df.columns:
            df['Revenue'] = df['Price'] * df['Quantity']
        return df

    @staticmethod
    def normalize_query(query: str) -> str:
        """Standardize query terms for better matching."""
        replacements = {
            'show me': 'show',
            'display': 'show',
            'graph': 'plot',
            'chart': 'plot',
            'diagram': 'plot',
            'numbers': 'count',
            'average': 'mean'
        }
        query = query.lower()
        for old, new in replacements.items():
            query = query.replace(old, new)
        return query

    @staticmethod
    def get_column_stats(df: pd.DataFrame, column: str) -> dict:
        """Generate statistics for a specific column."""
        if column not in df.columns:
            return {"error": f"Column '{column}' not found"}
        
        stats = {
            "column": column,
            "type": str(df[column].dtype),
            "count": len(df[column]),
            "missing": df[column].isna().sum()
        }
        
        if pd.api.types.is_numeric_dtype(df[column]):
            stats.update({
                "mean": df[column].mean(),
                "min": df[column].min(),
                "max": df[column].max(),
                "median": df[column].median()
            })
        else:
            stats["unique_values"] = df[column].nunique()
            stats["most_common"] = df[column].mode().iloc[0] if not df[column].empty else None
        
        return stats
