from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.schemas.login import (
    AdminLogin,
    Token,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from src.app.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    decode_token,
    generate_reset_code,
)
from src.app.database import get_db
from src.app.email_service import send_reset_code_email
from src.app.config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def normalize_email(email: str) -> str:
    return email.strip().lower()


def debug_log(message, data=None):
    print(f"[DEBUG] {message}")
    if data is not None:
        print(f"        → {data}")


# --------------------------------------------------
# Login
# --------------------------------------------------

@router.post("/login", response_model=Token)
async def login(credentials: AdminLogin):
    db = get_db()

    email = normalize_email(credentials.email)
    debug_log("Login attempt", email)

    admin = await db.admin.find_one({"email": email})
    debug_log("Admin found", admin)

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(credentials.password, admin["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not admin.get("is_active", True):
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated"
        )

    if admin.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Insufficient privileges"
        )

    access_token = create_access_token(
        data={
            "sub": admin["email"],
            "role": admin["role"],
            "id": str(admin["_id"]),
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": admin["email"],
            "role": admin["role"],
            "id": str(admin["_id"]),
        },
    }


# --------------------------------------------------
# Forgot password
# --------------------------------------------------

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
):
    db = get_db()
    email = normalize_email(request.email)

    admin = await db.admin.find_one({
        "email": email,
        "role": "admin",
    })
    debug_log("Forgot-password admin search", admin)

    # Security: do NOT reveal if admin exists
    if not admin:
        return {
            "message": (
                "If an admin account exists with this email, "
                "a reset code will be sent"
            )
        }

    reset_code = generate_reset_code()
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.RESET_CODE_EXPIRY_MINUTES
    )

    await db.password_resets.insert_one({
        "email": email,
        "code": reset_code,
        "expires_at": expires_at,
        "used": False,
        "created_at": datetime.utcnow(),
    })

    background_tasks.add_task(
        send_reset_code_email,
        email,
        reset_code,
    )

    return {
        "message": (
            "If an admin account exists with this email, "
            "a reset code will be sent"
        )
    }


# --------------------------------------------------
# Verify reset code
# --------------------------------------------------

@router.post("/verify-reset-code")
async def verify_reset_code(email: str, code: str):
    db = get_db()
    email = normalize_email(email)

    reset_doc = await db.password_resets.find_one({
        "email": email,
        "code": code,
        "used": False,
        "expires_at": {"$gt": datetime.utcnow()},
    })

    if not reset_doc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset code",
        )

    return {"valid": True, "email": email}


# --------------------------------------------------
# Reset password
# --------------------------------------------------

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    db = get_db()
    email = normalize_email(request.email)

    reset_doc = await db.password_resets.find_one({
        "email": email,
        "code": request.code,
        "used": False,
        "expires_at": {"$gt": datetime.utcnow()},
    })

    if not reset_doc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset code",
        )

    new_password_hash = get_password_hash(request.new_password)

    result = await db.admin.update_one(
        {"email": email},
        {
            "$set": {
                "hashed_password": new_password_hash,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Admin not found",
        )

    await db.password_resets.update_one(
        {"_id": reset_doc["_id"]},
        {
            "$set": {
                "used": True,
                "used_at": datetime.utcnow(),
            }
        },
    )

    return {
        "message": "Password reset successful. You can now login."
    }


# --------------------------------------------------
# Auth dependency
# --------------------------------------------------

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    payload = decode_token(credentials.credentials)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return payload


@router.get("/me")
async def get_current_user(
    current_user: dict = Depends(get_current_admin),
):
    return {
        "email": current_user["sub"],
        "role": current_user["role"],
        "id": current_user["id"],
    }
