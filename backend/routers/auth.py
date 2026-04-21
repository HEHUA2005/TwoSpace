from fastapi import APIRouter, HTTPException, status
from auth import authenticate, create_token, get_current_user, USERS
from schemas import LoginRequest, TokenOut, UserOut
from fastapi import Depends

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginRequest):
    user = authenticate(body.user_id, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户ID或密码错误")
    token = create_token(user["id"])
    return TokenOut(
        access_token=token,
        user=UserOut(id=user["id"], name=user["name"], avatar=user["avatar"]),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    return UserOut(id=current_user["id"], name=current_user["name"], avatar=current_user["avatar"])


@router.get("/users", response_model=list[UserOut])
def list_users():
    """登录页用：返回两个用户的基本信息（不含密码）"""
    return [
        UserOut(id=u["id"], name=u["name"], avatar=u["avatar"])
        for u in USERS.values()
    ]
