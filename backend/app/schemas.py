from pydantic import BaseModel
from typing import Optional, List
import datetime

# --- Diagnostics & Health ---
class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    total_embeddings: int
    total_unique_identities: int
    device: str
    message: str

class ConfigResponse(BaseModel):
    threshold: float
    embedding_dim: int
    device: str
    model_name: str
    liveness_enabled: bool

class SpoofSettingRequest(BaseModel):
    enabled: bool

class SpoofSettingResponse(BaseModel):
    liveness_enabled: bool
    message: str

# --- Authentication Schemas ---
class UserRegisterRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str

# --- Biometric Verification & Enrollment ---
class VerifyResponse(BaseModel):
    match_found: bool
    identity: Optional[str] = None
    distance: Optional[float] = None
    confidence: Optional[float] = None
    is_live: bool = True
    liveness_score: Optional[float] = None
    status: str # GRANTED, DENIED, SPOOF_DETECTED, NO_FACE
    message: str

class EnrollResponse(BaseModel):
    success: bool
    identity: str
    total_embeddings: int
    message: str

class IdentitiesResponse(BaseModel):
    total_count: int
    unique_count: int
    unique_identities: List[str]

class DeleteIdentityResponse(BaseModel):
    success: bool
    identity: str
    remaining_embeddings: int
    message: str

# --- Audit & Analytics Schemas ---
class AccessLogItem(BaseModel):
    id: int
    timestamp: datetime.datetime
    status: str
    matched_identity: Optional[str] = None
    l2_distance: Optional[float] = None
    confidence_score: Optional[float] = None
    is_live: bool
    liveness_score: Optional[float] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True

class AccessLogsListResponse(BaseModel):
    total: int
    page: int
    limit: int
    logs: List[AccessLogItem]

class AnalyticsSummaryResponse(BaseModel):
    total_verifications: int
    granted_count: int
    denied_count: int
    spoof_detected_count: int
    no_face_count: int
    pass_rate_percentage: float
    enrolled_identities_count: int
    active_device: str

# --- User Portal Schemas ---
class UserRegisterFaceRequest(BaseModel):
    full_name: str
    display_name: Optional[str] = None

class UserRegisterFaceResponse(BaseModel):
    success: bool
    full_name: str
    display_name: Optional[str] = None
    message: str

class UserLoginFaceResponse(BaseModel):
    granted: bool
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    confidence: Optional[float] = None
    is_live: bool = True
    status: str
    message: str
    total_access: Optional[int] = None

class RegisteredUserItem(BaseModel):
    id: int
    full_name: str
    display_name: Optional[str] = None
    is_active: bool
    registered_at: datetime.datetime
    last_seen_at: Optional[datetime.datetime] = None
    total_access: int

    class Config:
        from_attributes = True

class RegisteredUsersListResponse(BaseModel):
    total: int
    users: List[RegisteredUserItem]
