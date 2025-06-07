import pandas as pd
import numpy as np
import re
from typing import Tuple, Dict, Any, List
import io

class DataProcessor:
    """
    Handles Excel file loading, data preprocessing, and column normalization.
    Designed to be completely schema-agnostic.
    """
    
    def __init__(self):
        self.df = None
        self.original_columns = {}  # Maps normalized names to original names
        self.column_types = {}
        self.numeric_columns = []
        self.categorical_columns = []
        self.binary_columns = []
        self.datetime_columns = []
    
    def load_excel(self, uploaded_file) -> Tuple[bool, str]:
        """
        Load and preprocess Excel file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file, sheet_name=0)  # Read first sheet only
            
            # Basic validation
            if df.empty:
                return False, "The Excel file is empty."
            
            if df.shape[0] > 500:
                return False, f"File has {df.shape[0]} rows. Maximum allowed is 500 rows."
            
            if df.shape[1] > 20:
                return False, f"File has {df.shape[1]} columns. Maximum allowed is 20 columns."
            
            if df.shape[1] < 1:
                return False, "File must have at least 1 column."
            
            # Store original column names and normalize them
            self.original_columns = {}
            normalized_columns = []
            
            for col in df.columns:
                normalized_col = self._normalize_column_name(str(col))
                self.original_columns[normalized_col] = col
                normalized_columns.append(normalized_col)
            
            # Check for duplicate normalized column names
            if len(set(normalized_columns)) != len(normalized_columns):
                return False, "Column names result in duplicates after normalization. Please ensure column names are distinct."
            
            # Update dataframe with normalized column names
            df.columns = normalized_columns
            self.df = df
            
            # Infer column types
            self._infer_column_types()
            
            return True, "File loaded successfully."
            
        except Exception as e:
            return False, f"Error reading Excel file: {str(e)}"
    
    def _normalize_column_name(self, col_name: str) -> str:
        """
        Normalize column names by removing special characters, 
        converting to lowercase, and replacing spaces with underscores.
        """
        # Remove leading/trailing whitespace
        col_name = col_name.strip()
        
        # Convert to lowercase
        col_name = col_name.lower()
        
        # Replace spaces and special characters with underscores
        col_name = re.sub(r'[^a-z0-9_]', '_', col_name)
        
        # Remove multiple consecutive underscores
        col_name = re.sub(r'_+', '_', col_name)
        
        # Remove leading/trailing underscores
        col_name = col_name.strip('_')
        
        # Ensure it's not empty
        if not col_name:
            col_name = 'unnamed_column'
        
        return col_name
    
    def _infer_column_types(self):
        """
        Automatically infer column types and categorize them.
        """
        self.column_types = {}
        self.numeric_columns = []
        self.categorical_columns = []
        self.binary_columns = []
        self.datetime_columns = []
        
        if self.df is not None:
            for col in self.df.columns:
                dtype = self.df[col].dtype
                
                # Try to infer datetime columns
                if self._is_datetime_column(col):
                    self.datetime_columns.append(col)
                    self.column_types[col] = 'datetime'
                    continue
                
                # Check if it's numeric
                if pd.api.types.is_numeric_dtype(dtype):
                    self.numeric_columns.append(col)
                    self.column_types[col] = 'numeric'
                
                # Check if it's binary (Yes/No, True/False, 0/1)
                elif self._is_binary_column(col):
                    self.binary_columns.append(col)
                    self.column_types[col] = 'binary'
                
                # Otherwise, treat as categorical
                else:
                    self.categorical_columns.append(col)
                    self.column_types[col] = 'categorical'
    
    def _is_datetime_column(self, col: str) -> bool:
        """Check if a column contains datetime values."""
        try:
            if self.df is None:
                return False
            # Try to convert a sample of non-null values to datetime
            sample = self.df[col].dropna().head(10)
            if len(sample) == 0:
                return False
            
            # Try to parse as datetime
            pd.to_datetime(sample, errors='raise')
            
            # If successful, convert the entire column
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            return True
        except:
            return False
    
    def _is_binary_column(self, col: str) -> bool:
        """Check if a column is binary (Yes/No, True/False, 0/1)."""
        try:
            if self.df is None:
                return False
            unique_values = self.df[col].dropna().unique()
            
            # Remove case sensitivity and strip whitespace
            unique_str = [str(val).strip().lower() for val in unique_values]
            unique_set = set(unique_str)
            
            # Check for various binary patterns
            binary_patterns = [
                {'yes', 'no'},
                {'true', 'false'},
                {'1', '0'},
                {'y', 'n'},
                {'1.0', '0.0'},
                {'male', 'female'},
                {'m', 'f'}
            ]
            
            for pattern in binary_patterns:
                if unique_set.issubset(pattern) and len(unique_set) <= 2:
                    return True
            
            # Check if it's numeric with only 0s and 1s
            if self.df is not None and pd.api.types.is_numeric_dtype(self.df[col]):
                unique_numeric = set(unique_values)
                if unique_numeric.issubset({0, 1, 0.0, 1.0}) and len(unique_numeric) <= 2:
                    return True
            
            return False
        except:
            return False
    
    def get_column_info(self) -> pd.DataFrame:
        """
        Get information about columns including their types and statistics.
        """
        if self.df is None:
            return pd.DataFrame()
        
        info_data = []
        
        for col in self.df.columns:
            col_info = {
                'Column': self.original_columns.get(col, col),
                'Normalized_Name': col,
                'Type': self.column_types.get(col, 'unknown'),
                'Non_Null_Count': self.df[col].count(),
                'Null_Count': self.df[col].isnull().sum(),
                'Unique_Values': self.df[col].nunique()
            }
            
            # Add type-specific statistics
            if col in self.numeric_columns:
                col_info['Min'] = self.df[col].min()
                col_info['Max'] = self.df[col].max()
                try:
                    mean_val = float(self.df[col].mean())
                    col_info['Mean'] = round(mean_val, 2) if not pd.isna(mean_val) else None
                except:
                    col_info['Mean'] = None
            elif col in self.categorical_columns or col in self.binary_columns:
                top_value = self.df[col].mode()
                col_info['Most_Common'] = top_value.iloc[0] if len(top_value) > 0 else None
            
            info_data.append(col_info)
        
        return pd.DataFrame(info_data)
    
    def get_column_suggestions(self, query_keywords: List[str]) -> List[str]:
        """
        Suggest relevant columns based on query keywords.
        """
        if self.df is None:
            return []
        
        suggestions = []
        query_lower = [kw.lower() for kw in query_keywords]
        
        for norm_col, orig_col in self.original_columns.items():
            # Check if any keyword matches column name
            for keyword in query_lower:
                if (keyword in norm_col.lower() or 
                    keyword in orig_col.lower() or
                    any(keyword in word for word in norm_col.lower().split('_'))):
                    suggestions.append(norm_col)
                    break
        
        return list(set(suggestions))
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the dataset.
        """
        if self.df is None:
            return {}
        
        stats = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'numeric_columns': len(self.numeric_columns),
            'categorical_columns': len(self.categorical_columns),
            'binary_columns': len(self.binary_columns),
            'datetime_columns': len(self.datetime_columns),
            'missing_values': self.df.isnull().sum().sum()
        }
        
        return stats
    
    def search_columns_by_content(self, search_term: str) -> List[str]:
        """
        Find columns that contain specific values or patterns.
        """
        if self.df is None:
            return []
        
        matching_columns = []
        search_lower = search_term.lower()
        
        for col in self.df.columns:
            # Check if the search term appears in column values
            try:
                col_str = self.df[col].astype(str).str.lower()
                if col_str.str.contains(search_lower, na=False).any():
                    matching_columns.append(col)
            except:
                continue
        
        return matching_columns
