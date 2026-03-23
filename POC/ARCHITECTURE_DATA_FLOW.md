# Architecture & Data Flow Reference
## Modular Workflow Engine POC

---

## System Architecture Overview

```

                    ┌─────────────────────────────────────────┐
                    │     MODULAR WORKFLOW ENGINE POC         │
                    └─────────────────────────────────────────┘

        ┌──────────────────────────────────────────────────────────────┐
        │                                                              │
        │  ┌────────────────────┐              ┌──────────────────┐   │
        │  │   Next.js UI       │◄─ HTTP/WS ──►│  FastAPI Backend │   │
        │  │   (React)          │              │                  │   │
        │  └────────────────────┘              │  • Executor      │   │
        │  • Step Sidebar        Port 3000     │  • Registry      │   │
        │  • Config Panel                      │  • State Mgr     │   │
        │  • Data Inspector                    │  • Validators    │   │
        │  • AI Chat                           │  • AI Service    │   │
        │                                      │                  │   │
        │                                      │    Port 8000     │   │
        │                                      └──────────────────┘   │
        │                                             │                │
        │                                             │ Pandas/Data   │
        │                                             ▼                │
        │                                      ┌──────────────────┐   │
        │                                      │  In-Memory Cache │   │
        │                                      │  (DataFrame Dict)│   │
        │                                      └──────────────────┘   │
        │                                             │                │
        │                                             │ File I/O      │
        │                                             ▼                │
        │                                      ┌──────────────────┐   │
        │                                      │  Uploads Dir     │   │
        │                                      │  • Excel files   │   │
        │                                      │  • CSV files     │   │
        │                                      │  • Results       │   │
        │                                      └──────────────────┘   │
        │                                                              │
        │  ┌────────────────────────────────────────────────────────┐ │
        │  │    PERSISTENT STORAGE (SQLite/PostgreSQL)             │ │
        │  │    • Workflows (definitions)                          │ │
        │  │    • Executions (history)                             │ │
        │  │    • Audit Logs                                       │ │
        │  │    • User Preferences                                 │ │
        │  └────────────────────────────────────────────────────────┘ │
        │                                                              │
        └──────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────┐
        │  EXTERNAL INTEGRATIONS                                     │
        │  • OpenAI API (Rule Generation)                            │
        │  • File Storage (S3/Blob for production)                   │
        │  • Slack/Email (Notifications)                             │
        └─────────────────────────────────────────────────────────────┘
```

---

## Request-Response Flow

### Scenario: User Modifies Failed Validation & Re-runs

```
┌───────────────────────────────────────────────────────────────────┐
│ USER ACTION SEQUENCE                                              │
└───────────────────────────────────────────────────────────────────┘

STEP 1: User Clicks on Failed Step 3
    │
    ├─► FRONTEND: GET /api/workflows/{id}
    │   Retrieves workflow definition
    │   ▼
    ├─► BACKEND: Returns Workflow + Step statuses
    │   ▼
    ├─► FRONTEND: Displays configuration panel
    │   Shows current params: tolerance_percent = 0.05
    │

STEP 2: User Changes Tolerance & Clicks "Re-run"
    │
    ├─► FRONTEND: Sends POST /workflows/{id}/steps/{id}/rerun
    │   Body: { "new_params": { "tolerance_percent": 0.08 } }
    │   ▼
    ├─► BACKEND (WorkflowExecutor.rerun_step):
    │   1. Find step in workflow
    │   2. Update params
    │   3. Load cached input (from previous steps)
    │   4. Execute step only (don't re-run steps 1-2)
    │   5. Store new result in cache
    │   ▼
    ├─► BACKEND: Returns { "status": "success", "result": {...} }
    │   ▼
    ├─► FRONTEND: Updates UI
    │   • Changes Step 3 status from 🔴 to ✅
    │   • Shows new validation result
    │   • Clears error message
    │

STEP 3: User Clicks "Inspect Data"
    │
    ├─► FRONTEND: GET /api/data/{session_id}/step_3
    │   ▼
    ├─► BACKEND: Returns cached dataframe as JSON
    │   {
    │     "shape": [5234, 3],
    │     "columns": ["Invoice_ID", "Revenue", "Date"],
    │     "data": [...first 100 rows...],
    │     "statistics": {...}
    │   }
    │   ▼
    ├─► FRONTEND: Renders data table with pagination
    │

└───────────────────────────────────────────────────────────────────┘
```

---

## Backend Service Interactions

### WorkflowExecutor ↔ ActionRegistry ↔ Validators

