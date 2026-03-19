import os
import json
import requests
import pandas as pd
import PyPDF2

# ==========================================
# CONFIGURATION
# ==========================================
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

INPUT_DIR = "input_invoices"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "extracted_data.xlsx")

def extract_text_from_pdf(pdf_path):
    """Reads a PDF and extracts its text layout."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def parse_with_llm(text):
    """Sends raw text to Local Llama 3.1 to extract structured JSON."""
    prompt = f"""You are an advanced RPA Data Extraction agent. 
Analyze the following invoice text and extract the core data.
Return ONLY a raw JSON object string with no markdown blocks, no formatting, and no extra text.
Required keys exactly as written: "CNPJ", "Value", "Date".
If a value is not found, return null for that key.

Invoice Text:
{text}
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # Forces JSON constraint in Ollama >= 0.1.30
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json().get("response", "{}")
        
        # Safely parse the JSON string returned by the LLM
        data = json.loads(result)
        return data
    except Exception as e:
        print(f"LLM Extraction failed or timed out: {e}")
        return {}

def main():
    print("=" * 60)
    print("🤖 INTELLIGENT RPA: AI-DRIVEN INVOICE EXTRACTOR")
    print("=" * 60)
    
    # Ensure directories exist
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️ No PDFs found in the '{INPUT_DIR}' directory.")
        print("Please place your invoice PDFs there and run the script again.")
        return
        
    extracted_data = []
        
    for filename in pdf_files:
        print(f"[Processing] {filename}...")
        pdf_path = os.path.join(INPUT_DIR, filename)
        
        # Step 1: Optical / Text Extraction
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text.strip():
            print(f"   -> ❌ Failed to extract text (possibly scanned image without OCR).")
            continue
            
        # Step 2: Cognitive Parsing via LLM
        print("   -> 🧠 Calling Local Vision/Language Model (Llama 3.1)...")
        parsed_data = parse_with_llm(raw_text)
        
        if parsed_data:
            parsed_data['Source_File'] = filename # Append metadata
            extracted_data.append(parsed_data)
            print(f"   -> ✅ Success: {parsed_data}")
        else:
            print(f"   -> ⚠️ Failed to interpret data correctly.")
            
    # Step 3: Structured State Export
    if extracted_data:
        print(f"\n💾 Exporting {len(extracted_data)} records to Excel...")
        df = pd.DataFrame(extracted_data)
        
        # Ensure column order if they exist
        cols = ['Source_File', 'CNPJ', 'Value', 'Date']
        # Filter only existing columns
        existing_cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
        df = df[existing_cols]
        
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"🚀 Operation Complete! Check the file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
