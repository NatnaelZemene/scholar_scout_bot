from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite for day-1 local development.
# Later we can switch to Postgres by changing this one URL.
DATABASE_URL = "sqlite:///./scholar_scout.db"

# echo=False keeps logs clean; set True when debugging SQL.
engine = create_engine(DATABASE_URL, echo=False, future=True)

# expire_on_commit=False prevents object fields from disappearing
# right after commit, which is easier for beginners.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)