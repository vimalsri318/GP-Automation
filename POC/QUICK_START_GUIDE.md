# Quick Start Implementation Guide
## Modular Workflow Engine POC

---

## Getting Started (Day 1)

### Step 1: Project Setup

```bash
# Navigate to workspace
cd c:\Users\vimalsrinivasan.r\Desktop\GP-AUTOMATION\POC

# Create directory structure
mkdir backend frontend
cd backend

# Initialize Python project
python -m venv venv
venv\Scripts\activate  # Windows

# Create requirements
echo. > requirements.txt
```

### Step 2: Install Core Dependencies (Backend)

Edit `backend/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.3
numpy==1.26.2
openpyxl==3.11.0
sqlalchemy==2.0.23
pydantic==2.5.0
openai==1.3.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

Then install:
```bash
pip install -r requirements.txt
```

### Step 3: Setup Frontend Project

```bash
cd ../frontend
npx create-next-app@latest . --typescript --tailwind --eslint

# Install additional packages
npm install @mui/material @emotion/react @emotion/styled
npm install zustand axios socket.io-client react-hook-form
npm install ag-grid-react ag-grid-community
```

### Step 4: Create Environment Files

**`backend/.env`:**
```env
DEBUG=True
API_PORT=8000
DATABASE_URL=sqlite:///./workflow_engine.db
OPENAI_API_KEY=sk-your-key-here
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=100
```

**`frontend/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Phase 1: MVP Implementation (Weeks 1-2)

### Backend Structure

Create this directory structure in `backend/`:

```
backend/
├── main.py
├── config.py
├── requirements.txt
├── .env
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── workflow.py
│   │   └── execution.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── workflows.py
│   │   ├── execution.py
│   │   └── data_inspector.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── workflow_executor.py
│   │   ├── action_registry.py
│   │   ├── state_manager.py
│   │   └── validation_builders.py
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── compare_sums.py
│   │   ├── merge_validation.py
│   │   └── format_validation.py
│   │
│   └── db/
│       ├── __init__.py
│       ├── models.py
│       └── database.py
│
├── tests/
│   ├── __init__.py
│   ├── test_validators.py
│   └── test_executor.py
│
└── uploads/  # File upload directory
```

### Day 1 Implementation: Core Backend

**`backend/main.py`:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routes import workflows, execution, data_inspector

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Modular Workflow Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api/workflows")
app.include_router(execution.router, prefix="/api")
app.include_router(data_inspector.router, prefix="/api/data")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**`backend/config.py`:**

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Modular Workflow Engine"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    DATABASE_URL: str = os.getenv("DATABASE_URL", 
                                   "sqlite:///./workflow_engine.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 100

settings = Settings()
```

**`backend/app/models/workflow.py`:**

```python
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from enum import Enum

class StepStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class StepType(str, Enum):
    INPUT = "input"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    OUTPUT = "output"

class Step(BaseModel):
    id: str
    order: int
    name: str
    type: StepType
    action: str
    params: Dict[str, Any]
    status: StepStatus = StepStatus.IDLE
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None

