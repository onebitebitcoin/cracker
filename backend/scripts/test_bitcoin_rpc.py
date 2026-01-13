#!/usr/bin/env python3
"""
Bitcoin RPC 연결 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.config import settings
from backend.app.services.bitcoin_rpc import BitcoinRPCService
from backend.app.utils.logger import logger


def test_connection():
    """Bitcoin RPC 연결 테스트"""

    print("=" * 60)
    print("Bitcoin RPC 연결 테스트")
    print("=" * 60)
    print()

    # 설정 정보 출력
    print(f"호스트: {settings.bitcoin_rpc_host}")
    print(f"포트: {settings.bitcoin_rpc_port}")
    print(f"사용자: {settings.bitcoin_rpc_user or '(없음)'}")
    print(f"SSL: {settings.bitcoin_rpc_use_ssl}")
    print()
    print("-" * 60)
    print()

    # Bitcoin RPC 서비스 생성
    rpc_service = BitcoinRPCService(
        host=settings.bitcoin_rpc_host,
        port=settings.bitcoin_rpc_port,
        user=settings.bitcoin_rpc_user,
        password=settings.bitcoin_rpc_password,
        use_ssl=settings.bitcoin_rpc_use_ssl
    )

    # 연결 테스트
    print("연결 시도 중...")
    result = rpc_service.test_connection()
    print()

    if result.get("connected"):
        print("✅ 연결 성공!")
        print()
        print("노드 정보:")
        print(f"  - 블록 높이: {result.get('block_count')}")
        print(f"  - 체인: {result.get('chain')}")
        print(f"  - 블록 수: {result.get('blocks')}")
        print(f"  - 헤더 수: {result.get('headers')}")
        print(f"  - 동기화 진행률: {result.get('verification_progress', 0) * 100:.2f}%")
        print(f"  - 네트워크 버전: {result.get('network_version')}")
        print(f"  - 프로토콜 버전: {result.get('protocol_version')}")
        print(f"  - 연결 수: {result.get('connections')}")
        print()

        return True, rpc_service
    else:
        print("❌ 연결 실패!")
        print(f"에러: {result.get('error')}")
        print()
        print("문제 해결 방법:")
        print("1. 호스트와 포트가 올바른지 확인하세요")
        print("2. Bitcoin Core 노드가 실행 중인지 확인하세요")
        print("3. RPC 설정이 올바른지 확인하세요 (bitcoin.conf)")
        print("4. 방화벽 설정을 확인하세요")
        print()

        return False, None


def test_get_latest_blocks(rpc_service: BitcoinRPCService, num_blocks: int = 5):
    """최신 블록 정보 조회 테스트"""

    print("-" * 60)
    print(f"최신 블록 {num_blocks}개 조회 테스트")
    print("-" * 60)
    print()

    # 현재 블록 높이 조회
    block_count = rpc_service.get_block_count()
    if not block_count:
        print("❌ 블록 높이 조회 실패")
        return

    print(f"현재 블록 높이: {block_count}")
    print()

    # 최신 블록들 조회
    for i in range(num_blocks):
        height = block_count - i
        print(f"블록 #{height} 조회 중...")

        # 블록 해시 조회
        block_hash = rpc_service.get_block_hash(height)
        if not block_hash:
            print(f"  ❌ 블록 해시 조회 실패")
            continue

        print(f"  해시: {block_hash}")

        # 블록 상세 정보 조회 (verbosity=1, 트랜잭션 제외)
        block = rpc_service.get_block(block_hash, verbosity=1)
        if not block:
            print(f"  ❌ 블록 상세 정보 조회 실패")
            continue

        print(f"  시간: {block.get('time')}")
        print(f"  트랜잭션 수: {block.get('nTx')}")
        print(f"  크기: {block.get('size')} bytes")
        print()

    print("✅ 블록 조회 테스트 완료")
    print()


def test_get_transaction(rpc_service: BitcoinRPCService, txid: str = None):
    """트랜잭션 조회 테스트"""

    print("-" * 60)
    print("트랜잭션 조회 테스트")
    print("-" * 60)
    print()

    if not txid:
        # 최신 블록에서 첫 번째 트랜잭션 조회
        block_count = rpc_service.get_block_count()
        if not block_count:
            print("❌ 블록 높이 조회 실패")
            return

        block_hash = rpc_service.get_block_hash(block_count)
        if not block_hash:
            print("❌ 블록 해시 조회 실패")
            return

        block = rpc_service.get_block(block_hash, verbosity=1)
        if not block or "tx" not in block:
            print("❌ 블록 정보 조회 실패")
            return

        txid = block["tx"][0]
        print(f"최신 블록의 첫 번째 트랜잭션 조회")

    print(f"TXID: {txid}")
    print()

    # 트랜잭션 상세 정보 조회
    tx = rpc_service.get_raw_transaction(txid, verbose=True)
    if not tx:
        print("❌ 트랜잭션 조회 실패")
        return

    print("트랜잭션 정보:")
    print(f"  - 해시: {tx.get('hash')}")
    print(f"  - 크기: {tx.get('size')} bytes")
    print(f"  - 입력 수: {len(tx.get('vin', []))}")
    print(f"  - 출력 수: {len(tx.get('vout', []))}")

    if "blockheight" in tx:
        print(f"  - 블록 높이: {tx.get('blockheight')}")

    if "time" in tx:
        print(f"  - 시간: {tx.get('time')}")

    print()
    print("✅ 트랜잭션 조회 테스트 완료")
    print()


def main():
    """메인 함수"""

    try:
        # 1. 연결 테스트
        success, rpc_service = test_connection()

        if not success:
            sys.exit(1)

        # 2. 최신 블록 조회 테스트
        try:
            test_get_latest_blocks(rpc_service, num_blocks=3)
        except Exception as e:
            logger.error(f"블록 조회 테스트 실패: {str(e)}", exc_info=True)
            print(f"⚠️  블록 조회 테스트 중 에러 발생: {str(e)}")
            print()

        # 3. 트랜잭션 조회 테스트
        try:
            test_get_transaction(rpc_service)
        except Exception as e:
            logger.error(f"트랜잭션 조회 테스트 실패: {str(e)}", exc_info=True)
            print(f"⚠️  트랜잭션 조회 테스트 중 에러 발생: {str(e)}")
            print()

        print("=" * 60)
        print("모든 테스트 완료")
        print("=" * 60)

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