```
┌─────────────────────────────────────────────────────────────────┐
│ WORKFLOW EXECUTION FLOW (Step-by-Step)                         │
└─────────────────────────────────────────────────────────────────┘

WorkflowExecutor.execute_workflow(workflow, session_id, files)
    │
    ├─► FOR EACH step IN workflow.steps:
    │
    │   1. Update Step Status → RUNNING
    │      state_manager.set_status(session_id, step.id, "running")
    │      └─► Frontend WebSocket notified
    │
    │   2. Retrieve Action Function
    │      action = registry.get(step.action)
    │      └─► Example: get("compare_sums") → compare_sums()
    │
    │   3. Load Inputs
    │      If step.input_type == "file":
    │          df = pd.read_excel(files[file_key])
    │      If step.input_type == "previous_step":
    │          df = state_manager.get_dataframe(session_id, 
    │                                          step.input_step_id)
    │
    │   4. Execute Action With Parameters
    │      result = await action(**step.params, **inputs)
    │      Example call:
    │      await compare_sums(
    │          left_df=revenue_df,
    │          right_df=cost_df,
    │          left_col="Revenue",
    │          right_col="Total_Cost",
    │          tolerance_percent=0.05
    │      )
    │
    │   5. Validate Result
    │      if step.validation_rule:
    │          is_valid, message = validate(result)
    │          if not is_valid:
    │              raise ValidationError(message)
    │
    │   6. Cache Output
    │      state_manager.cache_dataframe(session_id, step.id, result)
    │      └─► DataFrame stored in memory
    │
    │   7. Update Status → SUCCESS
    │      state_manager.set_status(session_id, step.id, "success")
    │      └─► Frontend WebSocket notified
    │
    │   EXCEPTION → Status → FAILED
    │      state_manager.set_status(session_id, step.id, 
    │                               {"status": "failed", 
    │                                "error": "message"})
    │      └─► Workflow may stop (if fail_fast=true) OR continue
    │
    └─► NEXT STEP (or WORKFLOW_COMPLETE)

```

---

## State Management Examples

### Execution State After Steps 1-2 Complete, Step 3 Failed

```python
# StateManager.cache (In-Memory)
{
    "session_001": {
        # Dataframes stored
        "step_1": DataFrame({
            'Invoice_ID': ['INV-001', 'INV-002', ...],
            'Revenue': [50000, 75000, ...],
            'Date': ['2026-01-01', '2026-01-02', ...]
        }),  # 5,234 rows × 3 columns
        
        "step_2": DataFrame({
            'Invoice_ID': ['INV-001', 'INV-002', ...],
            'Cost': [40000, 60000, ...],
            'Supplier': ['Supplier A', 'Supplier B', ...]
        }),  # 1,200 rows × 3 columns
        
        # step_3 not cached yet (failed during validation)
    }
}

# StateManager.status (Execution State)
{
    "session_001": {
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
            "error": "Sum mismatch: $5,234,100 vs $4,645,230 (12.3% diff)"
        }
    }
}

# After user modifies Step 3 params and re-runs:
{
    "session_001": {
        "step_1": { "status": "success", ... },
        "step_2": { "status": "success", ... },
        "step_3": {
            "status": "success",  # ← Changed!
            "execution_time_ms": 95,
            "error": null  # ← Cleared!
        }
    }
}
```

---

## API Contract Examples

### 1. Create Workflow

**REQUEST**
```http
POST /api/workflows
Content-Type: application/json

{
  "name": "Revenue vs Cost Reconciliation",
  "description": "Validates revenue matches cost",
  "steps": [
    {
      "id": "step_1",
      "order": 1,
      "name": "Upload Revenue File",
      "type": "input",
      "action": "parse_excel",
      "params": {
        "file_key": "revenue.xlsx",
        "sheet_name": "Data"
      }
    },
    {
      "id": "step_2",
      "order": 2,
      "name": "Upload Cost File",
      "type": "input",
      "action": "parse_excel",
      "params": {
        "file_key": "cost.xlsx",
        "sheet_name": "Summary"
      }
    },
    {
      "id": "step_3",
      "order": 3,
      "name": "Compare Revenue vs Cost",
      "type": "validation",
      "action": "compare_sums",
      "params": {
        "left_col": "Revenue",
        "right_col": "Total_Cost",
        "tolerance_percent": 0.05
      }
    }
  ]
}
```

**RESPONSE**
```json
{
  "id": "wf_abc123",
  "name": "Revenue vs Cost Reconciliation",
  "description": "Validates revenue matches cost",
  "steps": [...same as above...],
  "created_at": "2026-03-23T10:00:00Z",
  "version": "1.0"
}
```

---

### 2. Execute Workflow

**REQUEST**
```http
POST /api/workflows/wf_abc123/execute
Content-Type: multipart/form-data

files: [revenue.xlsx, cost.xlsx]
```

**RESPONSE**
```json
{
  "session_id": "session_001",
  "status": "started"
}
```

**WebSocket Updates (Real-time):**
```json
{
  "type": "step_status_update",
  "session_id": "session_001",
  "step_id": "step_1",
  "status": "running",
  "timestamp": "2026-03-23T10:00:01Z"
}
```

