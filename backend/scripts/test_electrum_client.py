#!/usr/bin/env python3
"""
Electrum 클라이언트 연결 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.config import settings
from backend.app.services.electrum_client import ElectrumClient
from backend.app.utils.logger import logger


def test_connection():
    """Electrum 서버 연결 테스트"""

    print("=" * 60)
    print("Electrum 서버 연결 테스트")
    print("=" * 60)
    print()

    # 설정 정보 출력
    print(f"호스트: {settings.bitcoin_rpc_host}")
    print(f"포트: {settings.bitcoin_rpc_port}")
    print(f"SSL: {settings.bitcoin_rpc_use_ssl}")
    print()
    print("-" * 60)
    print()

    # Electrum 클라이언트 생성
    client = ElectrumClient(
        host=settings.bitcoin_rpc_host,
        port=settings.bitcoin_rpc_port,
        use_ssl=settings.bitcoin_rpc_use_ssl
    )

    # 연결 시도
    print("연결 시도 중...")
    if not client.connect():
        print("❌ 연결 실패!")
        return None

    # 연결 테스트
    result = client.test_connection()
    print()

    if result.get("connected"):
        print("✅ 연결 성공!")
        print()
        print("서버 정보:")
        print(f"  - 서버 버전: {result.get('server_version')}")
        print(f"  - 프로토콜 버전: {result.get('protocol_version')}")
        print(f"  - 블록 높이: {result.get('block_height')}")
        print(f"  - 추정 수수료 (6블록): {result.get('estimated_fee')} BTC/KB")
        print()

        return client
    else:
        print("❌ 연결 테스트 실패!")
        print(f"에러: {result.get('error')}")
        print()
        return None


def test_get_balance(client: ElectrumClient, address: str):
    """주소 잔액 조회 테스트"""

    print("-" * 60)
    print(f"주소 잔액 조회 테스트")
    print("-" * 60)
    print(f"주소: {address}")
    print()

    balance = client.get_balance(address)

    if balance:
        confirmed_btc = balance.get("confirmed", 0) / 100_000_000
        unconfirmed_btc = balance.get("unconfirmed", 0) / 100_000_000

        print(f"✅ 잔액 조회 성공")
        print(f"  - 확인된 잔액: {confirmed_btc:.8f} BTC ({balance.get('confirmed', 0)} satoshi)")
        print(f"  - 미확인 잔액: {unconfirmed_btc:.8f} BTC ({balance.get('unconfirmed', 0)} satoshi)")
        print()
    else:
        print("❌ 잔액 조회 실패")
        print()


def test_get_history(client: ElectrumClient, address: str, limit: int = 10):
    """주소 트랜잭션 히스토리 조회 테스트"""

    print("-" * 60)
    print(f"트랜잭션 히스토리 조회 테스트")
    print("-" * 60)
    print(f"주소: {address}")
    print()

    history = client.get_history(address)

    if history is not None:
        print(f"✅ 트랜잭션 히스토리 조회 성공")
        print(f"총 트랜잭션 수: {len(history)}")
        print()

        if len(history) > 0:
            print(f"최근 {min(limit, len(history))}개 트랜잭션:")
            for i, tx in enumerate(history[:limit]):
                print(f"  {i+1}. TXID: {tx.get('tx_hash')}")
                print(f"     블록 높이: {tx.get('height')}")
                print()
        else:
            print("트랜잭션이 없습니다.")
            print()
    else:
        print("❌ 트랜잭션 히스토리 조회 실패")
        print()


def test_get_transaction(client: ElectrumClient, txid: str):
    """트랜잭션 조회 테스트"""

    print("-" * 60)
    print("트랜잭션 조회 테스트")
    print("-" * 60)
    print(f"TXID: {txid}")
    print()

    # Raw hex 조회
    tx_hex = client.get_transaction(txid, verbose=False)

    if tx_hex:
        print(f"✅ 트랜잭션 조회 성공")
        print(f"  - Raw Hex: {tx_hex[:100]}...")
        print(f"  - 길이: {len(tx_hex)} 문자")
        print()
    else:
        print("❌ 트랜잭션 조회 실패")
        print()


def test_get_block_header(client: ElectrumClient, height: int):
    """블록 헤더 조회 테스트"""

    print("-" * 60)
    print("블록 헤더 조회 테스트")
    print("-" * 60)
    print(f"블록 높이: {height}")
    print()

    header = client.get_block_header(height)

    if header:
        print(f"✅ 블록 헤더 조회 성공")
        print(f"  - 헤더: {header[:100]}...")
        print()
    else:
        print("❌ 블록 헤더 조회 실패")
        print()


def main():
    """메인 함수"""

    try:
        # 1. 연결 테스트
        client = test_connection()

        if not client:
            sys.exit(1)

        # 2. 잘 알려진 Bitcoin 주소로 테스트
        # Satoshi의 Genesis block 주소
        test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

        print("=" * 60)
        print("주소 조회 테스트")
        print("=" * 60)
        print(f"테스트 주소: {test_address}")
        print("(Satoshi의 Genesis block 주소)")
        print()

        # 잔액 조회
        try:
            test_get_balance(client, test_address)
        except Exception as e:
            logger.error(f"잔액 조회 실패: {str(e)}", exc_info=True)
            print(f"⚠️  잔액 조회 중 에러: {str(e)}")
            print()

        # 트랜잭션 히스토리 조회
        try:
            test_get_history(client, test_address, limit=5)
        except Exception as e:
            logger.error(f"히스토리 조회 실패: {str(e)}", exc_info=True)
            print(f"⚠️  히스토리 조회 중 에러: {str(e)}")
            print()

        # 3. 블록 헤더 조회 테스트
        try:
            # Genesis block
            test_get_block_header(client, 0)
        except Exception as e:
            logger.error(f"블록 헤더 조회 실패: {str(e)}", exc_info=True)
            print(f"⚠️  블록 헤더 조회 중 에러: {str(e)}")
            print()

        # 4. 트랜잭션 조회 테스트
        try:
            # Genesis block의 coinbase 트랜잭션
            genesis_tx = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
            test_get_transaction(client, genesis_tx)
        except Exception as e:
            logger.error(f"트랜잭션 조회 실패: {str(e)}", exc_info=True)
            print(f"⚠️  트랜잭션 조회 중 에러: {str(e)}")
            print()

        print("=" * 60)
        print("모든 테스트 완료")
        print("=" * 60)

        # 연결 종료
        client.disconnect()

    except KeyboardInterrupt:
        print()
        print("테스트 중단됨")
        sys.exit(0)
    except Exception as e:
        logger.error(f"테스트 실행 중 에러: {str(e)}", exc_info=True)
        print(f"❌ 예상치 못한 에러 발생: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
