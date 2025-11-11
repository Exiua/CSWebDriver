from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

class GetNetworkUrlsRequest(BaseModel):
    url: str = Field(..., description="The URL to retrieve.")
    timeout: float = Field(5, description="Timeout in seconds for the request. (default: 5 seconds)")

class GetNetworkUrlResponse(BaseModel):
    urls: list[str] = Field(..., description="List of network URLs retrieved during the page load.")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message describing what went wrong.")
    details: Optional[str] = Field(None, description="Additional details about the error.")