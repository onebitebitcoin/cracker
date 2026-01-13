"""Address API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Address, Transaction, TransactionInput, TransactionOutput
from ...schemas.address import AddressResponse, AddressListResponse
from ...schemas.transaction import TransactionListResponse
from ...schemas.common import PaginatedResponse
from ...utils.logger import logger
from ...utils.exceptions import AddressNotFoundException

router = APIRouter()


@router.get("/{address}", response_model=AddressResponse)
async def get_address(address: str, db: Session = Depends(get_db)):
    """
    주소 상세 정보 조회

    Args:
        address: Bitcoin 주소
        db: Database session

    Returns:
        주소 상세 정보

    Raises:
        HTTPException: 주소를 찾을 수 없는 경우 404
    """
    logger.info(f"주소 조회 요청: {address}")

    addr = db.query(Address).filter(Address.address == address).first()

    if not addr:
        logger.warning(f"주소를 찾을 수 없음: {address}")
        raise HTTPException(
            status_code=404,
            detail={
                "message": "주소를 찾을 수 없습니다",
                "error": f"Address not found: {address}",
                "type": "AddressNotFound"
            }
        )

    logger.info(f"주소 조회 성공: {address}")
    return addr


@router.get("/{address}/transactions", response_model=PaginatedResponse[TransactionListResponse])
async def get_address_transactions(
    address: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="결과 개수"),
    offset: int = Query(0, ge=0, description="시작 위치")
):
    """
    주소의 트랜잭션 히스토리 조회

    Args:
        address: Bitcoin 주소
        limit: 페이지 크기
        offset: 시작 위치
        db: Database session

    Returns:
        트랜잭션 목록 (페이지네이션)

    Raises:
        HTTPException: 주소를 찾을 수 없는 경우 404
    """
    logger.info(f"주소 트랜잭션 조회: {address}, limit={limit}, offset={offset}")

    # Check if address exists
    addr = db.query(Address).filter(Address.address == address).first()
    if not addr:
        raise HTTPException(status_code=404, detail="주소를 찾을 수 없습니다")

    # Get transactions where address is in inputs or outputs
    tx_ids_from_inputs = db.query(TransactionInput.txid).filter(
        TransactionInput.address == address
    ).distinct()

    tx_ids_from_outputs = db.query(TransactionOutput.txid).filter(
        TransactionOutput.address == address
    ).distinct()

    # Union the two queries
    all_txids = tx_ids_from_inputs.union(tx_ids_from_outputs)

    # Get transaction details
    total = all_txids.count()
    txids = [row[0] for row in all_txids.limit(limit).offset(offset).all()]

    transactions = db.query(Transaction).filter(Transaction.txid.in_(txids)).all()

    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    current_page = (offset // limit) + 1

    logger.info(f"트랜잭션 조회 완료: {len(transactions)}개")

    return PaginatedResponse(
        data=[TransactionListResponse.from_orm(tx) for tx in transactions],
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/{address}/cluster")
async def get_address_cluster(address: str, db: Session = Depends(get_db)):
    """
    주소가 속한 클러스터 정보 조회

    Args:
        address: Bitcoin 주소
        db: Database session

    Returns:
        클러스터 정보

    Raises:
        HTTPException: 주소를 찾을 수 없는 경우 404
    """
    logger.info(f"주소 클러스터 조회: {address}")

    addr = db.query(Address).filter(Address.address == address).first()
    if not addr:
        raise HTTPException(status_code=404, detail="주소를 찾을 수 없습니다")

    if not addr.cluster_id:
        logger.info(f"주소가 클러스터에 속하지 않음: {address}")
        return {
            "address": address,
            "cluster_id": None,
            "message": "이 주소는 클러스터에 속하지 않습니다"
        }

    # Get cluster info
    from ...models import Cluster
    cluster = db.query(Cluster).filter(Cluster.id == addr.cluster_id).first()

    if not cluster:
        logger.warning(f"클러스터를 찾을 수 없음: {addr.cluster_id}")
        return {
            "address": address,
            "cluster_id": addr.cluster_id,
            "message": "클러스터 정보를 찾을 수 없습니다"
        }

    # Get all addresses in the cluster
    cluster_addresses = db.query(Address).filter(Address.cluster_id == addr.cluster_id).all()

    logger.info(f"클러스터 조회 완료: {cluster.label}, {len(cluster_addresses)}개 주소")

    return {
        "address": address,
        "cluster_id": cluster.id,
        "cluster_label": cluster.label,
        "cluster_address_count": len(cluster_addresses),
        "cluster_balance": cluster.total_balance,
        "addresses": [a.address for a in cluster_addresses[:20]]  # Limit to 20
    }
