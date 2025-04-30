"""
PDF report template configuration.

This module defines the styles and layout for PDF reports.
"""
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def get_report_styles():
    """
    Get styles for PDF reports.
    
    Returns:
        dict: Dictionary of styles
    """
    styles = getSampleStyleSheet()
    
    # Add custom styles
    styles.add(
        ParagraphStyle(
            name='ArticleTitle',
            parent=styles['Heading3'],
            fontSize=12,
            leading=14,
            textColor=colors.darkblue
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArticleSource',
            parent=styles['Italic'],
            fontSize=9,
            textColor=colors.gray
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArticleRelevance',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.darkgreen
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArticleURL',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.blue,
            underline=True
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ExecutiveSummaryTitle',
            parent=styles['Heading2'],
            fontSize=14,
            leading=16,
            textColor=colors.black,
            spaceAfter=0.1*inch
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ClientInfo',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            textColor=colors.black
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ReportHeader',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ReportDate',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            textColor=colors.gray,
            alignment=1  # Center alignment
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            leading=16,
            textColor=colors.darkblue,
            spaceBefore=0.2*inch,
            spaceAfter=0.1*inch
        )
    )
    
    return styles


def get_table_styles():
    """
    Get table styles for PDF reports.
    
    Returns:
        dict: Dictionary of table styles
    """
    table_styles = {
        'header': [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.lightgrey),
        ],
        'client_info': [
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ],
        'article': [
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]
    }
    
    return table_styles