import os
import shutil
import requests
import json
from dotenv import load_dotenv
from app.services.automation_engine import CACHE_DIR

# Load API Configuration
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

def clear_pipeline_cache(ignore_errors=True):
    """Cleanup old .cache files for a fresh monthly run."""
    if os.path.exists(CACHE_DIR):
        print(f"🧹 [Housekeeping] Wiping Step Checkpoints from: {CACHE_DIR}")
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            try:
                if os.path.isfile(file_path): os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(f"   ⚠️ Could not delete {file_path}: {e}")

def resolve_columns_with_ai(headers_list, target_concept, context="Financial Reconciliation"):
    """
    REAL GROQ AI IMPLEMENTATION.
    Identifies the best matching Excel header for a given logical concept.
    """
    # 1. HARDCODED FALLBACK (The 'Standard Brain')
    brain = {
        "accounting document": ["doc id", "ac doc", "accounting doc", "ref no", "sap trans number", "document number"],
        "so no.": ["sales order", "so #", "order id", "sales ref", "so no", "so number"],
        "revenue": ["sales", "billing val", "amount cr", "turnover", "revenue"],
        "cost": ["expense", "purchase val", "amount dr", "cost val", "cost"]
    }
    
    target_clean = target_concept.lower().strip()
    if target_clean in brain:
        for header in headers_list:
            if str(header).lower().strip() in brain[target_clean]:
                return header

    # 2. GROQ AI INTELLIGENCE (The 'Deep Brain')
    if not GROQ_API_KEY or GROQ_API_KEY == "your_key_here":
        return None # Silent fail if no API key provided

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            f"Context: {context}\n"
            f"Available Excel Headers: {headers_list}\n"
            f"Question: Which exact column header from the list represents the concept '{target_concept}'?\n"
            "Rules:\n"
            "1. Only return the EXACT string from the list.\n"
            "2. If no match is found, return the word 'NONE'.\n"
            "3. Do not explain anything, just give the string."
        )
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0 # Strict accuracy
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            ai_choice = response.json()['choices'][0]['message']['content'].strip().strip('"').strip("'")
            if ai_choice in headers_list:
                print(f"🧠 [GROQ AI] High-Intelligence Match: '{ai_choice}' -> '{target_concept}'")
                return ai_choice
    except Exception as e:
        print(f"📡 [AI Resolver] Connectivity issue: {e}")
        
    return None
