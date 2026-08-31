---
name: salesforce-governance
description: Enterprise Salesforce Apex and LWC engineering rules, security standards, SOQL bulkification, and unit test assertions.
---

# Salesforce Governance & Quality Engineering Skill

## 1. Apex Class Security & Architecture
- **Sharing Mode:** ALWAYS declare `public with sharing class ClassName` to enforce Salesforce record-level security.
- **SOQL Bulkification:** NEVER execute SOQL queries or DML statements inside `for` loops. Always query outside and process in collections (`List`, `Map`, `Set`).
- **Standard Object Schema Compatibility:** For Developer Edition org deployment compatibility, use standard Salesforce objects (`Contact`, `Lead`, `Account`, `Opportunity`) and standard fields (`FirstName`, `LastName`, `Email`, `Phone`, `Company`). Avoid assuming custom objects exist unless explicitly specified.

## 2. Apex Unit Testing Requirements
- Annotate test classes with `@IsTest`.
- Include `Test.startTest()` and `Test.stopTest()` around governor limit resets.
- Use explicit assertions (`System.assertNotEquals(null, recordId)` or `System.assertEquals(...)`) to verify business logic.

## 3. Lightning Web Component (LWC) Standards
- Ensure LWC JS imports `LightningElement`, `api`, `wire`, or `track` cleanly.
- Export bundle metadata (`js-meta.xml`) with `<isExposed>true</isExposed>` and target support for `lightning__AppPage`, `lightning__RecordPage`, and `lightning__HomePage`.
