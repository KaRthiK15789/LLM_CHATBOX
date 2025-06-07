import streamlit as st
import openai
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
from utils import DataUtils
from visualization import ChartGenerator

# Configure page
st.set_page_config(
    page_title="Excel Insights Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'available_products' not in st.session_state:
    st.session_state.available_products = []

class ExcelChatbot:
    def __init__(self):
        self.utils = DataUtils()
        self.chart_gen = ChartGenerator()
        
    def load_excel(self, file):
        """Load and process the uploaded Excel file."""
        try:
            df = pd.read_excel(file)
            
            # Basic data cleaning
            df = df.dropna(how='all')
            df.columns = df.columns.str.strip()
            
            # Convert date columns if detected
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            st.session_state.df = df
            st.session_state.available_products = df['Product'].unique().tolist() if 'Product' in df.columns else []
            return True, "File loaded successfully"
            
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def process_query(self, query):
        """Process user query and generate response."""
        df = st.session_state.df
        if df is None:
            return {"type": "error", "content": "No data loaded. Please upload an Excel file first."}
        
        # First try basic queries
        basic_response = self._process_basic_queries(query)
        if basic_response["type"] != "text" or basic_response["content"] == "":
            return basic_response
        
        # Then try visualization requests
        if any(word in query.lower() for word in ["plot", "chart", "graph", "visualize"]):
            return self._process_visualization(query)
        
        # Fall back to statistical analysis
        return self._process_statistical_query(query)
    
    def _process_basic_queries(self, query):
        """Handle common queries without LLM when possible."""
        query_lower = query.lower()
        df = st.session_state.df.copy()
        response = {"type": "text", "content": ""}
        
        try:
            # Product-specific queries
            if "product" in query_lower and st.session_state.available_products:
                product = self.utils.extract_product_name(query, st.session_state.available_products)
                filtered = df[df['Product'].str.lower() == product.lower()]
                
                if "date" in query_lower and "quantity" in query_lower:
                    return {
                        "type": "dataframe",
                        "content": filtered[['Date', 'Quantity']],
                        "explanation": f"Date and quantity for {product}:"
                    }
                else:
                    return {
                        "type": "dataframe",
                        "content": filtered,
                        "explanation": f"All records for {product}:"
                    }
            
            # Revenue calculations
            if "revenue" in query_lower and 'Price' in df.columns and 'Quantity' in df.columns:
                df['Revenue'] = df['Price'] * df['Quantity']
                
                if "total" in query_lower:
                    total = df['Revenue'].sum()
                    return {
                        "type": "text",
                        "content": f"Total revenue: ${total:,.2f}"
                    }
                    
                if "by product" in query_lower:
                    by_product = df.groupby('Product')['Revenue'].sum().reset_index()
                    return {
                        "type": "combined",
                        "text": "Total revenue by product:",
                        "dataframe": by_product,
                        "chart": px.pie(by_product, values='Revenue', names='Product', 
                                       title='Revenue Share by Product')
                    }
            
            # Quantity analysis
            if "quantity" in query_lower:
                if "highest" in query_lower:
                    max_product = df.loc[df['Quantity'].idxmax()]['Product']
                    max_qty = df['Quantity'].max()
                    return {
                        "type": "text",
                        "content": f"The product with highest quantity is {max_product} ({max_qty} units)"
                    }
                    
                if "by region" in query_lower and 'Region' in df.columns:
                    by_region = df.groupby('Region')['Quantity'].sum().reset_index()
                    return {
                        "type": "combined",
                        "text": "Total quantity by region:",
                        "dataframe": by_region,
                        "chart": px.bar(by_region, x='Region', y='Quantity', 
                                        title='Quantity Sold by Region')
                    }
            
            # Time-based analysis
            if any(word in query_lower for word in ["date", "day", "daily"]) and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                daily = df.groupby(df['Date'].dt.date)['Quantity'].sum().reset_index()
                return {
                    "type": "combined",
                    "text": "Daily sales quantities:",
                    "dataframe": daily,
                    "chart": px.line(daily, x='Date', y='Quantity', 
                                   title='Daily Sales Quantities')
                }
                
        except Exception as e:
            return {"type": "error", "content": f"Couldn't process your request: {str(e)}"}
        
        return response
    
    def _process_visualization(self, query):
        """Handle visualization requests."""
        df = st.session_state.df
        try:
            fig = self.chart_gen.create_chart(df, query, df.columns.tolist())
            if fig:
                return {
                    "type": "chart",
                    "content": fig,
                    "explanation": f"Here's the visualization for: {query}"
                }
            else:
                return {
                    "type": "error",
                    "content": "Couldn't determine what to visualize. Please be more specific."
                }
        except Exception as e:
            return {
                "type": "error",
                "content": f"Failed to generate chart: {str(e)}"
            }
    
    def _process_statistical_query(self, query):
        """Handle statistical queries."""
        df = st.session_state.df
        try:
            # Simple column statistics
            if "average" in query.lower() or "mean" in query.lower():
                col = next((c for c in df.columns if c.lower() in query.lower()), None)
                if col and pd.api.types.is_numeric_dtype(df[col]):
                    avg = df[col].mean()
                    return {
                        "type": "text",
                        "content": f"The average {col} is {avg:.2f}"
                    }
            
            # Count queries
            if "how many" in query.lower():
                if "product" in query.lower():
                    count = len(df['Product'].unique())
                    return {
                        "type": "text",
                        "content": f"There are {count} different products"
                    }
                if "region" in query.lower() and 'Region' in df.columns:
                    count = len(df['Region'].unique())
                    return {
                        "type": "text",
                        "content": f"There are {count} different regions"
                    }
            
            # Default statistical summary
            desc = df.describe(include='all').round(2)
            return {
                "type": "dataframe",
                "content": desc,
                "explanation": "Here's a statistical summary of your data:"
            }
            
        except Exception as e:
            return {
                "type": "error",
                "content": f"Couldn't analyze your query: {str(e)}"
            }

def main():
    st.title("📊 Excel Insights Chatbot")
    st.markdown("Upload an Excel file and ask questions in natural language to get insights, statistics, and visualizations.")
    
    # Initialize chatbot
    chatbot = ExcelChatbot()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 File Upload")
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file (.xlsx)",
            type=['xlsx'],
            help="Upload an Excel file with up to 500 rows and 10-20 columns. The file should have a header row and one sheet."
        )
        
        if uploaded_file is not None:
            if st.session_state.uploaded_file_name != uploaded_file.name:
                # New file uploaded
                st.session_state.uploaded_file_name = uploaded_file.name
                
                with st.spinner("Processing your Excel file..."):
                    success, message = chatbot.load_excel(uploaded_file)
                    
                    if success:
                        st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
                        if st.session_state.df is not None:
                            st.info(f"📈 Dataset: {st.session_state.df.shape[0]} rows, {st.session_state.df.shape[1]} columns")
                        
                        # Clear previous messages when new file is loaded
                        st.session_state.messages = []
                        
                        # Show dataset preview
                        if st.session_state.df is not None:
                            st.subheader("Data Preview")
                            st.dataframe(st.session_state.df.head(), use_container_width=True)
                            
                            # Show column information
                            st.subheader("Column Information")
                            col_info = pd.DataFrame({
                                'Column': st.session_state.df.columns,
                                'Type': st.session_state.df.dtypes.astype(str),
                                'Missing Values': st.session_state.df.isna().sum()
                            })
                            st.dataframe(col_info, use_container_width=True)
                        
                    else:
                        st.error(f"❌ Error loading file: {message}")
        
        elif st.session_state.df is not None:
            # Show current file info
            st.success(f"✅ Current file: {st.session_state.uploaded_file_name}")
            st.info(f"📈 Dataset: {st.session_state.df.shape[0]} rows, {st.session_state.df.shape[1]} columns")
    
    # Main chat interface
    if st.session_state.df is None:
        st.info("👆 Please upload an Excel file to start chatting!")
        
        # Show example queries
        st.subheader("Example Questions You Can Ask:")
        examples = [
            "Show all records for Laptops",
            "What is the total revenue by product?",
            "Plot daily sales quantities",
            "Which product has the highest sales quantity?",
            "Compare sales across regions",
            "Draw a pie chart of revenue share"
        ]
        
        for example in examples:
            st.markdown(f"• {example}")
    
    else:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["type"] == "text":
                    st.markdown(message["content"])
                elif message["type"] == "dataframe":
                    st.dataframe(message["content"], use_container_width=True)
                elif message["type"] == "chart":
                    st.plotly_chart(message["content"], use_container_width=True)
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your data..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your question..."):
                    response = chatbot.process_query(prompt)
                    
                    if response["type"] == "error":
                        st.error(response["content"])
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": f"❌ {response['content']}"})
                    
                    elif response["type"] == "text":
                        st.markdown(response["content"])
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": response["content"]})
                    
                    elif response["type"] == "dataframe":
                        st.markdown(response.get("explanation", "Here's the data you requested:"))
                        st.dataframe(response["content"], use_container_width=True)
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": response.get("explanation", "Here's the data you requested:")})
                        st.session_state.messages.append({"role": "assistant", "type": "dataframe", "content": response["content"]})
                    
                    elif response["type"] == "chart":
                        if "explanation" in response:
                            st.markdown(response["explanation"])
                            st.session_state.messages.append({"role": "assistant", "type": "text", "content": response["explanation"]})
                        
                        st.plotly_chart(response["content"], use_container_width=True)
                        st.session_state.messages.append({"role": "assistant", "type": "chart", "content": response["content"]})
                    
                    elif response["type"] == "combined":
                        if "text" in response:
                            st.markdown(response["text"])
                            st.session_state.messages.append({"role": "assistant", "type": "text", "content": response["text"]})
                        
                        if "dataframe" in response:
                            st.dataframe(response["dataframe"], use_container_width=True)
                            st.session_state.messages.append({"role": "assistant", "type": "dataframe", "content": response["dataframe"]})
                        
                        if "chart" in response:
                            st.plotly_chart(response["chart"], use_container_width=True)
                            st.session_state.messages.append({"role": "assistant", "type": "chart", "content": response["chart"]})

if __name__ == "__main__":
    main()
