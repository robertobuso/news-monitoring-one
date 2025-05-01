"""
PDF service for generating report PDFs.

This service uses ReportLab to create PDF reports with client information,
executive summaries, and relevant articles.
"""
import logging
import os
from datetime import date
from io import BytesIO
from typing import Dict, List, Optional, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, ListFlowable, ListItem
)

from app.models.client_profile import ClientProfile

logger = logging.getLogger(__name__)


class PDFService:
    """
    Service for generating PDF reports.
    """

    def __init__(self):
        """Initialize PDF service."""
        self.styles = getSampleStyleSheet()
        
        # Create custom styles
        self.styles.add(
            ParagraphStyle(
                name='ArticleTitle',
                parent=self.styles['Heading3'],
                fontSize=12,
                leading=14,
                textColor=colors.darkblue
            )
        )
        
        self.styles.add(
            ParagraphStyle(
                name='ArticleSource',
                parent=self.styles['Italic'],
                fontSize=9,
                textColor=colors.gray
            )
        )
        
        self.styles.add(
            ParagraphStyle(
                name='ArticleRelevance',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.darkgreen
            )
        )
        
        self.styles.add(
            ParagraphStyle(
                name='ArticleURL',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.blue,
                underline=True
            )
        )

    async def create_pdf_report(
        self,
        client_profile: ClientProfile,
        articles: List[Dict[str, Any]],
        executive_summary: str,
        report_date: date
    ) -> BytesIO:
        """
        Create a PDF report for a client.
        
        Args:
            client_profile: Client profile
            articles: List of article data (article and relevance)
            executive_summary: Executive summary text
            report_date: Report date
            
        Returns:
            BytesIO: PDF buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        elements = []

        # Add header with logo and date
        try:
            logo_path = "app/static/logo.png"
            if os.path.exists(logo_path):
                header_data = [
                    [
                        Image(logo_path, width=1.5*inch, height=0.5*inch),
                        Paragraph(f"News Report: {report_date.strftime('%B %d, %Y')}", self.styles["Heading1"])
                    ]
                ]
            else:
                header_data = [
                    [
                        Paragraph("NewsMonitor", self.styles["Heading1"]),
                        Paragraph(f"News Report: {report_date.strftime('%B %d, %Y')}", self.styles["Heading1"])
                    ]
                ]
                
            header = Table(
                header_data,
                colWidths=[2*inch, 4*inch]
            )
            header.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            elements.append(header)
        except Exception as e:
            logger.error(f"Error adding header: {e}")
            elements.append(Paragraph(f"News Report: {report_date.strftime('%B %d, %Y')}", self.styles["Heading1"]))
        
        elements.append(Spacer(1, 20))

        # Add client information
        elements.append(Paragraph(f"Client: {client_profile.name}", self.styles["Heading2"]))
        elements.append(Paragraph(f"Industry: {client_profile.industry}", self.styles["Normal"]))
        if client_profile.description:
            elements.append(Paragraph(f"Description: {client_profile.description}", self.styles["Normal"]))
        elements.append(Paragraph(f"Keywords: {', '.join(client_profile.keywords)}", self.styles["Normal"]))
        elements.append(Spacer(1, 15))

        # Add executive summary
        elements.append(Paragraph("Executive Summary", self.styles["Heading2"]))
        elements.append(Paragraph(executive_summary, self.styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Add articles
        elements.append(Paragraph("Relevant Articles", self.styles["Heading2"]))
        elements.append(Spacer(1, 10))

        for item in articles:
            article = item["article"]
            relevance = item["relevance"]
            
            # Article title
            elements.append(Paragraph(article.title, self.styles["ArticleTitle"]))
            
            # Source and date
            source_text = f"Source: {article.source} | Date: {article.published_at.strftime('%Y-%m-%d')}"
            if article.author:
                source_text += f" | Author: {article.author}"
            elements.append(Paragraph(source_text, self.styles["ArticleSource"]))
            
            # Relevance score
            score_text = f"Relevance Score: {relevance.relevance_score:.2f}"
            elements.append(Paragraph(score_text, self.styles["ArticleRelevance"]))
            
            # Summary
            if relevance.summary:
                elements.append(Paragraph(relevance.summary, self.styles["Normal"]))
            
            # URL
            elements.append(Paragraph(f"URL: {article.url}", self.styles["ArticleURL"]))
            
            elements.append(Spacer(1, 15))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def save_pdf_report(self, pdf_buffer: BytesIO, report_id: str) -> str:
        """
        Save a PDF report to disk.
        
        Args:
            pdf_buffer: PDF buffer
            report_id: Report ID
            
        Returns:
            str: Path to saved PDF
        """
        # Create absolute path to reports directory
        import os
        # Get the current working directory
        cwd = os.getcwd()
        # Create reports directory path
        reports_dir = os.path.join(cwd, "backend", "app", "static", "reports")
        os.makedirs(reports_dir, exist_ok=True)

        # Save PDF to file
        file_path = os.path.join(reports_dir, f"report_{report_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(pdf_buffer.read())

        return file_path