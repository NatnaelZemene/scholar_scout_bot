from app.db.models import Base
from app.db.session import engine


def init_db() -> None:
    # Reads all model classes registered under Base and creates tables.
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")