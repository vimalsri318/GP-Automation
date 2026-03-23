# Project Setup & Implementation Guide
## Revenue Automation Engine - Step 1 Implementation

**Date:** March 23, 2026  
**Status:** ✅ Ready for Development  
**Version:** 1.0.0

---

## 📁 Project Structure

```
POC/
├── app/
│   ├── backend/                          # FastAPI Backend
│   │   ├── app/
│   │   │   ├── models/                   # Pydantic data models
│   │   │   │   ├── __init__.py
│   │   │   │   └── step.py              # Step 1 models
│   │   │   ├── routes/                   # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   └── step1.py             # Step 1 routes
│   │   │   ├── services/                 # Business logic
│   │   │   │   ├── __init__.py
│   │   │   │   └── step1_service.py     # Step 1 service
│   │   │   ├── validators/               # Validation functions
│   │   │   └── __init__.py
│   │   ├── uploads/                      # Uploaded files storage
│   │   ├── tests/                        # Unit tests
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── config.py                     # Configuration
│   │   ├── requirements.txt              # Python dependencies
│   │   ├── Dockerfile                    # Backend container
│   │   └── .env                          # Environment variables
│   │
│   ├── frontend/                         # Next.js Frontend
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   └── Step1FileUpload.tsx  # Step 1 UI component
│   │   │   ├── lib/
│   │   │   │   ├── api.ts               # API client
│   │   │   │   ├── store.ts             # Zustand state
│   │   │   │   └── utils.ts             # Utilities
│   │   │   ├── hooks/                    # React hooks
│   │   │   ├── globals.css              # Global styles
│   │   │   ├── layout.tsx               # Root layout
│   │   │   └── page.tsx                 # Home page
│   │   ├── components/ui/                # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   └── card.tsx
│   │   ├── package.json                 # Node dependencies
│   │   ├── tsconfig.json                # TypeScript config
│   │   ├── tailwind.config.js           # Tailwind config
│   │   ├── postcss.config.js            # PostCSS config
│   │   ├── next.config.js               # Next.js config
│   │   ├── Dockerfile                   # Frontend container
│   │   └── .env.local                   # Frontend environment
│   │
│   ├── docker-compose.yml               # Docker container setup
│   └── .gitignore                       # Git ignore
│
├── Input Files/                         # Source data files
│   ├── Revenue Dump.xlsx
│   ├── Cost Dump.xlsx
│   ├── Invoice Listing.xlsx
│   └── ...
│
└── Documentation/                       # (Previous PRD files)
```

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Node.js 18+ with npm
- Python 3.11+
- Docker & Docker Compose (optional, for containerized setup)
- Git

### Option 1: Local Development (Recommended for Development)

#### Backend Setup
```bash
cd app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn main:app --reload
```

Backend running on: **http://localhost:8000**  
API Docs available on: **http://localhost:8000/docs**

#### Frontend Setup (New Terminal)
```bash
cd app/frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend running on: **http://localhost:3000**

### Option 2: Docker Compose (One Command Setup)

```bash
cd app

# Start both services
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

---

## 📋 What's Implemented: Step 1

### Backend (FastAPI)

#### Endpoint: `POST /api/step1/upload`
Accepts file uploads and processes them.

**Request:**
```http
POST /api/step1/upload HTTP/1.1
Content-Type: multipart/form-data

files: [file1.xlsx, file2.xlsx]
```

**Response (Success):**
```json
{
  "step_id": "step_1",
  "name": "Upload Revenue Files",
  "status": "success",
  "message": "Successfully uploaded and processed 2 file(s)",
  "data_summary": {
    "row_count": 5234,
    "column_count": 3,
    "columns": ["Invoice_ID", "Revenue", "Date"],
    "file_path": "Revenue Dump.xlsx",
    "first_rows": [...]
  },
  "uploaded_files": ["Revenue Dump.xlsx", "Cost dump.xlsx"],
  "execution_time_ms": 450
}
```

#### Endpoint: `GET /api/step1/preview/{filename}`
Get data preview from uploaded file.

**Response:**
```json
{
  "filename": "Revenue Dump.xlsx",
  "rows": 10,
  "data": [
    {"Invoice_ID": "INV001", "Revenue": 50000, "Date": "2026-01-01"},
    ...
  ]
}
```

