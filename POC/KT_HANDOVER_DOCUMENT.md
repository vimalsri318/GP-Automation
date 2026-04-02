# Randstad GP-Automation: Knowledge Transfer (KT) Guide

Welcome to the GP-Automation Reconciliation Suite! This document serves as the ultimate Knowledge Transfer (KT) guide for any lead, developer, or analyst taking over or maintaining this system.

---

## 🏗️ 1. Project Overview & Architecture

**The Problem:** The monthly financial reconciliation process required matching thousands of records across 5 different massive SAP Excel exports (Z-Recon, Revenue, Costs, Invoices, Sales Orders), managing name changes, format errors, and bridging fields across completely disjointed files.
**The Solution:** A hybrid web application (Python/FastAPI Backend + Next.js Frontend) that completely automates this process using hash-bridging, statistical sampling, and Large Language Models (LLMs) to intelligently adapt to SAP schema changes dynamically.

### Architecture Choice: Hybrid Local-Web Application
Instead of a slow desktop executable or a dangerous cloud-upload portal, this app runs locally as a native web server. 
*   **Security:** Massive 14MB Excel files never leave the Randstad VPN/Local environment.
*   **Performance:** Python handles heavy Pandas data manipulation locally in milliseconds.
*   **Intelligence:** Only logical concept questions ("Which column means 'Sales Order'?") are sent to the GROQ AI cloud.

---

## 🧠 2. Core Intelligent Systems (How it is "Unbreakable")

### The AI Semantic Mapper (GROQ Llama-3)
If SAP exports slightly change a column name, standard scripts crash. Our script routes through `housekeeping_service.py`. It first checks a hard-coded dictionary (e.g. `so no.` = `sales order`). If not found, it pushes a zero-temperature strict prompt to the GROQ Llama-3 70B model to ask exactly which available column most semantically resembles the needed data point.

### Cache Janitor & Hash Syncing
Reading a 65,000 row `.xlsx` file 5 times takes minutes. Our engine reads it **once**, converts it to a highly optimized `.pkl` cache file (`Z_Recon_StepX.pkl`), and uses O(1) dictionary Hash Map lookups (`pandas.Series.map(dict)`) to bridge data across files instantly. 

### Statistical Sampling
For detecting complex patterns across multiple sheets (e.g., in Step 4), the engine intercepts scanning over 65K rows and instead evaluates only the first 5,000 rows. It statistically selects the "winning" search strategy and applies it to the entire dataset, turning an hour-long loop into a millisecond check.

---

## 🚦 3. The 6-Step Pipeline

*   **Step 0 (Standardizer):** Automatically clears the cache from last month, loads the template file, extracts the current month from file names, and standardizes the Raw Z-Recon file. This is saved as `Z_Recon_Step0.pkl` and ensures pipeline continuity.
*   **Step 1 (Ingestion):** Confirms presence of all 5 critical files in the `Input Files/` directory.
*   **Step 2 (Cross-Invoice Validation):** The most complex bridge. Takes `Accounting Document` from Z-Recon, maps it to `Reference Key 3` in the Revenue File, finds that Invoice in the Invoice Dump, and bridges it back to finally capture the `Sales Order`.
*   **Step 3 (CMIR Alignment):** Syncs `Sales Order` to retrieve the `CMIR Type`.
*   **Step 4/5 (Narration Fallbacks):** Tries to recover Narration from the Primary Source. If a cell is blank, it defaults to the Cost Dump (using Document Numbers) to patch the hole. 
*   **Step 6 (Category Waterfall):**
    1. Special Case Priority: If `Accounting Document` starts with "1", assigns to `Vendor manual`.
    2. Dynamic Logic: Consults the "Master Excel File", loading the dynamic mapped matrix for mapping CMIR Types generated in Step 3 to the actual output `Category`.

---

## 📁 4. Codebase Structure (Directory Map)

```text
POC/
├── start_app.py                      # (START HERE) Unified Multi-Thread Launcher script
├── .gitlab-ci.yml                    # GitLab CI/CD DevOps Pipeline
├── .gitignore                        # Security protocol (Ignores .env and large Excel dumps)
├── QUICK_START.md                    # Basic setup instructions
├── Input Files/                      # Directory to drop the 5 monthly SAP Excel files
│
├── app/
│   ├── frontend/                     # Next.js UI (React / TailwindCSS)
│   │   ├── package.json              # Node dependencies
│   │   ├── app/
│   │   │   ├── page.tsx              # Main Dashboard (Holds all UI State & Pipeline Triggers)
│   │   │   ├── layout.tsx
│   │   │   ├── components/           # Reusable UI Blocks
│   │   │   │   └── CategoryMasterEditor.tsx # Editable dynamic matrix UI
│   │
│   ├── backend/                      # FastAPI Python Server
│   │   ├── main.py                   # FastAPI Routing Hub & Server Entrypoint
│   │   ├── requirements.txt          # Python dependencies (pip install -r)
│   │   ├── .env                      # Contains GROQ_API_KEY (DO NOT SHARE)
│   │   ├── tests/                    # Pytest framework ("The Logic Guardians")
│   │   │   ├── test_full_recon_pipeline.py  # Full flow simulated test
│   │   │   ├── test_pipeline_logic.py       # Unit tests for hash bridging logic
│   │   │   └── test_step6_logic.py          # Category mapping edge-case verification
│   │   │
│   │   ├── app/
│   │   │   ├── routes/               # URL Endpoints (e.g., localhost:8000/api/step1/)
│   │   │   │   ├── step1.py ... step6.py
│   │   │   │   └── categories.py
│   │   │   ├── services/             # Core Business Logic (The brains of the project)
│   │   │   │   ├── automation_engine.py      # Core data loading, ID cleaning, caching tools
│   │   │   │   ├── housekeeping_service.py   # Cache janitor & AI Semantic Mapping logic
│   │   │   │   ├── recon_standardizer.py     # Step 0 logic
│   │   │   │   ├── step1_service.py          # Input Validation logic
│   │   │   │   ├── step2_service.py          # Hash-Bridge logic: Z-Recon -> Rev -> Inv -> SO
│   │   │   │   ├── step6_service.py          # Category Mapping logic
│   │   │   │   └── category_master_service.py# Direct Excel R/W integration for logic updating
```

---

## 🛠️ 5. Run & Deployment Lifecycle

### For Daily Users (Execution)
1. Add `.xlsx` files to `Input Files/`.
2. Open terminal in the `POC/` folder.
3. Run `python start_app.py`.
4. The dashboard will automatically open. Click through Steps 1 to 6. Collect final `.xlsx` from the root folder.

### For Developers (GitLab & GitHub CI/CD)
The project utilizes **Dual-Mirroring** and an **Unbreakable CI Pipeline**.
If a developer updates Python logic in `app/services`:
1. Developer runs `git push origin main`.
2. Git automatically pushes the exact same commit to BOTH **GitHub** and **GitLab**.
3. **GitLab CI** awakens and begins a DevOps Pipeline (`.gitlab-ci.yml`):
    * **Stage 1 (Linting):** Non-blocking stylistic checks for Python and Next.js.
    * **Stage 2 (Logic Guardians - Pytest):** Uses a masked pipeline secret (`GROQ_API_KEY`) to run mocked SAP data through the full 6-step engine. If any math is wrong, the pipeline flags as FAILED, preventing deployment errors.
