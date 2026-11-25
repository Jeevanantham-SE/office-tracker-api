import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException, status

load_dotenv()

EXPECTED_API_KEY = os.getenv("API_KEY", "dev-office-key-123")


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if not x_api_key or x_api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )
    return x_api_key