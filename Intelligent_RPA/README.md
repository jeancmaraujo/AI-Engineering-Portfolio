# Intelligent RPA: AI-Driven Invoice Extractor

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Ollama](https://img.shields.io/badge/LLM-Llama%203.1-orange)

## 📌 Overview
Traditional RPA (Robotic Process Automation) relies on hardcoded coordinates or RegEx to extract information, which breaks instantly when a vendor changes their invoice layout.

This project introduces a **Cognitive RPA Approach**. It leverages a local **Large Language Model (Llama 3.1 via Ollama)** to semantically parse the raw text out of multiple PDF invoices, intelligently locating the CNPJ, Total Value, and Document Date regardless of the visual layout. Finally, it structures the output directly into a consolidated **Excel (XLSX)** file.

Because it runs completely on local LLMs, data privacy is 100% guaranteed (No cloud API fees, no data leaks).

## 🚀 Features
- **Zero-Shot Semantic Extraction:** Uses AI prompting rather than rigid REGEX to find fields.
- **Privacy First:** Fully offline processing through Local LLMs.
- **Automated Structuring:** Exports highly unstructured invoice PDFs into a clean, analytics-ready Excel table.
- **Scalable Pipeline:** Automatically batch-processes all PDFs placed in the input folder.

## 🛠️ Tech Stack
- **Language:** Python
- **LLM Engine:** Ollama (Llama 3.1)
- **PDF Extraction:** `PyPDF2`
- **Data Structuring/Export:** `pandas`, `openpyxl`

## ⚙️ Installation & Setup

1. **Install Ollama & Download the Model**
   - Download Ollama from [ollama.com](https://ollama.com)
   - Open your terminal and run:
     ```bash
     ollama run llama3.1
     ```

2. **Clone the Repository & Install Dependencies**
   - Navigate to this project folder.
   - Install the Python requirements:
     ```bash
     pip install -r requirements.txt
     ```

3. **Prepare the Workspace**
   - The script expects a folder named `input_invoices/` in the same directory.
   - Drop your target PDF invoices into this folder.

## 💻 Usage
Simply execute the Python script:
```bash
python rpa_invoice_extractor.py
```

The AI will spin up, process every PDF sequentially, and generate an `extracted_data.xlsx` file inside the `output/` directory!

## 👔 Business Value
This script drastically reduces manual data-entry overhead in finance and accounting departments, replacing error-prone manual labor with a deterministic, easily auditable LLM-Agent.