```json
{
  "type": "step_status_update",
  "session_id": "session_001",
  "step_id": "step_1",
  "status": "success",
  "execution_time_ms": 234,
  "timestamp": "2026-03-23T10:00:02Z"
}
```

```json
{
  "type": "step_status_update",
  "session_id": "session_001",
  "step_id": "step_3",
  "status": "failed",
  "error": "Sum mismatch: $5,234,100 vs $4,645,230 (12.3% diff)",
  "execution_time_ms": 89,
  "timestamp": "2026-03-23T10:00:05Z"
}
```

---

### 3. Re-run Failed Step

**REQUEST**
```http
POST /api/workflows/wf_abc123/steps/step_3/rerun
Content-Type: application/json

{
  "new_params": {
    "tolerance_percent": 0.15
  }
}
```

**RESPONSE**
```json
{
  "status": "success",
  "step_id": "step_3",
  "execution_time_ms": 92,
  "result": {
    "left_sum": 5234100,
    "right_sum": 4824600,
    "diff_percent": 0.078,
    "status": "PASS"
  }
}
```

---

### 4. Inspect Data After Step

**REQUEST**
```http
GET /api/data/session_001/step_1?skip=0&limit=100
```

**RESPONSE**
```json
{
  "shape": [5234, 3],
  "columns": ["Invoice_ID", "Revenue", "Date"],
  "dtypes": {
    "Invoice_ID": "object",
    "Revenue": "int64",
    "Date": "datetime64[ns]"
  },
  "data": [
    {"Invoice_ID": "INV-001", "Revenue": 50000, "Date": "2026-01-01"},
    {"Invoice_ID": "INV-002", "Revenue": 75000, "Date": "2026-01-02"},
    ...
  ],
  "statistics": {
    "Revenue": {
      "count": 5234,
      "mean": 45200,
      "std": 32100,
      "min": 1000,
      "25%": 25000,
      "50%": 40000,
      "75%": 60000,
      "max": 500000
    }
  }
}
```

---

### 5. Generate AI Rule

**REQUEST**
```http
POST /api/generate-rule
Content-Type: application/json

{
  "description": "Flag rows where Revenue is more than 50% higher than average",
  "available_columns": ["Revenue", "Cost", "Date", "Product_ID"],
  "sample_dataframe": {
    "columns": ["Revenue", "Cost", "Date"],
    "data": [
      {"Revenue": 50000, "Cost": 40000, "Date": "2026-01-01"},
      {"Revenue": 75000, "Cost": 60000, "Date": "2026-01-02"}
    ]
  }
}
```

**RESPONSE**
```json
{
  "code": "def validate_revenue_spike(df):\n    avg_revenue = df['Revenue'].mean()\n    spike = df['Revenue'] > (avg_revenue * 1.5)\n    return df[spike], f'Found {spike.sum()} rows with revenue >50% above average'",
  "language": "python",
  "framework": "pandas"
}
```

---

## Frontend Component Hierarchy

```
App (page.tsx)
│
├── Sidebar (250px width)
│   └── WorkflowList
│       ├── List of workflows
│       │   └── WorkflowCard (clickable)
│       │       └── workflow.name
│       │       └── step count
│       │
│       └── [Create New Workflow] button
│
└── MainContent (flex-1)
    │
    ├── Header
    │   ├── Workflow Title
    │   ├── [Execute] button
    │   └── [Export] button
    │
    ├── StepList (left panel)
    │   └── FOR each step IN workflow.steps:
    │       └── StepCard
    │           ├── Step number
    │           ├── Step name
    │           ├── Status icon (🟢🔴⚪)
    │           ├── Execution time (if complete)
    │           └── [Click to configure] handler
    │
    └── DetailPanel (right panel - changes based on selection)
        │
        ├── IF step selected:
        │   └── ConfigurationPanel
        │       ├── Step name
        │       ├── Action dropdown
        │       ├── Parameters form
        │       │   ├── Input field (parameter)
        │       │   ├── Input field (parameter)
        │       │   └── Input field (parameter)
        │       ├── Validation rule (if present)
        │       ├── [AI Helper] button
        │       │   └── AIRuleGenerator
        │       │       ├── Text input
        │       │       ├── [Generate] button
        │       │       ├── Code preview
        │       │       └── [Use | Edit | Cancel]
        │       ├── [Data Inspector] button
        │       │   └── DataInspector
        │       │       ├── Row count & columns
        │       │       ├── DataFrame table (paginated)
        │       │       ├── Column statistics
        │       │       └── [Download] button
        │       │
        │       └── [Save] [Re-run] [Delete] buttons
        │
        └── IF no selection:
            └── "Select a step to configure"
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────┐
│ ERROR SCENARIO: Sum Validation Fails                    │
└─────────────────────────────────────────────────────────┘

STEP 3: compare_sums validator executes
    │
    ├─ Calculates left_sum = 5,234,100
    ├─ Calculates right_sum = 4,645,230
    ├─ Calculates diff_percent = 12.3%
    │
    ├─ Checks: if diff_percent > tolerance_percent (0.05)
    │   └─► TRUE! (12.3% > 5%)
    │
    ├─ Raises ValidationError:
    │   "Sum mismatch: $5,234,100 vs $4,645,230 (12.3% difference)"
    │
    └─► WorkflowExecutor catches exception
        │
        ├─► Sets step.status = FAILED
        ├─► Sets step.error = error message
        ├─► Updates state_manager.set_status()
        │
        ├─► Sends WebSocket update to Frontend:
        │   {
        │     "type": "step_status_update",
        │     "step_id": "step_3",
        │     "status": "failed",
        │     "error": "Sum mismatch: $5,234,100 vs $4,645,230 (12.3% diff)",
        │     "recoverable": true
        │   }
        │
        └─► Frontend receives update
            │
            ├─► Change UI: step_3 → 🔴 FAILED
            ├─► Display error message in panel
            ├─► Show [Re-run] button
            ├─► Allow user to modify tolerance & retry
            │
            └─► User modifies params & clicks Re-run
                └─► New tolerance: 0.15 (> 12.3%)
                └─► Step re-executes
                └─► Now passes! ✅
```

