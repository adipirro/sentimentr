from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def DB_Init():
    engine = create_engine("postgres://sentimentr_db:sentimentr_db@localhost:5432/sentimentr_db")
    Base.metadata.create_all(engine)

def DB_Drop():
    engine = create_engine("postgres://sentimentr_db:sentimentr_db@localhost:5432/sentimentr_db")
    Base.metadata.drop_all(engine)

class GHUser(Base):
    __tablename__ = "gh_user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Repository(Base):
    __tablename__ = "repository"

    id = Column(Integer, primary_key=True)
    owner = Column(String(50))
    name = Column(String(50))
    create_dt = Column(DateTime)

class Issue(Base):
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    gh_user_id = Column(Integer, ForeignKey('gh_user.id'))
    title = Column(String)
    body = Column(String)
    create_dt = Column(DateTime)

class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey('issue.id'))
    gh_user_id = Column(Integer, ForeignKey('gh_user.id'))
    body = Column(String)
    create_dt = Column(DateTime)

class Sentiment(Base):
    __tablename__ = "sentiment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    polarity = Column(Numeric)
    subjectivity = Column(Numeric)
