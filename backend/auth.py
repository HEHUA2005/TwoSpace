import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30

# 两个用户硬编码，密码哈希从环境变量读取
# 生成哈希：python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"
USERS = {
    1: {
        "id": 1,
        "username": "user1",
        "name": os.getenv("USER1_NAME", "TA"),
        "avatar": os.getenv("USER1_AVATAR", "/uploads/avatar1.jpg"),
        "password_hash": os.getenv("USER1_PASSWORD_HASH", ""),
    },
    2: {
        "id": 2,
        "username": "user2",
        "name": os.getenv("USER2_NAME", "我"),
        "avatar": os.getenv("USER2_AVATAR", "/uploads/avatar2.jpg"),
        "password_hash": os.getenv("USER2_PASSWORD_HASH", ""),
    },
}

bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_id(user_id: int) -> Optional[dict]:
    return USERS.get(user_id)


def authenticate(user_id: int, password: str) -> Optional[dict]:
    user = USERS.get(user_id)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 无效")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user
