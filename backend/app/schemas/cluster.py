"""Cluster Pydantic schemas"""
from typing import Optional, List
from pydantic import BaseModel, Field


class AddressInCluster(BaseModel):
    """Address in cluster (simplified)"""
    address: str
    balance: float
    tx_count: int

    class Config:
        from_attributes = True


class ClusterResponse(BaseModel):
    """Cluster response schema"""
    id: str = Field(..., description="Cluster ID (UUID)")
    label: Optional[str] = Field(None, description="Cluster label")
    address_count: int = Field(..., description="Number of addresses in cluster")
    total_balance: float = Field(..., description="Total balance in BTC")
    total_received: float = Field(..., description="Total received in BTC")
    total_sent: float = Field(..., description="Total sent in BTC")
    tx_count: int = Field(..., description="Total number of transactions")
    first_seen: Optional[str] = Field(None, description="First seen timestamp")
    last_seen: Optional[str] = Field(None, description="Last seen timestamp")
    created_at: str = Field(..., description="Created timestamp")
    updated_at: str = Field(..., description="Updated timestamp")
    addresses: List[AddressInCluster] = Field(default_factory=list, description="Addresses in this cluster")

    class Config:
        from_attributes = True


class ClusterListResponse(BaseModel):
    """Cluster list item (simplified)"""
    id: str
    label: Optional[str] = None
    address_count: int
    total_balance: float
    tx_count: int

    class Config:
        from_attributes = True


class ClusterStatsResponse(BaseModel):
    """Cluster statistics"""
    id: str
    label: Optional[str] = None
    address_count: int
    total_balance: float
    total_received: float
    total_sent: float
    tx_count: int
    avg_balance_per_address: float

    class Config:
        from_attributes = True


class ClusterDistribution(BaseModel):
    """Cluster size distribution"""
    range: str = Field(..., description="Size range (e.g., '1-10')")
    count: int = Field(..., description="Number of clusters in this range")

    class Config:
        from_attributes = True
