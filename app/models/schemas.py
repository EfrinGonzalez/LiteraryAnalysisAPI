from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisMode(str, Enum):
    fast = "fast"
    smart = "smart"


class SourceType(str, Enum):
    text = "text"
    url = "url"
    image = "image"


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")
    mode: AnalysisMode = Field(default=AnalysisMode.fast, description="Analysis mode: fast (VADER) or smart (transformer)")


class URLAnalysisRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL to fetch and analyze")
    mode: AnalysisMode = Field(default=AnalysisMode.fast, description="Analysis mode: fast or smart")


class SentimentResult(BaseModel):
    polarity_label: str = Field(..., description="Sentiment label: positive, negative, or neutral")
    polarity_score: float = Field(..., description="Sentiment polarity score")
    confidence: Optional[float] = Field(None, description="Confidence score (if available)")
    compound: Optional[float] = Field(None, description="Compound score from VADER (if using fast mode)")
    positive: Optional[float] = Field(None, description="Positive score")
    negative: Optional[float] = Field(None, description="Negative score")
    neutral: Optional[float] = Field(None, description="Neutral score")


class AnalysisResult(BaseModel):
    word_count: int
    sentiment: SentimentResult
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    top_words: Optional[List[tuple]] = Field(None, description="Most frequent words")


class AnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis identifier")
    created_at: datetime
    source_type: SourceType
    mode: str
    result: AnalysisResult
    url: Optional[str] = None
    filename: Optional[str] = None
    
    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    analyses: List[AnalysisResponse]


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
