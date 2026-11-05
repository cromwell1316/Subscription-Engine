from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from billing.infrastructure.persistence.sql.models import Base


def create_db_engine(database_url: str) -> Engine:
    """Creates a configured SQLAlchemy Engine."""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        database_url,
        connect_args=connect_args,
        echo=False,
    )


def create_session_factory(engine: Engine) -> sessionmaker:
    """Creates a thread-safe Session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(engine: Engine) -> None:
    """Initializes tables in the target database."""
    Base.metadata.create_all(bind=engine)
