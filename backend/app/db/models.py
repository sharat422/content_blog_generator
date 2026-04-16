from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from app.db.session import Base
# from sqlalchemy import Column, JSON

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

class Content(Base):
    __tablename__ = "contents"
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    type = Column(String)  # text / image / audio
    content_text = Column(String)
    meta_data = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    # Uniqueness tracking fields
    content_hash = Column(String, index=True)  # SHA256 hash for deduplication
    prompt_hash = Column(String, index=True)  # Hash of original prompt
    template = Column(String)  # Template used for generation
    variation_count = Column(Integer, default=0)  # How many times this prompt was generated
    uniqueness_score = Column(Float, default=0.0)  # 0-100 uniqueness metric
    is_unique = Column(Integer, default=1)  # Boolean: 1=unique, 0=duplicate

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"))
    score = Column(Integer)
    feedback_type = Column(String)
    notes = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    tone_preference = Column(JSON)
    creativity_level = Column(Float, default=0.5)
    avg_length = Column(Integer, default=0)
    style_tags = Column(JSON)  # works on both SQLite and PostgreSQL
    updated_at = Column(TIMESTAMP, server_default=text("now()"))

class UserEmbeddings(Base):
    __tablename__ = "user_embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"))
    vector_id = Column(String)
    similarity = Column(Float)
    created_at = Column(TIMESTAMP, server_default=text("now()"))


class GenerationHistory(Base):
    __tablename__ = "generation_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"))
    prompt_hash = Column(String, index=True)  # Hash of the prompt
    content_hash = Column(String, index=True)  # Hash of generated content
    template = Column(String)  # Template used
    variation_count = Column(Integer, default=0)  # Which variation is this
    content_type = Column(String, default="text")  # Type of content generated
    content_length = Column(Integer)  # Length of generated content
    uniqueness_score = Column(Float, default=0.0)  # Uniqueness metric
    generation_time_ms = Column(Integer, default=0)  # Time taken to generate
    temperature_used = Column(Float)  # Temperature setting used
    is_duplicate = Column(Integer, default=0)  # Whether this was a duplicate
    created_at = Column(TIMESTAMP, server_default=text("now()"), index=True)
