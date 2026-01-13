"""
Electrum Client Service
Electrum 서버와 연결하여 블록체인 데이터를 수집하는 서비스
"""
import socket
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from ..utils.logger import logger
from ..utils.bitcoin import address_to_scripthash


class ElectrumClient:
    """Electrum 서버 클라이언트"""

    def __init__(self, host: str, port: int, use_ssl: bool = False):
        """
        Electrum 클라이언트 초기화

        Args:
            host: Electrum 서버 호스트
            port: 서버 포트 (일반적으로 50001=TCP, 50002=SSL)
            use_ssl: SSL 사용 여부
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.socket = None
        self.request_id = 0

        logger.info(f"Electrum 클라이언트 초기화: {host}:{port} (SSL: {use_ssl})")

    def connect(self) -> bool:
        """
        Electrum 서버 연결

        Returns:
            연결 성공 여부
        """
        try:
            logger.info(f"Electrum 서버 연결 시도: {self.host}:{self.port}")

            # SSL 사용 여부에 따라 소켓 생성
            if self.use_ssl:
                import ssl
                context = ssl.create_default_context()
                raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket = context.wrap_socket(
                    raw_socket,
                    server_hostname=self.host
                )
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.settimeout(60)  # 60초로 증가
            self.socket.connect((self.host, self.port))

            # 연결 테스트 (server.version)
            version_info = self.get_server_version()
            if version_info:
                logger.info(f"Electrum 서버 연결 성공: {version_info}")
                return True
            else:
                logger.error("server.version 응답 없음")
                return False

        except Exception as e:
            logger.error(f"Electrum 서버 연결 실패: {str(e)}", exc_info=True)
            return False

    def disconnect(self):
        """연결 종료"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Electrum 서버 연결 종료")
            except Exception as e:
                logger.error(f"연결 종료 실패: {str(e)}")

    def _ensure_connected(self) -> bool:
        """연결 상태 확인 및 필요시 재연결"""
        if not self.socket:
            logger.info("연결되지 않아 재연결 시도")
            return self.connect()

        try:
            # 소켓 상태 확인
            if self.socket.fileno() == -1:
                logger.info("소켓이 닫혀있어 재연결 시도")
                return self.connect()
        except Exception:
            logger.info("소켓 상태 확인 실패, 재연결 시도")
            return self.connect()

        return True

    def _send_request(self, method: str, params: List = None) -> Optional[Dict]:
        """
        Electrum 서버에 요청 전송

        Args:
            method: 메서드 이름
            params: 파라미터 리스트

        Returns:
            응답 데이터
        """
        # 연결 확인
        if not self._ensure_connected():
            logger.error("Electrum 서버 연결 실패")
            return None

        try:
            self.request_id += 1
            request = {
                "id": self.request_id,
                "method": method,
                "params": params or []
            }

            # 요청 전송
            message = json.dumps(request) + "\n"
            logger.debug(f"요청 전송: {request}")
            self.socket.sendall(message.encode())

            # 응답 수신
            response_data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in chunk:
                    break

            # JSON 파싱
            logger.debug(f"응답 수신: {response_data.decode().strip()[:200]}")
            response = json.loads(response_data.decode().strip())

            # 에러 체크
            if "error" in response and response["error"]:
                logger.error(f"Electrum 에러: {response['error']}")
                return None

            return response.get("result")

        except Exception as e:
            logger.error(f"요청 전송 실패 ({method}): {str(e)}", exc_info=True)
            return None

    def get_server_version(self) -> Optional[List]:
        """
        서버 버전 정보 조회

        Returns:
            [서버 소프트웨어, 프로토콜 버전]
        """
        return self._send_request("server.version", ["bitcoin-cracker", "1.4"])

    def _address_to_scripthash(self, address: str) -> Optional[str]:
        """
        Bitcoin 주소를 scripthash로 변환

        Electrum은 주소 대신 scripthash를 사용합니다.
        scripthash = sha256(scriptPubKey)의 역순 hex

        Args:
            address: Bitcoin 주소

        Returns:
            scripthash (hex) 또는 None
        """
        return address_to_scripthash(address)

    def get_balance(self, address: str) -> Optional[Dict]:
        """
        주소 잔액 조회

        Args:
            address: Bitcoin 주소

        Returns:
            {"confirmed": int, "unconfirmed": int} (satoshi 단위)
        """
        scripthash = self._address_to_scripthash(address)
        if not scripthash:
            logger.error(f"주소를 scripthash로 변환 실패: {address}")
            return None

        result = self._send_request("blockchain.scripthash.get_balance", [scripthash])

        if result:
            logger.info(f"주소 {address} 잔액: {result}")

        return result

    def get_history(self, address: str) -> Optional[List[Dict]]:
        """
        주소 트랜잭션 히스토리 조회

        Args:
            address: Bitcoin 주소

        Returns:
            트랜잭션 리스트
            [{"tx_hash": str, "height": int}, ...]
        """
        scripthash = self._address_to_scripthash(address)
        if not scripthash:
            logger.error(f"주소를 scripthash로 변환 실패: {address}")
            return None

        result = self._send_request("blockchain.scripthash.get_history", [scripthash])

        if result:
            logger.info(f"주소 {address} 트랜잭션 수: {len(result)}")

        return result

    def get_transaction(self, txid: str, verbose: bool = False) -> Optional[Union[str, Dict]]:
        """
        트랜잭션 조회

        Args:
            txid: 트랜잭션 ID
            verbose: 상세 정보 포함 여부

        Returns:
            트랜잭션 hex 또는 상세 정보
        """
        result = self._send_request("blockchain.transaction.get", [txid, verbose])

        if result:
            logger.info(f"트랜잭션 {txid} 조회 성공")

        return result

    def get_block_header(self, height: int) -> Optional[Dict]:
        """
        블록 헤더 조회

        Args:
            height: 블록 높이

        Returns:
            블록 헤더 정보
        """
        result = self._send_request("blockchain.block.header", [height])

        if result:
            logger.info(f"블록 #{height} 헤더 조회 성공")

        return result

    def subscribe_headers(self) -> Optional[Dict]:
        """
        블록 헤더 구독 (새 블록 알림)

        Returns:
            현재 블록 헤더
        """
        return self._send_request("blockchain.headers.subscribe")

    def get_fee_histogram(self) -> Optional[List]:
        """
        수수료 히스토그램 조회 (mempool 분석)

        Returns:
            수수료 분포 리스트
        """
        return self._send_request("mempool.get_fee_histogram")

    def estimate_fee(self, num_blocks: int = 6) -> Optional[float]:
        """
        수수료 추정

        Args:
            num_blocks: 확인 블록 수

        Returns:
            BTC/KB 단위 수수료
        """
        result = self._send_request("blockchain.estimatefee", [num_blocks])

        if result and result > 0:
            logger.info(f"{num_blocks}블록 내 확인 수수료 추정: {result} BTC/KB")

        return result

    def test_connection(self) -> Dict[str, Any]:
        """
        연결 테스트 및 서버 정보 조회

        Returns:
            서버 정보 딕셔너리
        """
        try:
            # 서버 버전
            version = self.get_server_version()

            # 최신 블록 헤더
            headers = self.subscribe_headers()

            # 수수료 추정
            fee = self.estimate_fee(6)

            result = {
                "connected": True,
                "server_version": version[0] if version else "Unknown",
                "protocol_version": version[1] if version and len(version) > 1 else "Unknown",
                "block_height": headers.get("height") if headers else None,
                "estimated_fee": fee,
            }

            logger.info(f"Electrum 서버 테스트 성공: {result}")
            return result

        except Exception as e:
            logger.error(f"연결 테스트 실패: {str(e)}", exc_info=True)
            return {
                "connected": False,
                "error": str(e)
            }


# 싱글톤 인스턴스
_electrum_client_instance = None


def get_electrum_client(
    host: str = "localhost",
    port: int = 50001,
    use_ssl: bool = False
) -> ElectrumClient:
    """
    Electrum 클라이언트 인스턴스 가져오기 (싱글톤)

    Args:
        host: Electrum 서버 호스트
        port: 서버 포트
        use_ssl: SSL 사용 여부

    Returns:
        ElectrumClient 인스턴스
    """
    global _electrum_client_instance

    if _electrum_client_instance is None:
        _electrum_client_instance = ElectrumClient(
            host=host,
            port=port,
            use_ssl=use_ssl
        )

    return _electrum_client_instance
