# All Things Agentic Hackathon: Project Master Strategy & Roadmap

## 1. Project Overview & Hackathon Alignment

* **Project Name**: Multi-Agent Enterprise Salesforce SDLC Orchestrator
* **Target Track**: **The Fortified Enterprise Fleet** ($20,000 Prize Category) + **Grand Prize** ($50,000)
* **Persona**: University Product Manager (PM) managing an Enterprise Salesforce Ecosystem (Website + Salesforce Org + Jira).
* **Core Value Proposition**: An autonomous, multi-agent AI pipeline that listens to Jira Epics, decomposes them into stories/tasks, writes Apex/LWC code, executes unit tests, manages Git branches, and deploys across Salesforce orgs with strict Human-in-the-Loop (HITL) governance and self-correcting error handling.

---

## 2. Google Product & Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Core AI Model** | **Gemini 3.5 Pro & Flash** (via Vertex AI) | Code generation, schema decomposition, and automated code review reasoning chains. |
| **Agent Framework** | **Google ADK** (Agent Development Kit) | Multi-agent orchestration, tool definitions, and structured reasoning. |
| **Compute & Microservices** | **Google Cloud Run** | Serverless containerized Python backend for listening to Jira webhooks and running CLI tools. |
| **Event Messaging** | **Google Cloud Pub/Sub** | Asynchronous event mesh for agent task delegation and webhook event queuing. |
| **State & Memory Bank** | **Google Firestore** | Persistent cross-session state store (Memory Bank) holding pipeline status during human approval waits. |
| **Security & Guardrails** | **Gemma 2** (via Vertex AI) + **Model Armor** | Static code analysis scanning Apex/LWC for security vulnerabilities (SOQL injection, PII exposure). |
| **Observability** | **Vertex AI Telemetry / Cloud Logging** | OpenTelemetry-compliant audit logs visualizing agent reasoning chains. |

---

## 3. Official Hackathon Rules & Scoring Criteria (6.0 Max Score)

### Stage Two: Weighted Scoring Pillars
1. **Innovation & Operational Utility (40%)**:
   - Autonomous background execution (not a simple conversational chatbot).
   - Solves real friction for an enterprise persona.
   - Intelligent delegation across a network of specialized sub-agents.
2. **Architectural Discipline & Tech Stack (30%)**:
   - **Failure-Tolerant Inter-Agent Routing**: Self-correcting retry loops when tests fail.
   - Modularized design, tool isolation, and secure scoping.
   - Persistent Memory Bank via Firestore.
3. **Demo & Production Readiness (30%)**:
   - Unedited live execution proof in a ≤ 4 minute video.
   - Visual proof of backend running on Google Cloud (Cloud Run Console & Vertex AI logs).
   - Clear setup instructions in GitHub `README.md`.

### Stage Three: Bonus Point Additions (+1.0 Max)
- **Google AI Model Integrations (+0.6 max / +0.2 per model)**: Using Gemini 3.5 Pro + Gemma 2 (security scanner).
- **Public Article / Blog (+0.2 pts)**: Dev.to article detailing the multi-agent architecture.
- **Social Media Post (+0.2 pts)**: LinkedIn/X post with `#AllThingsAgenticHackathon`.

---

## 4. Multi-Agent Fleet Architecture

```
                       ┌─────────────────────────┐
                       │ Jira Epic Created/Tagged│
                       └────────────┬────────────┘
                                    │ Webhook
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. PM Decomposer Agent (Google ADK + Gemini 3.5 Pro)                   │
│    - Parses Epic into User Stories, LWC components, Apex Classes, Tests │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
                        [ Human Approval Email #1 ]
                        (Breakdown & Scope Sign-off)
                                    │ (Approved)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. Salesforce Developer Agent (Python + SF CLI + Git)                   │
│    - Spins up Scratch Org (`sf org create scratch`)                     │
│    - Generates Apex & LWC code                                          │
│    - Executes Unit Tests (`sf apex run test`)                           │
│    - Self-Correction Loop (retries up to 3x if tests fail)              │
│    - Commits & Pushes to GitHub Feature Branch                          │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. Security & Governance Agent (Gemma 2 / Model Armor)                  │
│    - Static analysis for SOQL injection, hardcoded credentials & PII    │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
                        [ Human Approval Email #2 ]
                        (Code Diff & Visual Preview Sign-off)
                                    │ (Approved)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. Enterprise Release Agent (SF CLI Deploy)                             │
│    - Deploys to QA/Testing Sandbox Org (`sf project deploy start`)      │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
                        [ Human Approval Email #3 ]
                        (Production Release Sign-off)
                                    │ (Approved)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. Production Deployment                                                │
│    - Deploys metadata to Production Org with full test verification     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4.1 Iterative Human Feedback & Re-Prompting Loop (Conversational Approvals)

To support real-world collaboration and score maximum points under **The Collaborative Partner** criteria, all human approval checkpoints support an **Iterative Feedback Loop** rather than just a binary Approve/Reject choice.

```
[ Agent Completes Stage Work ]
              │
              ▼
   [ Approval Request Sent ]
   (Email & Dashboard Web Portal)
              │
              ├──► Option A: [ Approve ] ───────────► Proceed to Next Stage
              │
              ├──► Option B: [ Request Changes ] ──► Feed Human Feedback back to Agent
              │                                      (Agent Mutates Code/Stories & Re-submits)
              │
              └──► Option C: [ Reject & Cancel ] ──► Cancel Workflow & Log Reason
