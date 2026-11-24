import sys
import os
from pathlib import Path

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
import re
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import engine, Base, get_db
from app.db.models import AdminUser, AccessLog, RegisteredUser, RevokedToken, SystemSetting
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_admin,
    get_optional_admin,
    revoke_token
)
from app.schemas import (
    HealthResponse,
    ConfigResponse,
    SpoofSettingRequest,
    SpoofSettingResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    VerifyResponse,
    EnrollResponse,
    IdentitiesResponse,
    DeleteIdentityResponse,
    AccessLogsListResponse,
    AccessLogItem,
    AnalyticsSummaryResponse,
    UserRegisterFaceResponse,
    UserLoginFaceResponse,
    RegisteredUsersListResponse,
    RegisteredUserItem,
)
from app.services.face_service import face_service

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB maximum upload limit

async def read_and_validate_image(file: UploadFile) -> bytes:
    """Security helper: validates MIME type and enforces file size limit to prevent DoS."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a supported image format (JPEG, PNG, WebP)"
        )
    content = await file.read(MAX_FILE_SIZE_BYTES + 1)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image payload is empty"
        )
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file exceeds 10MB limit"
        )
    return content

def sanitize_identity_name(name: str) -> str:
    """Security helper: prevents path traversal and injection in identity names."""
    cleaned = name.strip()
    if not re.match(r"^[a-zA-Z0-9_\- ]{2,50}$", cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identity name must be 2-50 characters containing only letters, numbers, hyphens, and underscores."
        )
    return cleaned.replace(" ", "_")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite Database Schema
    print("[FastAPI] Initializing SQLite relational tables...")
    Base.metadata.create_all(bind=engine)

    # 2. Pre-warm Neural Networks & Faiss Store
    print("[FastAPI] Pre-warming MTCNN, FaceNet, and Faiss Vector Store...")
    face_service.load_models()
    
    # 3. Create default admin user if none exists
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not existing_admin:
            default_admin = AdminUser(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="SUPER_ADMIN"
            )
            db.add(default_admin)
            db.commit()
            print("[FastAPI] Default admin created: username='admin', password='admin123'")
    finally:
        db.close()

    yield
    print("[FastAPI] Server shutting down cleanly.")

app = FastAPI(
    title="Face Recognition & Access Control API",
    description="Enterprise Multimodal Biometric Security API with MTCNN, FaceNet, Faiss, Anti-Spoofing Liveness, and Audit Logs.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend clients (Supports local dev, Render subdomains, and custom env origins)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if allowed_origins_env:
    for origin in allowed_origins_env.split(","):
        cleaned = origin.strip()
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 1. GENERAL & DIAGNOSTICS
# ============================================================================

@app.get("/", tags=["General"])
def read_root():
    return {
        "service": "Enterprise Face Recognition API",
        "version": "2.0.0",
        "status": "online",
        "documentation": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["Diagnostics"])
def health_check():
    """Returns system status, active models, hardware device, and vector counts."""
    stats = face_service.get_stats()
    return HealthResponse(
        status="ok",
        models_loaded=stats["models_loaded"],
        total_embeddings=stats["total_embeddings"],
        total_unique_identities=stats["total_unique_identities"],
        device=stats["device"],
        message="Biometric engine and database are operational"
    )

def is_spoof_detection_enabled(db: Session) -> bool:
    """Helper to check persistent system setting for spoof detection."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "spoof_detection_enabled").first()
    if setting is not None:
        return setting.value.lower() in ("true", "1", "yes")
    return True

@app.get("/config", response_model=ConfigResponse, tags=["Diagnostics"])
def get_system_config(db: Session = Depends(get_db)):
    """Returns active hyperparameters, L2 thresholds, and model details."""
    stats = face_service.get_stats()
    return ConfigResponse(
        threshold=stats["threshold"],
        embedding_dim=stats["embedding_dim"],
        device=stats["device"],
        model_name=stats["model_name"],
        liveness_enabled=is_spoof_detection_enabled(db)
    )