---

## Performance Considerations

### Memory Usage Example

```
5 concurrent workflows × 5,000 rows × 3 columns × 8 bytes/value ≈ 60MB

StateManager cache structure:
{
    "session_001": {
        "step_1": <DataFrame 5000×3>,  ≈ 12 MB (per dataframe)
        "step_2": <DataFrame 5000×3>,  ≈ 12 MB
        "step_3": <Result object>,     ≈ 0.1 MB
    },
    "session_002": { ... },
    ...
}

Optimization:
• Auto-cleanup sessions after 1 hour (configurable)
• Lazy-load dataframes (don't load until clicked)
• Use Polars instead of Pandas for 10x faster I/O
• Compress cached dataframes with pickle + gzip
```

---

## Testing Strategy

```
BACKEND TESTS
├── Unit Tests
│   ├── ActionRegistry (register/retrieve actions)
│   ├── State Manager (cache operations)
│   ├── Validators (compare_sums logic)
│   └── Error handling
│
├── Integration Tests
│   ├── Full workflow execution
│   ├── Step re-execution
│   ├── State transitions
│   └── API endpoints
│
└── E2E Tests
    ├── Upload workflow
    ├── Execute workflow
    ├── Modify & re-run step
    └── Download results

FRONTEND TESTS
├── Unit Tests
│   ├── Components render correctly
│   ├── Event handlers work
│   └── State updates propagate
│
├── Integration Tests
│   ├── API calls successful
│   ├── WebSocket updates flow
│   └── Data displayed correctly
│
└── E2E Tests (Selenium/Playwright)
    ├── User workflow
    ├── Error scenario
    └── Data inspection
```

---

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ PRODUCTION DEPLOYMENT (AWS Example)                           │
└────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────┐
        │  CloudFront (CDN)               │
        │  • Frontend static assets       │
        │  • Compress + cache             │
        └─────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
    ┌───────────┐            ┌─────────────┐
    │   S3      │            │  ALB        │
    │ (Frontend)│            │(Load Bal)   │
    └───────────┘            └─────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
                ┌────────┐    ┌────────┐    ┌────────┐
                │ ECS    │    │ ECS    │    │ ECS    │
                │Service │    │Service │    │Service │
                │(3 pods)│    │(3 pods)│    │(3 pods)│
                └───┬────┘    └───┬────┘    └───┬────┘
                    │            │            │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
                ┌────────────────┐    ┌──────────────┐
                │ RDS PostgreSQL │    │ElastiCache   │
                │ (Primary DB)   │    │(Redis Cache) │
                └────────────────┘    └──────────────┘
                    │
                    ▼
                ┌────────────────┐
                │ S3 (Backups)   │
                │ CloudWatch     │
                └────────────────┘

Scaling:
• Horizontal: Add more ECS tasks (auto-scaling group)
• Vertical: Increase instance type
• Cache: ElastiCache distributes dataframe cache
• DB: RDS read replicas for reporting
```

---

## Summary

This architecture provides:

1. **Modularity:** Each step is independent, composable
2. **Observability:** Real-time status + detailed error messages
3. **Flexibility:** Steps can be modified and re-run without restart
4. **Scalability:** Stateless backend, can add workers horizontally
5. **Debugging:** Full data inspection at each step
6. **Transparency:** Users understand exactly where/why failures occur

Ready to develop! 🚀
