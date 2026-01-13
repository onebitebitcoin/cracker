"""Address model"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database import Base


class Address(Base):
    """Bitcoin address model"""
    __tablename__ = "addresses"

    address = Column(String, primary_key=True)
    cluster_id = Column(String, ForeignKey("clusters.id"), nullable=True)
    balance = Column(Float, default=0.0)
    total_received = Column(Float, default=0.0)
    total_sent = Column(Float, default=0.0)
    tx_count = Column(Integer, default=0)
    first_seen = Column(String, nullable=True)
    last_seen = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    cluster = relationship("Cluster", back_populates="addresses")

    # Indexes
    __table_args__ = (
        Index('idx_addresses_cluster', 'cluster_id'),
        Index('idx_addresses_balance', 'balance'),
        Index('idx_addresses_cluster_balance', 'cluster_id', 'balance'),
    )

    def __repr__(self):
        return f"<Address {self.address[:10]}... balance={self.balance}>"