@app.post("/admin/spoof-detection", response_model=SpoofSettingResponse, tags=["Administration"])
def toggle_spoof_detection(
    payload: SpoofSettingRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin-only: Enables or disables global Anti-Spoofing / Liveness detection across the system.
    Persisted to the SQLite database.
    """
    setting = db.query(SystemSetting).filter(SystemSetting.key == "spoof_detection_enabled").first()
    if not setting:
        setting = SystemSetting(key="spoof_detection_enabled", value=str(payload.enabled).lower())
        db.add(setting)
    else:
        setting.value = str(payload.enabled).lower()
    db.commit()

    action = "enabled" if payload.enabled else "disabled"
    return SpoofSettingResponse(
        liveness_enabled=payload.enabled,
        message=f"Anti-spoofing detection has been successfully {action}."
    )

# ============================================================================
# 2. AUTHENTICATION & SESSION MANAGEMENT
# ============================================================================

@app.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
def register_admin(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
    current_admin: Optional[dict] = Depends(get_optional_admin)
):
    """
    Registers a new security administrator account.
    Security: Protected. If any admin exists, requires an existing SUPER_ADMIN.
    """
    admin_count = db.query(AdminUser).count()
    if admin_count > 0:
        if not current_admin or current_admin.get("role") != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative registration is restricted. Super Admin credentials required."
            )

    if db.query(AdminUser).filter(AdminUser.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    new_admin = AdminUser(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role="ADMIN"
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    token = create_access_token({"sub": new_admin.username, "role": new_admin.role})
    return TokenResponse(access_token=token, username=new_admin.username, role=new_admin.role)

@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login_admin(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticates admin and issues signed JWT bearer token."""
    user = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token, username=user.username, role=user.role)

@app.post("/auth/logout", tags=["Authentication"])
def logout_admin(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Secure server-side logout:
    Adds the JWT token to the revoked tokens blacklist so it cannot be reused.
    """
    token = admin.get("token")
    exp = admin.get("exp")
    expires_at = datetime.datetime.utcfromtimestamp(exp) if exp else datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    revoke_token(token, expires_at, db)
    return {
        "success": True,
        "message": f"Successfully logged out. Session for '{admin.get('username')}' has been revoked."
    }

# ============================================================================
# 3. BIOMETRIC VERIFICATION & ENROLLMENT
# ============================================================================

@app.post("/verify", response_model=VerifyResponse, tags=["Biometrics"])
async def verify_identity(
    request: Request,
    file: UploadFile = File(..., description="Facial snapshot from live camera"),
    threshold: Optional[float] = None,
    check_liveness: bool = Query(True, description="Enable anti-spoofing liveness filter"),
    db: Session = Depends(get_db)
):
    """
    Core Access Verification Pipeline:
    1. Validates image payload and enforces size limits (< 10MB)
    2. Runs passive liveness check (Anti-spoofing)
    3. Crops face with MTCNN & extracts 512-D embedding with FaceNet
    4. Searches nearest neighbor in Faiss Vector Database
    5. Automatically logs the audit event to SQLite database
    """
    image_bytes = await read_and_validate_image(file)

    # Check effective spoof detection setting (global setting && request param)
    effective_liveness = check_liveness and is_spoof_detection_enabled(db)

    # Perform Verification via FaceService
    result = face_service.verify_face(
        image_bytes=image_bytes,
        threshold=threshold,
        check_liveness=effective_liveness
    )

    # Persistent Audit Log insertion
    client_ip = request.client.host if request.client else "unknown"
    log_entry = AccessLog(
        status=result["status"],
        matched_identity=result.get("identity"),
        l2_distance=result.get("distance"),
        confidence_score=result.get("confidence"),
        is_live=result.get("is_live", True),
        liveness_score=result.get("liveness_score"),
        ip_address=client_ip,
        message=result.get("message")
    )
    db.add(log_entry)
    db.commit()

    return VerifyResponse(**result)

@app.post("/enroll", response_model=EnrollResponse, tags=["Biometrics"])
async def enroll_new_identity(
    file: UploadFile = File(..., description="Clear facial image for employee enrollment"),
    identity_name: str = Form(..., description="Unique person name / Employee badge ID"),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Enrolls a new employee into the vector database (Requires Admin JWT):
    - Validates image payload and sanitized identity name
    - Extracts 512-D embedding
    - Adds to Faiss index and updates mapping
    - Persists immediately to disk
    """
    clean_name = sanitize_identity_name(identity_name)
    image_bytes = await read_and_validate_image(file)

    result = face_service.enroll_face(image_bytes=image_bytes, identity_name=clean_name)
    if not result["success"]:
        err_status = status.HTTP_409_CONFLICT if result.get("already_enrolled") else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(
            status_code=err_status,
            detail=result["message"]
        )

    return EnrollResponse(**result)

@app.get("/identities", response_model=IdentitiesResponse, tags=["Biometrics"])
def list_enrolled_identities():
    """Lists all enrolled employees/identities currently active in the Faiss database."""
    identities = face_service.get_identities()
    total_embeddings = face_service.faiss_manager.index.ntotal if face_service.faiss_manager else 0
    return IdentitiesResponse(
        total_count=total_embeddings,
        unique_count=len(identities),
        unique_identities=identities
    )

@app.delete("/identities/{identity_name}", response_model=DeleteIdentityResponse, tags=["Biometrics"])
def delete_enrolled_identity(
    identity_name: str,
    current_admin: dict = Depends(get_current_admin)
):
    """De-registers an employee and rebuilds the Faiss index (Requires Admin JWT)."""
    result = face_service.delete_identity(identity_name=identity_name)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    return DeleteIdentityResponse(**result)

# ============================================================================
# 4. AUDIT LOGS & ANALYTICS
# ============================================================================

@app.get("/logs", response_model=AccessLogsListResponse, tags=["Audit & Security"])
def get_access_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by GRANTED, DENIED, SPOOF_DETECTED"),
    db: Session = Depends(get_db)
):
    """Retrieves paginated verification audit logs with optional status filtering."""
    query = db.query(AccessLog)
    if status_filter:
        query = query.filter(AccessLog.status == status_filter.upper())

    total = query.count()
    offset = (page - 1) * limit
    logs = query.order_by(AccessLog.timestamp.desc()).offset(offset).limit(limit).all()

    return AccessLogsListResponse(
        total=total,
        page=page,
        limit=limit,
        logs=logs
    )

