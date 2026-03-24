# Revenue POC - Quick Start Guide

## Minimal POC Setup

This POC demonstrates **Step 1: File Upload & Parsing** with minimal code.

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Backend Setup

```bash
cd app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # on Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python -m uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Frontend Setup (NEW TERMINAL)

```bash
cd app/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Expected output:
```
ready - started server on 0.0.0.0:3000
```

### Test End-to-End

1. Open browser: **http://localhost:3000**
2. Select Excel files from `Input Files/` folder
3. Click "Upload"
4. See JSON response with file summaries

### Sample Files to Test
Located in: `Input Files/`
- Revenue Dump.xlsx
- Cost dump.xlsx
- Invoice Listing.xlsx
- SO Listing.xlsx
- Z Recon.xlsx

### Backend API

**Endpoint**: `POST http://localhost:8000/api/step1/upload`

**Request**: Multipart form with files

**Response**:
```json
{
  "success": true,
  "message": "Processed 2 files",
  "files": {
    "Revenue Dump.xlsx": {
      "rows": 1000,
      "columns": ["Date", "Amount", "Product"],
      "dtypes": {"Date": "object", "Amount": "float64", "Product": "object"},
      "preview": [...]
    }
  },
  "execution_time_ms": 245
}
```

### Project Structure

```
app/
├── backend/              # FastAPI server
│   ├── main.py          # Entry point
│   ├── config.py        # Simple config
│   ├── requirements.txt  # 6 essential packages only
│   └── app/
│       ├── routes/
│       │   └── step1.py  # Upload endpoint
│       └── services/
│           └── step1_service.py  # File parsing logic
│
└── frontend/            # Next.js frontend
    ├── app/
    │   ├── page.tsx     # Simple upload UI
    │   ├── layout.tsx   # Root layout
    │   └── globals.css  # Basic Tailwind
    ├── lib/
    │   └── api.ts       # Simple axios wrapper
    └── package.json     # Minimal deps
```

### Key Facts

- **Backend**: ~200 lines of code
- **Frontend**: ~150 lines of code
- **Total**: ~350 lines for working POC
- **Dependencies**: Minimized to essentials only
- **No Database**: Files stored in `app/backend/uploads/`
- **No Complex State**: Simple useState in React

### Troubleshooting

**CORS error**?
- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000
- Check firewall settings

**Module not found**?
- Frontend: `npm install` in `app/frontend/`
- Backend: `pip install -r requirements.txt` in `app/backend/`

**Python module error**?
- Ensure venv is activated: `source venv/Scripts/activate`
- Check Python 3.11+: `python --version`

### Next Steps After POC Works

Once Step 1 is confirmed working:
1. [ ] Step 2: Data Validation
2. [ ] Step 3: Data Transformation
3. [ ] Steps 4-5: Report Generation

---

**Created**: 2024
**Status**: ✅ Ready to test
