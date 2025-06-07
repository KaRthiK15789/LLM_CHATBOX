# 📊 Excel Insights Chatbot

A production-ready Streamlit web application that provides natural language chatbot interface for Excel data analysis and visualization. Ask questions in plain English and get instant insights, statistics, and charts from your Excel data.

## 🌟 Key Features

### Core Functionality
- **Excel File Upload**: Support for .xlsx files with up to 500 rows and 10-20 columns
- **Schema-Agnostic Design**: Automatically adapts to any Excel structure without hardcoded assumptions
- **Natural Language Interface**: Ask questions in plain English
- **Multiple Response Types**: Text summaries, filtered tables, and interactive visualizations
- **Smart Column Detection**: Automatically infers column types (numeric, categorical, binary, datetime)
- **Dual Processing Modes**: AI-powered analysis with OpenAI or rule-based fallback when API unavailable
- **Robust Error Handling**: Graceful error handling with clear user feedback

### Supported Query Types
- **Summary Statistics**: "What is the average income?", "How many records do we have?"
- **Filtered Queries**: "How many customers are under 30?", "Show me records where status is active"
- **Comparisons**: "Compare sales across regions", "Show performance by department"
- **Visualizations**: "Show a bar chart of employee count by department", "Create a histogram of age distribution"
- **Correlations**: "Show correlation between income and age"

### Chart Types Available
- Bar Charts and Column Charts
- Histograms for distribution analysis
- Line Charts for time series data
- Scatter Plots for correlation analysis
- Pie Charts for categorical breakdown
- Box Plots for statistical distribution
- Correlation Heatmaps for numeric relationships

## 🛠️ Technical Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: Pandas, NumPy
- **AI/LLM**: OpenAI GPT-4o (with intelligent fallback)
- **Visualizations**: Plotly (interactive charts)
- **Excel Processing**: openpyxl

### System Components
- **DataProcessor**: Handles Excel file loading, column normalization, and type inference
- **QueryHandler**: Manages natural language processing using OpenAI API
- **FallbackQueryHandler**: Provides rule-based query processing when AI is unavailable
- **ChartGenerator**: Creates appropriate visualizations based on data and query intent
- **Streamlit App**: Main user interface with chat functionality

## 📋 Requirements

- Python 3.8 or higher
- OpenAI API Key (optional - application works without it using fallback mode)
- Modern web browser for accessing the Streamlit interface

## 🚀 Getting Started

### 1. Environment Setup
The application works in two modes:

**With OpenAI API (Recommended)**:
```bash
# Set your OpenAI API key for AI-powered analysis
export OPENAI_API_KEY="your-api-key-here"
```

**Without OpenAI API (Basic Mode)**:
The application will automatically fall back to rule-based analysis if no API key is provided.

### 2. Running the Application
```bash
# Start the Streamlit application
streamlit run app.py --server.port 5000
```

The application will be available at `http://localhost:5000`

### 3. Using the Application

1. **Upload Excel File**: Click "Choose an Excel file" and select your .xlsx file
2. **Wait for Processing**: The app will automatically analyze your data structure
3. **Ask Questions**: Type natural language questions in the chat interface
4. **View Results**: Get instant responses with text, tables, or charts

## 📄 Sample Data Files

The repository includes sample Excel files for testing:

- `sample_employee_data.xlsx` - Employee records with salary, department, age data
- `sample_sales_data.xlsx` - Sales transactions with customer demographics
- `sample_survey_data.xlsx` - Customer survey responses and ratings

## 💬 Example Queries

### Statistical Analysis
- "What is the average age of employees?"
- "How many sales transactions were there?"
- "What's the total revenue by region?"
- "Show me the minimum and maximum salaries"

### Data Filtering
- "How many customers are under 30?"
- "Show me employees in the IT department"
- "Filter sales above $500"
- "Display high-rated products only"

### Visualizations
- "Create a bar chart of sales by region"
- "Show a histogram of age distribution"
- "Generate a pie chart of department sizes"
- "Plot salary vs experience as a scatter chart"

### Comparisons
- "Compare average salary across departments"
- "Show sales performance by customer type"
- "Analyze ratings by age group"
- "Compare revenue between regions"

### Correlations
- "Show correlation between age and salary"
- "Display relationships between numeric variables"
- "Create a correlation heatmap"

## 🔧 Technical Details

### File Requirements
- **Format**: Excel files (.xlsx only)
- **Size**: Maximum 500 rows and 20 columns
- **Structure**: Single sheet with header row
- **Data Types**: Supports numeric, text, dates, and binary (Yes/No) data

### Column Normalization
The system automatically:
- Converts column names to lowercase
- Replaces spaces and special characters with underscores
- Removes leading/trailing whitespace
- Handles duplicate column names

### Data Type Inference
Automatically detects:
- **Numeric**: Integers, decimals, percentages
- **Categorical**: Text values, categories
- **Binary**: Yes/No, True/False, 1/0, Male/Female
- **Datetime**: Date and time values

### Processing Modes

**AI Mode (with OpenAI API)**:
- Advanced natural language understanding
- Context-aware query interpretation
- Intelligent column selection
- Sophisticated analysis suggestions

**Fallback Mode (without OpenAI API)**:
- Rule-based query parsing
- Pattern matching for common questions
- Basic statistical operations
- Standard visualization generation

## 🚀 Deployment

### Local Development
```bash
git clone <repository-url>
cd excel-insights-chatbot
pip install -r requirements.txt
streamlit run app.py --server.port 5000
```

### Production Deployment
The application is designed for deployment on:
- **Streamlit Cloud**: Direct deployment from GitHub
- **Heroku**: Container-based deployment
- **AWS/GCP/Azure**: Cloud platform deployment
- **Docker**: Containerized deployment

### Environment Variables
```bash
OPENAI_API_KEY=your-openai-api-key  # Optional
```

## 🛡️ Error Handling

The application includes comprehensive error handling for:
- **File Upload Issues**: Invalid formats, file size limits
- **Data Processing Errors**: Corrupted files, missing headers
- **Query Processing**: Unrecognized questions, column mismatches
- **API Limitations**: Rate limits, quota exceeded, network issues
- **Visualization Errors**: Incompatible data types, missing values

## 📊 Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  Data Processor  │    │ Query Handler   │
│                 │    │                  │    │                 │
│ • File Upload   │───▶│ • Excel Loading  │───▶│ • OpenAI API    │
│ • Chat Interface│    │ • Type Inference │    │ • Fallback Mode │
│ • Visualization │    │ • Normalization  │    │ • Intent Analysis│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Chart Generator  │    │  Response Gen   │
                       │                  │    │                 │
                       │ • Plotly Charts  │    │ • Text Answers  │
                       │ • Auto Selection │    │ • Data Tables   │
                       │ • Interactive UI │    │ • Explanations  │
                       └──────────────────┘    └─────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For issues and questions:
1. Check the error messages in the application
2. Review the example queries above
3. Ensure your Excel file meets the requirements
4. Verify your OpenAI API key (if using AI mode)

## 🎯 Project Goals

This application was built to meet the NeoStats internship assignment requirements:
- Natural language interface for Excel data analysis
- Schema-agnostic design for any data structure
- Professional visualizations and insights
- Production-ready code with proper error handling
- Flexible deployment options

The chatbot demonstrates advanced data analysis capabilities while maintaining simplicity for non-technical users.
