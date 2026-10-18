# Project Scaffold + X4-ARX369 Ω Beast Arsenal

This repository remains the Node.js/Express application scaffold and now contains a **dependency-light X4 runtime MVP** under `x4/`.

## X4 runtime

The current MVP provides:

- immutable-style Constitution and Policy Wall rejection
- task classification (`TaskDNA`)
- cost/quality/reliability-aware provider selection
- Ollama + Groq adapters
- AST-based Python syntax verification for code tasks
- append-only JSONL audit ledger
- HTTP `/health` and `/v1/chat/completions` endpoints

### Run locally

```bash
python -m x4.serve --host 127.0.0.1 --port 8080
```

Test a health check:

```bash
curl http://127.0.0.1:8080/health
```

Send a request:

```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a Python function that adds two numbers","task_type":"code_generation","estimated_budget":0.01}'
```

Ollama is selected only when healthy. Groq requires `GROQ_API_KEY`.

<!-- X4-APEX-DIAGRAM-START:project-scaffold -->

```mermaid
flowchart TD
    CLIENT[Local Client] --> HEALTH[GET /health]
    CLIENT --> CHAT[POST /v1/chat/completions]
    CHAT --> CLASSIFY[TaskDNA Classification]
    CLASSIFY --> WALL[Constitution and Policy Wall]
    WALL -->|reject| DENY[Policy Rejection]
    WALL -->|allow| SELECT[Provider Selection]
    SELECT --> OLLAMA[Ollama Adapter]
    SELECT --> GROQ[Groq Adapter]
    OLLAMA --> RESULT[Candidate Response]
    GROQ --> RESULT
    RESULT --> AST[Python AST Syntax Verification for Code Tasks]
    AST --> LEDGER[Append-only JSONL Audit Ledger]
    LEDGER --> RESPONSE[API Response]
    NOTE[Provider tests, security scan, deploy and rollback evidence still required] -. promotion gate .-> RESPONSE
```

<!-- X4-APEX-DIAGRAM-END:project-scaffold -->

## Validation

X4 CI runs compile, Ruff lint, and pytest checks from `.github/workflows/x4-arsenal.yml`.

The MVP is an **implementation foundation**, not a claim of production validation. Production promotion still requires provider integration tests, security scanning, benchmark evidence, deployment verification, and rollback testing.

## Existing ARIEX service

The repository also retains the existing AriexCore model-fleet service under `src/arx/ai/`.

## Azure deployment

The existing Azure Developer CLI configuration remains available for the Node application:

```bash
azd up
```

MIT License.

## APEX Architecture Map

> Status: architecture documentation; implementation and deployment claims require independent verification.

```mermaid
flowchart TB
  Developer[Developer] --> Verify[scripts/verify_x4.sh]
  Verify --> Detect{Project components}
  Detect --> Node[Node / TypeScript checks]
  Detect --> Python[Python checks]
  Node --> NodeInstall[Dependency install]
  NodeInstall --> NodeLint[Lint + typecheck]
  NodeLint --> NodeTest[Node tests]
  Python --> PyInstall[Install project]
  PyInstall --> PyLint[Lint / format check]
  PyLint --> PyTest[pytest]
  NodeTest --> Merge{All required jobs pass?}
  PyTest --> Merge
  Merge -->|no| Fail[Non-zero exit + logs]
  Merge -->|yes| Ready[Verified scaffold baseline]
  Ready --> CI[Hosted CI]
```
**Evidence note:** The dual-stack flow is a target map. Verify the scripts and workflow job graph before claiming every step exists or passes.

