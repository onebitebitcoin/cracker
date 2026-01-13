"""
API Dependencies
FastAPI 의존성 주입을 위한 함수들
"""
from .services.electrum_client import ElectrumClient
from .config import settings
from .utils.logger import logger


def get_electrum_client() -> ElectrumClient:
    """
    Electrum 클라이언트 의존성

    매번 새로운 클라이언트 인스턴스를 생성하여 연결 문제 방지

    Returns:
        ElectrumClient 인스턴스
    """
    logger.info("새 Electrum 클라이언트 생성...")
    client = ElectrumClient(
        host=settings.bitcoin_rpc_host,
        port=settings.bitcoin_rpc_port,
        use_ssl=settings.bitcoin_rpc_use_ssl
    )

    # 연결 시도
    connected = client.connect()
    if not connected:
        logger.warning("Electrum 서버 연결 실패")

    return client
