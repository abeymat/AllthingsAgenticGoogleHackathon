import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_filename = "NexusDev_AI_Architecture_Flow_Diagram.pdf"

doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
)

styles = getSampleStyleSheet()
normal = styles['Normal']

title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=20,
    leading=24,
    textColor=colors.HexColor('#0284c7'),
    spaceAfter=6
)

subtitle_style = ParagraphStyle(
    'SubTitleStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#475569'),
    spaceAfter=15
)

section_style = ParagraphStyle(
    'SectionStyle',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=colors.HexColor('#0f172a'),
    spaceBefore=12,
    spaceAfter=8
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#334155')
)

code_style = ParagraphStyle(
    'CodeStyle',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#0f172a'),
    backColor=colors.HexColor('#f1f5f9'),
    borderColor=colors.HexColor('#cbd5e1'),
    borderWidth=1,
    borderPadding=8,
    spaceBefore=6,
    spaceAfter=10
)

story = []

# Title & Subtitle
story.append(Paragraph("NexusDev AI — System Architecture & Process Flow Blueprint", title_style))
story.append(Paragraph("Google ADK 2.0 &bull; Gemini 3.6 Flash / 3.5 Pro &bull; Google Cloud Run &bull; Model Context Protocol", subtitle_style))
story.append(Spacer(1, 10))

# Section 1: Process Flow Diagram
story.append(Paragraph("🔄 1. End-to-End Step-by-Step SDLC Process Flow", section_style))

flow_text = """
<b>[Trigger Input]</b> Jira Cloud Webhook / Google Cloud Pub-Sub / Cloud Scheduler Cron (0 0 * * *)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow;<br/>
<b>[Stage 1: Epic Decomposition]</b> Node 1: PM Decomposer Agent (Gemini 3.6 Flash / temp=0.2)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow; <i>Dispatches Real Stage 1 Email Alert to abeycm@gmail.com</i><br/>
<b>[Human Gate #1]</b> Approver Clicks Magic Link & Sign-Off<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow;<br/>
<b>[Stage 2: Development & Security]</b> Node 2: Developer Agent (Gemini 3.5 Pro) with SF CLI Self-Correction Retries<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow;<br/>
<b>[Security Governance Audit]</b> Node 3: Security Governance Agent (Gemma 2 / Risk Score Audit)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow;<br/>
<b>[GitOps & Version Control]</b> Node 4: GitOps Agent (Gemini 3.6 Flash) Commits & Pushes Branch<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow; <i>Dispatches Real Stage 2 Email Alert to abeycm@gmail.com</i><br/>
<b>[Human Gate #2]</b> Approver Clicks Magic Link & Sign-Off<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow;<br/>
<b>[Stage 3: QA Sandbox Deployment]</b> Node 5: Enterprise Release Agent Deploys to QA Sandbox Org<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow; <i>Dispatches Real Stage 3 Email Alert to abeycm@gmail.com</i><br/>
<b>[Human Gate #3]</b> Approver Clicks Magic Link & Sign-Off<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&Downarrow;<br/>
<b>[Live Production Release]</b> Promotes Metadata to Live Production Org (epic.8fb9d0d7217c@orgfarm.salesforce.com)
"""
story.append(Paragraph(flow_text, code_style))
story.append(Spacer(1, 10))

# Section 2: Technical Architecture Matrix
story.append(Paragraph("🏗️ 2. 6-Layer Enterprise Technical Architecture Matrix", section_style))

data = [
    ["Subsystem Layer", "Google Technology / Framework", "Enterprise Function"],
    ["Layer 1: Ingestion", "Cloud Pub/Sub, Cloud Scheduler, FastAPI", "Real-time Webhook push ingestion, Pub/Sub events, and recurring nightly cron security audits (0 0 * * *)."],
    ["Layer 2: 5 ADK Agents", "Google ADK 2.0, Gemini 3.6 Flash / 3.5 Pro, Gemma 2", "Autonomous code generation with SF CLI self-correction, static security auditing, GitOps, and release notes."],
    ["Layer 3: Tools & Skills", "Model Context Protocol (MCP), Agent Skills", "Standardized JSON-RPC tool binding across Jira, Salesforce DX, and Git servers + domain rule manuals."],
    ["Layer 4: Memory Bank", "Google Cloud Firestore", "Cross-session state persistence managing pipeline state across asynchronous Human-in-the-Loop approval gates."],
    ["Layer 5: HITL Email", "Email Notification Service (smtplib)", "Dispatches interactive HTML emails with Magic Approval Links to abeycm@gmail.com."],
    ["Layer 6: Observability", "OpenTelemetry, Eval Engine, ADK Optimizer", "Structured OpenTelemetry trace spans, quantitative LLM quality benchmark scores, and ~35% AFC token savings."]
]

t = Table(data, colWidths=[110, 150, 280])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 9),
    ('BOTTOMPADDING', (0,0), (-1,0), 8),
    ('TOPPADDING', (0,0), (-1,0), 8),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,1), (-1,-1), 8),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

story.append(t)

doc.build(story)
print(f"Generated PDF successfully: {pdf_filename}")
