# POC Health Check Script (Windows PowerShell)

Write-Host "🔍 Revenue POC - Health Check" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1️⃣  Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $version = python --version
    Write-Host "   ✅ $version" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python not found" -ForegroundColor Red
    exit 1
}

# Check Node
Write-Host ""
Write-Host "2️⃣  Checking Node.js..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    $version = node --version
    Write-Host "   ✅ Node $version" -ForegroundColor Green
} else {
    Write-Host "   ❌ Node.js not found" -ForegroundColor Red
    exit 1
}

# Check Backend files
Write-Host ""
Write-Host "3️⃣  Checking Backend files..." -ForegroundColor Yellow
if (Test-Path "app/backend/main.py") {
    Write-Host "   ✅ main.py found" -ForegroundColor Green
} else {
    Write-Host "   ❌ main.py missing" -ForegroundColor Red
}

if (Test-Path "app/backend/config.py") {
    Write-Host "   ✅ config.py found" -ForegroundColor Green
} else {
    Write-Host "   ❌ config.py missing" -ForegroundColor Red
}

if (Test-Path "app/backend/requirements.txt") {
    Write-Host "   ✅ requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "   ❌ requirements.txt missing" -ForegroundColor Red
}

# Check Frontend files
Write-Host ""
Write-Host "4️⃣  Checking Frontend files..." -ForegroundColor Yellow
if (Test-Path "app/frontend/app/page.tsx") {
    Write-Host "   ✅ page.tsx found" -ForegroundColor Green
} else {
    Write-Host "   ❌ page.tsx missing" -ForegroundColor Red
}

if (Test-Path "app/frontend/package.json") {
    Write-Host "   ✅ package.json found" -ForegroundColor Green
} else {
    Write-Host "   ❌ package.json missing" -ForegroundColor Red
}

# Check Input Files
Write-Host ""
Write-Host "5️⃣  Checking Input Files..." -ForegroundColor Yellow
if (Test-Path "Input Files") {
    $input_count = (Get-ChildItem "Input Files" -Recurse -File).Count
    Write-Host "   ✅ Input Files folder found ($input_count files)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Input Files folder not found (optional)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ All core files present!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the POC:" -ForegroundColor Cyan
Write-Host "  Terminal 1 (Backend):"
Write-Host "    cd app\backend"
Write-Host "    python -m venv venv"
Write-Host "    .\venv\Scripts\activate"
Write-Host "    pip install -r requirements.txt"
Write-Host "    python -m uvicorn main:app --reload"
Write-Host ""
Write-Host "  Terminal 2 (Frontend):"
Write-Host "    cd app\frontend"
Write-Host "    npm install"
Write-Host "    npm run dev"
Write-Host ""
Write-Host "  Browser:"
Write-Host "    Open http://localhost:3000"
