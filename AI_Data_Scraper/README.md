# AI Data Scraper & Market Intelligence Generator

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Data Pipeline](https://img.shields.io/badge/Pipeline-Data%20Engineering-orange)
![Ollama](https://img.shields.io/badge/AI-Local%20Llama%203.1-purple)

## 📌 Business Overview
In the modern corporate technology ecosystem, reading through dozens of disparate news articles every morning is inefficient. This project presents an **Automated Market Intelligence** pipeline.

By combining fundamental **Web Scraping** skills with an advanced Local AI, this architecture independently navigates public unstructured HTML (like Hacker News), rips the crucial data anchors (Top 5 globally trending headlines), and feeds them into a zero-latency internal data loop. 

Finally, **Llama 3.1** acts as an Executive Analyst to automatically categorize the noise and condense the insight into a single, high-impact Executive Summary (TL;DR).

## 🚀 Key Achievements
- **Robust Web Scraping:** Cleanly dissects HTML Document Object Models (DOMs) using `BeautifulSoup`.
- **End-to-end Data Pipeline:** Moves data from raw HTML directly to a formatted AI-rendered Markdown artifact without human intervention.
- **Automated Market Intelligence:** LLMs effectively turn chaotic string arrays into clear managerial directives.

## 🛠️ Tech Stack
- **Language:** Python
- **Scraping Engine:** `BeautifulSoup4` + `requests`
- **Generative AI:** Local Llama 3.1 Inference (`ollama`)

## ⚙️ Installation & Setup

1. **Install Ollama**
   - Download the model runner from [ollama.com](https://ollama.com)
   - Serve your LLM using:
     ```bash
     ollama run llama3.1
     ```

2. **Clone & Install Dependencies**
   - Move into the repository directory and spin up the package manager:
     ```bash
     pip install -r requirements.txt
     ```

## 💻 Usage
Simply execute the pipeline:
```bash
python news_scraper_ai.py
```

The script will dump the final evaluation as a highly professional report named `daily_executive_report.md`. This artifact can easily be plugged into email servers or Slack integrations for automated daily delivery.
