import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os
from data_processor import DataProcessor
from query_handler import QueryHandler
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
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = None
if 'query_handler' not in st.session_state:
    st.session_state.query_handler = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

def main():
    st.title("📊 Excel Insights Chatbot")
    st.markdown("Upload an Excel file and ask questions in natural language to get insights, statistics, and visualizations.")
    
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
                    try:
                        # Initialize data processor
                        st.session_state.data_processor = DataProcessor()
                        success, message = st.session_state.data_processor.load_excel(uploaded_file)
                        
                        if success:
                            # Initialize query handler
                            st.session_state.query_handler = QueryHandler(st.session_state.data_processor)
                            
                            st.success(f"✅ File '{uploaded_file.name}' loaded successfully!")
                            if st.session_state.data_processor.df is not None:
                                st.info(f"📈 Dataset: {st.session_state.data_processor.df.shape[0]} rows, {st.session_state.data_processor.df.shape[1]} columns")
                            
                            # Clear previous messages when new file is loaded
                            st.session_state.messages = []
                            
                            # Show dataset preview
                            if st.session_state.data_processor.df is not None:
                                st.subheader("Data Preview")
                                st.dataframe(st.session_state.data_processor.df.head(), use_container_width=True)
                                
                                # Show column information
                                st.subheader("Column Information")
                                col_info = st.session_state.data_processor.get_column_info()
                                st.dataframe(col_info, use_container_width=True)
                            
                        else:
                            st.error(f"❌ Error loading file: {message}")
                            st.session_state.data_processor = None
                            st.session_state.query_handler = None
                            
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
                        st.session_state.data_processor = None
                        st.session_state.query_handler = None
        
        elif st.session_state.data_processor is not None:
            # Show current file info
            st.success(f"✅ Current file: {st.session_state.uploaded_file_name}")
            st.info(f"📈 Dataset: {st.session_state.data_processor.df.shape[0]} rows, {st.session_state.data_processor.df.shape[1]} columns")
    
    # Main chat interface
    if st.session_state.data_processor is None:
        st.info("👆 Please upload an Excel file to start chatting!")
        
        # Show example queries
        st.subheader("Example Questions You Can Ask:")
        examples = [
            "What is the average income?",
            "How many customers are under 30?",
            "Compare sales across regions",
            "Show a bar chart of employee count by department",
            "What are the top 10 values in sales?",
            "Create a histogram of age distribution",
            "Show correlation between income and age"
        ]
        
        for example in examples:
            st.markdown(f"• {example}")
    
    else:
        # Check if OpenAI API key is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            st.warning("⚠️ OpenAI API key not found. The chatbot will use basic rule-based analysis instead of AI-powered insights.")
            st.info("💡 To enable full AI features, please add your OpenAI API key in the environment settings.")
        
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
                    try:
                        if st.session_state.query_handler:
                            response = st.session_state.query_handler.process_query(prompt)
                        else:
                            response = {"type": "error", "content": "Query handler not initialized properly."}
                        
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
                    
                    except Exception as e:
                        error_msg = f"❌ Sorry, I encountered an error while processing your question: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": error_msg})

if __name__ == "__main__":
    main()
