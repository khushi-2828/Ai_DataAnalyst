# 📊 AI Data Analyst

An AI-powered data analytics application built with **Python and Streamlit**.

The application allows users to upload CSV datasets, ask questions using natural language, generate SQL queries, explore datasets, create visualizations, detect anomalies, generate business insights, and build interactive dashboards.

## 🚀 Live Demo

👉 **[Try AI Data Analyst](https://aidataanalyst28.streamlit.app/)**

## 🔗 GitHub Repository

👉 **[View Source Code on GitHub](https://github.com/khushi-2828/AI_data_analyst)**

---

## 🚀 Features

### 📂 CSV Upload

Upload any compatible CSV dataset and automatically inspect its structure.

### 🤖 AI Dataset Summary

Automatically generates a high-level summary of the uploaded dataset.

The summary includes:

* Dataset overview
* Data quality
* Numerical insights
* Business observations

### 💬 Natural Language → SQL

Users can ask questions such as:

> What are the total sales?

> Which category has the highest sales?

> Show the top 10 customers.

The application converts natural-language questions into SQL queries and executes them against the dataset.

### 📊 Dataset Explorer

Explore:

* Dataset preview
* Column information
* Data types
* Missing values
* Unique values
* Numerical statistics

### 📈 Exploratory Data Analysis

The application provides:

* Distributions
* Correlation analysis
* Numerical analysis

### 🎨 Data Visualization

Create:

* Bar charts
* Line charts
* Pie charts
* Scatter plots
* Histograms
* Box plots
* Area charts

### 🤖 AI Chart Recommendations

The application analyzes the structure of the dataset and recommends suitable visualizations.

### 🔎 Smart Filters

Users can filter the dataset using:

* Date ranges
* Categories
* Other categorical columns

All major analysis features operate on the filtered dataset.

### 🧠 Business Insights

Automatically identifies:

* Key metrics
* Best-performing categories
* Lowest-performing categories
* Trends
* Unusual values
* Business recommendations

### 📊 Dashboard Builder

Users can ask multiple questions and generate a dashboard from the results.

### 🚨 Anomaly Detection

Detect unusual numerical values using:

* IQR
* Z-score

### 📄 Analyst Report

Generate a report containing:

* Dataset overview
* Data quality
* Business insights
* Chart recommendations
* Numerical analysis

---

## 🛠️ Tech Stack

* Python
* Pandas
* NumPy
* Streamlit
* Plotly
* SQLite
* Google Gemini API
* python-dotenv

---

## 📁 Project Structure

```text
AI_data_analyst/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── utils/
│   ├── __init__.py
│   ├── nl_to_sql.py
│   └── dataset_summary.py
│
└── test/
    └── test_dataset_summary.py
```

> **Note:** The `.env` file is intentionally excluded from the repository for security because it contains API credentials.

---

## 💡 How It Works

```text
CSV Dataset
     ↓
Data Upload
     ↓
Data Profiling
     ↓
Data Quality Check
     ↓
AI Dataset Summary
     ↓
Natural Language Questions
     ↓
SQL Query Generation
     ↓
Query Execution
     ↓
Results + Visualizations
     ↓
Business Insights
     ↓
Analyst Report
```

---

## 🎯 Project Objective

The objective of this project is to simplify data analysis by allowing users to interact with datasets using **natural language** instead of writing SQL queries or performing manual analysis.

It combines **data analytics, SQL, visualization, anomaly detection, and generative AI** into a single interactive application.

---

## 👩‍💻 Author

**Khushi Aggarwal**

🎓 Computer Science Student

🔗 [GitHub](https://github.com/khushi-2828)

🚀 [Live Project](https://aidataanalyst28.streamlit.app/)

---

⭐ If you find this project useful, consider giving the repository a star!
