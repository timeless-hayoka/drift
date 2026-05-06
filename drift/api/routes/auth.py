"""Simple API key validation for the DRIFT API.

Reads the expected key from the DRIFT_API_KEY environment variable.
If the variable is unset, the API is open (demo mode).
"""

import os
from typing import Optional

from fastapi import Header, HTTPException, status

DRIFT_API_KEY = os.getenv("DRIFT_API_KEY", "")


async def verify_api_key(x_api_key: Optional[str] = Header(default=None, alias="x-api-key")) -> bool:
    """Validate the x-api-key header against DRIFT_API_KEY.

    Returns True when no key is configured or when the supplied key matches.
    Raises HTTPException 401 otherwise.
    """
    if not DRIFT_API_KEY:
        return True
    if not x_api_key or x_api_key != DRIFT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True