@app.get("/analytics/summary", response_model=AnalyticsSummaryResponse, tags=["Audit & Security"])
def get_analytics_summary(db: Session = Depends(get_db)):
    """Computes real-time KPI metrics for dashboard visualizations."""
    total = db.query(AccessLog).count()
    granted = db.query(AccessLog).filter(AccessLog.status == "GRANTED").count()
    denied = db.query(AccessLog).filter(AccessLog.status == "DENIED").count()
    spoofs = db.query(AccessLog).filter(AccessLog.status == "SPOOF_DETECTED").count()
    no_faces = db.query(AccessLog).filter(AccessLog.status == "NO_FACE").count()

    pass_rate = round((granted / total * 100), 2) if total > 0 else 0.0
    enrolled_count = len(face_service.get_identities())

    return AnalyticsSummaryResponse(
        total_verifications=total,
        granted_count=granted,
        denied_count=denied,
        spoof_detected_count=spoofs,
        no_face_count=no_faces,
        pass_rate_percentage=pass_rate,
        enrolled_identities_count=enrolled_count,
        active_device=str(face_service.device)
    )

# ============================================================================
# 5. USER PORTAL  (public self-registration + face-based login)
# ============================================================================

@app.post("/user/register", response_model=UserRegisterFaceResponse, tags=["User Portal"])
async def user_register(
    request: Request,
    file: UploadFile = File(..., description="Clear frontal face photo"),
    full_name: str = Form(..., description="Your full name (used as identity key)"),
    display_name: Optional[str] = Form(None, description="Optional friendly display name"),
    db: Session = Depends(get_db)
):
    """
    Public self-registration endpoint.
    1. Validates and sanitizes name.
    2. Validates image payload and size limit (< 10MB).
    3. Checks the name is not already registered.
    4. Enrolls the face embedding into Faiss.
    5. Creates a RegisteredUser row in SQLite.
    """
    clean_name = sanitize_identity_name(full_name)

    # Prevent duplicate registration
    existing = db.query(RegisteredUser).filter(RegisteredUser.full_name == clean_name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"'{clean_name}' is already registered. Please sign in instead."
        )

    image_bytes = await read_and_validate_image(file)

    # Enroll into Faiss (with duplicate biometric check)
    result = face_service.enroll_face(image_bytes=image_bytes, identity_name=clean_name)
    if not result["success"]:
        err_status = status.HTTP_409_CONFLICT if result.get("already_enrolled") else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=err_status, detail=result["message"])

    # Persist to SQLite
    friendly = (display_name or full_name).strip()
    user_row = RegisteredUser(
        full_name=clean_name,
        display_name=friendly,
        registered_at=datetime.datetime.utcnow()
    )
    db.add(user_row)
    db.commit()

    return UserRegisterFaceResponse(
        success=True,
        full_name=clean_name,
        display_name=friendly,
        message=f"Welcome, {friendly}! Your face has been registered successfully."
    )


