"""Cluster API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Cluster, Address
from ...schemas.cluster import ClusterResponse, ClusterListResponse
from ...schemas.common import PaginatedResponse, GraphData
from ...services.graph import GraphService
from ...utils.logger import logger

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ClusterListResponse])
async def get_clusters(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="결과 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    min_size: int = Query(1, ge=1, description="최소 주소 수")
):
    """
    클러스터 목록 조회

    Args:
        limit: 페이지 크기
        offset: 시작 위치
        min_size: 최소 주소 수
        db: Database session

    Returns:
        클러스터 목록 (페이지네이션)
    """
    logger.info(f"클러스터 목록 조회: limit={limit}, offset={offset}, min_size={min_size}")

    # Query clusters with minimum size
    query = db.query(Cluster).filter(Cluster.address_count >= min_size).order_by(Cluster.total_balance.desc())

    total = query.count()
    clusters = query.limit(limit).offset(offset).all()

    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    current_page = (offset // limit) + 1

    logger.info(f"클러스터 조회 완료: {len(clusters)}개")

    return PaginatedResponse(
        data=[ClusterListResponse.from_orm(c) for c in clusters],
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: str, db: Session = Depends(get_db)):
    """
    클러스터 상세 정보 조회

    Args:
        cluster_id: Cluster UUID
        db: Database session

    Returns:
        클러스터 상세 정보 (주소 목록 포함)

    Raises:
        HTTPException: 클러스터를 찾을 수 없는 경우 404
    """
    logger.info(f"클러스터 조회 요청: {cluster_id}")

    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()

    if not cluster:
        logger.warning(f"클러스터를 찾을 수 없음: {cluster_id}")
        raise HTTPException(
            status_code=404,
            detail={
                "message": "클러스터를 찾을 수 없습니다",
                "error": f"Cluster not found: {cluster_id}",
                "type": "ClusterNotFound"
            }
        )

    # 클러스터에 속한 주소들 가져오기
    addresses = db.query(Address).filter(Address.cluster_id == cluster_id).all()

    logger.info(f"클러스터 조회 성공: {cluster.label}, 주소 {len(addresses)}개")

    # ClusterResponse에 addresses 포함
    from ...schemas.cluster import ClusterResponse, AddressInCluster

    return ClusterResponse(
        id=cluster.id,
        label=cluster.label,
        address_count=cluster.address_count,
        total_balance=cluster.total_balance,
        total_received=cluster.total_received,
        total_sent=cluster.total_sent,
        tx_count=cluster.tx_count,
        first_seen=cluster.first_seen,
        last_seen=cluster.last_seen,
        created_at=cluster.created_at,
        updated_at=cluster.updated_at,
        addresses=[AddressInCluster(
            address=addr.address,
            balance=addr.balance,
            tx_count=addr.tx_count
        ) for addr in addresses]
    )


@router.get("/{cluster_id}/addresses", response_model=PaginatedResponse[dict])
async def get_cluster_addresses(
    cluster_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    클러스터 내 주소 목록 조회

    Args:
        cluster_id: Cluster UUID
        limit: 페이지 크기
        offset: 시작 위치
        db: Database session

    Returns:
        주소 목록 (페이지네이션)

    Raises:
        HTTPException: 클러스터를 찾을 수 없는 경우 404
    """
    logger.info(f"클러스터 주소 조회: {cluster_id}, limit={limit}, offset={offset}")

    # Check if cluster exists
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="클러스터를 찾을 수 없습니다")

    # Get addresses
    query = db.query(Address).filter(Address.cluster_id == cluster_id).order_by(Address.balance.desc())
    total = query.count()
    addresses = query.limit(limit).offset(offset).all()

    # Calculate total pages
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    current_page = (offset // limit) + 1

    logger.info(f"클러스터 주소 조회 완료: {len(addresses)}개")

    return PaginatedResponse(
        data=[{
            "address": addr.address,
            "balance": addr.balance,
            "tx_count": addr.tx_count,
            "total_received": addr.total_received,
            "total_sent": addr.total_sent
        } for addr in addresses],
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/{cluster_id}/graph", response_model=GraphData)
async def get_cluster_graph(
    cluster_id: str,
    db: Session = Depends(get_db)
):
    """
    클러스터 그래프 데이터 조회

    Args:
        cluster_id: Cluster UUID
        db: Database session

    Returns:
        그래프 데이터 (nodes, edges)

    Raises:
        HTTPException: 클러스터를 찾을 수 없는 경우 404
    """
    logger.info(f"클러스터 그래프 조회: {cluster_id}")

    # Check if cluster exists
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="클러스터를 찾을 수 없습니다")

    # Get addresses in cluster
    addresses = db.query(Address).filter(Address.cluster_id == cluster_id).limit(100).all()

    # Get transactions (simplified - would need proper transaction query)
    from ...models import Transaction, TransactionInput, TransactionOutput

    # Get transactions related to cluster addresses
    address_list = [addr.address for addr in addresses]
    txids = db.query(TransactionInput.txid).filter(TransactionInput.address.in_(address_list)).distinct().limit(200).all()
    txids = [t[0] for t in txids]

    transactions = []
    for txid in txids:
        tx = db.query(Transaction).filter(Transaction.txid == txid).first()
        if tx:
            inputs = db.query(TransactionInput).filter(TransactionInput.txid == txid).all()
            outputs = db.query(TransactionOutput).filter(TransactionOutput.txid == txid).all()

            transactions.append({
                'txid': tx.txid,
                'timestamp': tx.timestamp,
                'inputs': [{'address': i.address, 'amount': i.amount} for i in inputs],
                'outputs': [{'address': o.address, 'amount': o.amount} for o in outputs]
            })

    # Generate graph
    addresses_dict = [{
        'address': addr.address,
        'balance': addr.balance,
        'cluster_id': addr.cluster_id
    } for addr in addresses]

    graph_data = GraphService.generate_cluster_graph(cluster_id, addresses_dict, transactions)

    logger.info(f"클러스터 그래프 생성 완료: {len(graph_data.nodes)}개 노드")
    return graph_data
