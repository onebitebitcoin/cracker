"""Address Pydantic schemas"""
from typing import Optional
from pydantic import BaseModel, Field


class AddressResponse(BaseModel):
    """Address response schema"""
    address: str = Field(..., description="Bitcoin address")
    cluster_id: Optional[str] = Field(None, description="Cluster ID")
    balance: float = Field(..., description="Current balance in BTC")
    total_received: float = Field(..., description="Total received in BTC")
    total_sent: float = Field(..., description="Total sent in BTC")
    tx_count: int = Field(..., description="Number of transactions")
    first_seen: Optional[str] = Field(None, description="First seen timestamp")
    last_seen: Optional[str] = Field(None, description="Last seen timestamp")
    created_at: str = Field(..., description="Created timestamp")
    updated_at: str = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True


class AddressListResponse(BaseModel):
    """Address list item (simplified)"""
    address: str
    balance: float
    tx_count: int
    cluster_id: Optional[str] = None

    class Config:
        from_attributes = True


class AddressStatsResponse(BaseModel):
    """Address statistics"""
    address: str
    balance: float
    total_received: float
    total_sent: float
    tx_count: int
    cluster_size: Optional[int] = Field(None, description="Number of addresses in cluster")

    class Config:
        from_attributes = True
