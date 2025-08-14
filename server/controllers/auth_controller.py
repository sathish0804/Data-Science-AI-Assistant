from fastapi import APIRouter, Depends, HTTPException, Header

from models.auth_models import LoginRequest, TokenResponse, UserResponse
from services.auth_service import authenticate_user, generate_jwt, verify_jwt


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
  if not authenticate_user(req.email, req.password):
    raise HTTPException(status_code=401, detail="Invalid credentials")
  token = generate_jwt(req.email)
  return TokenResponse(access_token=token)


def get_current_user(authorization: str = Header(None)) -> UserResponse:
  if not authorization or not authorization.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Missing token")
  token = authorization.split(" ", 1)[1]
  email = verify_jwt(token)
  if not email:
    raise HTTPException(status_code=401, detail="Invalid or expired token")
  return UserResponse(email=email)


@router.get("/me", response_model=UserResponse)
async def me(user: UserResponse = Depends(get_current_user)):
  return user

from fastapi import APIRouter, Depends, HTTPException, Header

from models.auth_models import LoginRequest, TokenResponse, UserResponse
from services.auth_service import authenticate_user, generate_jwt, verify_jwt


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
  if not authenticate_user(req.email, req.password):
    raise HTTPException(status_code=401, detail="Invalid credentials")
  token = generate_jwt(req.email)
  return TokenResponse(access_token=token)


def get_current_user(authorization: str = Header(None)) -> UserResponse:
  if not authorization or not authorization.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Missing token")
  token = authorization.split(" ", 1)[1]
  email = verify_jwt(token)
  if not email:
    raise HTTPException(status_code=401, detail="Invalid or expired token")
  return UserResponse(email=email)


@router.get("/me", response_model=UserResponse)
async def me(user: UserResponse = Depends(get_current_user)):
  return user

