# NexusDev AI — Complete Functional Testing Guide & Documentation

This document outlines the step-by-step procedure for verifying **NexusDev AI**, an autonomous **5-agent software engineering fleet** built on **Google ADK 2.0**, **Gemini 3.6 Flash / 3.5 Pro**, **Model Context Protocol (MCP)**, **Agent Skills**, **OpenTelemetry Tracing**, **Cloud Pub/Sub**, **Cloud Scheduler Cron**, **LLM-as-a-Judge Evaluation Benchmarks**, **Email Approval Notifications**, and **ADK Fleet Optimization**.

---

## 🏗️ 5-Agent Fleet & System Overview

NexusDev AI features 5 specialized autonomous agents:
1. **PM Decomposer Agent** (`decomposer_agent.py`): Root agent using Gemini 3.6 Flash (`temperature=0.2`) & `response_schema=DecompositionResult` to decompose Jira Epics.
2. **Salesforce Developer Agent** (`developer_agent.py`): Uses Gemini 3.5 Pro (`temperature=0.1`) with an autonomous **Self-Correction Test Loop** to generate Apex and LWC code.
3. **Security & Governance Agent** (`security_agent.py`): Uses Gemma 2 / Model Armor rules (`temperature=0.0`) to audit code for SOQL injection and hardcoded credentials.
4. **GitOps Agent** (`git_agent.py`): Formulates conventional commit messages (`temperature=0.1`), commits to Git, generates AI PR summaries, and pushes feature branches to GitHub.
5. **Enterprise Release Agent** (`release_agent.py`): Validates pre-flight deployment safety (`temperature=0.2`), deploys metadata via SF CLI to QA Sandbox & Production Orgs, and generates Release Notes.

---

## 🧪 Automated End-to-End Test Execution

You can run the complete 5-agent functional test suite using the standalone Python runner:

```bash
venv/bin/python3 test_e2e_sdlc_pipeline.py
```

### Expected Output Log:
```text
==================================================
  NexusDev AI - Complete E2E SDLC Functional Test 
==================================================
[1/5] Health Check Passed: 200 -> Status: healthy (MCP: True, AFC: True, Telemetry: True, PubSub: True, Cron: True, Eval: True, Email: True, Optimize: True)
      ✓ ADK 2.0 Automatic Function Calling (AFC) Enabled across 5 Agents.
      ✓ MCP Protocol Active: Registered 8 tools across Jira, Salesforce, and Git servers.
      ✓ OpenTelemetry Tracing Active: Multi-agent Cloud Trace spans initialized.
      ✓ Google Cloud Pub/Sub & Cloud Scheduler Cron Triggers Active.
      ✓ Email Approval Notifications Active -> Decomposer: decomposerEmail@nexusdev.ai | Developer: developerEmail@nexusdev.ai | Release: releaseEmail@nexusdev.ai
      ✓ Google Cloud Pub/Sub Push Message Ingested: Status: PROCESSED
      ✓ Google Cloud Scheduler Cron Triggered (0 0 * * *): Status: COMPLETED
      ✓ LLM-as-a-Judge Eval Engine Benchmark Score: 60.4/100 (Recovery Rate: 100.0%)
      ✓ ADK Fleet Optimizer Engine Active: Token Savings: 35% | Framework: Google ADK 2.0 / GenAI SDK

[2/5] Triggering PM Decomposer Agent for SCRUM-1...
      Stage 1 Approval Token Generated: tok-a3017470544a4a19ba73c4a6ca34aaee

[3/5] Approving Stage 1 (Triggers Developer Agent & GitOps Agent)...
      ✓ Stage 1 Approved!
      ✓ GitOps Agent (ADK Agent #4): Committed changes to branch 'feature/SCRUM-1-student-app' (0c18d04)
      ✓ AI Commit Message: "feat(agent): update Student Application Form & Apex Controller"
      ✓ Stage 2 Approval Token Generated: tok-64a22ea4dff0462a9f0e9a4a877ce73c

[4/5] Approving Stage 2 (Triggers Enterprise Release Agent -> QA Testing Org)...
      ✓ Stage 2 Approved!
      ✓ Enterprise Release Agent (ADK Agent #5): Deployed metadata to QA Testing Org (abeycm@curious-fox-3xbrbu.com)
      ✓ AI Release Notes: # Enterprise Release Notes ...
      ✓ Stage 3 Approval Token Generated: tok-d54d65355b1e4235917ec156c811ee27

[5/5] Approving Stage 3 (Triggers Enterprise Release Agent -> Live Production Release)...
      ✓ Stage 3 Approved!
      ✓ Enterprise Release Agent (ADK Agent #5): Executed live release to Production Org (epic.8fb9d0d7217c@orgfarm.salesforce.com)
      ✓ Production Release Status: RELEASED_TO_PRODUCTION

[Telemetry Log] OpenTelemetry Engine Captured 16 Trace Spans Across 5 Agents.

==================================================
  🎉 ALL 5 ADK AGENTS PASSED PIPELINE SUCCESSFULLY!
==================================================
```

---

## 🔗 Live Endpoint Verification Table

| Endpoint | Method | Expected Output |
| :--- | :--- | :--- |
| `http://localhost:8000/` | `GET` | HTML Web Control Center GUI |
| `http://localhost:8000/health` | `GET` | `{"status": "healthy", "mcp_enabled": true, "adk_afc_enabled": true, "telemetry_enabled": true, "pubsub_enabled": true, "cron_enabled": true, "eval_engine_enabled": true, "email_notifications_enabled": true, "adk_optimizer_enabled": true}` |
| `http://localhost:8000/api/v1/mcp/tools` | `GET` | List of 8 registered MCP tools across Jira, Salesforce, and Git servers |
| `http://localhost:8000/api/v1/telemetry/traces` | `GET` | Array of OpenTelemetry-compliant trace spans (`trace_id`, `span_id`, latency) |
| `http://localhost:8000/api/v1/eval/benchmark` | `GET` | LLM-as-a-Judge Evaluation Benchmark suite scores (`overall_quality_score`, recovery rate) |
| `http://localhost:8000/api/v1/adk/optimize` | `GET` | Google ADK 2.0 optimization profile (temperature profiles, AFC token savings, fallback routing) |
| `http://localhost:8000/api/v1/pubsub/events` | `POST` | `{"status": "PROCESSED", "pubsub_event": "INGESTED"}` |
| `http://localhost:8000/api/v1/cron/nightly-audit` | `POST` | `{"cron_status": "COMPLETED", "schedule": "0 0 * * *"}` |
