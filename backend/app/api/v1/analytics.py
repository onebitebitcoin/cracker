"""Analytics API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...database import get_db
from ...models import Address, Transaction, Cluster
from ...schemas.cluster import ClusterDistribution
from ...utils.logger import logger

router = APIRouter()


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """
    전체 시스템 통계

    Args:
        db: Database session

    Returns:
        시스템 통계 정보
    """
    logger.info("전체 통계 조회 요청")

    # Count totals
    total_addresses = db.query(func.count(Address.address)).scalar()
    total_clusters = db.query(func.count(Cluster.id)).scalar()
    total_transactions = db.query(func.count(Transaction.txid)).scalar()

    # Sum balances
    total_balance = db.query(func.sum(Address.balance)).scalar() or 0.0

    # Average cluster size
    avg_cluster_size = db.query(func.avg(Cluster.address_count)).scalar() or 0.0

    # Largest cluster
    largest_cluster = db.query(Cluster).order_by(Cluster.address_count.desc()).first()

    logger.info(f"통계 조회 완료: {total_addresses}개 주소, {total_clusters}개 클러스터")

    return {
        "total_addresses": total_addresses,
        "total_clusters": total_clusters,
        "total_transactions": total_transactions,
        "total_balance": round(total_balance, 8),
        "avg_cluster_size": round(avg_cluster_size, 2),
        "largest_cluster": {
            "id": largest_cluster.id if largest_cluster else None,
            "label": largest_cluster.label if largest_cluster else None,
            "address_count": largest_cluster.address_count if largest_cluster else 0
        } if largest_cluster else None
    }


@router.get("/cluster-distribution", response_model=list[ClusterDistribution])
async def get_cluster_distribution(db: Session = Depends(get_db)):
    """
    클러스터 크기 분포

    Args:
        db: Database session

    Returns:
        클러스터 크기별 분포
    """
    logger.info("클러스터 분포 조회 요청")

    # Define size ranges
    ranges = [
        ("1", 1, 1),
        ("2-5", 2, 5),
        ("6-10", 6, 10),
        ("11-20", 11, 20),
        ("21-50", 21, 50),
        ("51+", 51, 1000000)
    ]

    distribution = []

    for range_label, min_size, max_size in ranges:
        count = db.query(Cluster).filter(
            Cluster.address_count >= min_size,
            Cluster.address_count <= max_size
        ).count()

        distribution.append(ClusterDistribution(
            range=range_label,
            count=count
        ))

    logger.info(f"클러스터 분포 조회 완료: {len(distribution)}개 범위")
    return distribution


@router.get("/top-addresses")
async def get_top_addresses(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    잔액 상위 주소 목록

    Args:
        limit: 결과 개수
        db: Database session

    Returns:
        상위 주소 목록
    """
    logger.info(f"상위 주소 조회: top {limit}")

    addresses = db.query(Address).order_by(Address.balance.desc()).limit(limit).all()

    return [{
        "address": addr.address,
        "balance": addr.balance,
        "tx_count": addr.tx_count,
        "cluster_id": addr.cluster_id
    } for addr in addresses]


@router.get("/top-clusters")
async def get_top_clusters(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    잔액 상위 클러스터 목록

    Args:
        limit: 결과 개수
        db: Database session

    Returns:
        상위 클러스터 목록
    """
    logger.info(f"상위 클러스터 조회: top {limit}")

    clusters = db.query(Cluster).order_by(Cluster.total_balance.desc()).limit(limit).all()

    return [{
        "id": cluster.id,
        "label": cluster.label,
        "address_count": cluster.address_count,
        "total_balance": cluster.total_balance,
        "tx_count": cluster.tx_count
    } for cluster in clusters]
