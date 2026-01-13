"""Transaction Pydantic schemas"""
from typing import Optional, List
from pydantic import BaseModel, Field


class TransactionInputResponse(BaseModel):
    """Transaction input response schema"""
    id: int
    txid: str
    vout_index: Optional[int] = None
    prev_txid: Optional[str] = None
    prev_vout: Optional[int] = None
    address: Optional[str] = None
    amount: float
    script_sig: Optional[str] = None
    sequence: Optional[int] = None

    class Config:
        from_attributes = True


class TransactionOutputResponse(BaseModel):
    """Transaction output response schema"""
    id: int
    txid: str
    vout: int
    address: Optional[str] = None
    amount: float
    script_pubkey: Optional[str] = None
    spent: int
    spent_in_txid: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Transaction response schema"""
    txid: str = Field(..., description="Transaction ID")
    block_height: Optional[int] = Field(None, description="Block height")
    block_hash: Optional[str] = Field(None, description="Block hash")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp")
    fee: float = Field(..., description="Transaction fee")
    size: int = Field(..., description="Transaction size in bytes")
    input_count: int = Field(..., description="Number of inputs")
    output_count: int = Field(..., description="Number of outputs")
    total_input: float = Field(..., description="Total input amount")
    total_output: float = Field(..., description="Total output amount")
    created_at: str = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True


class TransactionDetailResponse(BaseModel):
    """Transaction detail with inputs/outputs"""
    txid: str
    block_height: Optional[int] = None
    block_hash: Optional[str] = None
    timestamp: Optional[str] = None
    fee: float
    size: int
    input_count: int
    output_count: int
    total_input: float
    total_output: float
    inputs: List[TransactionInputResponse]
    outputs: List[TransactionOutputResponse]

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Transaction list item (simplified)"""
    txid: str
    timestamp: Optional[str] = None
    total_input: float
    total_output: float
    fee: float

    class Config:
        from_attributes = True