#### Key Files:
- **main.py** - FastAPI app entry point
- **app/models/step.py** - Pydantic models for type validation
- **app/services/step1_service.py** - Core Step 1 logic
  - `validate_file()` - File validation
  - `save_file()` - Save uploaded file
  - `parse_excel()` - Parse Excel files using Pandas
  - `get_data_summary()` - Generate data summary
  - `process_revenue_files()` - Main orchestration
- **app/routes/step1.py** - API endpoints

### Frontend (Next.js 14 + shadcn/ui)

#### Components:
- **Step1FileUpload.tsx** - Main upload UI
  - Drag & drop file upload
  - File list with preview
  - Upload progress
  - Success/error handling
  - Data summary display

#### API Client:
- **app/lib/api.ts** - HTTP client using Axios
  - `step1API.uploadFiles()` - Upload files to backend
  - `step1API.getFilePreview()` - Fetch file preview
  - Automatic error handling with toast notifications

#### State Management:
- **app/lib/store.ts** - Zustand store
  - `useStep1Store()` - Step 1 state (files, loading, errors)
  - `useWorkflowStore()` - Workflow progress tracking

#### UI Components (shadcn/ui):
- **Card** - Used to organize content
- **Button** - Upload and action buttons
- **Forms** - File input

---

## 🔧 Configuration

### Backend (.env)
```env
DEBUG=True
API_PORT=8000
DATABASE_URL=sqlite:///./automation_engine.db
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
MAX_FILE_SIZE_MB=100
CHUNK_SIZE=1000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Revenue Automation Engine"
```

---

## 📝 Step 1 Workflow

### What Happens When You Upload Files:

1. **Frontend (UI)**
   - User selects files via drag-drop or file picker
   - Validates file types (.xlsx, .xls, .csv)
   - Shows file list with sizes
   - User clicks "Upload Files"

2. **HTTP Request**
   - Frontend sends multipart form data to `POST /api/step1/upload`
   - Files encoded in request body

3. **Backend Processing**
   - FastAPI receives request
   - For each file:
     - ✅ Validates file extension and size
     - ✅ Saves file to `uploads/` directory
     - ✅ Reads Excel file using Pandas
     - ✅ Generates data summary (row count, columns, types)
     - ✅ Extracts first 5 rows for preview
   - Returns results as JSON

4. **Frontend Display**
   - Shows upload success message
   - Displays file summaries (row count, columns)
   - Shows first 5 rows preview
   - Updates store with uploaded file data

---

## 🧪 Testing Step 1

### Manual Testing with cURL

```bash
# Test health check
curl http://localhost:8000/health

# Upload files
curl -X POST http://localhost:8000/api/step1/upload \
  -F "files=@/path/to/file1.xlsx" \
  -F "files=@/path/to/file2.xlsx"

# Get file preview
curl "http://localhost:8000/api/step1/preview/Revenue%20Dump.xlsx?rows=10"
```

### Testing with Python
```python
import requests

# Upload files
with open('Revenue Dump.xlsx', 'rb') as f:
    files = {'files': f}
    response = requests.post(
        'http://localhost:8000/api/step1/upload',
        files=files
    )
    print(response.json())
```

### Browser Testing
Simply visit **http://localhost:3000** and:
1. Drag & drop Excel files or click to select
2. Click "Upload Files"
3. See results with data summary

---

## 📊 Using Sample Data

The `Input Files/` directory contains sample Excel files:

- **Revenue Dump - 1st to 26th Feb 2026.xlsx** - Revenue data
- **Cost dump Feb 1st to Feb 26th.XLSX** - Cost data
- **Invoice Listing - 1st Jan to 28th Feb 2026.XLSX** - Invoice data
- **SO Listing - 1st Jan to 28th Feb 2026.XLSX** - Sales order data
- **Z Recon - 1st Feb to 26th Feb 2026 - Base File.XLSX** - Reconciliation base

### To Test:
1. Export these files to `app/backend/uploads/` (optional)
2. Or upload directly through the UI
3. Watch the app process them

---

## 🔄 How to Extend Step 1

### Add New Validation

**In `app/backend/app/services/step1_service.py`:**

```python
def validate_data_quality(self, df: pd.DataFrame) -> Dict:
    """Validate data quality"""
    issues = []
    
    # Check for duplicates
    if df.duplicated().any():
        issues.append("Data contains duplicates")
    
    # Check for nulls
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        issues.append(f"Columns with nulls: {null_cols}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }
```

### Add New API Endpoint

**In `app/backend/app/routes/step1.py`:**

