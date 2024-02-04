# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Text, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True, server_default=text("nextval('article_id_seq'::regclass)"))
    title = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    title_tsvector = Column(TSVECTOR, index=True)
    body_tsvector = Column(TSVECTOR, index=True)
    link_tsvector = Column(TSVECTOR, index=True)