```

### Stage-by-Stage Feedback Handling:

1. **Stage 1 (PM Decomposer Agent)**:
   - *User Feedback*: "Add a story for validation of international phone numbers and rename LWC component to StudentRegistrationForm."
   - *Agent Action*: `PM_Decomposer_Agent` ingests feedback + previous breakdown, mutates Jira tasks, and generates **Approval Request #1 (v2)**.

2. **Stage 2 (Salesforce Developer Agent)**:
   - *User Feedback*: "Change the LWC form layout to a 2-column grid and add duplicate email check in the Apex trigger."
   - *Agent Action*: `Salesforce_Developer_Agent` modifies code, re-runs `sf apex run test`, updates Git branch, and resubmits **Approval Request #2 (v2)**.

3. **Stage 3 (Enterprise Release Agent)**:
   - *User Feedback*: "Bulk testing in QA Sandbox failed for 200 records."
   - *Agent Action*: Re-triggers `Salesforce_Developer_Agent` to fix Apex bulkification, re-run tests, push commit, and re-request staging deployment.

---

## 5. Phase-by-Phase Development Roadmap

### Phase 1: Environment & Secrets Setup
- [x] Create Google Cloud Project & enable APIs (`run`, `aiplatform`, `firestore`, `pubsub`).
- [x] Claim $150 Google Cloud Hackathon Credits on Devpost.
- [x] Set up Free Jira Cloud Instance (`abeycm.atlassian.net` / Project Key: `SCRUM`).
- [x] Generate Jira API Token & configure credentials in `.env`.
- [x] Set up Salesforce Developer/Scratch Orgs & Connected App (JWT authentication key).

### Phase 2: Python Backend & Google ADK Agent Fleet
- [x] Initialize Python backend (`fastapi` / `google-adk` / `google-genai`).
- [x] Implement `PM_Decomposer_Agent` with Pydantic JSON schemas.
- [x] Implement `Salesforce_Dev_Agent` with `subprocess` wrappers for `sf` CLI (`sf apex run test`, `git`).
- [x] Implement self-correcting retry loop for failed Apex test compilation.
- [x] Implement `Security_Governance_Agent` (Model Armor / Gemma 2 static analysis).

### Phase 3: Firestore Memory Bank & HITL Approval Links
- [x] Build Firestore pipeline state transitions (`PENDING_APPROVAL_1`, `DEVELOPING`, `PENDING_APPROVAL_2`, etc.).
- [x] Implement tokenized magic approval endpoints (`/api/v1/approve/token` and `/action`).
- [x] Render interactive HTML Human Approval Portal supporting Approve, Request Changes, and Reject.

### Phase 4: Cloud Run Containerization & Telemetry
- [x] Write `Dockerfile` containerizing Python 3.11 + Node.js + Salesforce CLI (`sf`).
- [x] Create automated `deploy_cloud_run.sh` script for Google Cloud Run deployment.
- [x] Connect OpenTelemetry-compliant structured logging (`telemetry.py`) for Cloud Logging.

### Phase 5: Web UI Dashboard & Submission Assets
- [x] Build modern single-page dashboard (`frontend/index.html`) displaying live agent reasoning chains & active pipeline states.
- [x] Draft public GitHub `README.md` with step-by-step spin-up instructions & architecture diagram.
- [ ] Record ≤ 4 minute unedited demo video showing live execution + Google Cloud Run console.
- [ ] Publish Dev.to blog post & Social post with `#AllThingsAgenticHackathon`.
