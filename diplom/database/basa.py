from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

DATABASE = "postgresql+psycopg2://postgres:14092022shb@localhost/diplom"

engine = create_engine(DATABASE, echo=True,
                       pool_size=20,
                       max_overflow=15,
                       pool_timeout=30,
                       pool_pre_ping=True,
                       pool_recycle=1800)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def session_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
