from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from auth import decode_token

security = HTTPBearer()


def get_current_user(token=Depends(security)):
    data = decode_token(token.credentials)
    if not data:
        raise HTTPException(401, "Invalid token")
    return data


def require_role(roles):
    def wrapper(user=Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(403, "Forbidden")
        return user
    return wrapper
