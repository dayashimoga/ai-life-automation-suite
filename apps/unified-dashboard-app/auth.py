"""
Shared Authentication Layer — JWT-based login/register with SQLite user store.
"""

import os
import sqlite3
import jwt
import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.hash import bcrypt

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET", "ai-suite-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

# ─── SQLite User Store ───────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


# ─── Pydantic Models ─────────────────────────────────────────


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


# ─── Helpers ─────────────────────────────────────────────────


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    return payload["sub"]


# ─── Routes ──────────────────────────────────────────────────


@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate):
    db = _get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ?", (user.username,)
    ).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed = bcrypt.hash(user.password)
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (user.username, hashed),
    )
    db.commit()
    db.close()

    token = create_token(user.username)
    return TokenResponse(access_token=token, username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    db = _get_db()
    row = db.execute(
        "SELECT * FROM users WHERE username = ?", (user.username,)
    ).fetchone()
    db.close()

    if not row or not bcrypt.verify(user.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.username)
    return TokenResponse(access_token=token, username=user.username)


@router.get("/me")
async def get_me(username: str = Depends(get_current_user)):
    return {"username": username}
