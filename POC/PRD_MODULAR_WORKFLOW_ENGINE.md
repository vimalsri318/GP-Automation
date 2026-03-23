# Product Requirements Document (PRD)
## Modular Workflow Engine - Automation POC

**Document Version:** 1.0  
**Last Updated:** March 23, 2026  
**Status:** Ready for Development  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Product Overview](#product-overview)
3. [Technical Architecture](#technical-architecture)
4. [Tech Stack & Justification](#tech-stack--justification)
5. [Detailed Feature Requirements](#detailed-feature-requirements)
6. [UI/UX Specifications](#uiux-specifications)
7. [Backend Architecture](#backend-architecture)
8. [Data Flow & State Management](#data-flow--state-management)
9. [Implementation Details](#implementation-details)
10. [Development Roadmap](#development-roadmap)
11. [Deployment & DevOps](#deployment--devops)

---

## Executive Summary

### Problem Statement
Current automation workflows are rigid, static Python scripts that cannot be modified mid-execution without complete restart. Users cannot:
- See step-by-step progress
- Modify validation rules on-the-fly
- Fix data errors without reprocessing
- Understand why a specific step failed

### Solution Overview
Build a **Modular Workflow Engine** that treats automation tasks as configurable "Step Blocks" with:
- JSON-based workflow definitions
- Interactive UI for real-time step visualization
- Ability to modify and re-run individual steps
- AI-assisted rule generation
- Visual debugging and data inspection

### Success Criteria
- ✅ Users can configure workflows in UI without code
- ✅ Failed steps can be modified and re-run independently
- ✅ Data state is visible after each step
- ✅ 90% reduction in troubleshooting time
- ✅ Support 5+ built-in validation types
- ✅ Custom AI-generated rules work in POC

---

## Product Overview

### Core Concept
Transform automation from a "run once, hope it works" model to an **Observable, Modular, Interactive** workflow engine.

### Key Features (MVP)

| Feature | Priority | Description |
|---------|----------|-------------|
| Step-Based Workflow | P0 | Execute automation as sequential steps |
| Workflow Upload/Download | P0 | Save/load workflow JSON definitions |
| Step Visualization | P0 | Real-time status dashboard (✅🔴⚪) |
| Step Configuration UI | P0 | Click step to modify parameters |
| Data Inspection | P1 | View dataframe state after each step |
| Step Re-execution | P1 | Modify and re-run failed steps |
| Validation Rules Library | P1 | Pre-built: sum checks, merge validation, format checks |
| AI Rule Generator | P2 | Text-to-rule: "Flag rows where Revenue > 1M" |
| Error Reporting | P1 | Detailed error messages with row-level failures |
| Audit Trail | P2 | Log all modifications and re-runs |

---

## Technical Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────┐
│              MODULAR WORKFLOW ENGINE POC                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────┐        ┌─────────────────────────┐
│   Next.js Frontend      │        │   Python FastAPI        │
│  (React Components)     │◄─────►│   (Workflow Engine)     │
│                         │        │                         │
│ • Workflow Step List    │        │ • Action Registry       │
│ • Configuration Panel   │        │ • State Manager         │
│ • Data Inspector        │        │ • DataFrame Cache       │
│ • AI Chat Box           │        │ • Validator Functions   │
└─────────────────────────┘        └─────────────────────────┘
         ▲                                    ▲
         │                                    │
         │ HTTP/JSON                          │ File I/O
         │                                    │
         ▼                                    ▼
    ┌────────────────┐              ┌─────────────────┐
    │  Browser Local │              │ File System     │
    │  Storage (JWT) │              │ (Excel, CSV)    │
    └────────────────┘              └─────────────────┘

    ┌────────────────────────────────────────────────┐
    │  Persistent Storage (PostgreSQL/SQLite)        │
    │  • Workflow definitions                        │
    │  • Execution history                           │
    │  • Audit logs                                  │
    └────────────────────────────────────────────────┘
```

### Workflow Execution Flow

```
User Uploads Files
        ↓
Frontend Initializes Workflow (Step 1: Upload → Idle)
        ↓
User clicks "Start Workflow"
        ↓
Backend loads workflow JSON
        ↓
FOR EACH STEP:
    ├─ Load Input (from previous step output or file)
    ├─ Execute Action (e.g., sum_check, merge_files)
    ├─ Run Validation (check constraints)
    ├─ Store Output (cache dataframe)
    ├─ Update Status (✅ or 🔴)
    └─ Send Update to Frontend (via WebSocket/Polling)
        ↓
Step Failed?
    ├─ YES → Show error, user modifies parameters, Re-run same step
    └─ NO → Next step or Workflow Complete
        ↓
Workflow Complete / User Downloads Results
```

---

## Tech Stack & Justification

### Frontend

#### **Framework: Next.js 14 (React)**
**Why:**
- Server-Side Rendering (SSR) for quick initial page load
- API Routes for lightweight backend calls
- Rich React ecosystem for interactive dashboards
- Built-in TypeScript support
- Excellent for real-time UI updates with WebSockets

**Justification:** State-heavy workflow UI requires reactive framework. Next.js gives us both frontend and lightweight server layer.

#### **UI Library: Material-UI (MUI) v5 + React Hook Form**
**Why:**
- Pre-built Stepper component for workflow visualization
- Form handling for configuration panels
- Accessibility out-of-the-box (WCAG compliant)
- Professional appearance for enterprise POC

**Justification:** Don't reinvent controls. MUI's Stepper is perfect for step visualization.

#### **Real-time Updates: Socket.IO (React Client)**
**Why:**
- Two-way communication for live step status updates
- Fallback to polling if WebSockets unavailable
- Auto-reconnection handling
- Lower latency than REST polling

**Justification:** As steps execute, we need real-time feedback to UI. REST polling every second is wasteful.

#### **HTTP Client: Axios**
**Why:**
- Interceptor support for auth tokens
- Request/response transformation
- Better error handling than fetch

#### **State Management: Zustand (Lightweight)**
**Why:**
- Minimal boilerplate vs Redux
- Perfect for workflow state (steps, current status, cache)
- Built-in persistence for browser localStorage

#### **Data Inspection: AG Grid (Community)**
**Why:**
- Display dataframes as tables
- Sorting, filtering, pagination out-of-the-box
- Handles 10K+ rows smoothly

**Alternative:** If cost is concern, use simple TaNSTACK Table (free)

#### **Styling: Tailwind CSS**
**Why:**
- Rapid UI development
- Utility-first approach matches MUI
- Small bundle size

---

### Backend

#### **Framework: FastAPI + Python 3.11**
**Why:**
- Async-first (handle concurrent step executions)
- Built-in OpenAPI/Swagger docs (great for debugging)
- Type hints catch bugs early
- Extremely fast (near C performance)
- Auto-validation with Pydantic

**Justification:** We need to handle polling/WebSocket updates while executing data operations. FastAPI's async is perfect.

#### **Data Processing: Pandas + NumPy**
**Why:**
- Industry standard for data manipulation
- Built-in validation functions
- Memory-efficient operations
- Rich integration ecosystem

**Justification:** Your automation likely involves Excel/CSV processing. Pandas is the standard.

#### **File Handling: Openpyxl (Excel) + Polars (Alternative for speed)**
**Why:**
- Openpyxl: Read/write Excel with formatting preserved
- Polars: 10-100x faster than Pandas for large files (optional upgrade)

**Justification:** Your POC processes Excel files. Openpyxl is battle-tested.

#### **Cache/State Management: Redis or In-Memory (Dict)**
**Why:**
- Store dataframes between steps
- Fast retrieval (< 1ms)
- Session-specific data isolation

**For POC:** Start with in-memory cache. Upgrade to Redis for multi-session support.

#### **Database: SQLite (POC) → PostgreSQL (Production)**
**Why:**
- SQLite: Zero setup, file-based, perfect for POC
- PostgreSQL: Scalable, ACID compliant, full-text search for audit logs

**Justification:** POC needs quick turnaround. SQLite requires zero infrastructure.

#### **WebSocket Server: FastAPI + WebSockets**
**Why:**
- Built into FastAPI
- No separate service needed
- Handles two-way communication naturally

#### **AI Integration: OpenAI API or Anthropic**
**Why:**
- Generate custom validation rules from natural language
- Example: "Revenue > cost" → Pandas code generation

**API to Use:**
```python
# Example: Generate validation from text
user_rule = "Revenue should be greater than cost"
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": f"Generate Pandas-compatible validation code for: {user_rule}"
    }]
)
validation_code = response.choices[0].message.content
```

#### **Logging & Monitoring: Python logging + Structlog**
**Why:**
- Structured logs for debugging
- Easy to parse for audit trails

---

### DevOps & Infrastructure

#### **Containerization: Docker + Docker Compose**
**Why:**
- Reproducible environment across machines
- Easy deployment to cloud
- Isolate dependencies

#### **Local Development: Docker Compose (2 containers)**
1. FastAPI backend on port 8000
2. Next.js frontend on port 3000

#### **Cloud Deployment (When needed): AWS / Azure**
- Backend: ECS (Docker) or Lambda (serverless)
- Frontend: S3 + CloudFront
- Database: RDS PostgreSQL
- Cache: ElastiCache (Redis)

---

## Detailed Feature Requirements

### Feature 1: Workflow Definition & Upload

#### Acceptance Criteria
- [x] User uploads existing Python/YAML workflow
- [x] System converts it to JSON step format
- [x] Each step displays as a card in the UI
- [x] Workflow can be saved as JSON artifact

#### JSON Schema for Workflow

```json
{
  "id": "workflow_001",
  "name": "Revenue vs Cost Reconciliation",
  "description": "Validates that revenue matches cost data",
  "created_at": "2026-03-23T10:00:00Z",
  "version": "1.0",
  "steps": [
    {
      "id": "step_1",
      "order": 1,
      "name": "Upload Revenue File",
      "type": "input",
      "description": "Parse main revenue Excel file",
      "action": "parse_excel",
      "params": {
        "file_key": "revenue_main.xlsx",
        "sheet_name": "Data",
        "header_row": 1
      },
      "input_type": "file",
      "output_schema": {
        "columns": ["Invoice_ID", "Revenue", "Date"],
        "type": "dataframe"
      },
      "status": "idle",
      "error": null,
      "execution_time_ms": null
    },
    {
      "id": "step_2",
      "order": 2,
      "name": "Upload Cost File",
      "type": "input",
      "action": "parse_excel",
      "params": {
        "file_key": "cost_dump.xlsx",
        "sheet_name": "Summary",
        "header_row": 0
      },
      "status": "idle",
      "error": null
    },
    {
      "id": "step_3",
      "order": 3,
      "name": "Revenue vs Cost Validation",
      "type": "validation",
      "description": "Compare total revenue against total cost",
      "action": "compare_sums",
      "params": {
        "left_input_step": "step_1",
        "right_input_step": "step_2",
        "left_column": "Revenue",
        "right_column": "Total_Cost",
        "tolerance_percent": 0.05,
        "exact_match": false
      },
      "status": "idle",
      "error": null,
      "validation_rule": "SUM(left.Revenue) ~= SUM(right.Total_Cost) ±5%"
    },
    {
      "id": "step_4",
      "order": 4,
      "name": "Export Consolidated Report",
      "type": "output",
      "action": "export_excel",
      "params": {
        "input_step": "step_3",
        "filename": "reconciliation_report.xlsx",
        "include_summary": true
      },
      "status": "idle"
    }
  ],
  "globals": {
    "max_execution_time_seconds": 300,
    "fail_fast": false,
    "retry_failed_steps": true
  }
}
```

---

### Feature 2: Step Configuration Panel

#### UI Components
When user clicks on a step, show:

```
┌─────────────────────────────────────┐
│ STEP CONFIGURATION PANEL            │
├─────────────────────────────────────┤
│                                     │
│ Step Name: [Revenue Validation   ] │
│                                     │
│ ─── ACTION SELECTION ───            │
│ Action Type: [compare_sums    ▼]   │
│              (merge, filter, etc)  │
│                                     │
│ ─── INPUT PARAMETERS ───            │
│ Left Column:  [Revenue        ▼]   │
│ Right Column: [Total_Cost     ▼]   │
│ Tolerance %:  [5              ]    │
│                                     │
│ ─── ADVANCED ───                    │
│ ☐ Exact Match                      │
│ ☐ Ignore Null Values               │
│ ☐ Case-Sensitive                   │
│                                     │
│ ─── AI HELPER ───                   │
│ [Ask AI to modify this step]        │
│ "Flag rows where Revenue < 1000"    │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Load Template | Save | Cancel   │ │
│ │ Re-run Step  | Delete           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### Acceptance Criteria
- [x] All parameters dynamically populate from step JSON
- [x] User can modify any parameter
- [x] "Save" updates workflow and re-runs step
- [x] "Load Template" shows pre-built validation rules
- [x] AI helper integrates with OpenAI API

---

### Feature 3: Workflow Step Status Visualization

#### Sidebar Workflow List

```
WORKFLOW STEPS (Reconciliation v1.0)

[1] 📁 Upload Revenue File
    Status: ✅ Complete (234ms)
    Output: 5,234 rows

[2] 📁 Upload Cost File
    Status: ✅ Complete (156ms)
    Output: 1,200 rows

[3] ⚙️  Revenue vs Cost Validation
    Status: 🔴 FAILED
    Error: Sum mismatch by 12.3%
    Left Total: $5,234,100
    Right Total: $4,645,230
    [Click to configure] [View Details]

[4] 📤 Export Report
    Status: ⚪ Pending
    (Waiting for step 3)

[5] 📧 Send Email Notification
    Status: ⚪ Pending
```

#### Status Icons & Colors
| Icon | Color | Meaning |
|------|-------|---------|
| ⚪ | Gray | Idle/Pending |
| 🔵 | Blue | Running |
| ✅ | Green | Success |
| 🔴 | Red | Failed |
| ⚠️ | Yellow | Warning (passed with alerts) |
| ⏭️ | Purple | Skipped |

#### Acceptance Criteria
- [x] Status updates in real-time via WebSocket
- [x] Execution time displayed for completed steps
- [x] Clicking a step opens configuration panel
- [x] Error message visible inline
- [x] Smooth animations for status transitions

---

### Feature 4: Data Inspector (View DataFrame State)

#### Data Inspector Panel

```
STEP 1: Upload Revenue File OUTPUT
┌───────────────────────────────────────────────┐
│ DataFrame: 5,234 rows × 3 columns             │
│ [Refresh] [Download as CSV] [Export to Excel] │
├───────────────────────────────────────────────┤
│
│ Invoice_ID │ Revenue │ Date              │
│ ─────────────────────────────────────────────│
│ INV-001    │ 50000   │ 2026-01-01        │
│ INV-002    │ 75000   │ 2026-01-02        │
│ INV-003    │ 100000  │ 2026-01-03        │
│ ... (5,231 more rows)
│
│ [Show All] [Previous] Page 1/262 [Next]
│
π Data Type Info:
│ • Invoice_ID: object (string)
│ • Revenue: int64 (numeric)
│ • Date: datetime64[ns]
│
│ Statistics:
│ • Revenue - Mean: $45,200 | Median: $40,000 | Min: $1,000 | Max: $500,000
│ • Missing Values: 0
│
└───────────────────────────────────────────────┘
```

#### Acceptance Criteria
- [x] View dataframe after ANY step execution
- [x] Download as CSV/Excel for manual inspection
- [x] Show column data types and statistics
- [x] Filter rows by column value
- [x] Sort by any column
- [x] Pagination for large dataframes (>1000 rows)

---

### Feature 5: Step Re-execution & Modification

#### Use Case: User modifies failed validation rule

1. **Current State:** Revenue vs Cost validation failed (Step 3)
2. **User Action:** 
   - Clicks on Step 3
   - Changes tolerance from 5% to 8%
   - Clicks "Re-run Step"
3. **Backend Process:**
   - Load cached DataFrame from Step 2
   - Reload previous step inputs
   - Re-execute Step 3 with new parameters
   - Update status + show new error/success
4. **UI Update:** Step 3 status changes, no need to re-run steps 1-2

#### Acceptance Criteria
- [x] Ability to modify parameters of any completed step
- [x] "Re-run" keeps steps 1 through N-1 cached
- [x] Only the modified step re-executes
- [x] Can re-run multiple times without issue
- [x] Audit log tracks all re-runs

---

### Feature 6: Validation Rules Library

Pre-built validators available as dropdown in configuration:

#### Built-in Validators

| Validator Name | Parameters | Example Use |
|---|---|---|
| `compare_sums` | left_col, right_col, tolerance% | Revenue = Cost ±5% |
| `merge_keys_match` | key_column, datasets | Invoice IDs match across files |
| `no_nulls` | columns | Revenue column has no blanks |
| `unique_check` | column | Invoice IDs are unique |
| `date_range` | column, min_date, max_date | Dates within fiscal year |
| `numeric_range` | column, min, max | Revenue between $0-$1M |
| `regex_match` | column, pattern | Invoice IDs match format "INV-\d+" |
| `cross_join_validation` | left_table, right_table, logic | For each cost record, revenue exists |

#### Custom Validator (via AI)
- User types: "Revenue should be 3x the cost"
- AI generates validation code
- User reviews + approves
- Saved to custom library

```python
# Generated by AI for: "Revenue should be 3x the cost"
def custom_validation(revenue_df, cost_df):
    revenue_sum = revenue_df['Revenue'].sum()
    cost_sum = cost_df['Cost'].sum()
    ratio = revenue_sum / cost_sum
    if ratio < 2.8 or ratio > 3.2:
        return False, f"Ratio {ratio:.2f}x is outside expected 3x range"
    return True, f"Ratio {ratio:.2f}x is valid"
```

---

### Feature 7: AI-Assisted Rule Generation

#### AI Helper UI

```
┌──────────────────────────────────────┐
│ 🤖 AI VALIDATION ASSISTANT           │
├──────────────────────────────────────┤
│                                      │
│ Describe what you want to validate:  │
│ ┌──────────────────────────────────┐ │
│ │ "Flag rows where revenue is more │ │
│ │ than 50% higher than last month" │ │
│ └──────────────────────────────────┘ │
│                                      │
│ [Available Columns:                  │
│  • Revenue (numeric)                 │
│  • Cost (numeric)                    │
│  • Date (datetime)                   │
│  • Product (string)]                 │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ Generate Rule                    │ │
│ └──────────────────────────────────┘ │
│                                      │
│ Generated Code:                      │
│ ┌──────────────────────────────────┐ │
│ │ def validate_revenue_spike(df):  │ │
│ │   df_sorted = df.sort_values(    │ │
│ │     'Date')                      │ │
│ │   df['prev_revenue'] =           │ │
│ │     df['Revenue'].shift(1)       │ │
│ │   spike = (df['Revenue'] -       │ │
│ │     df['prev_revenue']) /        │ │
│ │     df['prev_revenue'] > 0.5     │ │
│ │   return df[spike]               │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ☐ This looks good                    │
│ ┌──────────────────────────────────┐ │
│ │ Use in Step | Edit | Cancel      │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

#### Backend Processing

```python
# FastAPI endpoint
@app.post("/api/generate-rule")
async def generate_rule(request: GenerateRuleRequest):
    """
    request.description: "Flag rows where revenue > cost"
    request.available_columns: ["Revenue", "Cost", "Date"]
    request.available_dataframes: {"current_df": <shape>}
    """
    
    # Build prompt
    prompt = f"""
    Generate a Python Pandas validation function.
    Requirements: {request.description}
    
    Available columns: {request.available_columns}
    Available dataframe: current_df (shape: {request.shape})
    
    Function should:
    1. Return (is_valid: bool, message: str)
    2. Use only Pandas operations
    3. Handle edge cases (nulls, mismatched types)
    4. Be readable and maintainable
    
    def validate(df):
        # Your code here
    """
    
    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    generated_code = response.choices[0].message.content
    
    # Sandbox test (optional)
    # try:
    #     exec(generated_code)
    # except Exception as e:
    #     return {"error": str(e)}
    
    return {"generated_code": generated_code}
```

#### Acceptance Criteria
- [x] User can describe validation in natural language
- [x] AI generates executable Python code
- [x] Code preview shown before applying
- [x] Generated code tested in sandbox
- [x] Fallback to template if AI fails

---

## UI/UX Specifications

### Layout: Master-Detail Pattern

```
┌─────────────────────────────────────────────────────────┐
│ Header: Workflow Name | Status | Export | Settings     │
├─────────┬───────────────────────────────────────────────┤
│         │                                               │
│ STEPS   │  CONFIGURATION / DETAIL VIEW                  │
│ PANEL   │                                               │
│ (250px) │  (Responsive: changes based on selection)    │
│         │                                               │
│ [1] Up- │  ┌─────────────────────────────────────────┐ │
│ load    │  │ Step 3: Revenue Validation          [X] │ │
│ 🟢      │  ├─────────────────────────────────────────┤ │
│         │  │ Status: 🔴 FAILED                       │ │
│ [2] Up- │  │ Error: Sum mismatch by 12.3%            │ │
│ load    │  │                                         │ │
│ 🟢      │  │ [View Error Details] [Download Report] │ │
│         │  │                                         │ │
│ [3] Val­│  │ ─── Modify Parameters ───              │ │
│ Check   │  │ Tolerance %: [5 → 10                ] │ │
│ 🔴      │  │ Exact Match: [☐]                       │ │
│         │  │                                         │ │
│ [Conf]  │  │ ┌─────────────────────────────────────┐ │ │
│ [Re-run]│  │ │ [Re-run Step] [Save] [Cancel]       │ │ │
│ [Delete]│  │ └─────────────────────────────────────┘ │ │
│         │  │                                         │ │
│ DATA    │  │ ─── Data Inspector ───                 │ │
│ ┌─────┐ │  │ View output dataframe after this step  │ │
│ │5,234│ │  │                                         │ │
│ │rows │ │  │ [Inspect Data]                         │ │
│ │3 col│ │  │                                         │ │
│ └─────┘ │  └─────────────────────────────────────────┘ │
│         │                                               │
└─────────┴───────────────────────────────────────────────┘
```

### Mobile Responsive

On mobile, use:
- Bottom sheet (swipe up for configuration)
- Single column layout
- Collapsible step details

---

### Color Scheme & Theme

| Element | Color | Usage |
|---------|-------|-------|
| Success | `#4CAF50` | ✅ Status, validation passed |
| Error | `#F44336` | 🔴 Status, failed steps |
| Warning | `#FF9800` | ⚠️ Warnings, partial success |
| Pending | `#9E9E9E` | ⚪ Idle, pending steps |
| Info | `#2196F3` | ℹ️ Messages, help text |
| Accent | `#673AB7` | Primary CTA buttons |

### Typography

- **Headers:** Inter Bold, 24px (workflow title)
- **Step Names:** Inter SemiBold, 16px
- **Parameters:** Inter Regular, 14px
- **Code/Data:** Monaco/Courier, 12px (monospace)

---

## Backend Architecture

### Directory Structure

```
backend/
├── main.py                    # FastAPI app initialization
├── config.py                  # Environment config
├── requirements.txt           # Python dependencies
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── workflow.py        # Workflow/Step Pydantic models
│   │   ├── execution.py       # Execution state models
│   │   └── validation.py      # Validation result models
│   │
│   ├── routes/
│   │   ├── workflows.py       # GET/POST /workflows
│   │   ├── steps.py           # PUT /steps/{id}, POST /steps/{id}/rerun
│   │   ├── execution.py       # POST /execute, WS /ws/status
│   │   ├── ai_rules.py        # POST /generate-rule
│   │   └── data_inspector.py  # GET /data/{step_id}
│   │
│   ├── services/
│   │   ├── workflow_executor.py    # Main execution engine
│   │   ├── action_registry.py      # Validator function registry
│   │   ├── state_manager.py        # DataFrame cache
│   │   ├── ai_service.py           # OpenAI integration
│   │   └── validation_builder.py   # Rule generation
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── compare_sums.py         # Sum comparison logic
│   │   ├── merge_validation.py     # Key matching
│   │   ├── format_validation.py    # Regex/pattern checks
│   │   └── custom_validators.py    # User-defined rules
│   │
│   └── db/
│       ├── models.py         # SQLAlchemy ORM models
│       ├── database.py       # DB connection
│       └── repositories.py   # CRUD operations
│
├── tests/
│   ├── test_validators.py
│   ├── test_executor.py
│   └── test_api.py
│
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

### Core Services

#### 1. WorkflowExecutor (Orchestration)

```python
# app/services/workflow_executor.py

class WorkflowExecutor:
    def __init__(self, state_manager, action_registry):
        self.state = state_manager
        self.registry = action_registry
    
    async def execute_workflow(self, workflow: Workflow, 
                              input_files: Dict):
        """Execute all steps in sequence"""
        results = []
        
        for step in workflow.steps:
            try:
                result = await self.execute_step(step, input_files)
                step.status = StepStatus.SUCCESS
                step.error = None
                results.append(result)
                
                # Broadcast status update via WebSocket
                await self.broadcast_status(step)
                
            except ValidationError as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                results.append(e)
                
                if workflow.globals.fail_fast:
                    break
        
        return results
    
    async def execute_step(self, step: Step, context: Dict):
        """Execute single step"""
        # Get action function from registry
        action_func = self.registry.get(step.action)
        
        # Load input (from prev step or file)
        inputs = await self._prepare_inputs(step)
        
        # Execute action
        output = await action_func(**step.params, **inputs)
        
        # Apply validation if present
        if step.get('validation_rule'):
            is_valid, message = await self._validate(output, step)
            if not is_valid:
                raise ValidationError(message)
        
        # Cache output for next step
        await self.state.cache_dataframe(step.id, output)
        
        return {
            "step_id": step.id,
            "status": "success",
            "output_shape": output.shape,
            "execution_time": step.execution_time_ms
        }
    
    async def rerun_step(self, workflow_id: str, step_id: str, 
                        new_params: Dict):
        """Re-execute a specific step with new parameters"""
        step = self._find_step(step_id)
        step.params.update(new_params)
        
        # Re-execute only this step (previous steps already cached)
        result = await self.execute_step(step, {})
        
        return result
```

#### 2. ActionRegistry (Validator Functions)

```python
# app/services/action_registry.py

class ActionRegistry:
    """Registry of all available workflow actions"""
    
    def __init__(self):
        self.actions = {}
        self._register_base_actions()
    
    def register(self, action_name: str, func: Callable):
        """Register new validator function"""
        self.actions[action_name] = func
    
    def get(self, action_name: str) -> Callable:
        """Retrieve validator function"""
        if action_name not in self.actions:
            raise ValueError(f"Unknown action: {action_name}")
        return self.actions[action_name]
    
    def _register_base_actions(self):
        """Register built-in validators"""
        self.register('parse_excel', parse_excel)
        self.register('compare_sums', compare_sums)
        self.register('merge_dataframes', merge_dataframes)
        self.register('export_excel', export_excel)
        # ... more validators

# Built-in validator example
async def compare_sums(left_df, right_df, left_col, right_col, 
                       tolerance_percent=0.05):
    left_sum = left_df[left_col].sum()
    right_sum = right_df[right_col].sum()
    
    diff_percent = abs(left_sum - right_sum) / left_sum
    
    if diff_percent > tolerance_percent:
        raise ValidationError(
            f"Sum mismatch: {left_sum} vs {right_sum} "
            f"({diff_percent*100:.1f}% difference)"
        )
    
    return pd.DataFrame({
        'left_sum': [left_sum],
        'right_sum': [right_sum],
        'diff_percent': [diff_percent],
        'status': ['PASS']
    })
```

#### 3. StateManager (Dataframe Cache)

```python
# app/services/state_manager.py

class StateManager:
    """Manage execution state & DataFrame caching"""
    
    def __init__(self):
        # In-memory cache: {session_id: {step_id: dataframe}}
        self.cache = defaultdict(dict)
    
    async def cache_dataframe(self, session_id: str, step_id: str, 
                             df: pd.DataFrame):
        """Store dataframe in cache"""
        self.cache[session_id][step_id] = df
    
    async def get_dataframe(self, session_id: str, step_id: str) \
                           -> pd.DataFrame:
        """Retrieve cached dataframe"""
        if session_id not in self.cache or \
           step_id not in self.cache[session_id]:
            raise ValueError(f"Dataframe not found: {step_id}")
        return self.cache[session_id][step_id]
    
    async def clear_session(self, session_id: str):
        """Clean up after execution"""
        if session_id in self.cache:
            del self.cache[session_id]
```

#### 4. AI Service (Rule Generation)

```python
# app/services/ai_service.py

class AIService:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
    
    async def generate_validation_rule(
        self, 
        description: str,
        available_columns: List[str],
        sample_df: pd.DataFrame = None
    ) -> str:
        """Generate Pandas code from natural language"""
        
        df_sample = sample_df.head(3).to_string() if sample_df else ""
        
        prompt = f"""
        Generate a Python function that validates data using Pandas.
        
        Requirement: {description}
        Available columns: {', '.join(available_columns)}
        
        Sample data:
        {df_sample}
        
        Return a function called `validate(df: pd.DataFrame) -> 
        Tuple[bool, str]` that:
        1. Returns (True, "message") if validation passes
        2. Returns (False, "error message") if validation fails
        3. Handles edge cases (null values, type mismatches)
        
        Only return the function code, no explanations.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    async def test_generated_code(self, code: str, 
                                  test_df: pd.DataFrame) -> \
                                  Tuple[bool, str]:
        """Safely test generated code in sandbox"""
        try:
            local_ns = {"pd": pd, "np": np}
            exec(code, local_ns)
            validate_func = local_ns['validate']
            
            result = validate_func(test_df)
            return (True, result)
        except Exception as e:
            return (False, str(e))
```

---

### FastAPI Routes

#### Workflow Management

```python
# app/routes/workflows.py

@router.get("/workflows")
async def list_workflows():
    """List all workflows"""
    return await WorkflowService.list_all()

@router.post("/workflows")
async def create_workflow(workflow: WorkflowCreate):
    """Upload/create new workflow"""
    return await WorkflowService.create(workflow)

@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow definition"""
    return await WorkflowService.get(workflow_id)

@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, 
                         changes: WorkflowUpdate):
    """Update workflow (add/remove/modify steps)"""
    return await WorkflowService.update(workflow_id, changes)
```

#### Execution Control

```python
# app/routes/execution.py

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, 
                          files: List[UploadFile]):
    """Start workflow execution"""
    workflow = await WorkflowService.get(workflow_id)
    executor = WorkflowExecutor(state_manager, registry)
    
    session_id = str(uuid4())
    asyncio.create_task(
        executor.execute_workflow(workflow, files)
    )
    
    return {"session_id": session_id, "status": "started"}

@router.post("/workflows/{workflow_id}/steps/{step_id}/rerun")
async def rerun_step(workflow_id: str, step_id: str, 
                    request: RerunRequest):
    """Re-execute step with modified parameters"""
    executor = WorkflowExecutor(state_manager, registry)
    result = await executor.rerun_step(
        workflow_id, 
        step_id, 
        request.new_params
    )
    return result

@router.websocket("/ws/{session_id}")
async def websocket_status(websocket: WebSocket, 
                          session_id: str):
    """WebSocket for real-time status updates"""
    await websocket.accept()
    
    while True:
        status_update = await state_manager.get_status(session_id)
        await websocket.send_json(status_update)
        await asyncio.sleep(1)  # Polling fallback
```

#### AI Rule Generation

```python
# app/routes/ai_rules.py

@router.post("/generate-rule")
async def generate_rule(request: GenerateRuleRequest):
    """Generate validation code from natural language"""
    ai_service = AIService()
    
    code = await ai_service.generate_validation_rule(
        request.description,
        request.available_columns
    )
    
    # Optionally test the code
    if request.test_dataframe:
        is_valid, result = await ai_service.test_generated_code(
            code, 
            request.test_dataframe
        )
        return {
            "code": code,
            "test_result": result if is_valid else None,
            "error": result if not is_valid else None
        }
    
    return {"code": code}
```

#### Data Inspector

```python
# app/routes/data_inspector.py

@router.get("/data/{session_id}/{step_id}")
async def get_step_data(session_id: str, step_id: str,
                       skip: int = 0, limit: int = 100):
    """Retrieve dataframe state after a step"""
    df = await state_manager.get_dataframe(session_id, step_id)
    
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.to_dict(),
        "data": df.iloc[skip:skip+limit].to_dict('records'),
        "statistics": df.describe().to_dict()
    }

@router.get("/data/{session_id}/{step_id}/download")
async def download_step_data(session_id: str, step_id: str,
                            format: str = "csv"):
    """Download dataframe as CSV/Excel"""
    df = await state_manager.get_dataframe(session_id, step_id)
    
    if format == "excel":
        df.to_excel(f"/tmp/{step_id}.xlsx", index=False)
        return FileResponse(f"/tmp/{step_id}.xlsx")
    else:
        return StreamingResponse(
            iter([df.to_csv(index=False)]),
            media_type="text/csv"
        )
```

---

### Database Schema (SQLAlchemy)

```python
# app/db/models.py

class WorkflowModel(Base):
    __tablename__ = "workflows"
    
    id: str = Column(String, primary_key=True)
    name: str = Column(String)
    description: str = Column(String, nullable=True)
    definition: JSON = Column(JSON)  # Full step JSON
    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)
    created_by: str = Column(String)
    status: str = Column(String, default="draft")
    
    steps = relationship("StepModel", backref="workflow")
    executions = relationship("ExecutionModel", backref="workflow")

class StepModel(Base):
    __tablename__ = "steps"
    
    id: str = Column(String, primary_key=True)
    workflow_id: str = Column(String, ForeignKey("workflows.id"))
    order: int = Column(Integer)
    name: str = Column(String)
    action: str = Column(String)
    params: JSON = Column(JSON)
    validation_rule: str = Column(String, nullable=True)

class ExecutionModel(Base):
    __tablename__ = "executions"
    
    id: str = Column(String, primary_key=True)  # session_id
    workflow_id: str = Column(String, 
                             ForeignKey("workflows.id"))
    started_at: datetime = Column(DateTime)
    completed_at: datetime = Column(DateTime, nullable=True)
    status: str = Column(String)  # running, success, failed
    error_message: str = Column(String, nullable=True)
    
    step_executions = relationship("StepExecutionModel", 
                                   backref="execution")

class StepExecutionModel(Base):
    __tablename__ = "step_executions"
    
    id: str = Column(String, primary_key=True)
    execution_id: str = Column(String, 
                              ForeignKey("executions.id"))
    step_id: str = Column(String)
    status: str = Column(String)  # success, failed, skipped
    error_message: str = Column(String, nullable=True)
    execution_time_ms: int = Column(Integer)
    input_data_shape: String = Column(String)
    output_data_shape: String = Column(String)
    output_preview: JSON = Column(JSON)  # First 5 rows
```

---

## Data Flow & State Management

### Execution State Diagram

```
IDLE
  ↓
User clicks "Execute"
  ↓
RUNNING
  ├─ Step 1: RUNNING → SUCCESS
  ├─ Step 2: RUNNING → SUCCESS
  ├─ Step 3: RUNNING → FAILED (error stored)
  │  ↓
  │  User modifies params
  │  ↓
  │  Step 3: RUNNING → SUCCESS
  ├─ Step 4: RUNNING → SUCCESS
  └─ Workflow: SUCCESS

OR

RUNNING
  ├─ Step 1-2: SUCCESS
  ├─ Step 3: FAILED
  │  ↓
  │  fail_fast=true
  └─ Workflow: FAILED (stopped)
```

### Session State (In-Memory Cache Structure)

```python
{
    "session_001": {
        "workflow_id": "workflow_001",
        "status": "running",
        "started_at": "2026-03-23T10:00:00Z",
        "dataframes": {
            "step_1": <DataFrame 5234 rows × 3 columns>,
            "step_2": <DataFrame 1200 rows × 4 columns>,
            "step_3": <DataFrame 1 rows × 4 columns>  # validation result
        },
        "step_status": {
            "step_1": {
                "status": "success",
                "execution_time_ms": 234,
                "error": null
            },
            "step_2": {
                "status": "success",
                "execution_time_ms": 156,
                "error": null
            },
            "step_3": {
                "status": "failed",
                "execution_time_ms": 89,
                "error": "Sum mismatch by 12.3%"
            }
        }
    }
}
```

### WebSocket Message Format

```json
{
  "type": "step_status_update",
  "session_id": "session_001",
  "step_id": "step_3",
  "status": "failed",
  "timestamp": "2026-03-23T10:05:30Z",
  "error": {
    "message": "Sum mismatch by 12.3%",
    "details": "Left: $5,234,100 vs Right: $4,645,230",
    "recoverable": true
  },
  "execution_time_ms": 89
}
```

---

## Implementation Details

### Configuration File (config.py)

```python
# app/config.py

import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # FastAPI
    APP_NAME = "Modular Workflow Engine"
    API_VERSION = "v1"
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./workflow_engine.db"
    )
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_MODEL = "gpt-4"
    
    # File Storage
    UPLOAD_DIR = "./uploads"
    MAX_FILE_SIZE_MB = 100
    ALLOWED_EXTENSIONS = {"xlsx", "csv", "json"}
    
    # Execution
    MAX_EXECUTION_TIME_SECONDS = 300
    STEP_TIMEOUT_SECONDS = 60
    
    # Cache
    REDIS_URL = os.getenv("REDIS_URL", None)
    USE_REDIS = REDIS_URL is not None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment File (.env.example)

```bash
# FastAPI
DEBUG=True
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./workflow_engine.db
# DATABASE_URL=postgresql://user:pass@localhost/workflow_db

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Redis (optional)
REDIS_URL=redis://localhost:6379

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=100
```

### Docker Compose Setup

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=sqlite:///./workflow_engine.db
    volumes:
      - ./backend:/app
      - workflow_cache:/tmp
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # Optional: Redis for production caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  workflow_cache:
  redis_data:
```

### Dockerfile (Backend)

```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Requirements.txt

```txt
# Backend Dependencies

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Data Processing
pandas==2.1.3
numpy==1.26.2
openpyxl==3.11.0
polars==0.19.12  # Optional: faster alternative to Pandas

# Database
sqlalchemy==2.0.23
sqlmodel==0.0.14
psycopg2-binary==2.9.9  # PostgreSQL driver

# Caching
redis==5.0.1
hiredis==2.2.3

# AI/API
openai==1.3.0
aiohttp==3.9.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Logging & Monitoring
structlog==23.2.0
python-json-logger==2.0.7

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# WebSocket
websockets==12.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
```

---

## Development Roadmap

### Phase 1: MVP (Weeks 1-2)

**Deliverables:**
- ✅ Basic Next.js frontend with step sidebar
- ✅ FastAPI backend with action registry
- ✅ 3 built-in validators (compare_sums, merge, format_check)
- ✅ Simple in-memory state management
- ✅ Step re-execution logic
- ✅ Data inspector (view dataframe after step)
- ✅ SQLite database for workflow persistence

**Tasks:**
1. Set up project structure (backend + frontend)
2. Implement core WorkflowExecutor service
3. Build ActionRegistry with 3 validators
4. Create Next.js UI with step list + config panel
5. Add REST API endpoints for workflow CRUD
6. Implement data caching + state management
7. Build data inspector component
8. Write integration tests

**Success Criteria:**
- User can upload a workflow JSON
- Execute all steps sequentially
- Modify a failed step and re-run
- View dataframe after each step
- Download results

---

### Phase 2: AI Integration (Week 3)

**Deliverables:**
- ✅ AI rule generation endpoint
- ✅ UI for natural language rule input
- ✅ Generated code validation/testing
- ✅ 3+ pre-built validation templates

**Tasks:**
1. Integrate OpenAI API
2. Create AIService for prompt engineering
3. Build UI dialog for AI helper
4. Add code sandbox testing
5. Create validation template library
6. Write E2E tests for AI flow

**Success Criteria:**
- User can describe rule in English
- AI generates executable Pandas code
- Code can be tested before applying
- Generated rules work in actual workflow

---

### Phase 3: Production Ready (Week 4)

**Deliverables:**
- ✅ PostgreSQL database integration
- ✅ Redis caching for multi-session support
- ✅ WebSocket real-time updates
- ✅ Comprehensive error handling
- ✅ Audit logging
- ✅ User authentication
- ✅ Docker & deployment guides

**Tasks:**
1. Migrate SQLite → PostgreSQL
2. Add Redis for distributed caching
3. Implement WebSocket updates
4. Add JWT authentication
5. Create audit trail system
6. Write deployment documentation
7. Performance optimization
8. Security hardening

**Success Criteria:**
- Multiple users can run workflows simultaneously
- Real-time status updates via WebSocket
- Audit trail tracks all modifications
- Secure deployment ready
- Performance tested with 1GB+ files

---

### Phase 4: Polish & Scaling (Future)

**Future Features:**
- Parallel step execution (where independent)
- Workflow versioning & rollback
- Scheduled workflow execution
- Slack/Email notifications
- Plugin system for custom actions
- Advanced data visualization
- Workflow templates marketplace
- Multi-tenancy support

---

## Deployment & DevOps

### Local Development Setup

```bash
# Clone repository
git clone <repo>
cd GP-AUTOMATION/POC

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your OpenAI API key

# Setup frontend
cd ../frontend
npm install

# Run with Docker Compose
cd ..
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml

name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install Python dependencies
        run: |
          pip install -r backend/requirements.txt pytest pytest-asyncio
      
      - name: Run backend tests
        run: pytest backend/tests
      
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      
      - name: Install Node dependencies
        run: npm --prefix frontend install
      
      - name: Run frontend tests
        run: npm --prefix frontend run test
      
      - name: Build Docker image
        run: docker-compose build
```

### Deployment Checklist

- [ ] Environment variables configured (.env)
- [ ] Database migrations run
- [ ] SSL certificates installed
- [ ] OpenAI API key verified
- [ ] Upload directory permissions set
- [ ] Log rotation configured
- [ ] Monitoring alerts set up
- [ ] Backup strategy defined
- [ ] Load testing completed
- [ ] Security scan passed

---

## Success Metrics

### Technical KPIs

| Metric | Target | Rationale |
|--------|--------|-----------|
| API Response Time | <500ms | Users expect instant feedback |
| Step Execution Time | <60s per step | Large file processing |
| Dataframe Cache Hit Rate | >85% | Minimize re-computation |
| Error Recovery Time | <10s | Quick re-run capability |
| Deployment Time | <5min | CI/CD efficiency |

### Business KPIs

| Metric | Target |
|--------|--------|
| User Manual Intervention Time | 90% reduction |
| Workflow Accuracy | 99.5% |
| Failed Step Identification | <2 sec |
| User Satisfaction | >4.5/5 |
| Time to Resolution | <30 min |

---

## Appendix: API Reference Summary

### Key Endpoints

```
POST   /api/workflows                 # Create workflow
GET    /api/workflows                 # List workflows
GET    /api/workflows/{id}            # Get workflow details
PUT    /api/workflows/{id}            # Update workflow
DELETE /api/workflows/{id}            # Delete workflow

POST   /api/workflows/{id}/execute    # Start execution
GET    /api/executions/{session_id}   # Get execution status
POST   /api/workflows/{id}/steps/{step_id}/rerun   # Re-run step

GET    /api/data/{session_id}/{step_id}           # View dataframe
GET    /api/data/{session_id}/{step_id}/download  # Download data

POST   /api/generate-rule             # AI rule generation
GET    /api/validators                # List available validators

WS     /ws/{session_id}               # WebSocket status stream
```

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Revenue sum mismatch",
    "details": {
      "step_id": "step_3",
      "expected": 5234100,
      "actual": 4645230,
      "diff_percent": 12.3
    },
    "recoverable": true,
    "suggested_action": "Increase tolerance to 0.15 or verify source data"
  }
}
```

---

## Conclusion

This Modular Workflow Engine POC provides a bridge between rigid static automation and flexible, user-controlled workflows. By treating each step as a configurable block with clear inputs/outputs, we enable non-technical users to debug, modify, and optimize their automation processes.

### Key Takeaways

1. **Architecture:** JSON-based step definitions + modular Python validators
2. **Tech Stack:** Next.js (React) + FastAPI + Pandas + PostgreSQL
3. **Timeline:** 4 weeks from MVP to production-ready
4. **Value:** 90% reduction in troubleshooting, real-time visibility, AI-assisted rules

---

**Document Prepared By:** Workflow Automation Team  
**Ready for:** Development Kickoff  
**Questions?** Review architecture sections or consult with team lead.
