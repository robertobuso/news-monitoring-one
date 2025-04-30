"""
Email service for sending report emails.

This service uses SendGrid to deliver report emails to users with PDF attachments.
"""
import base64
import logging
import os
from datetime import date
from typing import Dict, Any, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, 
    FileType, Disposition, ContentId
)

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails.
    """

    def __init__(self):
        """Initialize email service."""
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.from_email = os.environ.get("SENDGRID_FROM_EMAIL", "reports@newsmonitor.app")
        self.from_name = os.environ.get("SENDGRID_FROM_NAME", "NewsMonitor")
        self.base_url = settings.BASE_URL

    async def send_report_email(
        self,
        user_email: str,
        client_name: str,
        report_date: date,
        pdf_path: str,
        report_id: str
    ) -> Dict[str, Any]:
        """
        Send a report email with PDF attachment.
        
        Args:
            user_email: Recipient email address
            client_name: Client name
            report_date: Report date
            pdf_path: Path to PDF file
            report_id: Report ID
            
        Returns:
            Dict: Email sending result
        """
        if not self.api_key:
            logger.error("SendGrid API key not configured")
            return {"success": False, "error": "Email service not configured"}

        try:
            # Create SendGrid client
            sg = SendGridAPIClient(api_key=self.api_key)

            # Create email content
            subject = f"NewsMonitor Report for {client_name} - {report_date.strftime('%Y-%m-%d')}"

            # Load email template
            template_path = "app/templates/email/report_email.html"
            if os.path.exists(template_path):
                with open(template_path, "r") as f:
                    template = f.read()
            else:
                # Fallback to basic template
                template = """
                <html>
                <body>
                    <h1>NewsMonitor Daily Report</h1>
                    <p>Hello,</p>
                    <p>Your daily news report for {{client_name}} is ready.</p>
                    <p>Date: {{report_date}}</p>
                    <p>You can view the report online at: <a href="{{view_url}}">View Report</a></p>
                    <p>The report is also attached to this email as a PDF.</p>
                    <p>Thank you for using NewsMonitor!</p>
                </body>
                </html>
                """

            # Replace placeholders
            html_content = template.replace("{{client_name}}", client_name)
            html_content = html_content.replace("{{report_date}}", report_date.strftime("%B %d, %Y"))
            html_content = html_content.replace("{{view_url}}", f"{self.base_url}/reports/{report_id}")

            # Create message
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=user_email,
                subject=subject,
                html_content=html_content
            )

            # Attach PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    file_content = f.read()
                    file_name = f"{client_name}_Report_{report_date.strftime('%Y-%m-%d')}.pdf"
                    
                    encoded_content = base64.b64encode(file_content).decode()
                    
                    attachment = Attachment()
                    attachment.file_content = FileContent(encoded_content)
                    attachment.file_name = FileName(file_name)
                    attachment.file_type = FileType("application/pdf")
                    attachment.disposition = Disposition("attachment")
                    attachment.content_id = ContentId("Report PDF")
                    
                    message.attachment = attachment
            else:
                logger.warning(f"PDF file not found: {pdf_path}")

            # Send email
            response = sg.send(message)
            
            logger.info(f"Email sent to {user_email}, status code: {response.status_code}")
            
            return {
                "success": True, 
                "status_code": response.status_code,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "error": str(e)}