import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class ChartGenerator:
    """
    Generates various types of charts using Plotly based on data and query intent.
    """
    
    def __init__(self):
        # Default color palette
        self.colors = px.colors.qualitative.Set3
    
    def create_chart(self, df: pd.DataFrame, columns: List[str], chart_type: str, 
                    original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """
        Create a chart based on specified parameters.
        
        Args:
            df: DataFrame with data
            columns: List of column names to visualize
            chart_type: Type of chart to create
            original_columns: Mapping from normalized to original column names
            column_types: Column type information
            
        Returns:
            Plotly figure or None if chart cannot be created
        """
        try:
            if not columns or len(columns) == 0:
                return None
            
            # Map chart type to appropriate method
            if chart_type.lower() in ['bar', 'column']:
                return self._create_bar_chart(df, columns, original_columns, column_types)
            elif chart_type.lower() in ['histogram', 'hist']:
                return self._create_histogram(df, columns, original_columns, column_types)
            elif chart_type.lower() in ['line', 'time_series']:
                return self._create_line_chart(df, columns, original_columns, column_types)
            elif chart_type.lower() in ['scatter', 'scatterplot']:
                return self._create_scatter_plot(df, columns, original_columns, column_types)
            elif chart_type.lower() in ['pie']:
                return self._create_pie_chart(df, columns, original_columns, column_types)
            elif chart_type.lower() in ['box', 'boxplot']:
                return self._create_box_plot(df, columns, original_columns, column_types)
            else:
                # Default to bar chart for categorical data, histogram for numeric
                if len(columns) == 1:
                    col = columns[0]
                    if column_types.get(col) == 'numeric':
                        return self._create_histogram(df, columns, original_columns, column_types)
                    else:
                        return self._create_bar_chart(df, columns, original_columns, column_types)
                else:
                    return self._create_bar_chart(df, columns, original_columns, column_types)
        
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None
    
    def _create_bar_chart(self, df: pd.DataFrame, columns: List[str], 
                         original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a bar chart."""
        try:
            if len(columns) == 1:
                col = columns[0]
                orig_name = original_columns.get(col, col)
                
                if column_types.get(col) == 'numeric':
                    # For numeric columns, create bins
                    bins = pd.cut(df[col].dropna(), bins=10)
                    counts = bins.value_counts().sort_index()
                    
                    fig = px.bar(
                        x=[str(interval) for interval in counts.index],
                        y=counts.values,
                        title=f'Distribution of {orig_name}',
                        labels={'x': orig_name, 'y': 'Count'}
                    )
                else:
                    # For categorical columns, show value counts
                    value_counts = df[col].value_counts().head(20)  # Limit to top 20
                    
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f'Count by {orig_name}',
                        labels={'x': orig_name, 'y': 'Count'}
                    )
            
            elif len(columns) == 2:
                col1, col2 = columns[0], columns[1]
                orig_name1 = original_columns.get(col1, col1)
                orig_name2 = original_columns.get(col2, col2)
                
                # Group by first column and aggregate second column
                if column_types.get(col2) == 'numeric':
                    grouped = df.groupby(col1)[col2].mean().reset_index()
                    fig = px.bar(
                        grouped,
                        x=col1,
                        y=col2,
                        title=f'Average {orig_name2} by {orig_name1}',
                        labels={col1: orig_name1, col2: f'Average {orig_name2}'}
                    )
                else:
                    # Cross-tabulation
                    crosstab = pd.crosstab(df[col1], df[col2])
                    fig = px.bar(
                        crosstab,
                        title=f'{orig_name2} by {orig_name1}',
                        labels={'value': 'Count', 'index': orig_name1}
                    )
            
            else:
                return None
            
            # Update layout for better appearance
            fig.update_layout(
                showlegend=True,
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16,
                xaxis_tickangle=-45
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
            return None
    
    def _create_histogram(self, df: pd.DataFrame, columns: List[str], 
                         original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a histogram."""
        try:
            if len(columns) != 1:
                return None
            
            col = columns[0]
            orig_name = original_columns.get(col, col)
            
            if column_types.get(col) != 'numeric':
                return None
            
            fig = px.histogram(
                df,
                x=col,
                title=f'Distribution of {orig_name}',
                labels={col: orig_name, 'count': 'Frequency'},
                nbins=20
            )
            
            # Add mean line
            mean_val = df[col].mean()
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {mean_val:.2f}"
            )
            
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating histogram: {e}")
            return None
    
    def _create_line_chart(self, df: pd.DataFrame, columns: List[str], 
                          original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a line chart."""
        try:
            if len(columns) < 2:
                return None
            
            x_col, y_col = columns[0], columns[1]
            x_orig = original_columns.get(x_col, x_col)
            y_orig = original_columns.get(y_col, y_col)
            
            # Sort by x column for proper line chart
            df_sorted = df.sort_values(x_col)
            
            fig = px.line(
                df_sorted,
                x=x_col,
                y=y_col,
                title=f'{y_orig} over {x_orig}',
                labels={x_col: x_orig, y_col: y_orig}
            )
            
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating line chart: {e}")
            return None
    
    def _create_scatter_plot(self, df: pd.DataFrame, columns: List[str], 
                            original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a scatter plot."""
        try:
            if len(columns) < 2:
                return None
            
            x_col, y_col = columns[0], columns[1]
            x_orig = original_columns.get(x_col, x_col)
            y_orig = original_columns.get(y_col, y_col)
            
            # Use third column for color if available
            color_col = columns[2] if len(columns) > 2 else None
            color_orig = original_columns.get(color_col, color_col) if color_col else None
            
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f'{y_orig} vs {x_orig}',
                labels={
                    x_col: x_orig, 
                    y_col: y_orig,
                    color_col: color_orig if color_col else None
                }
            )
            
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating scatter plot: {e}")
            return None
    
    def _create_pie_chart(self, df: pd.DataFrame, columns: List[str], 
                         original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a pie chart."""
        try:
            if len(columns) != 1:
                return None
            
            col = columns[0]
            orig_name = original_columns.get(col, col)
            
            if column_types.get(col) == 'numeric':
                return None  # Pie charts not suitable for numeric data
            
            value_counts = df[col].value_counts().head(10)  # Limit to top 10
            
            fig = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=f'Distribution of {orig_name}'
            )
            
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return None
    
    def _create_box_plot(self, df: pd.DataFrame, columns: List[str], 
                        original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a box plot."""
        try:
            if len(columns) == 1:
                col = columns[0]
                orig_name = original_columns.get(col, col)
                
                if column_types.get(col) != 'numeric':
                    return None
                
                fig = px.box(
                    df,
                    y=col,
                    title=f'Box Plot of {orig_name}',
                    labels={col: orig_name}
                )
            
            elif len(columns) == 2:
                x_col, y_col = columns[0], columns[1]
                x_orig = original_columns.get(x_col, x_col)
                y_orig = original_columns.get(y_col, y_col)
                
                if column_types.get(y_col) != 'numeric':
                    return None
                
                fig = px.box(
                    df,
                    x=x_col,
                    y=y_col,
                    title=f'{y_orig} by {x_orig}',
                    labels={x_col: x_orig, y_col: y_orig}
                )
            
            else:
                return None
            
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating box plot: {e}")
            return None
    
    def create_comparison_chart(self, df: pd.DataFrame, columns: List[str], 
                               original_columns: Dict[str, str], column_types: Dict[str, str]) -> Optional[go.Figure]:
        """Create a comparison chart for multiple columns."""
        try:
            if len(columns) < 2:
                return None
            
            # If we have one categorical and one numeric column
            categorical_cols = [col for col in columns if column_types.get(col) in ['categorical', 'binary']]
            numeric_cols = [col for col in columns if column_types.get(col) == 'numeric']
            
            if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                
                cat_orig = original_columns.get(cat_col, cat_col)
                num_orig = original_columns.get(num_col, num_col)
                
                # Group by categorical column and show statistics for numeric column
                grouped = df.groupby(cat_col)[num_col].agg(['mean', 'count']).reset_index()
                
                fig = px.bar(
                    grouped,
                    x=cat_col,
                    y='mean',
                    title=f'Average {num_orig} by {cat_orig}',
                    labels={cat_col: cat_orig, 'mean': f'Average {num_orig}'},
                    hover_data=['count']
                )
                
                fig.update_layout(
                    template='plotly_white',
                    font=dict(size=12),
                    title_font_size=16,
                    xaxis_tickangle=-45
                )
                
                return fig
            
            # If all columns are numeric, create a correlation chart
            elif len(numeric_cols) >= 2:
                correlation_matrix = df[numeric_cols].corr()
                return self.create_correlation_heatmap(correlation_matrix, original_columns)
            
            else:
                # Default to grouped bar chart
                return self._create_bar_chart(df, columns, original_columns, column_types)
                
        except Exception as e:
            print(f"Error creating comparison chart: {e}")
            return None
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame, 
                                  original_columns: Dict[str, str]) -> Optional[go.Figure]:
        """Create a correlation heatmap."""
        try:
            # Replace column names with original names
            display_matrix = correlation_matrix.copy()
            display_columns = [original_columns.get(col, col) for col in correlation_matrix.columns]
            display_index = [original_columns.get(col, col) for col in correlation_matrix.index]
            
            fig = px.imshow(
                display_matrix.values,
                x=display_columns,
                y=display_index,
                color_continuous_scale='RdBu_r',
                aspect='auto',
                title='Correlation Matrix',
                zmin=-1,
                zmax=1
            )
            
            # Add correlation values as text
            for i in range(len(display_index)):
                for j in range(len(display_columns)):
                    fig.add_annotation(
                        x=j, y=i,
                        text=f"{display_matrix.iloc[i, j]:.2f}",
                        showarrow=False,
                        font=dict(color="white" if abs(display_matrix.iloc[i, j]) > 0.5 else "black")
                    )
            
            fig.update_layout(
                template='plotly_white',
                font=dict(size=12),
                title_font_size=16
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating correlation heatmap: {e}")
            return None
