from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, get_replica_db
from app.models import User
from app.schemas import HelloRequest, NewUserRequest, SpyResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    '''Generate a co-routine object'''
    Base.metadata.create_all(bind=engine)
    yield   #Yield makes a function behave like a generator


app = FastAPI(title="User Service", lifespan=lifespan)


def create_or_find_user(
    first_name: str, last_name: str, db: Session
) -> str:
    today = date.today()
    insert_user = (
        insert(User)
        .values(
            first_name=first_name,
            last_name=last_name,
            last_access=today,
            use_count=0,
        )
        .on_conflict_do_nothing(index_elements=[User.first_name, User.last_name])
        .returning(User.user_id)
    )
    #scalar is any ORM Object-Relational Model.  ORM can be int, string, dict, etc
    user_id = db.scalar(insert_user)

    if user_id is not None:
        status = "Created"
    else:
        update_user = (
            update(User)
            .where(User.first_name == first_name, User.last_name == last_name)
            .values(last_access=today, use_count=User.use_count + 1)
            .returning(User.user_id)
        )
        user_id = db.scalar(update_user)
        status = "Found"

    db.commit()
    return f"{status} {first_name} {last_name} with ID: {user_id}"


def greet_user(user_id: UUID, db: Session) -> str:
    user = db.scalar(select(User).where(User.user_id == user_id).with_for_update())
    if user is None:
        return f"{user_id} is not a recognized user."

    response = (
        f"Hello {user.first_name} {user.last_name} I haven't seen you since "
        f"{user.last_access}. You have visited {user.use_count} times."
    )
    db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(last_access=date.today(), use_count=User.use_count + 1)
    )
    db.commit()
    return response


@app.get("/healthcheck", response_class=PlainTextResponse)
def healthcheck() -> str:
    return "OK"


@app.get("/newuser", response_class=PlainTextResponse)
def newuser_get(
    first_name: Annotated[str, Query(min_length=1, max_length=32)],
    last_name: Annotated[str, Query(min_length=1, max_length=32)],
    db: Annotated[Session, Depends(get_db)],
) -> str:
    return create_or_find_user(first_name, last_name, db)


@app.post("/newuser", response_class=PlainTextResponse)
def newuser_post(
    request: NewUserRequest, db: Annotated[Session, Depends(get_db)]
) -> str:
    return create_or_find_user(request.first_name, request.last_name, db)


@app.get("/hello", response_class=PlainTextResponse)
def hello_get(
    user_id: UUID, db: Annotated[Session, Depends(get_db)]
) -> str:
    return greet_user(user_id, db)


@app.post("/hello", response_class=PlainTextResponse)
def hello_post(
    request: HelloRequest, db: Annotated[Session, Depends(get_db)]
) -> str:
    return greet_user(request.user_id, db)


@app.post("/spy", response_model=SpyResponse)
def spy_post(
    request: HelloRequest,
    db: Annotated[Session, Depends(get_replica_db)],
) -> SpyResponse | PlainTextResponse:
    user = db.scalar(select(User).where(User.user_id == request.user_id))
    if user is None:
        return PlainTextResponse("Invalid User ID")

    return SpyResponse(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        last_access=user.last_access,
        use_count=user.use_count,
    )