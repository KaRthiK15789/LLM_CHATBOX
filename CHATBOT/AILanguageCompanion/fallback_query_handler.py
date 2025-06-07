import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List, Optional
from visualization import ChartGenerator

class FallbackQueryHandler:
    """
    Handles natural language queries using rule-based parsing when OpenAI is unavailable.
    Provides basic data analysis capabilities without external API dependencies.
    """
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.chart_generator = ChartGenerator()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query using rule-based approach.
        
        Args:
            query: Natural language question about the data
            
        Returns:
            Dictionary with response type and content
        """
        try:
            query_lower = query.lower().strip()
            
            # Analyze query intent using rule-based patterns
            if self._is_summary_query(query_lower):
                return self._handle_summary_query(query_lower)
            elif self._is_visualization_query(query_lower):
                return self._handle_visualization_query(query_lower)
            elif self._is_filter_query(query_lower):
                return self._handle_filter_query(query_lower)
            elif self._is_comparison_query(query_lower):
                return self._handle_comparison_query(query_lower)
            elif self._is_correlation_query(query_lower):
                return self._handle_correlation_query(query_lower)
            else:
                return self._handle_general_query(query_lower)
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"An error occurred while processing your query: {str(e)}"
            }
    
    def _is_summary_query(self, query: str) -> bool:
        """Check if query is asking for summary statistics."""
        summary_keywords = [
            'average', 'mean', 'sum', 'total', 'count', 'minimum', 'maximum', 
            'min', 'max', 'median', 'std', 'standard deviation', 'statistics',
            'how many', 'what is the'
        ]
        return any(keyword in query for keyword in summary_keywords)
    
    def _is_visualization_query(self, query: str) -> bool:
        """Check if query is asking for visualization."""
        viz_keywords = [
            'chart', 'graph', 'plot', 'histogram', 'bar chart', 'line chart',
            'scatter plot', 'pie chart', 'box plot', 'show', 'visualize',
            'display', 'create a'
        ]
        return any(keyword in query for keyword in viz_keywords)
    
    def _is_filter_query(self, query: str) -> bool:
        """Check if query involves filtering."""
        filter_keywords = [
            'where', 'filter', 'under', 'over', 'above', 'below', 'greater than',
            'less than', 'equal to', 'customers who', 'records where'
        ]
        return any(keyword in query for keyword in filter_keywords)
    
    def _is_comparison_query(self, query: str) -> bool:
        """Check if query involves comparison."""
        comparison_keywords = [
            'compare', 'comparison', 'by', 'across', 'between', 'vs', 'versus'
        ]
        return any(keyword in query for keyword in comparison_keywords)
    
    def _is_correlation_query(self, query: str) -> bool:
        """Check if query asks for correlation."""
        correlation_keywords = [
            'correlation', 'relationship', 'related', 'correlated'
        ]
        return any(keyword in query for keyword in correlation_keywords)
    
    def _find_columns_in_query(self, query: str) -> List[str]:
        """Find column names mentioned in the query."""
        found_columns = []
        
        # Check normalized column names
        for col in self.data_processor.df.columns:
            if col.replace('_', ' ') in query or col in query:
                found_columns.append(col)
        
        # Check original column names
        for norm_col, orig_col in self.data_processor.original_columns.items():
            if orig_col.lower() in query:
                found_columns.append(norm_col)
        
        # Look for common data terms and map to likely columns
        if not found_columns:
            found_columns = self._infer_columns_from_terms(query)
        
        return list(set(found_columns))
    
    def _infer_columns_from_terms(self, query: str) -> List[str]:
        """Infer columns based on common terms in query."""
        term_mappings = {
            'age': ['age'],
            'income': ['income', 'salary', 'wage'],
            'sales': ['sales', 'revenue'],
            'price': ['price', 'cost', 'amount'],
            'gender': ['gender', 'sex'],
            'region': ['region', 'location', 'area'],
            'department': ['department', 'dept'],
            'employee': ['employee', 'staff', 'worker'],
            'customer': ['customer', 'client'],
            'date': ['date', 'time'],
            'status': ['status', 'state']
        }
        
        found_columns = []
        for term, possible_cols in term_mappings.items():
            if term in query:
                for col in self.data_processor.df.columns:
                    col_lower = col.lower()
                    orig_lower = self.data_processor.original_columns.get(col, '').lower()
                    
                    if any(pc in col_lower or pc in orig_lower for pc in possible_cols):
                        found_columns.append(col)
        
        return found_columns
    
    def _handle_summary_query(self, query: str) -> Dict[str, Any]:
        """Handle summary statistics queries."""
        try:
            columns = self._find_columns_in_query(query)
            
            if not columns:
                # If no specific columns found, show general dataset statistics
                stats = {
                    "Dataset Summary": "General Statistics",
                    "Total Rows": len(self.data_processor.df),
                    "Total Columns": len(self.data_processor.df.columns),
                    "Numeric Columns": len(self.data_processor.numeric_columns),
                    "Categorical Columns": len(self.data_processor.categorical_columns),
                    "Missing Values": self.data_processor.df.isnull().sum().sum()
                }
                
                explanation = "Here's a general summary of your dataset:"
                return {
                    "type": "combined",
                    "text": explanation,
                    "dataframe": pd.DataFrame([stats])
                }
            
            results = []
            for col in columns[:5]:  # Limit to 5 columns
                if col in self.data_processor.df.columns:
                    orig_name = self.data_processor.original_columns.get(col, col)
                    col_data = self.data_processor.df[col].dropna()
                    
                    if col in self.data_processor.numeric_columns:
                        if 'average' in query or 'mean' in query:
                            value = round(col_data.mean(), 2) if len(col_data) > 0 else 0
                            results.append({"Statistic": f"Average {orig_name}", "Value": value})
                        elif 'sum' in query or 'total' in query:
                            value = round(col_data.sum(), 2) if len(col_data) > 0 else 0
                            results.append({"Statistic": f"Total {orig_name}", "Value": value})
                        elif 'count' in query:
                            results.append({"Statistic": f"Count of {orig_name}", "Value": len(col_data)})
                        elif 'min' in query:
                            value = col_data.min() if len(col_data) > 0 else 0
                            results.append({"Statistic": f"Minimum {orig_name}", "Value": value})
                        elif 'max' in query:
                            value = col_data.max() if len(col_data) > 0 else 0
                            results.append({"Statistic": f"Maximum {orig_name}", "Value": value})
                        else:
                            # Default comprehensive stats
                            stats = {
                                "Column": orig_name,
                                "Count": len(col_data),
                                "Mean": round(col_data.mean(), 2) if len(col_data) > 0 else None,
                                "Min": col_data.min() if len(col_data) > 0 else None,
                                "Max": col_data.max() if len(col_data) > 0 else None
                            }
                            results.append(stats)
                    
                    elif col in self.data_processor.categorical_columns + self.data_processor.binary_columns:
                        if 'count' in query:
                            unique_count = col_data.nunique()
                            results.append({"Statistic": f"Unique values in {orig_name}", "Value": unique_count})
                        else:
                            value_counts = col_data.value_counts()
                            most_common = value_counts.index[0] if len(value_counts) > 0 else "None"
                            results.append({"Statistic": f"Most common {orig_name}", "Value": most_common})
            
            if results:
                results_df = pd.DataFrame(results)
                explanation = f"Here are the statistics for the columns I found in your query:"
                return {
                    "type": "combined",
                    "text": explanation,
                    "dataframe": results_df
                }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't find the specific columns you mentioned. Please check the column names in your data."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing summary query: {str(e)}"
            }
    
    def _handle_visualization_query(self, query: str) -> Dict[str, Any]:
        """Handle visualization requests."""
        try:
            columns = self._find_columns_in_query(query)
            
            if not columns:
                return {
                    "type": "error",
                    "content": "I couldn't identify which columns to visualize. Please specify the data you want to see."
                }
            
            # Determine chart type from query
            chart_type = "bar"
            if 'histogram' in query or 'distribution' in query:
                chart_type = "histogram"
            elif 'line' in query or 'trend' in query:
                chart_type = "line"
            elif 'scatter' in query:
                chart_type = "scatter"
            elif 'pie' in query:
                chart_type = "pie"
            elif 'box' in query:
                chart_type = "box"
            
            chart = self.chart_generator.create_chart(
                df=self.data_processor.df,
                columns=columns,
                chart_type=chart_type,
                original_columns=self.data_processor.original_columns,
                column_types=self.data_processor.column_types
            )
            
            if chart:
                col_names = [self.data_processor.original_columns.get(col, col) for col in columns]
                explanation = f"Here's your {chart_type} chart for {', '.join(col_names)}:"
                return {
                    "type": "chart",
                    "content": chart,
                    "explanation": explanation
                }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't create a chart with the specified data. Please try a different visualization request."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error creating visualization: {str(e)}"
            }
    
    def _handle_filter_query(self, query: str) -> Dict[str, Any]:
        """Handle filtered queries."""
        try:
            filtered_df = self.data_processor.df.copy()
            condition_applied = False
            
            # Look for age-based filters
            age_pattern = r'under (\d+)|over (\d+)|above (\d+)|below (\d+)'
            matches = re.findall(age_pattern, query)
            
            if matches:
                age_cols = [col for col in self.data_processor.numeric_columns 
                           if 'age' in col.lower() or 'age' in self.data_processor.original_columns.get(col, '').lower()]
                
                if age_cols:
                    age_col = age_cols[0]
                    for match in matches:
                        if match[0]:  # under X
                            filtered_df = filtered_df[filtered_df[age_col] < int(match[0])]
                            condition_applied = True
                        elif match[1] or match[2]:  # over X or above X
                            threshold = int(match[1] or match[2])
                            filtered_df = filtered_df[filtered_df[age_col] > threshold]
                            condition_applied = True
                        elif match[3]:  # below X
                            filtered_df = filtered_df[filtered_df[age_col] < int(match[3])]
                            condition_applied = True
            
            # Look for specific value filters
            for col in self.data_processor.categorical_columns + self.data_processor.binary_columns:
                col_values = self.data_processor.df[col].dropna().unique()
                for value in col_values:
                    if str(value).lower() in query:
                        filtered_df = filtered_df[filtered_df[col] == value]
                        condition_applied = True
                        break
            
            if condition_applied:
                count = len(filtered_df)
                explanation = f"Found {count} records matching your criteria."
                
                if count > 0:
                    display_df = filtered_df.head(20)
                    display_df.columns = [self.data_processor.original_columns.get(col, col) for col in display_df.columns]
                    
                    return {
                        "type": "combined",
                        "text": explanation,
                        "dataframe": display_df
                    }
                else:
                    return {
                        "type": "text",
                        "content": "No records found matching your criteria."
                    }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't understand the filter conditions. Please try being more specific about what you want to filter."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing filter: {str(e)}"
            }
    
    def _handle_comparison_query(self, query: str) -> Dict[str, Any]:
        """Handle comparison queries."""
        try:
            columns = self._find_columns_in_query(query)
            
            if len(columns) < 2:
                return {
                    "type": "error",
                    "content": "I need at least two columns to make a comparison. Please specify what you want to compare."
                }
            
            chart = self.chart_generator.create_comparison_chart(
                df=self.data_processor.df,
                columns=columns,
                original_columns=self.data_processor.original_columns,
                column_types=self.data_processor.column_types
            )
            
            if chart:
                col_names = [self.data_processor.original_columns.get(col, col) for col in columns]
                explanation = f"Comparison of {' and '.join(col_names)}:"
                return {
                    "type": "chart",
                    "content": chart,
                    "explanation": explanation
                }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't create a comparison chart with the specified columns."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error creating comparison: {str(e)}"
            }
    
    def _handle_correlation_query(self, query: str) -> Dict[str, Any]:
        """Handle correlation queries."""
        try:
            numeric_cols = self.data_processor.numeric_columns
            
            if len(numeric_cols) < 2:
                return {
                    "type": "error",
                    "content": "I need at least two numeric columns to calculate correlations."
                }
            
            # Calculate correlation matrix
            correlation_matrix = self.data_processor.df[numeric_cols].corr()
            
            # Create heatmap
            chart = self.chart_generator.create_correlation_heatmap(
                correlation_matrix, 
                self.data_processor.original_columns
            )
            
            if chart:
                explanation = "Here's the correlation matrix showing relationships between numeric variables:"
                return {
                    "type": "chart",
                    "content": chart,
                    "explanation": explanation
                }
            else:
                return {
                    "type": "combined",
                    "text": "Here's the correlation matrix:",
                    "dataframe": correlation_matrix
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error calculating correlations: {str(e)}"
            }
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries."""
        try:
            columns = self._find_columns_in_query(query)
            
            if columns:
                # Show basic info about the mentioned columns
                info_data = []
                for col in columns[:5]:
                    if col in self.data_processor.df.columns:
                        orig_name = self.data_processor.original_columns.get(col, col)
                        col_type = self.data_processor.column_types.get(col, 'unknown')
                        non_null = self.data_processor.df[col].count()
                        unique_vals = self.data_processor.df[col].nunique()
                        
                        info_data.append({
                            "Column": orig_name,
                            "Type": col_type,
                            "Non-null Count": non_null,
                            "Unique Values": unique_vals
                        })
                
                if info_data:
                    info_df = pd.DataFrame(info_data)
                    explanation = "Here's information about the columns you mentioned:"
                    return {
                        "type": "combined",
                        "text": explanation,
                        "dataframe": info_df
                    }
            
            # Default response with dataset overview
            summary_stats = {
                "Total Rows": len(self.data_processor.df),
                "Total Columns": len(self.data_processor.df.columns),
                "Numeric Columns": len(self.data_processor.numeric_columns),
                "Categorical Columns": len(self.data_processor.categorical_columns)
            }
            
            explanation = "I'm not sure exactly what you're looking for. Here's a general overview of your dataset. Try asking specific questions like 'What is the average age?' or 'Show a bar chart of sales by region'."
            
            return {
                "type": "combined",
                "text": explanation,
                "dataframe": pd.DataFrame([summary_stats])
            }
            
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing query: {str(e)}"
            }