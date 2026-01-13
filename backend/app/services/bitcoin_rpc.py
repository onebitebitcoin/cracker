"""
Bitcoin RPC Service
Bitcoin Core 노드와 연결하여 블록체인 데이터를 수집하는 서비스
"""
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from ..utils.logger import logger

class BitcoinRPCService:
    """Bitcoin Core RPC 연결 및 데이터 수집 서비스"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str = "",
        password: str = "",
        use_ssl: bool = False
    ):
        """
        Bitcoin RPC 서비스 초기화

        Args:
            host: Bitcoin Core 호스트 주소
            port: RPC 포트 (기본: 8332)
            user: RPC 사용자명 (옵션)
            password: RPC 비밀번호 (옵션)
            use_ssl: SSL 사용 여부
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.use_ssl = use_ssl

        # RPC 연결 URL 생성
        protocol = "https" if use_ssl else "http"

        if user and password:
            self.rpc_url = f"{protocol}://{user}:{password}@{host}:{port}"
        else:
            self.rpc_url = f"{protocol}://{host}:{port}"

        self.rpc_connection = None
        logger.info(f"Bitcoin RPC 서비스 초기화: {host}:{port}")

    def connect(self) -> bool:
        """
        Bitcoin Core RPC 연결

        Returns:
            연결 성공 여부
        """
        try:
            logger.info(f"Bitcoin Core RPC 연결 시도: {self.rpc_url}")
            self.rpc_connection = AuthServiceProxy(self.rpc_url, timeout=120)

            # 연결 테스트
            block_count = self.rpc_connection.getblockcount()
            logger.info(f"Bitcoin Core RPC 연결 성공. 현재 블록 높이: {block_count}")
            return True

        except JSONRPCException as e:
            logger.error(f"Bitcoin RPC 에러: {e.error}")
            return False
        except Exception as e:
            logger.error(f"Bitcoin Core RPC 연결 실패: {str(e)}", exc_info=True)
            return False

    def test_connection(self) -> Dict[str, Any]:
        """
        연결 테스트 및 기본 정보 조회

        Returns:
            노드 정보 딕셔너리
        """
        if not self.rpc_connection:
            if not self.connect():
                return {
                    "connected": False,
                    "error": "연결 실패"
                }

        try:
            block_count = self.rpc_connection.getblockcount()
            blockchain_info = self.rpc_connection.getblockchaininfo()
            network_info = self.rpc_connection.getnetworkinfo()

            result = {
                "connected": True,
                "block_count": block_count,
                "chain": blockchain_info.get("chain"),
                "blocks": blockchain_info.get("blocks"),
                "headers": blockchain_info.get("headers"),
                "verification_progress": blockchain_info.get("verificationprogress"),
                "network_version": network_info.get("version"),
                "protocol_version": network_info.get("protocolversion"),
                "connections": network_info.get("connections"),
            }

            logger.info(f"연결 테스트 성공: {result}")
            return result

        except JSONRPCException as e:
            logger.error(f"Bitcoin RPC 에러: {e.error}")
            return {
                "connected": False,
                "error": f"RPC 에러: {e.error}"
            }
        except Exception as e:
            logger.error(f"연결 테스트 실패: {str(e)}", exc_info=True)
            return {
                "connected": False,
                "error": str(e)
            }

    def get_block_count(self) -> Optional[int]:
        """
        현재 블록 높이 조회

        Returns:
            블록 높이 또는 None
        """
        try:
            return self.rpc_connection.getblockcount()
        except Exception as e:
            logger.error(f"블록 높이 조회 실패: {str(e)}")
            return None

    def get_block_hash(self, height: int) -> Optional[str]:
        """
        블록 해시 조회

        Args:
            height: 블록 높이

        Returns:
            블록 해시 또는 None
        """
        try:
            return self.rpc_connection.getblockhash(height)
        except Exception as e:
            logger.error(f"블록 해시 조회 실패 (height={height}): {str(e)}")
            return None

    def get_block(self, block_hash: str, verbosity: int = 2) -> Optional[Dict]:
        """
        블록 상세 정보 조회

        Args:
            block_hash: 블록 해시
            verbosity: 상세도 (0: hex, 1: json, 2: json with tx)

        Returns:
            블록 정보 딕셔너리 또는 None
        """
        try:
            return self.rpc_connection.getblock(block_hash, verbosity)
        except Exception as e:
            logger.error(f"블록 조회 실패 (hash={block_hash}): {str(e)}")
            return None

    def get_raw_transaction(
        self,
        txid: str,
        verbose: bool = True,
        block_hash: Optional[str] = None
    ) -> Optional[Dict]:
        """
        트랜잭션 상세 정보 조회

        Args:
            txid: 트랜잭션 ID
            verbose: 상세 정보 포함 여부
            block_hash: 블록 해시 (옵션)

        Returns:
            트랜잭션 정보 딕셔너리 또는 None
        """
        try:
            if block_hash:
                return self.rpc_connection.getrawtransaction(txid, verbose, block_hash)
            else:
                return self.rpc_connection.getrawtransaction(txid, verbose)
        except Exception as e:
            logger.error(f"트랜잭션 조회 실패 (txid={txid}): {str(e)}")
            return None

    def get_blockchain_info(self) -> Optional[Dict]:
        """
        블록체인 정보 조회

        Returns:
            블록체인 정보 딕셔너리
        """
        try:
            return self.rpc_connection.getblockchaininfo()
        except Exception as e:
            logger.error(f"블록체인 정보 조회 실패: {str(e)}")
            return None

    def get_network_info(self) -> Optional[Dict]:
        """
        네트워크 정보 조회

        Returns:
            네트워크 정보 딕셔너리
        """
        try:
            return self.rpc_connection.getnetworkinfo()
        except Exception as e:
            logger.error(f"네트워크 정보 조회 실패: {str(e)}")
            return None

    def parse_block_transactions(self, block: Dict) -> List[Dict]:
        """
        블록 내 트랜잭션 파싱

        Args:
            block: 블록 데이터 (verbosity=2)

        Returns:
            파싱된 트랜잭션 리스트
        """
        transactions = []

        if "tx" not in block:
            logger.warning("블록에 트랜잭션 정보가 없습니다")
            return transactions

        for tx in block["tx"]:
            try:
                parsed_tx = {
                    "txid": tx["txid"],
                    "block_height": block["height"],
                    "block_hash": block["hash"],
                    "timestamp": block.get("time"),
                    "size": tx.get("size"),
                    "fee": self._calculate_fee(tx),
                    "inputs": self._parse_inputs(tx),
                    "outputs": self._parse_outputs(tx),
                }
                transactions.append(parsed_tx)

            except Exception as e:
                logger.error(f"트랜잭션 파싱 실패 (txid={tx.get('txid')}): {str(e)}")
                continue

        return transactions

    def _parse_inputs(self, tx: Dict) -> List[Dict]:
        """트랜잭션 입력 파싱"""
        inputs = []

        for vin in tx.get("vin", []):
            # Coinbase 트랜잭션 제외
            if "coinbase" in vin:
                continue

            input_data = {
                "prev_txid": vin.get("txid"),
                "prev_vout": vin.get("vout"),
                "script_sig": vin.get("scriptSig", {}).get("hex"),
                "sequence": vin.get("sequence"),
            }

            # 이전 트랜잭션에서 주소 및 금액 추출 (필요시)
            # 실제 구현에서는 prevout 정보를 조회해야 함

            inputs.append(input_data)

        return inputs

    def _parse_outputs(self, tx: Dict) -> List[Dict]:
        """트랜잭션 출력 파싱"""
        outputs = []

        for vout in tx.get("vout", []):
            script_pubkey = vout.get("scriptPubKey", {})
            addresses = script_pubkey.get("addresses", [])

            output_data = {
                "vout": vout.get("n"),
                "amount": Decimal(str(vout.get("value", 0))),
                "script_pubkey": script_pubkey.get("hex"),
                "address": addresses[0] if addresses else None,
            }

            outputs.append(output_data)

        return outputs

    def _calculate_fee(self, tx: Dict) -> Optional[Decimal]:
        """
        트랜잭션 수수료 계산

        Note: 정확한 수수료 계산을 위해서는 입력의 이전 출력 값이 필요
        """
        # 간단한 구현: vout의 총합 계산
        # 실제로는 vin의 이전 출력 값 - vout의 총합
        try:
            total_output = sum(
                Decimal(str(vout.get("value", 0)))
                for vout in tx.get("vout", [])
            )
            # 실제 수수료는 total_input - total_output
            # 여기서는 임시로 None 반환
            return None
        except Exception as e:
            logger.error(f"수수료 계산 실패: {str(e)}")
            return None


# 싱글톤 인스턴스를 위한 글로벌 변수
_bitcoin_rpc_instance = None


def get_bitcoin_rpc(
    host: str = "localhost",
    port: int = 8332,
    user: str = "",
    password: str = "",
    use_ssl: bool = False
) -> BitcoinRPCService:
    """
    Bitcoin RPC 서비스 인스턴스 가져오기 (싱글톤)

    Args:
        host: Bitcoin Core 호스트
        port: RPC 포트
        user: RPC 사용자명
        password: RPC 비밀번호
        use_ssl: SSL 사용 여부

    Returns:
        BitcoinRPCService 인스턴스
    """
    global _bitcoin_rpc_instance

    if _bitcoin_rpc_instance is None:
        _bitcoin_rpc_instance = BitcoinRPCService(
            host=host,
            port=port,
            user=user,
            password=password,
            use_ssl=use_ssl
        )

    return _bitcoin_rpc_instance
