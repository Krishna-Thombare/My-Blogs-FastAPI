from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings

# Create a secure password hashing configuration using the recommended algorithm
password_hash = PasswordHash.recommended()

# Configure OAuth2 to extract Bearer tokens from requests
# The client gets the token from this endpoint
oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/users/token")

# Hash a plain-text password before storing it in the database
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Verify a plain-text password against the hashed password stored in the database
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# Create Access Token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""

    # Make a copy so the original data is not modified
    to_encode = data.copy()

    # Set custom expiration time if provided
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        # Or, use the default expiration time from settings
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    # Add expiration time to the JWT payload
    to_encode.update({"exp": expire})

    # Encode and sign the JWT using the secret key and algorithm
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )

    return encoded_jwt

# Verify Access Token
def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user id) if valid."""

    try:
        # Decode and verify the JWT using the secret key and algorithm
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],

            # Require expiration time and user ID in the token
            options={"require": ["exp", "sub"]}
        )

    # Return None if the token is invalid, expired, or malformed
    except jwt.InvalidTokenError:
        return None
    else:
        # Return the user ID stored in the "sub" field
        return payload.get("sub")

