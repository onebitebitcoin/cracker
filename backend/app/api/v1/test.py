"""Test API endpoints"""
from fastapi import APIRouter, Depends
from ...dependencies import get_electrum_client
from ...services.electrum_client import ElectrumClient
from ...utils.logger import logger

router = APIRouter()


@router.get("/electrum/status")
async def electrum_status(electrum: ElectrumClient = Depends(get_electrum_client)):
    """Electrum 서버 연결 상태 확인"""
    logger.info("Electrum 상태 확인 요청")

    result = electrum.test_connection()

    return {
        "electrum_status": result,
        "socket_status": "connected" if electrum.socket else "disconnected"
    }


@router.get("/electrum/balance/{address}")
async def get_balance_test(address: str, electrum: ElectrumClient = Depends(get_electrum_client)):
    """Electrum 서버에서 잔액 조회 (디버그용)"""
    logger.info(f"잔액 조회 테스트: {address}")

    # 연결 확인
    if not electrum.socket:
        logger.warning("소켓이 None, 재연결 시도")
        connected = electrum.connect()
        if not connected:
            return {"error": "Electrum 서버 연결 실패"}

    # 잔액 조회
    balance = electrum.get_balance(address)

    return {
        "address": address,
        "balance_data": balance,
        "socket_status": "connected" if electrum.socket else "disconnected"
    }
