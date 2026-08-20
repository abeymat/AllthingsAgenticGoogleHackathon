# Implementation Plan: Multi-Agent Enterprise Salesforce SDLC Orchestrator

This document outlines the design, architecture, and step-by-step roadmap for building the **Multi-Agent Enterprise Salesforce SDLC Orchestrator** for the **All Things Agentic Hackathon**.

## User Review Required

> [!IMPORTANT]
> **Track Target**: Submitting to **The Fortified Enterprise Fleet** category ($20,000 Prize) with eligibility for the **Grand Prize ($50,000)** and **Best Architectural Design ($5,000)**.
> 
> **Core Requirement Check**:
> 1. Uses Gemini 3.5 Pro / Flash via Vertex AI.
> 2. Uses Google ADK (Agent Development Kit).
> 3. Deployed on Google Cloud Run + Firestore + Pub/Sub.
> 4. Multi-agent network with self-correcting error loops & 3-stage Human-in-the-Loop approval gates.
> 5. **Iterative Human Feedback Loop**: Approvers can request modifications at any stage (PM breakdown, Dev code, or QA release), triggering the agent to mutate code/stories and resubmit.

## Open Questions

> [!NOTE]
> None at this stage. All requirements, hackathon rules, timelines, and architectural decisions have been verified.

## Proposed Changes

We are initializing the project repository structure under [`/Users/abeymathews/AntiGravityProjects/AllthingsAgenticGoogleHackathon`](file:///Users/abeymathews/AntiGravityProjects/AllthingsAgenticGoogleHackathon).

### Project Documentation & Setup

#### [NEW] [.env.example](file:///Users/abeymathews/AntiGravityProjects/AllthingsAgenticGoogleHackathon/.env.example)
Pre-configured environment configuration template containing Jira domain (`abeycm.atlassian.net`) and project key (`SCRUM`).

#### [NEW] [HACKATHON_STRATEGY.md](file:///Users/abeymathews/AntiGravityProjects/AllthingsAgenticGoogleHackathon/HACKATHON_STRATEGY.md)
Comprehensive master strategy document detailing rules, criteria, tech stack, multi-agent fleet architecture, and phase-by-phase implementation plan.

---

### Backend Components (To be initialized in Phase 1)

#### [NEW] `backend/app/main.py`
FastAPI server hosting Jira webhook endpoints and human approval link handlers.

#### [NEW] `backend/app/agents/`
* `decomposer_agent.py`: Google ADK agent breaking Jira Epics into User Stories & Apex/LWC task specifications.
* `developer_agent.py`: Google ADK agent generating Apex/LWC code, running local Salesforce CLI tests (`sf apex run test`), and managing Git branches.
* `security_agent.py`: Static analysis & Model Armor guardrail scanning code with Gemma 2.
* `devops_agent.py`: Salesforce DX deployment agent managing Scratch Orgs and deploying metadata (`sf project deploy start`) to QA & Production orgs.

### Frontend & Submission Assets

#### [NEW] [frontend/index.html](file:///Users/abeymathews/AntiGravityProjects/AllthingsAgenticGoogleHackathon/frontend/index.html)
Glassmorphic single-page web operations dashboard visualizing real-time agent reasoning chains, active Jira Epics, and human approval portals.

#### [NEW] [README.md](file:///Users/abeymathews/AntiGravityProjects/AllthingsAgenticGoogleHackathon/README.md)
Comprehensive, reproducible setup guide for hackathon judges containing system architecture Mermaid diagrams, API specs, and Cloud Run deployment guides.

---

## Verification Plan

### Automated Verification
- Unit tests for agent JSON parsing and tool wrappers.
- Execution of `sf apex run test` inside the container to verify Apex test runner integrations.
- Local API testing of Jira webhook triggers and Firestore state transitions.

### Manual Verification & Submission Proof
- **Live Demo Video (≤ 4 mins)**: Unedited recording showing Jira Epic creation → Multi-agent execution → Terminal logs → Salesforce Org update → Google Cloud Run Console.
- **GitHub README**: Clear step-by-step setup guide for judges.
- **Dev.to Article & Social Post**: Blog post and post on LinkedIn/X with `#AllThingsAgenticHackathon` for +0.4 bonus points.
