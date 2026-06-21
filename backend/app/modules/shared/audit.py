from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AuditActor:
    user_id: UUID | None
    source: str = "api"
