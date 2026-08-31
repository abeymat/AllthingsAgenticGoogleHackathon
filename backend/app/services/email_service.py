import smtplib
import logging
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.services.telemetry import telemetry

logger = logging.getLogger("email_service")

class EmailNotificationService:
    """
    Email Notification Service for Human-in-the-Loop (HITL) Approvals.
    Formats HTML emails with Magic Approval Links and dispatches notifications
    to stage-specific approver recipients (decomposerEmail, developerEmail, releaseEmail).
    """

    def send_approval_notification(
        self,
        stage_name: str,
        approval_token: str,
        recipient_email: str,
        summary_title: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format and send an interactive HTML approval email containing a direct Magic Approval Link.
        """
        magic_link = f"{settings.approval_base_url}/api/v1/approve/view?token={approval_token}"
        subject = f"🛡️ NexusDev AI Approval Needed: [{stage_name}] {summary_title}"

        # Build responsive HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f19; color: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #161e31; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px; }}
                .header {{ border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 20px; }}
                .badge {{ background: #38bdf8; color: #0b0f19; font-weight: bold; padding: 4px 10px; border-radius: 12px; font-size: 12px; }}
                .content {{ font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-bottom: 25px; }}
                .btn {{ display: inline-block; background: linear-gradient(135deg, #38bdf8, #0284c7); color: #0b0f19; text-decoration: none; font-weight: bold; padding: 14px 28px; border-radius: 8px; font-size: 15px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #64748b; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="badge">{stage_name}</span>
                    <h2 style="color: #ffffff; margin-top: 10px;">Human Sign-Off Required</h2>
                </div>
                <div class="content">
                    <p>Hello Approver (<code>{recipient_email}</code>),</p>
                    <p>NexusDev AI 5-Agent Fleet has completed automated task processing for <strong>{summary_title}</strong> and requires your human sign-off to proceed to the next SDLC stage.</p>
                    <p><strong>Approval Token:</strong> <code>{approval_token}</code></p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{magic_link}" class="btn" target="_blank">Review & Approve in Portal</a>
                </div>
                <div class="footer">
                    NexusDev AI &bull; Autonomous Enterprise SDLC Fleet &bull; Powered by Google ADK 2.0 & Gemini
                </div>
            </div>
        </body>
        </html>
        """

        # Log OpenTelemetry trace span
        telemetry.log_agent_event(
            agent_name="Email Notification Service",
            event_type="EMAIL_NOTIFICATION_SENT",
            pipeline_id=f"pipe-{approval_token[:8]}",
            summary=f"Sent approval notification email for [{stage_name}] to {recipient_email}",
            details={"recipient_email": recipient_email, "stage": stage_name, "token": approval_token, "magic_link": magic_link}
        )

        # SMTP dispatch when credentials configured
        sent_status = "FALLBACK_LOGGED"
        if settings.smtp_username and settings.smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = settings.smtp_username
                msg["To"] = recipient_email
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                    server.starttls()
                    server.login(settings.smtp_username, settings.smtp_password)
                    server.sendmail(settings.smtp_username, recipient_email, msg.as_string())
                sent_status = "SENT_VIA_SMTP"
                logger.info(f"Successfully sent approval email via SMTP to {recipient_email}")
            except Exception as e:
                logger.error(f"SMTP email dispatch error: {e}")
        else:
            logger.info(f"[Email Notification Logged] Recipient: {recipient_email} | Subject: '{subject}' | Magic Link: {magic_link}")

        return {
            "status": "DISPATCHED",
            "dispatch_method": sent_status,
            "recipient_email": recipient_email,
            "stage_name": stage_name,
            "magic_link": magic_link
        }

email_service = EmailNotificationService()
