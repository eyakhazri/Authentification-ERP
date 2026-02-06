from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from src.core.security import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def admin_only(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    if payload.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin uniquement")

    return payload
