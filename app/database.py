import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://users:users@localhost:5432/users",
)
REPLICA_DATABASE_URL = os.getenv("REPLICA_DATABASE_URL", DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
replica_engine = create_engine(REPLICA_DATABASE_URL, pool_pre_ping=True)
ReplicaSessionLocal = sessionmaker(
    bind=replica_engine, autoflush=False, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_replica_db():
    session = ReplicaSessionLocal()
    try:
        yield session
    finally:
        session.close()