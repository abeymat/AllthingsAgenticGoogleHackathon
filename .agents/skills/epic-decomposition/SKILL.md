---
name: epic-decomposition
description: Agile product management rules for decomposing Jira Epics into isolated User Stories, Apex tasks, and LWC UI bundles.
---

# Jira Epic Decomposition Skill

## 1. Task Isolation & Granularity
- Decompose Epics into distinct, isolated User Stories.
- Separate frontend LWC components from backend Apex controllers and unit test classes.
- Explicitly set `component_type` to one of: `ApexClass`, `ApexTrigger`, `LWC`, `ApexTest`, or `Config`.

## 2. Technical Specification Blueprinting
- For each decomposed task, provide target filenames (`StudentApplicationController.cls`, `studentApplicationForm.js`).
- Include detailed technical instructions in `description` so the Developer Agent can generate production-grade code without missing requirements.
