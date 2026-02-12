from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models.schemas import (
    TextAnalysisRequest, URLAnalysisRequest, AnalysisResponse,
    AnalysisListResponse, HealthResponse, SourceType, AnalysisResult, SentimentResult,
    LiteraryAnalysisRequest, LiteraryAnalysisResponse, LiteraryInsights,
    InfluenceItem, AestheticStyle
)
from app.database import get_db, AnalysisRecord
from app.services.analysis import analyze_text, compute_text_hash, analyze_text_file
from app.services.scraper import fetch_article_text
from app.services.ocr import ocr_image_bytes, ocr_pdf_bytes
from app.services.sentiment import get_model_info
from app.services.literary_analysis import analyze_literary_text

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== V1 API Endpoints ====================

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database="connected"
    )


@router.post("/v1/analyze/text", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_text_endpoint(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze text content
    
    - **text**: Text content to analyze
    - **mode**: Analysis mode - 'fast' (VADER) or 'smart' (transformer-based)
    """
    try:
        # Perform analysis
        result = analyze_text(request.text, mode=request.mode.value)
        
        # Create sentiment result model
        sentiment_result = SentimentResult(**result["sentiment"])
        analysis_result = AnalysisResult(
            word_count=result["word_count"],
            sentiment=sentiment_result,
            keywords=result["keywords"],
            top_words=result["top_words"]
        )
        
        # Store in database
        text_hash = compute_text_hash(request.text)
        model_version = get_model_info(request.mode.value)
        
        analysis_record = AnalysisRecord(
            source_type=SourceType.text.value,
            raw_input_hash=text_hash,
            extracted_text=request.text[:1000],  # Store first 1000 chars
            mode=request.mode.value,
            model_version=model_version,
            result=result
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        return AnalysisResponse(
            analysis_id=analysis_record.id,
            created_at=analysis_record.created_at,
            source_type=SourceType.text,
            mode=analysis_record.mode,
            result=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Error in text analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/v1/analyze/url", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_url_endpoint(
    request: URLAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze content from a URL
    
    - **url**: URL to fetch and analyze
    - **mode**: Analysis mode - 'fast' (VADER) or 'smart' (transformer-based)
    """
    try:
        # Fetch article text with SSRF protection
        url_str = str(request.url)
        text = fetch_article_text(url_str)
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from URL"
            )
        
        # Perform analysis
        result = analyze_text(text, mode=request.mode.value)
        
        # Create response models
        sentiment_result = SentimentResult(**result["sentiment"])
        analysis_result = AnalysisResult(
            word_count=result["word_count"],
            sentiment=sentiment_result,
            keywords=result["keywords"],
            top_words=result["top_words"]
        )
        
        # Store in database
        text_hash = compute_text_hash(text)
        model_version = get_model_info(request.mode.value)
        
        analysis_record = AnalysisRecord(
            source_type=SourceType.url.value,
            url=url_str,
            raw_input_hash=text_hash,
            extracted_text=text[:1000],
            mode=request.mode.value,
            model_version=model_version,
            result=result
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        return AnalysisResponse(
            analysis_id=analysis_record.id,
            created_at=analysis_record.created_at,
            source_type=SourceType.url,
            mode=analysis_record.mode,
            result=analysis_result,
            url=url_str
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in URL analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/v1/analyze/image", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    mode: str = Form(default="fast"),
    db: Session = Depends(get_db)
):
    """
    Analyze text extracted from an image or PDF using OCR
    
    - **file**: Image or PDF file to analyze
    - **mode**: Analysis mode - 'fast' (VADER) or 'smart' (transformer-based)
    
    Requires Tesseract OCR to be installed on the system.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type and perform OCR
        filename = file.filename.lower()
        ext = filename.split('.')[-1] if '.' in filename else ''
        
        try:
            if ext == "pdf":
                text = ocr_pdf_bytes(content)
            else:
                text = ocr_image_bytes(content)
        except Exception as ocr_error:
            logger.error(f"OCR error: {ocr_error}")
            raise HTTPException(
                status_code=500,
                detail="OCR processing failed. Please ensure Tesseract is installed on the system."
            )
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from image. The image may be blank or unreadable."
            )
        
        # Perform analysis
        result = analyze_text(text, mode=mode)
        
        # Create response models
        sentiment_result = SentimentResult(**result["sentiment"])
        analysis_result = AnalysisResult(
            word_count=result["word_count"],
            sentiment=sentiment_result,
            keywords=result["keywords"],
            top_words=result["top_words"]
        )
        
        # Store in database
        text_hash = compute_text_hash(text)
        model_version = get_model_info(mode)
        
        analysis_record = AnalysisRecord(
            source_type=SourceType.image.value,
            filename=file.filename,
            raw_input_hash=text_hash,
            extracted_text=text[:1000],
            mode=mode,
            model_version=model_version,
            result=result
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        return AnalysisResponse(
            analysis_id=analysis_record.id,
            created_at=analysis_record.created_at,
            source_type=SourceType.image,
            mode=analysis_record.mode,
            result=analysis_result,
            filename=file.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/v1/analyses/{analysis_id}", response_model=AnalysisResponse, tags=["Analysis"])
async def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific analysis by ID
    
    - **analysis_id**: Unique identifier of the analysis
    """
    analysis = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Reconstruct response
    result_data = analysis.result
    sentiment_result = SentimentResult(**result_data["sentiment"])
    analysis_result = AnalysisResult(
        word_count=result_data["word_count"],
        sentiment=sentiment_result,
        keywords=result_data.get("keywords", []),
        top_words=result_data.get("top_words", [])
    )
    
    return AnalysisResponse(
        analysis_id=analysis.id,
        created_at=analysis.created_at,
        source_type=SourceType(analysis.source_type),
        mode=analysis.mode,
        result=analysis_result,
        url=analysis.url,
        filename=analysis.filename
    )


@router.get("/v1/analyses", response_model=AnalysisListResponse, tags=["Analysis"])
async def list_analyses(
    source_type: Optional[SourceType] = Query(None, description="Filter by source type"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    List all analyses with optional filtering
    
    - **source_type**: Filter by source type (text, url, or image)
    - **limit**: Maximum number of results to return (1-100)
    - **offset**: Number of results to skip for pagination
    """
    query = db.query(AnalysisRecord)
    
    if source_type:
        query = query.filter(AnalysisRecord.source_type == source_type.value)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    analyses = query.order_by(AnalysisRecord.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response models
    analysis_responses = []
    for analysis in analyses:
        result_data = analysis.result
        sentiment_result = SentimentResult(**result_data["sentiment"])
        analysis_result = AnalysisResult(
            word_count=result_data["word_count"],
            sentiment=sentiment_result,
            keywords=result_data.get("keywords", []),
            top_words=result_data.get("top_words", [])
        )
        
        analysis_responses.append(AnalysisResponse(
            analysis_id=analysis.id,
            created_at=analysis.created_at,
            source_type=SourceType(analysis.source_type),
            mode=analysis.mode,
            result=analysis_result,
            url=analysis.url,
            filename=analysis.filename
        ))
    
    return AnalysisListResponse(
        total=total,
        limit=limit,
        offset=offset,
        analyses=analysis_responses
    )


@router.post("/v1/analyze/literary", response_model=LiteraryAnalysisResponse, tags=["Literary Analysis"])
async def analyze_literary_endpoint(
    request: LiteraryAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Perform enhanced literary analysis on text to extract:
    - Summary (short and/or medium length)
    - Literary movement or tendency
    - Influences (authors, philosophies, schools)
    - Aesthetic styles with confidence levels
    
    **Note**: This analysis is probabilistic and interpretive. Results should not be
    considered definitive literary criticism.
    
    - **text**: Text to analyze (minimum 200 characters)
    - **language**: Output language - 'english' (default) or 'spanish'
    - **summary_length**: Summary length - 'short' or 'medium' (default)
    """
    try:
        # Perform literary analysis
        insights_dict = analyze_literary_text(
            text=request.text,
            language=request.language.value,
            summary_length=request.summary_length.value
        )
        
        # Create response models
        influences = [
            InfluenceItem(
                name=inf["name"],
                type=inf["type"],
                rationale=inf["rationale"]
            )
            for inf in insights_dict["influences"]
        ]
        
        aesthetic_styles = [
            AestheticStyle(
                style=style["style"],
                confidence=style["confidence"]
            )
            for style in insights_dict["aesthetic_styles"]
        ]
        
        literary_insights = LiteraryInsights(
            summary_short=insights_dict.get("summary_short"),
            summary_medium=insights_dict.get("summary_medium"),
            movement_or_tendency=insights_dict["movement_or_tendency"],
            influences=influences,
            aesthetic_styles=aesthetic_styles,
            disclaimer=insights_dict["disclaimer"]
        )
        
        # Store in database
        text_hash = compute_text_hash(request.text)
        
        # Prepare result dict for storage
        result_dict = {
            "literary_insights": insights_dict
        }
        
        analysis_record = AnalysisRecord(
            source_type=SourceType.text.value,
            raw_input_hash=text_hash,
            extracted_text=request.text[:1000],
            mode="literary",
            model_version="literary_analysis_v1",
            result=result_dict
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        return LiteraryAnalysisResponse(
            analysis_id=analysis_record.id,
            created_at=analysis_record.created_at,
            source_type=SourceType.text,
            language=request.language.value,
            insights=literary_insights
        )
        
    except ValueError as e:
        # Handle validation errors (e.g., text too short)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in literary analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Literary analysis failed: {str(e)}")


# ==================== Legacy Endpoints (for backward compatibility) ====================

@router.post("/analyze-file/", tags=["Legacy"])
async def analyze_file(file: UploadFile = File(...)):
    """Legacy endpoint - use /v1/analyze/text instead"""
    text = await file.read()
    result = analyze_text_file(text.decode("utf-8"))
    return result


@router.post("/analyze-url/", tags=["Legacy"])
async def analyze_url(url: str = Form(...)):
    """Legacy endpoint - use /v1/analyze/url instead"""
    try:
        text = fetch_article_text(url)
        result = analyze_text_file(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze-image/", tags=["Legacy"])
async def analyze_image(file: UploadFile = File(...)):
    """Legacy endpoint - use /v1/analyze/image instead"""
    content = await file.read()
    ext = file.filename.lower().split('.')[-1]
    try:
        if ext == "pdf":
            text = ocr_pdf_bytes(content)
        else:
            text = ocr_image_bytes(content)
        result = analyze_text_file(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
