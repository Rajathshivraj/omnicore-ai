from datetime import timedelta
from uuid import UUID

import jwt

from app.core.config import Settings
from app.core.errors import AuthenticationError, ConflictError, NotFoundError
from app.core.jwt import TokenType, create_token, decode_token
from app.core.password import hash_password, verify_password
from app.db.enums import UserStatus
from app.modules.shared.permissions import RoleSlug
from app.modules.users.models import User
from app.modules.users.repository import RoleRepository, UserRepository


class AuthService:
    """Coordinates authentication workflows.

    Token persistence/revocation is intentionally left for the refresh-token
    repository when that table is introduced. This service does not perform
    route-level authorization.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        settings: Settings,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.settings = settings

    async def register_customer(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        phone: str | None = None,
    ) -> User:
        normalized_email = email.lower()
        existing_user = await self.user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise ConflictError("A user with this email already exists.")

        customer_role = await self.role_repository.get_by_slug(RoleSlug.CUSTOMER.value)
        if customer_role is None:
            raise NotFoundError("Customer role is not configured.")

        user = await self.user_repository.create(
            {
                "email": normalized_email,
                "password_hash": hash_password(password),
                "full_name": full_name,
                "phone": phone,
                "status": UserStatus.ACTIVE,
                "role_id": customer_role.id,
            }
        )
        return await self.user_repository.get_by_id_with_role(user.id) or user

    async def authenticate_user(self, *, email: str, password: str) -> User:
        user = await self.user_repository.get_by_email_with_role(email.lower())
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        if UserStatus(user.status) != UserStatus.ACTIVE:
            raise AuthenticationError("User account is not active.")
        return user

    async def get_current_user(self, *, access_token: str) -> User:
        payload = self._decode_expected_token(access_token, expected_type=TokenType.ACCESS)
        return await self._get_active_user_from_payload(payload)

    async def refresh_tokens(self, *, refresh_token: str) -> dict[str, str]:
        payload = self._decode_expected_token(refresh_token, expected_type=TokenType.REFRESH)
        user = await self._get_active_user_from_payload(payload)
        return self.create_token_pair(user)

    def create_token_pair(self, user: User) -> dict[str, str]:
        claims = {
            "role": user.role.slug if user.role else None,
        }
        access_token = create_token(
            subject=str(user.id),
            token_type=TokenType.ACCESS,
            settings=self.settings,
            expires_delta=timedelta(minutes=self.settings.access_token_expire_minutes),
            extra_claims=claims,
        )
        refresh_token = create_token(
            subject=str(user.id),
            token_type=TokenType.REFRESH,
            settings=self.settings,
            expires_delta=timedelta(days=self.settings.refresh_token_expire_days),
            extra_claims=claims,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def login(self, *, email: str, password: str) -> dict[str, str]:
        user = await self.authenticate_user(email=email, password=password)
        return self.create_token_pair(user)

    def _decode_expected_token(self, token: str, *, expected_type: TokenType) -> dict[str, object]:
        try:
            payload = decode_token(token=token, settings=self.settings)
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid or expired token.") from exc

        if payload.get("typ") != expected_type.value:
            raise AuthenticationError("Invalid token type.")
        if not payload.get("sub"):
            raise AuthenticationError("Invalid token subject.")
        return payload

    async def _get_active_user_from_payload(self, payload: dict[str, object]) -> User:
        try:
            user_id = UUID(str(payload["sub"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid token subject.") from exc

        user = await self.user_repository.get_by_id_with_role(user_id)
        if user is None:
            raise AuthenticationError("User account was not found.")
        if UserStatus(user.status) != UserStatus.ACTIVE:
            raise AuthenticationError("User account is not active.")
        return user
