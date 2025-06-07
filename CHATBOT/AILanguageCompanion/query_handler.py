import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from openai import OpenAI
from visualization import ChartGenerator
from fallback_query_handler import FallbackQueryHandler
import re

class QueryHandler:
    """
    Handles natural language queries using OpenAI GPT and generates appropriate responses.
    """
    
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.chart_generator = ChartGenerator()
        self.fallback_handler = FallbackQueryHandler(data_processor)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        self.openai_available = False
        
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                self.openai_available = True
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
                self.openai_available = False
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return appropriate response.
        
        Args:
            query: Natural language question about the data
            
        Returns:
            Dictionary with response type and content
        """
        try:
            # Check if OpenAI is available and try AI-powered analysis first
            if self.openai_available:
                try:
                    intent_analysis = self._analyze_query_intent(query)
                    
                    if intent_analysis:
                        # Execute the appropriate analysis based on intent
                        if intent_analysis["type"] == "summary_statistics":
                            return self._handle_summary_query(query, intent_analysis)
                        elif intent_analysis["type"] == "filtered_query":
                            return self._handle_filtered_query(query, intent_analysis)
                        elif intent_analysis["type"] == "visualization":
                            return self._handle_visualization_query(query, intent_analysis)
                        elif intent_analysis["type"] == "comparison":
                            return self._handle_comparison_query(query, intent_analysis)
                        elif intent_analysis["type"] == "correlation":
                            return self._handle_correlation_query(query, intent_analysis)
                        else:
                            return self._handle_general_query(query, intent_analysis)
                except Exception as e:
                    print(f"OpenAI processing failed: {e}")
                    # Fall back to rule-based processing
                    pass
            
            # Use fallback handler when OpenAI is unavailable or fails
            return self.fallback_handler.process_query(query)
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"An error occurred while processing your query: {str(e)}"
            }
    
    def _analyze_query_intent(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI to analyze query intent and extract relevant information.
        """
        try:
            # Get column information for context
            column_info = self._get_column_context()
            
            system_prompt = f"""You are a data analysis assistant. Analyze the user's natural language query about a dataset and determine the intent and required operations.

Dataset Context:
{column_info}

Classify the query into one of these types:
1. summary_statistics: Questions asking for averages, sums, counts, min, max, etc.
2. filtered_query: Questions with conditions (e.g., "customers under 30")
3. visualization: Questions asking for charts, graphs, plots
4. comparison: Questions comparing groups or categories
5. correlation: Questions about relationships between variables
6. general: Other data exploration questions

Extract:
- type: The query type from above
- columns: List of relevant column names (use normalized names from the context)
- operations: List of operations needed (e.g., "average", "count", "filter", "group_by")
- conditions: Any filter conditions mentioned
- chart_type: If visualization, suggest appropriate chart type
- explanation: Brief explanation of what the user wants

Respond in JSON format only."""

            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result
            return None
            
        except Exception as e:
            print(f"Error analyzing query intent: {e}")
            return None
    
    def _get_column_context(self) -> str:
        """
        Generate context about available columns for the LLM.
        """
        if not self.data_processor or self.data_processor.df is None:
            return "No data available."
        
        context_parts = []
        context_parts.append("Available columns and their information:")
        
        for col in self.data_processor.df.columns:
            orig_name = self.data_processor.original_columns.get(col, col)
            col_type = self.data_processor.column_types.get(col, 'unknown')
            
            context_parts.append(f"- {col} (original: '{orig_name}', type: {col_type})")
            
            # Add sample values for categorical/binary columns
            if col_type in ['categorical', 'binary']:
                unique_vals = self.data_processor.df[col].dropna().unique()[:5]
                context_parts.append(f"  Sample values: {list(unique_vals)}")
            elif col_type == 'numeric':
                min_val = self.data_processor.df[col].min()
                max_val = self.data_processor.df[col].max()
                context_parts.append(f"  Range: {min_val} to {max_val}")
        
        return "\n".join(context_parts)
    
    def _handle_summary_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle summary statistics queries."""
        try:
            columns = intent.get("columns", [])
            operations = intent.get("operations", [])
            
            if not columns:
                # If no specific columns mentioned, try to infer from query
                columns = self._infer_columns_from_query(query)
            
            results = []
            
            for col in columns:
                if col not in self.data_processor.df.columns:
                    continue
                
                orig_name = self.data_processor.original_columns.get(col, col)
                col_data = self.data_processor.df[col].dropna()
                
                if col in self.data_processor.numeric_columns:
                    stats = {
                        "Column": orig_name,
                        "Count": len(col_data),
                        "Mean": round(col_data.mean(), 2) if len(col_data) > 0 else None,
                        "Median": round(col_data.median(), 2) if len(col_data) > 0 else None,
                        "Min": col_data.min() if len(col_data) > 0 else None,
                        "Max": col_data.max() if len(col_data) > 0 else None,
                        "Std": round(col_data.std(), 2) if len(col_data) > 1 else None
                    }
                    results.append(stats)
                elif col in self.data_processor.categorical_columns + self.data_processor.binary_columns:
                    value_counts = col_data.value_counts()
                    stats = {
                        "Column": orig_name,
                        "Unique_Values": len(value_counts),
                        "Most_Common": value_counts.index[0] if len(value_counts) > 0 else None,
                        "Most_Common_Count": value_counts.iloc[0] if len(value_counts) > 0 else None,
                        "Total_Count": len(col_data)
                    }
                    results.append(stats)
            
            if results:
                results_df = pd.DataFrame(results)
                explanation = self._generate_explanation(query, results_df, "summary")
                
                return {
                    "type": "combined",
                    "text": explanation,
                    "dataframe": results_df
                }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't find the relevant columns to calculate statistics. Please check your question."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing summary query: {str(e)}"
            }
    
    def _handle_filtered_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filtered queries with conditions."""
        try:
            columns = intent.get("columns", [])
            conditions = intent.get("conditions", [])
            
            # Try to parse conditions from the query
            filtered_df = self.data_processor.df.copy()
            condition_applied = False
            
            # Look for common filter patterns
            age_pattern = r'under (\d+)|over (\d+)|above (\d+)|below (\d+)'
            matches = re.findall(age_pattern, query.lower())
            
            if matches:
                # Find age-related columns
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
                    if str(value).lower() in query.lower():
                        filtered_df = filtered_df[filtered_df[col] == value]
                        condition_applied = True
                        break
            
            if condition_applied:
                count = len(filtered_df)
                explanation = f"Found {count} records matching your criteria."
                
                if count > 0:
                    # Show first few rows
                    display_df = filtered_df.head(20)
                    # Use original column names for display
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
                    "content": "I couldn't understand the filter conditions in your query. Please try being more specific."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing filtered query: {str(e)}"
            }
    
    def _handle_visualization_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visualization requests."""
        try:
            columns = intent.get("columns", [])
            chart_type = intent.get("chart_type", "bar")
            
            if not columns:
                columns = self._infer_columns_from_query(query)
            
            if not columns:
                return {
                    "type": "error",
                    "content": "I couldn't identify which columns to visualize. Please specify the data you want to see."
                }
            
            # Generate chart based on intent
            chart = self.chart_generator.create_chart(
                df=self.data_processor.df,
                columns=columns,
                chart_type=chart_type,
                original_columns=self.data_processor.original_columns,
                column_types=self.data_processor.column_types
            )
            
            if chart:
                explanation = f"Here's a {chart_type} chart showing {', '.join([self.data_processor.original_columns.get(col, col) for col in columns])}:"
                return {
                    "type": "chart",
                    "content": chart,
                    "explanation": explanation
                }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't generate a chart with the specified data. Please try a different visualization request."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error creating visualization: {str(e)}"
            }
    
    def _handle_comparison_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comparison queries."""
        try:
            columns = intent.get("columns", [])
            
            if len(columns) < 2:
                columns = self._infer_columns_from_query(query)
            
            if len(columns) < 2:
                return {
                    "type": "error",
                    "content": "I need at least two columns to make a comparison. Please specify what you want to compare."
                }
            
            # Create comparison visualization
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
    
    def _handle_correlation_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle correlation analysis queries."""
        try:
            numeric_cols = self.data_processor.numeric_columns
            
            if len(numeric_cols) < 2:
                return {
                    "type": "error",
                    "content": "I need at least two numeric columns to analyze correlations."
                }
            
            # Calculate correlation matrix
            corr_data = self.data_processor.df[numeric_cols].corr()
            
            # Create correlation heatmap
            chart = self.chart_generator.create_correlation_heatmap(
                correlation_matrix=corr_data,
                original_columns=self.data_processor.original_columns
            )
            
            if chart:
                explanation = "Here's a correlation analysis of your numeric data:"
                return {
                    "type": "chart",
                    "content": chart,
                    "explanation": explanation
                }
            else:
                return {
                    "type": "error",
                    "content": "I couldn't generate a correlation analysis."
                }
                
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error analyzing correlations: {str(e)}"
            }
    
    def _handle_general_query(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general data exploration queries."""
        try:
            # Provide general dataset information
            stats = self.data_processor.get_summary_statistics()
            
            response_text = f"""Here's an overview of your dataset:

📊 **Dataset Summary:**
- Total Rows: {stats['total_rows']:,}
- Total Columns: {stats['total_columns']}
- Numeric Columns: {stats['numeric_columns']}
- Categorical Columns: {stats['categorical_columns']}
- Binary Columns: {stats['binary_columns']}
- Missing Values: {stats['missing_values']:,}

**Available Columns:**
"""
            
            for col in self.data_processor.df.columns:
                orig_name = self.data_processor.original_columns.get(col, col)
                col_type = self.data_processor.column_types.get(col, 'unknown')
                response_text += f"- {orig_name} ({col_type})\n"
            
            response_text += "\n💡 **Try asking questions like:**\n"
            response_text += "- What is the average [column name]?\n"
            response_text += "- Show a chart of [column name]\n"
            response_text += "- How many records have [condition]?\n"
            response_text += "- Compare [column1] across [column2]\n"
            
            return {
                "type": "text",
                "content": response_text
            }
            
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing general query: {str(e)}"
            }
    
    def _infer_columns_from_query(self, query: str) -> List[str]:
        """
        Infer relevant columns from the query text.
        """
        query_words = query.lower().split()
        relevant_columns = []
        
        for col in self.data_processor.df.columns:
            orig_name = self.data_processor.original_columns.get(col, col)
            
            # Check if column name (or parts of it) appear in query
            col_words = col.lower().split('_')
            orig_words = orig_name.lower().split()
            
            for word in query_words:
                if (word in col.lower() or 
                    word in orig_name.lower() or
                    any(word in col_word for col_word in col_words) or
                    any(word in orig_word for orig_word in orig_words)):
                    relevant_columns.append(col)
                    break
        
        return list(set(relevant_columns))
    
    def _generate_explanation(self, query: str, data: pd.DataFrame, analysis_type: str) -> str:
        """
        Generate natural language explanation for the results.
        """
        try:
            system_prompt = f"""You are a data analyst assistant. Generate a brief, clear explanation of the analysis results in response to the user's question.

Analysis Type: {analysis_type}
User Question: {query}

Provide a concise, helpful explanation that:
1. Directly answers the user's question
2. Highlights key insights from the data
3. Uses natural language (avoid technical jargon)
4. Is no more than 2-3 sentences

Data summary: {data.to_string() if len(data) < 10 else f"Dataset with {len(data)} records"}"""

            response = self.client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Explain these results: {data.head().to_string()}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            return content or "Unable to generate explanation."
            
        except Exception as e:
            return f"Here are the results for your query about {query}:"
