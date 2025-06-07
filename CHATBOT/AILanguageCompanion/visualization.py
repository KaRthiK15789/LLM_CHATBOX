import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Optional
from utils import DataUtils

class ChartGenerator:
    def __init__(self):
        self.utils = DataUtils()
        self.colors = px.colors.qualitative.Plotly

    def create_chart(self, df: pd.DataFrame, query: str, columns: List[str]) -> Optional[go.Figure]:
        """Main method to create appropriate chart based on query."""
        try:
            df = self.utils.calculate_revenue(df.copy())
            query = self.utils.normalize_query(query)
            
            # Handle specific chart requests
            if "pie" in query and "revenue" in query:
                return self._create_pie_chart(df, 'Product', 'Revenue', 'Revenue Share by Product')
            
            if "pie" in query:
                col = self._find_best_column(df, columns, ['Product', 'Category', 'Type'])
                if col:
                    return self._create_pie_chart(df, col, None, f'Distribution of {col}')
            
            if "bar" in query or "compare" in query:
                if "region" in query or "region" in [c.lower() for c in columns]:
                    region_col = next((c for c in columns if "region" in c.lower()), columns[0])
                    return self._create_bar_chart(df, region_col, 'Quantity', f'Quantity by {region_col}')
                return self._create_comparison_chart(df, columns)
            
            if "time" in query or "date" in query:
                date_col = next((c for c in columns if "date" in c.lower()), None)
                if date_col:
                    return self._create_time_series(df, date_col, self._find_numeric_column(df, columns))
            
            # Default to showing first categorical vs numeric columns
            return self._create_smart_default_chart(df, columns)
        
        except Exception as e:
            print(f"Chart generation error: {str(e)}")
            return None

    def _create_pie_chart(self, df: pd.DataFrame, names_col: str, values_col: str = None, 
                         title: str = None) -> go.Figure:
        """Create a pie chart."""
        if values_col:
            fig = px.pie(df, names=names_col, values=values_col, title=title)
        else:
            counts = df[names_col].value_counts().reset_index()
            counts.columns = [names_col, 'count']
            fig = px.pie(counts, names=names_col, values='count', title=title)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        return fig

    def _create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
        """Create a bar chart."""
        fig = px.bar(df, x=x_col, y=y_col, title=title, color=x_col)
        fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
        return fig

    def _create_time_series(self, df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
        """Create a time series line chart."""
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        fig = px.line(df, x=date_col, y=value_col, 
                     title=f'{value_col} over Time')
        fig.update_xaxes(title='Date')
        fig.update_yaxes(title=value_col)
        return fig

    def _create_comparison_chart(self, df: pd.DataFrame, columns: List[str]) -> go.Figure:
        """Create a comparison chart between columns."""
        numeric_cols = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]
        cat_cols = [c for c in columns if not pd.api.types.is_numeric_dtype(df[c])]
        
        if numeric_cols and cat_cols:
            # Compare numeric across categories
            return px.bar(df, x=cat_cols[0], y=numeric_cols[0], color=cat_cols[0],
                         title=f'{numeric_cols[0]} by {cat_cols[0]}')
        elif len(numeric_cols) >= 2:
            # Compare multiple numeric columns
            return px.bar(df[numeric_cols].mean().reset_index(), 
                         x='index', y=0, title='Comparison of Metrics')
        else:
            # Show value counts for categorical data
            return px.bar(df[cat_cols[0]].value_counts().reset_index(),
                         x='index', y=cat_cols[0], title=f'Count by {cat_cols[0]}')

    def _create_smart_default_chart(self, df: pd.DataFrame, columns: List[str]) -> go.Figure:
        """Create a sensible default chart based on data types."""
        numeric_cols = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]
        cat_cols = [c for c in columns if not pd.api.types.is_numeric_dtype(df[c])]
        
        if not numeric_cols and not cat_cols:
            return None
            
        if numeric_cols and cat_cols:
            # Show relationship between categorical and numeric
            return px.box(df, x=cat_cols[0], y=numeric_cols[0],
                         title=f'{numeric_cols[0]} by {cat_cols[0]}')
        elif numeric_cols:
            # Show distribution of numeric data
            return px.histogram(df, x=numeric_cols[0], 
                              title=f'Distribution of {numeric_cols[0]}')
        else:
            # Show value counts for categorical data
            return px.bar(df[cat_cols[0]].value_counts().reset_index(),
                         x='index', y=cat_cols[0],
                         title=f'Count by {cat_cols[0]}')

    def _find_best_column(self, df: pd.DataFrame, columns: List[str], 
                         preferred: List[str] = None) -> Optional[str]:
        """Find the most appropriate column for visualization."""
        if preferred:
            for col in preferred:
                if col in columns:
                    return col
        return columns[0] if columns else None

    def _find_numeric_column(self, df: pd.DataFrame, columns: List[str]) -> Optional[str]:
        """Find the first numeric column."""
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                return col
        return None
