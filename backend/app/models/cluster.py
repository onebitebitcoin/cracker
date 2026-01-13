"""Cluster models"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database import Base


class Cluster(Base):
    """Cluster model"""
    __tablename__ = "clusters"

    id = Column(String, primary_key=True)  # UUID를 TEXT로 저장
    label = Column(String, nullable=True)
    address_count = Column(Integer, default=0)
    total_balance = Column(Float, default=0.0)
    total_received = Column(Float, default=0.0)
    total_sent = Column(Float, default=0.0)
    tx_count = Column(Integer, default=0)
    first_seen = Column(String, nullable=True)
    last_seen = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    addresses = relationship("Address", back_populates="cluster")

    # Indexes
    __table_args__ = (
        Index('idx_clusters_address_count', 'address_count'),
        Index('idx_clusters_balance', 'total_balance'),
    )

    def __repr__(self):
        return f"<Cluster {self.id[:8]}... addrs={self.address_count}>"


class ClusterEdge(Base):
    """Cluster edge model (클러스터 간 트랜잭션 관계)"""
    __tablename__ = "cluster_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_cluster_id = Column(String, ForeignKey("clusters.id"), nullable=False)
    target_cluster_id = Column(String, ForeignKey("clusters.id"), nullable=False)
    tx_count = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    first_tx_timestamp = Column(String, nullable=True)
    last_tx_timestamp = Column(String, nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_cluster_edges_source', 'source_cluster_id'),
        Index('idx_cluster_edges_target', 'target_cluster_id'),
    )

    def __repr__(self):
        return f"<ClusterEdge {self.source_cluster_id[:8]}... -> {self.target_cluster_id[:8]}... txs={self.tx_count}>"
