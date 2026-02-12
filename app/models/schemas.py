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


# ==================== Literary Analysis Schemas ====================

class Language(str, Enum):
    english = "english"
    spanish = "spanish"


class SummaryLength(str, Enum):
    short = "short"
    medium = "medium"


class LiteraryAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")
    language: Language = Field(default=Language.english, description="Output language: english or spanish")
    summary_length: SummaryLength = Field(default=SummaryLength.medium, description="Summary length: short or medium")


class InfluenceItem(BaseModel):
    name: str = Field(..., description="Name of the influence (author, school, philosophy, etc.)")
    type: str = Field(..., description="Type of influence (author, school, philosophy, historical, cultural)")
    rationale: str = Field(..., description="Brief explanation of the influence")


class AestheticStyle(BaseModel):
    style: str = Field(..., description="Name of aesthetic style (e.g., Romanticism, Modernism, etc.)")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")


class LiteraryInsights(BaseModel):
    summary_short: Optional[str] = Field(None, description="Short summary of the text")
    summary_medium: Optional[str] = Field(None, description="Medium-length summary of the text")
    movement_or_tendency: str = Field(..., description="Literary/artistic movement or tendency")
    influences: List[InfluenceItem] = Field(default_factory=list, description="Detected influences in the text")
    aesthetic_styles: List[AestheticStyle] = Field(default_factory=list, description="Aesthetic styles present")
    disclaimer: str = Field(..., description="Disclaimer about interpretive nature of analysis")


class LiteraryAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis identifier")
    created_at: datetime
    source_type: SourceType
    language: str
    insights: LiteraryInsights
    
    class Config:
        from_attributes = True