```python
@router.post("/validate-quality")
async def validate_quality(filename: str):
    """Validate file data quality"""
    result = step1_service.validate_data_quality(filename)
    return result
```

### Update Frontend UI

**In `app/frontend/app/components/Step1FileUpload.tsx`:**

```typescript
// Add after upload success
const quality = await step1API.validateQuality(filename);
if (!quality.valid) {
  toast.warning(`Data quality issues: ${quality.issues.join(', ')}`);
}
```

---

## 📚 API Documentation

When backend is running, visit: **http://localhost:8000/docs**

This shows:
- ✅ All available endpoints
- 📝 Request/response schemas
- 🧪 Try-it-out interface
- 📊 Data model definitions

---

## 🐛 Debugging

### Backend Logs
```bash
# Check console output while running with --reload
python -m uvicorn main:app --reload

# Look for:
# - File validation errors
# - Excel parsing issues
# - Response times
```

### Frontend Logs
```bash
# Browser DevTools (F12)
# Check:
# - Network tab for API calls
# - Console for JavaScript errors
# - React DevTools for state
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Port 8000 already in use" | `lsof -i :8000` then kill process |
| "CORS error" | Check `FRONTEND_URL` in backend `.env` |
| "File upload fails" | Check `uploads/` directory permissions |
| "Pandas error reading Excel" | Ensure `openpyxl` installed: `pip install openpyxl` |
| "API not responding" | Check backend is running on http://localhost:8000 |

---

## 🚀 Next Steps (For Steps 2-5)

After Step 1 is working:

### Step 2: Data Validation
- ✅ Compare revenue totals vs cost totals
- ✅ Cross-file integrity checks
- ✅ Data type validation

### Step 3: Data Transformation
- Merge multiple files
- Aggregate by key fields
- Format standardization

### Step 4: Report Generation
- Generate Excel reports
- Summary statistics
- Variance analysis

### Step 5: Export & Notifications
- Export to final format
- Email integration
- Completion notifications

---

## 📝 Development Checklist

- [x] Project directory structure created
- [x] Backend (FastAPI) setup complete
- [x] Frontend (Next.js + shadcn/ui) setup complete
- [x] Step 1 service implemented
- [x] API endpoints created
- [x] UI components built
- [x] Docker setup configured
- [ ] Unit tests written
- [ ] E2E tests created
- [ ] Documentation complete
- [ ] Step 2 implementation ready

---

## 💡 Key Technologies

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI + Python | Async, auto-validation (Pydantic), fast |
| Frontend | Next.js 14 | SSR, App Router, great DX |
| UI Library | shadcn/ui | Better than MUI for this project, Tailwind-based |
| Data Processing | Pandas | Excel integration, flexible transformations |
| State Management | Zustand | Lightweight, perfect for workflow state |
| API Client | Axios | Better error handling than fetch |
| Container | Docker | Reproducible environment |

---

## 📖 File Reference

### Key Backend Files to Understand

1. **main.py** - Entry point, shows app structure
2. **config.py** - Configuration management
3. **app/models/step.py** - Data schemas
4. **app/services/step1_service.py** - Core logic (read first!)
5. **app/routes/step1.py** - API endpoints

### Key Frontend Files to Understand

1. **app/page.tsx** - Home page entry
2. **app/components/Step1FileUpload.tsx** - Main UI (read first!)
3. **app/lib/api.ts** - API communication
4. **app/lib/store.ts** - State management
5. **app/layout.tsx** - Styling and providers

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend starts without errors
- [ ] Frontend opens without errors
- [ ] Can see upload UI
- [ ] Can upload Excel files
- [ ] Files are processed and summary shown
- [ ] API docs available at /docs
- [ ] Docker containers start successfully
- [ ] No CORS errors in console
- [ ] Sample data uploads successfully

---

## 🎓 Learning Resources

- [FastAPI Guide](https://fastapi.tiangolo.com)
- [Next.js 14 Docs](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Pandas Documentation](https://pandas.pydata.org/docs)
- [Zustand Guide](https://github.com/pmndrs/zustand)

---

## 📞 Support

If you encounter issues:

1. Check the **Debugging** section above
2. Review **Common Issues** table
3. Check backend logs: `python -m uvicorn main:app --reload`
4. Check frontend console: F12 → Console tab
5. Verify ports are correct: 8000 (backend), 3000 (frontend)

---

**Status:** ✅ Ready for Development  
**Next:** Implement Step 2 (Data Validation)  
**Questions?** Refer to comprehensive PRD documents provided.

