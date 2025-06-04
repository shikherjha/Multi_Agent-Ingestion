from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import logging
import uuid

Base = declarative_base()

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(String, primary_key=True)  
    source = Column(String)
    format = Column(String)  
    intent = Column(String)
    payload = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MemoryLogger:
    def __init__(self, db_url="sqlite:///memory_logs.db"):  # Fixed __init__
        self.logger = logging.getLogger(self.__class__.__name__)
       
        try:
            self.engine = create_engine(db_url, echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.logger.info(f"Database initialized at: {db_url}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def log_entry(self, source: str, format_type: str, intent: str, payload: dict):
        session = self.Session()
        try:
            entry = LogEntry(
                id=str(uuid.uuid4()),  
                source=source,
                format=format_type,  
                intent=intent,
                payload=json.dumps(payload, default=str)
            )    
            session.add(entry)
            session.commit()
            self.logger.info(f"Logged entry for source: {source}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to log entry: {e}")
            raise
        finally:
            session.close()
    
    def fetch_all(self, limit=10):
        session = self.Session()
        try:
            entries = session.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit).all()
            return entries
        except Exception as e:
            self.logger.error(f"Failed to fetch entries: {e}")
            return []
        finally:
            session.close()
   
    def fetch_by_source(self, source: str, limit=10):
        """Fetch entries by source name"""
        session = self.Session()
        try:
            entries = session.query(LogEntry).filter(
                LogEntry.source == source
            ).order_by(LogEntry.timestamp.desc()).limit(limit).all()
            return entries
        except Exception as e:
            self.logger.error(f"Failed to fetch entries by source: {e}")
            return []
        finally:
            session.close()
   
    def fetch_by_intent(self, intent: str, limit=10):
        """Fetch entries by intent"""
        session = self.Session()
        try:
            entries = session.query(LogEntry).filter(
                LogEntry.intent == intent
            ).order_by(LogEntry.timestamp.desc()).limit(limit).all()
            return entries
        except Exception as e:
            self.logger.error(f"Failed to fetch entries by intent: {e}")
            return []
        finally:
            session.close()
    
    def get_stats(self):
        """Get statistics about logged entries"""
        session = self.Session()
        try:
            total_entries = session.query(LogEntry).count()
            
            # Get format distribution
            format_counts = {}
            formats = session.query(LogEntry.format).distinct().all()
            for (fmt,) in formats:
                if fmt:
                    count = session.query(LogEntry).filter(LogEntry.format == fmt).count()
                    format_counts[fmt] = count
            
            # Get intent distribution
            intent_counts = {}
            intents = session.query(LogEntry.intent).distinct().all()
            for (intent,) in intents:
                if intent:
                    count = session.query(LogEntry).filter(LogEntry.intent == intent).count()
                    intent_counts[intent] = count
            
            return {
                'total_entries': total_entries,
                'format_counts': format_counts,
                'intent_counts': intent_counts
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {'error': str(e)}
        finally:
            session.close()
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'engine'):
            self.engine.dispose()