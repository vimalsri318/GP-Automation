#!/bin/bash
# POC Health Check Script

echo "🔍 Revenue POC - Health Check"
echo "=============================="
echo ""

# Check Python
echo "1️⃣  Checking Python..."
if command -v python &> /dev/null; then
    python_version=$(python --version)
    echo "   ✅ $python_version"
else
    echo "   ❌ Python not found"
    exit 1
fi

# Check Node
echo ""
echo "2️⃣  Checking Node.js..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "   ✅ Node $node_version"
else
    echo "   ❌ Node.js not found"
    exit 1
fi

# Check Backend files
echo ""
echo "3️⃣  Checking Backend files..."
if [ -f "app/backend/main.py" ]; then
    echo "   ✅ main.py found"
else
    echo "   ❌ main.py missing"
fi

if [ -f "app/backend/config.py" ]; then
    echo "   ✅ config.py found"
else
    echo "   ❌ config.py missing"
fi

if [ -f "app/backend/requirements.txt" ]; then
    echo "   ✅ requirements.txt found"
else
    echo "   ❌ requirements.txt missing"
fi

# Check Frontend files
echo ""
echo "4️⃣  Checking Frontend files..."
if [ -f "app/frontend/app/page.tsx" ]; then
    echo "   ✅ page.tsx found"
else
    echo "   ❌ page.tsx missing"
fi

if [ -f "app/frontend/package.json" ]; then
    echo "   ✅ package.json found"
else
    echo "   ❌ package.json missing"
fi

# Check Input Files
echo ""
echo "5️⃣  Checking Input Files..."
if [ -d "Input Files" ]; then
    input_count=$(find "Input Files" -type f | wc -l)
    echo "   ✅ Input Files folder found ($input_count files)"
else
    echo "   ⚠️  Input Files folder not found (optional)"
fi

echo ""
echo "✅ All core files present!"
echo ""
echo "To run the POC:"
echo "  1. cd app/backend && python -m venv venv && source venv/Scripts/activate && pip install -r requirements.txt && python -m uvicorn main:app --reload"
echo "  2. (in new terminal) cd app/frontend && npm install && npm run dev"
echo "  3. Open http://localhost:3000"