class Workflow(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    steps: List[Step]
    created_at: Optional[str] = None
    version: str = "1.0"

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[Step]
```

**`backend/app/services/action_registry.py`:**

```python
from typing import Callable, Dict
import pandas as pd

class ActionRegistry:
    """Registry of all available workflow actions"""
    
    def __init__(self):
        self.actions: Dict[str, Callable] = {}
        self._register_base_actions()
    
    def register(self, action_name: str, func: Callable):
        self.actions[action_name] = func
    
    def get(self, action_name: str) -> Callable:
        if action_name not in self.actions:
            raise ValueError(f"Unknown action: {action_name}")
        return self.actions[action_name]
    
    def _register_base_actions(self):
        self.register('parse_excel', parse_excel)
        self.register('compare_sums', compare_sums)
        self.register('merge_dataframes', merge_dataframes)
        self.register('export_excel', export_excel)

# Built-in validators
async def parse_excel(file_path: str, sheet_name: str = "Sheet1", 
                     header_row: int = 0) -> pd.DataFrame:
    return pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

async def compare_sums(left_df: pd.DataFrame, right_df: pd.DataFrame,
                      left_col: str, right_col: str, 
                      tolerance_percent: float = 0.05) -> Dict:
    left_sum = left_df[left_col].sum()
    right_sum = right_df[right_col].sum()
    
    if left_sum == 0:
        raise ValueError("Left sum is 0, cannot calculate percentage")
    
    diff_percent = abs(left_sum - right_sum) / left_sum
    
    if diff_percent > tolerance_percent:
        raise ValueError(
            f"Sum mismatch: {left_sum} vs {right_sum} "
            f"({diff_percent*100:.1f}% difference)"
        )
    
    return {
        "left_sum": float(left_sum),
        "right_sum": float(right_sum),
        "diff_percent": float(diff_percent),
        "status": "PASS"
    }

async def merge_dataframes(left_df: pd.DataFrame, right_df: pd.DataFrame,
                          on_key: str, how: str = "inner") -> pd.DataFrame:
    return pd.merge(left_df, right_df, on=on_key, how=how)

async def export_excel(df: pd.DataFrame, filename: str) -> str:
    df.to_excel(filename, index=False)
    return filename

# Initialize global registry
registry = ActionRegistry()
```

**`backend/app/services/state_manager.py`:**

```python
from typing import Dict, Optional
import pandas as pd
from collections import defaultdict

class StateManager:
    """Manage execution state & dataframe caching"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, pd.DataFrame]] = defaultdict(dict)
        self.status: Dict[str, Dict] = defaultdict(dict)
    
    async def cache_dataframe(self, session_id: str, step_id: str, 
                             df: pd.DataFrame):
        self.cache[session_id][step_id] = df
    
    async def get_dataframe(self, session_id: str, 
                           step_id: str) -> Optional[pd.DataFrame]:
        return self.cache.get(session_id, {}).get(step_id)
    
    async def set_status(self, session_id: str, step_id: str, 
                        status: Dict):
        if session_id not in self.status:
            self.status[session_id] = {}
        self.status[session_id][step_id] = status
    
    async def get_status(self, session_id: str, 
                        step_id: str) -> Optional[Dict]:
        return self.status.get(session_id, {}).get(step_id)
    
    async def clear_session(self, session_id: str):
        if session_id in self.cache:
            del self.cache[session_id]
        if session_id in self.status:
            del self.status[session_id]

# Global instance
state_manager = StateManager()
```

**`backend/app/services/workflow_executor.py`:**

```python
from typing import Dict, List
import asyncio
import time
from app.models.workflow import Workflow, Step, StepStatus
from app.services.action_registry import registry
from app.services.state_manager import state_manager

class WorkflowExecutor:
    def __init__(self):
        self.registry = registry
        self.state = state_manager
    
    async def execute_workflow(self, workflow: Workflow, 
                              session_id: str, input_files: Dict):
        """Execute all steps in sequence"""
        
        for step in workflow.steps:
            try:
                step.status = StepStatus.RUNNING
                await self.state.set_status(session_id, step.id, 
                                           {"status": "running"})
                
                result = await self.execute_step(step, session_id, 
                                               input_files)
                step.status = StepStatus.SUCCESS
                await self.state.set_status(session_id, step.id,
                                           {"status": "success", 
                                            "result": result})
                
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                await self.state.set_status(session_id, step.id,
                                           {"status": "failed", 
                                            "error": str(e)})
                return {"status": "failed", "error": str(e)}
        
        return {"status": "success"}
    
    async def execute_step(self, step: Step, session_id: str, 
                          context: Dict):
        """Execute single step"""
        
        start_time = time.time()
        
        # Get action function
        action_func = self.registry.get(step.action)
        
        # Execute action
        result = await action_func(**step.params)
        
        # Cache if dataframe
        if hasattr(result, '__class__') and \
           result.__class__.__name__ == 'DataFrame':
            await self.state.cache_dataframe(session_id, step.id, result)
        
        step.execution_time_ms = int((time.time() - start_time) * 1000)
        return result

# Global instance
executor = WorkflowExecutor()
```

### Day 2: API Routes

**`backend/app/routes/workflows.py`:**

```python
from fastapi import APIRouter, HTTPException
from app.models.workflow import Workflow, WorkflowCreate
from typing import List
import json
from uuid import uuid4
from datetime import datetime

router = APIRouter()

# In-memory storage (replace with DB later)
workflows_db = {}

@router.post("/", response_model=Workflow)
async def create_workflow(workflow_create: WorkflowCreate):
    workflow = Workflow(
        id=str(uuid4()),
        name=workflow_create.name,
        description=workflow_create.description,
        steps=workflow_create.steps,
        created_at=datetime.now().isoformat()
    )
    workflows_db[workflow.id] = workflow
    return workflow

@router.get("/", response_model=List[Workflow])
async def list_workflows():
    return list(workflows_db.values())

@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, 
                          detail="Workflow not found")
    return workflows_db[workflow_id]

@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, 
                         workflow_update: WorkflowCreate):
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, 
                          detail="Workflow not found")
    
    workflow = workflows_db[workflow_id]
    workflow.name = workflow_update.name
    workflow.description = workflow_update.description
    workflow.steps = workflow_update.steps
    
    return workflow

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, 
                          detail="Workflow not found")
    del workflows_db[workflow_id]
    return {"deleted": True}
```

**`backend/app/routes/execution.py`:**

```python
from fastapi import APIRouter, UploadFile, File
from app.models.workflow import Workflow
from app.services.workflow_executor import executor
from app.services.state_manager import state_manager
from app.routes.workflows import workflows_db
from uuid import uuid4
from typing import List

router = APIRouter()

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, files: List[UploadFile] = []):
    if workflow_id not in workflows_db:
        return {"error": "Workflow not found"}
    
    workflow = workflows_db[workflow_id]
    session_id = str(uuid4())
    
    # Save uploaded files
    input_files = {}
    for file in files:
        file_path = f"./uploads/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(await file.read())
        input_files[file.filename] = file_path
    
    # Execute in background
    import asyncio
    asyncio.create_task(
        executor.execute_workflow(workflow, session_id, input_files)
    )
    
    return {"session_id": session_id, "status": "started"}

@router.get("/executions/{session_id}")
async def get_execution_status(session_id: str):
    return {"session_id": session_id}

@router.post("/workflows/{workflow_id}/steps/{step_id}/rerun")
async def rerun_step(workflow_id: str, step_id: str, 
                    new_params: dict):
    if workflow_id not in workflows_db:
        return {"error": "Workflow not found"}
    
    workflow = workflows_db[workflow_id]
    step = next((s for s in workflow.steps if s.id == step_id), None)
    
    if not step:
        return {"error": "Step not found"}
    
    # Update parameters
    step.params.update(new_params)
    
    return {"status": "updated", "step": step}
```

### Day 3: Frontend Components

**`frontend/app/page.tsx`:**

```tsx
'use client';

import { useState } from 'react';
import WorkflowList from '@/components/WorkflowList';
import WorkflowDetail from '@/components/WorkflowDetail';

export default function Home() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);

  return (
    <main className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 bg-gray-100 border-r border-gray-300 overflow-y-auto">
        <WorkflowList onSelect={setSelectedWorkflow} />
      </div>

      {/* Main Content */}
      <div className="flex-1 bg-white">
        {selectedWorkflow ? (
          <WorkflowDetail workflowId={selectedWorkflow} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            Select a workflow to begin
          </div>
        )}
      </div>
    </main>
  );
}
```

**`frontend/components/WorkflowList.tsx`:**

```tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface Workflow {
  id: string;
  name: string;
  steps: any[];
}

export default function WorkflowList({ onSelect }: { onSelect: (id: string) => void }) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/workflows`);
      setWorkflows(response.data);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">Workflows</h2>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="space-y-2">
          {workflows.map((workflow) => (
            <button
              key={workflow.id}
              onClick={() => onSelect(workflow.id)}
              className="w-full text-left p-3 bg-white rounded hover:bg-blue-50 cursor-pointer border border-gray-200"
            >
              <div className="font-semibold">{workflow.name}</div>
              <div className="text-sm text-gray-500">{workflow.steps.length} steps</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Implementation Checklist

### Week 1-2: MVP

- [ ] Project structure created (both backend + frontend)
- [ ] Core Pydantic models defined
- [ ] Action registry with 3 validators working
- [ ] Basic workflow CRUD endpoints
- [ ] State manager in-memory caching
- [ ] Workflow executor sequential logic
- [ ] Step re-execution logic
- [ ] React components for workflow list
- [ ] Configuration panel UI
- [ ] Data inspector component
- [ ] Integration tests passing
- [ ] Docker setup working locally

### Week 3: AI Integration

- [ ] OpenAI API integration working
- [ ] AI rule generation endpoint
- [ ] Natural language to Pandas code
- [ ] Code sandbox testing
- [ ] UI for "Ask AI" helper
- [ ] 3+ validation templates
- [ ] E2E test for AI flow

### Week 4: Production

- [ ] Migrate to PostgreSQL
- [ ] WebSocket real-time updates
- [ ] Redis caching setup
- [ ] JWT authentication
- [ ] Audit logging
- [ ] Error handling comprehensive
- [ ] Docker image building
- [ ] Deployment docs written
- [ ] Security review passed
- [ ] Performance tested

---

## Common Commands

```bash
# Backend - Start development server
cd backend
python -m uvicorn main:app --reload

# Frontend - Start development server
cd frontend
npm run dev

# Run tests
pytest backend/tests -v

# Docker - Start all services
docker-compose up --build

# Create new step validator
# 1. Create file in backend/app/validators/
# 2. Import in action_registry.py
# 3. Register with self.register()
```

---

## Next Steps

1. **Today:** Read through PRD_MODULAR_WORKFLOW_ENGINE.md thoroughly
2. **Day 1:** Set up project structure + install dependencies
3. **Day 2:** Implement core backend services
4. **Day 3:** Build basic React components
5. **Day 4:** Connect frontend to backend
6. **Day 5:** Test workflow execution end-to-end
7. **Week 2:** Add data inspector + re-run logic
8. **Week 3:** Integrate OpenAI for rule generation
9. **Week 4:** Move to production setup

---

**Questions?** Refer to the comprehensive PRD for detailed sections on:
- Architecture decisions
- API reference
- Database schema
- Tech stack justification

---

**Version:** 1.0  
**Status:** Ready for Development  
**Last Updated:** March 23, 2026
