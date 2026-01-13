"""Search API endpoint"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Address, Transaction, Cluster
from ...schemas.common import SearchResult
from ...utils.logger import logger

router = APIRouter()


@router.get("", response_model=List[SearchResult])
async def search(
    q: str = Query(..., min_length=1, description="검색 쿼리"),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="결과 개수")
):
    """
    통합 검색 (주소, 트랜잭션, 클러스터)

    Args:
        q: 검색 쿼리
        limit: 결과 개수
        db: Database session

    Returns:
        검색 결과 목록
    """
    logger.info(f"검색 요청: '{q}'")

    results: List[SearchResult] = []

    # Search addresses
    addresses = db.query(Address).filter(Address.address.like(f"%{q}%")).limit(limit // 3).all()
    for addr in addresses:
        results.append(SearchResult(
            type="address",
            id=addr.address,
            label=f"{addr.address[:20]}...",
            preview=f"잔액: {addr.balance} BTC, 트랜잭션: {addr.tx_count}개"
        ))

    # Search transactions
    transactions = db.query(Transaction).filter(Transaction.txid.like(f"%{q}%")).limit(limit // 3).all()
    for tx in transactions:
        results.append(SearchResult(
            type="transaction",
            id=tx.txid,
            label=f"{tx.txid[:20]}...",
            preview=f"블록: {tx.block_height}, 금액: {tx.total_output} BTC"
        ))

    # Search clusters
    clusters = db.query(Cluster).filter(
        (Cluster.id.like(f"%{q}%")) | (Cluster.label.like(f"%{q}%"))
    ).limit(limit // 3).all()
    for cluster in clusters:
        results.append(SearchResult(
            type="cluster",
            id=cluster.id,
            label=cluster.label or f"Cluster {cluster.id[:8]}...",
            preview=f"주소: {cluster.address_count}개, 잔액: {cluster.total_balance} BTC"
        ))

    logger.info(f"검색 완료: {len(results)}개 결과")
    return results[:limit]
