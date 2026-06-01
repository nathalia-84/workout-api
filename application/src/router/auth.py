from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import AsyncMongoClient
from src.core.database import get_database
from src.core.security import create_access_token
from src.core.security import pwd_context
from src.model.auth import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registrations", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(payload: UserCreate, db: AsyncMongoClient = Depends(get_database)):
    existing_user = await db.users.find_one(
        {"$or": [{"username": payload.username}, {"email": payload.email}]}
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário ou e-mail já cadastrado",
        )

    hashed_password = pwd_context.hash(payload.password)
    user_doc = {
        "username": payload.username,
        "email": payload.email,
        "hashed_password": hashed_password,
        "roles": ["user"],
    }

    result = await db.users.insert_one(user_doc)
    user_doc["id"] = str(result.inserted_id)
    return user_doc


@router.post("/tokens", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncMongoClient = Depends(get_database),
):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "roles": user["roles"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
