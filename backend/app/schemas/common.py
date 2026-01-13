"""Common Pydantic schemas"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema"""
    data: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(50, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = "error"
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Any] = Field(None, description="Additional error details")

    class Config:
        from_attributes = True


class SuccessResponse(BaseModel):
    """Success response schema"""
    status: str = "success"
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Search result item"""
    type: str = Field(..., description="Result type: address, transaction, cluster")
    id: str = Field(..., description="Item ID")
    label: Optional[str] = Field(None, description="Display label")
    preview: Optional[str] = Field(None, description="Preview text")

    class Config:
        from_attributes = True


class GraphNode(BaseModel):
    """Graph node schema"""
    id: str = Field(..., description="Node ID")
    type: str = Field(..., description="Node type: address or transaction")
    label: str = Field(..., description="Node label")
    balance: Optional[float] = Field(None, description="Balance (for address nodes)")
    cluster_id: Optional[str] = Field(None, description="Cluster ID")

    class Config:
        from_attributes = True


class GraphEdge(BaseModel):
    """Graph edge schema"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    amount: float = Field(..., description="Transaction amount")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp")

    class Config:
        from_attributes = True


class GraphData(BaseModel):
    """Graph data schema"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]

    class Config:
        from_attributes = True
