"""Transaction models"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database import Base


class Transaction(Base):
    """Bitcoin transaction model"""
    __tablename__ = "transactions"

    txid = Column(String, primary_key=True)
    block_height = Column(Integer, nullable=True)
    block_hash = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    fee = Column(Float, default=0.0)
    size = Column(Integer, default=0)
    input_count = Column(Integer, default=0)
    output_count = Column(Integer, default=0)
    total_input = Column(Float, default=0.0)
    total_output = Column(Float, default=0.0)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    inputs = relationship("TransactionInput", back_populates="transaction", cascade="all, delete-orphan")
    outputs = relationship("TransactionOutput", back_populates="transaction", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_transactions_block', 'block_height'),
        Index('idx_transactions_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<Transaction {self.txid[:10]}... block={self.block_height}>"


class TransactionInput(Base):
    """Transaction input model"""
    __tablename__ = "transaction_inputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    txid = Column(String, ForeignKey("transactions.txid"), nullable=False)
    vout_index = Column(Integer, nullable=True)
    prev_txid = Column(String, nullable=True)
    prev_vout = Column(Integer, nullable=True)
    address = Column(String, ForeignKey("addresses.address"), nullable=True)
    amount = Column(Float, default=0.0)
    script_sig = Column(String, nullable=True)
    sequence = Column(Integer, nullable=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="inputs")

    # Indexes
    __table_args__ = (
        Index('idx_tx_inputs_txid', 'txid'),
        Index('idx_tx_inputs_address', 'address'),
    )

    def __repr__(self):
        return f"<TransactionInput {self.txid[:10]}... addr={self.address[:10] if self.address else 'N/A'}>"


class TransactionOutput(Base):
    """Transaction output model"""
    __tablename__ = "transaction_outputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    txid = Column(String, ForeignKey("transactions.txid"), nullable=False)
    vout = Column(Integer, nullable=False)
    address = Column(String, ForeignKey("addresses.address"), nullable=True)
    amount = Column(Float, default=0.0)
    script_pubkey = Column(String, nullable=True)
    spent = Column(Integer, default=0)  # 0 = False, 1 = True
    spent_in_txid = Column(String, nullable=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="outputs")

    # Indexes
    __table_args__ = (
        Index('idx_tx_outputs_txid', 'txid'),
        Index('idx_tx_outputs_address', 'address'),
        Index('idx_tx_outputs_spent', 'spent'),
        Index('idx_tx_outputs_address_time', 'address', 'txid'),
    )

    def __repr__(self):
        return f"<TransactionOutput {self.txid[:10]}... vout={self.vout} addr={self.address[:10] if self.address else 'N/A'}>"
