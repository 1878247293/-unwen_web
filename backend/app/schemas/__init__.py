"""
Schemas包初始化
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    TokenResponse,
)

from app.schemas.paper import (
    PaperBase,
    PaperCreate,
    PaperUpdate,
    PaperResponse,
    PaperListResponse,
    PaperSearchParams,
    PaperFileUploadResponse,
)

from app.schemas.note import (
    NoteBase,
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
)

from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse,
    PaperTagCreate,
)

from app.schemas.reading import (
    ReadingProgressUpdate,
    ReadingSessionCreate,
    ReadingHistoryResponse,
    ReadingStatsResponse,
    PaperReadingStats,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserResponse",
    "TokenResponse",
    # Paper schemas
    "PaperBase",
    "PaperCreate",
    "PaperUpdate",
    "PaperResponse",
    "PaperListResponse",
    "PaperSearchParams",
    "PaperFileUploadResponse",
    # Note schemas
    "NoteBase",
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
    "NoteListResponse",
    # Tag schemas
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagListResponse",
    "PaperTagCreate",
    # Reading schemas
    "ReadingProgressUpdate",
    "ReadingSessionCreate",
    "ReadingHistoryResponse",
    "ReadingStatsResponse",
    "PaperReadingStats",
]
