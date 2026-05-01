# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Submissions(Base):
    __tablename__ = 'submissions'
    __table_args__ = {'schema': 'chefstojira'}
    # A key just for the database
    pk = Column(Integer, server_default=text("nextval('chefstojira.submissions_pk_seq'::regclass)"), primary_key=True)
    
    # The next few are directly from CHEFS
    submission_id = Column(String(50), nullable=False)
    form_id = Column(String(50), nullable=False)
    form_name = Column(String(50), nullable=False)
    form_version_id = Column(Integer, server_default=0, nullable=False)

    # When the event was retrieved from the CHEFS API. This helps us track how long since last successful CHEFS query.
    event_received = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    # CHEFS payload is encrypted by default, but cryptr outputs text, so we'll just store it as a string for now.
    payload = Column(String, nullable=False)

    # How many times we've attempted to process this submission. We can use this to decide when to give up.
    attempts = Column(Integer, server_default=text("0"), nullable=False)
