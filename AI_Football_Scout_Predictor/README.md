# AI Football Scout Predictor
*Status: Python, Data Pipeline, Ollama, Machine Learning*

### 📌 Overview
An advanced Python-based AI Engine that automates the incredibly complex task of predicting optimal football lineups for fantasy sports (Cartola FC). Built on strong mathematical logic, the system aggregates cross-platform match data and relies on a local instance of Llama 3.1 to construct high-scoring probability lineups.

### 🚀 Features
- **Data Ingestion:** Gathers data from multiple real-time REST APIs (Cartola, Sofascore) using custom scrapers.
- **Statistical Modeling:** Applies advanced math models to normalize player ratings. Features include split home/away performance analysis, time decay filtering for recent matches, and standard deviation calculations.
- **Local LLM Orchestration:** Unlike cloud APIs, it utilizes an offline 8B parameter Large Language Model (Llama-3 via Ollama) to analyze statistically transformed Parquet databases locally.

### 🛠️ Tech Stack
- **Language:** Python
- **Data Engineering:** pandas, pyarrow (Parquet)
- **Generative AI:** Local Llama 3.1 Inference (Ollama)

### ⚙️ Installation & Setup
1. **Install Ollama:** Head over to ollama.com and run `ollama run llama3.1`
2. **Install Dependencies:** `pip install -r requirements.txt`

### 💻 Usage
Ensure Ollama is running locally before executing the data engine.
```bash
python main.py
