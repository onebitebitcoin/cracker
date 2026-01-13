"""Address API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...database import get_db
from ...models import Address, Transaction, TransactionInput, TransactionOutput
from ...schemas.address import AddressResponse, AddressListResponse
from ...schemas.transaction import TransactionListResponse
from ...schemas.common import PaginatedResponse
from ...utils.logger import logger
from ...utils.exceptions import AddressNotFoundException
from ...dependencies import get_electrum_client
from ...services.electrum_client import ElectrumClient

router = APIRouter()


@router.get("/{address}")
async def get_address(
    address: str,
    electrum: ElectrumClient = Depends(get_electrum_client)
):
    """
    주소 상세 정보 조회 (Electrum 서버 사용)

    Args:
        address: Bitcoin 주소
        electrum: Electrum 클라이언트

    Returns:
        주소 상세 정보

    Raises:
        HTTPException: 조회 실패 시 500
    """
    logger.info(f"주소 조회 요청 (Electrum): {address}")

    try:
        # Electrum 서버에서 잔액 조회
        balance_data = electrum.get_balance(address)
        if balance_data is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "주소 정보를 가져올 수 없습니다",
                    "error": "Electrum server error"
                }
            )

        # Electrum 서버에서 트랜잭션 히스토리 조회
        history = electrum.get_history(address)
        if history is None:
            history = []

        # 잔액 변환 (satoshi -> BTC)
        confirmed_btc = balance_data.get("confirmed", 0) / 100_000_000
        unconfirmed_btc = balance_data.get("unconfirmed", 0) / 100_000_000
        total_balance = confirmed_btc + unconfirmed_btc

        # 응답 데이터 구성
        response = {
            "address": address,
            "balance": total_balance,
            "confirmed_balance": confirmed_btc,
            "unconfirmed_balance": unconfirmed_btc,
            "total_received": None,  # Electrum은 total_received를 직접 제공하지 않음
            "total_sent": None,
            "tx_count": len(history),
            "first_seen": None,
            "last_seen": None,
            "cluster_id": None,
            "source": "electrum"  # 데이터 출처 표시
        }

        logger.info(f"주소 조회 성공 (Electrum): {address}, 잔액={total_balance} BTC, 트랜잭션={len(history)}개")
        return response

    except Exception as e:
        logger.error(f"주소 조회 실패 (Electrum): {address}, 에러={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "주소 조회 중 오류 발생",
                "error": str(e),
                "type": "ElectrumError"
            }
        )


@router.get("/{address}/transactions")
async def get_address_transactions(
    address: str,
    electrum: ElectrumClient = Depends(get_electrum_client),
    limit: int = Query(50, ge=1, le=100, description="결과 개수"),
    offset: int = Query(0, ge=0, description="시작 위치")
):
    """
    주소의 트랜잭션 히스토리 조회 (Electrum 서버 사용)

    Args:
        address: Bitcoin 주소
        electrum: Electrum 클라이언트
        limit: 페이지 크기
        offset: 시작 위치

    Returns:
        트랜잭션 목록 (페이지네이션)

    Raises:
        HTTPException: 조회 실패 시 500
    """
    logger.info(f"주소 트랜잭션 조회 (Electrum): {address}, limit={limit}, offset={offset}")

    try:
        # Electrum 서버에서 트랜잭션 히스토리 조회
        history = electrum.get_history(address)
        if history is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "트랜잭션 정보를 가져올 수 없습니다",
                    "error": "Electrum server error"
                }
            )

        # 페이지네이션 적용
        total = len(history)
        paginated_history = history[offset:offset + limit]

        # 트랜잭션 데이터 변환
        transactions = []
        for tx_info in paginated_history:
            tx_data = {
                "txid": tx_info.get("tx_hash"),
                "block_height": tx_info.get("height"),
                "confirmations": None,  # Electrum은 confirmations를 직접 제공하지 않음
                "timestamp": None,
                "fee": None,
                "source": "electrum"
            }
            transactions.append(tx_data)

        # 페이지 계산
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        current_page = (offset // limit) + 1

        logger.info(f"트랜잭션 조회 완료 (Electrum): {len(transactions)}개 (전체 {total}개)")

        return {
            "data": transactions,
            "total": total,
            "page": current_page,
            "page_size": limit,
            "total_pages": total_pages
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"트랜잭션 조회 실패 (Electrum): {address}, 에러={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "message": "트랜잭션 조회 중 오류 발생",
                "error": str(e),
                "type": "ElectrumError"
            }
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
