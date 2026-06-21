from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.modules.auth.dependencies import AuthServiceDep, CurrentUser
from app.modules.auth.schemas import (
    CurrentUserResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPairResponse,
)
from app.modules.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPairResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    auth_service: AuthServiceDep,
    session: DbSession,
) -> dict[str, str]:
    user = await auth_service.register_customer(
        email=str(payload.email),
        password=payload.password,
        full_name=payload.full_name,
        phone=payload.phone,
    )
    await session.commit()
    return auth_service.create_token_pair(user)


@router.post("/login", response_model=TokenPairResponse)
async def login(payload: LoginRequest, auth_service: AuthServiceDep) -> dict[str, str]:
    return await auth_service.login(email=str(payload.email), password=payload.password)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    payload: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> dict[str, str]:
    return await auth_service.refresh_tokens(refresh_token=payload.refresh_token)


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(current_user: CurrentUser) -> User:
    return current_user
