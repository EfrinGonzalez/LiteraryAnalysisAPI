from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

DATABASE_URL = "sqlite:///./literary_analysis.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    source_type = Column(String, nullable=False)  # text, url, image
    raw_input_hash = Column(String, nullable=True)
    url = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    extracted_text = Column(Text, nullable=True)
    mode = Column(String, nullable=False, default="fast")  # fast or smart
    model_version = Column(String, nullable=True)
    result = Column(JSON, nullable=False)


def init_db():
    """Initialize the database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