@app.post("/user/login", response_model=UserLoginFaceResponse, tags=["User Portal"])
async def user_login(
    request: Request,
    file: UploadFile = File(..., description="Live face snapshot for verification"),
    check_liveness: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Public face-based login (no password needed).
    Runs liveness check → FaceNet → Faiss nearest-neighbour → returns GRANTED / DENIED.
    Also updates last_seen_at and total_access on success.
    """
    image_bytes = await read_and_validate_image(file)

    # Check effective spoof detection setting (global setting && request param)
    effective_liveness = check_liveness and is_spoof_detection_enabled(db)

    result = face_service.verify_face(
        image_bytes=image_bytes,
        check_liveness=effective_liveness
    )

    # Log the access attempt
    client_ip = request.client.host if request.client else "unknown"
    log_entry = AccessLog(
        status=result["status"],
        matched_identity=result.get("identity"),
        l2_distance=result.get("distance"),
        confidence_score=result.get("confidence"),
        is_live=result.get("is_live", True),
        liveness_score=result.get("liveness_score"),
        ip_address=client_ip,
        message=result.get("message")
    )
    db.add(log_entry)
    db.commit()

    # Update user record stats if granted
    display_name = None
    total_access = None
    if result["status"] == "GRANTED" and result.get("identity"):
        user_row = db.query(RegisteredUser).filter(
            RegisteredUser.full_name == result["identity"]
        ).first()
        if user_row:
            user_row.last_seen_at = datetime.datetime.utcnow()
            user_row.total_access = (user_row.total_access or 0) + 1
            db.commit()
            db.refresh(user_row)
            display_name = user_row.display_name
            total_access = user_row.total_access

    return UserLoginFaceResponse(
        granted=result["status"] == "GRANTED",
        full_name=result.get("identity"),
        display_name=display_name,
        confidence=result.get("confidence"),
        is_live=result.get("is_live", True),
        status=result["status"],
        message=result.get("message", ""),
        total_access=total_access
    )


@app.get("/user/list", response_model=RegisteredUsersListResponse, tags=["User Portal"])
def list_registered_users(db: Session = Depends(get_db)):
    """Returns all self-registered users (no auth needed — public leaderboard)."""
    users = db.query(RegisteredUser).order_by(RegisteredUser.registered_at.desc()).all()
    return RegisteredUsersListResponse(total=len(users), users=users)


@app.delete("/user/{full_name}", tags=["User Portal"])
def delete_registered_user(
    full_name: str,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: remove a registered user and their Faiss embedding."""
    user_row = db.query(RegisteredUser).filter(RegisteredUser.full_name == full_name).first()
    if not user_row:
        raise HTTPException(status_code=404, detail=f"User '{full_name}' not found")

    # Remove from Faiss
    face_service.delete_identity(identity_name=full_name)

    db.delete(user_row)
    db.commit()
    return {"success": True, "message": f"User '{full_name}' removed from system"}
