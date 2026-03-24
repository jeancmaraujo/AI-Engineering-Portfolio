# AI Football Scout Predictor

## 🧠 Overview
An advanced Python-based AI Engine that automates the incredibly complex task of predicting optimal football lineups for fantasy sports (Cartola FC). Built on strong mathematical logic, the system aggregates cross-platform match data and relies on a local instance of **Llama 3.1** to construct high-scoring probability lineups.

## ⚙️ Architecture & Data Engineering
- **Data Ingestion:** Gathers data from multiple real-time REST APIs (Cartola, Sofascore) using custom scrapers.
- **Statistical Modeling:** Applies advanced math models to normalize player ratings. Features include split home/away performance analysis, time decay filtering for recent matches, and standard deviation calculations.
- **Local LLM Orchestration:** Instead of using restrictive cloud AI, it utilizes an offline 8B parameter Large Language Model (Llama-3 via Ollama) to analyze the statistically transformed `Parquet` databases locally.

## 🚀 Business Application
While the application is focused on sports, the underlying technology proves high proficiency in:
1. Building independent **Data Pipelines** using Pandas and Parquet.
2. Integrating **Local AI** systems capable of reasoning over thousands of data points without incurring API costs.
3. Writing mathematical-driven algorithms for predictive analysis.

## Getting Started
Ensure [Ollama](https://ollama.ai/) is running locally before executing the data engine.
```bash
pip install -r requirements.txt
python main.py
```
