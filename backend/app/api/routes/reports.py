"""
API routes for report management.
"""
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, Body
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import Report, ReportWithArticles, ReportGenerateRequest
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("", response_model=List[Report])
async def get_reports(
    skip: int = 0,
    limit: int = 20,
    client_id: Optional[uuid.UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reports with filters.
    
    Args:
        skip: Number of reports to skip
        limit: Maximum number of reports to return
        client_id: Optional client profile ID filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[Report]: List of reports
    """
    report_service = ReportService(db)
    
    if client_id:
        result = await report_service.get_reports_for_client(
            client_id=client_id,
            user_id=current_user.id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
            
        return result["reports"]
    else:
        # Get all reports for user
        result = await report_service.get_reports_for_user(
            user_id=current_user.id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit
        )
        
        return result["reports"]


@router.get("/{report_id}", response_model=ReportWithArticles)
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get report by ID.
    
    Args:
        report_id: Report ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        ReportWithArticles: Report with articles
    """
    report_service = ReportService(db)
    result = await report_service.get_report_by_id(report_id, current_user.id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
        
    # Combine report with articles
    report_data = result["report"]
    report_data.report_articles = [item["report_article"] for item in result["articles"]]
    
    return report_data


@router.get("/download/{report_id}")
async def download_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download report PDF.
    
    Args:
        report_id: Report ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        FileResponse: PDF file
    """
    report_service = ReportService(db)
    result = await report_service.get_report_by_id(report_id, current_user.id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
        
    report = result["report"]
    
    if not report.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found for this report"
        )
        
    if not report.pdf_path or not report.pdf_path.strip():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF path is empty"
        )
        
    # Check if file exists
    import os
    if not os.path.exists(report.pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )
        
    client_name = result["client_profile"].name if result["client_profile"] else "Report"
    filename = f"{client_name}_Report_{report.report_date.strftime('%Y-%m-%d')}.pdf"
    
    return FileResponse(
        path=report.pdf_path,
        filename=filename,
        media_type="application/pdf"
    )


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    # Expect the request data from the body using the Pydantic model
    request_data: ReportGenerateRequest = Body(...),
    # Dependencies remain the same
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Queue report generation based on client ID and optional date from request body.
    """
    from app.celery_worker.tasks.report_tasks import generate_report_task # Keep import here for now

    # Extract data from the request_data model
    client_id = request_data.client_id
    report_date = request_data.report_date

    # --- Optional: Add verification that client_id belongs to current_user ---
    # You might want to fetch the client profile here to ensure authorization,
    # although maybe the task itself handles this implicitly later.
    # client_repo = ClientProfileRepository(db)
    # client = await client_repo.get_by_id_and_user_id(client_id, current_user.id)
    # if not client:
    #    raise HTTPException(status_code=404, detail="Client profile not found or not authorized")
    # -------------------------------------------------------------------------

    # Queue report generation task
    task = generate_report_task.delay(
        str(client_id), # Pass client_id as string to Celery
        report_date.isoformat() if report_date else None # Pass date as string or None
    )

    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Report generation has been queued"
    }


@router.get("/by-client/{client_id}", response_model=List[Report])
async def get_reports_by_client(
    client_id: uuid.UUID,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reports for client.
    
    Args:
        client_id: Client profile ID
        date_from: Optional start date filter
        date_to: Optional end date filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[Report]: List of reports
    """
    report_service = ReportService(db)
    result = await report_service.get_reports_for_client(
        client_id=client_id,
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
        
    return result["reports"]

@router.post("/{report_id}/send", status_code=status.HTTP_200_OK)
async def send_report(
    report_id: uuid.UUID,
    email_data: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a report via email.
    
    Args:
        report_id: Report ID
        email_data: Email data (recipient email)
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Send result
    """
    from app.services.email_service import EmailService
    
    report_service = ReportService(db)
    result = await report_service.get_report_by_id(report_id, current_user.id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    report = result["report"]
    client_profile = result["client_profile"]
    
    # Check if the report is ready to be sent
    if report.status not in ["ready", "sent"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is not ready to be sent"
        )
    
    # Check if the email is provided
    if "email" not in email_data or not email_data["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    # Send the report
    email_service = EmailService()
    send_result = await email_service.send_report_email(
        user_email=email_data["email"],
        client_name=client_profile.name,
        report_date=report.report_date,
        pdf_path=report.pdf_path,
        report_id=str(report.id)
    )
    
    if not send_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=send_result.get("error", "Failed to send report")
        )
    
    # Update report status and recipient email
    await report_service.report_repo.update_status(
        report_id=report_id,
        status="sent",
        recipient_email=email_data["email"]
    )
    
    return {
        "success": True,
        "message": f"Report sent to {email_data['email']}"
    }