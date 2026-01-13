#!/usr/bin/env python3
"""
Scripthash 변환 테스트 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.utils.bitcoin import address_to_scripthash
from backend.app.services.electrum_client import ElectrumClient
from backend.app.config import settings


def test_scripthash_conversion():
    """Scripthash 변환 테스트"""
    print("=" * 60)
    print("Scripthash 변환 테스트")
    print("=" * 60)
    print()

    # 테스트 주소들
    test_addresses = [
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Legacy (P2PKH)"),  # Genesis block
        ("3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy", "P2SH"),  # Bitfinex cold wallet
        ("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", "Bech32 (Segwit)"),  # Binance
        ("bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97", "Bech32 (Segwit)"),  # Random
    ]

    for address, addr_type in test_addresses:
        print(f"주소: {address}")
        print(f"타입: {addr_type}")

        scripthash = address_to_scripthash(address)

        if scripthash:
            print(f"✅ Scripthash: {scripthash}")
        else:
            print(f"❌ 변환 실패")

        print()


def test_electrum_balance():
    """Electrum 서버로 실제 잔액 조회 테스트"""
    print("=" * 60)
    print("Electrum 서버 잔액 조회 테스트")
    print("=" * 60)
    print()

    # Electrum 클라이언트 생성
    client = ElectrumClient(
        host=settings.bitcoin_rpc_host,
        port=settings.bitcoin_rpc_port,
        use_ssl=settings.bitcoin_rpc_use_ssl
    )

    # 연결
    if not client.connect():
        print("❌ Electrum 서버 연결 실패")
        return

    print("✅ Electrum 서버 연결 성공")
    print()

    # 테스트 주소 (활동이 있는 주소)
    test_addresses = [
        "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97",  # Bitfinex hot wallet
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis (잔액 있음)
        "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",  # Binance
    ]

    for address in test_addresses:
        print(f"주소: {address}")

        # Scripthash 변환
        scripthash = address_to_scripthash(address)
        if scripthash:
            print(f"  Scripthash: {scripthash[:32]}...")
        else:
            print(f"  ❌ Scripthash 변환 실패")
            print()
            continue

        # 잔액 조회
        balance = client.get_balance(address)

        if balance is not None:
            confirmed_btc = balance.get("confirmed", 0) / 100_000_000
            unconfirmed_btc = balance.get("unconfirmed", 0) / 100_000_000

            print(f"  ✅ 잔액 조회 성공")
            print(f"     - 확인된 잔액: {confirmed_btc:.8f} BTC")
            print(f"     - 미확인 잔액: {unconfirmed_btc:.8f} BTC")

            # 트랜잭션 히스토리 조회
            history = client.get_history(address)
            if history is not None:
                print(f"     - 트랜잭션 수: {len(history)}개")
        else:
            print(f"  ❌ 잔액 조회 실패")

        print()

    # 연결 종료
    client.disconnect()


def main():
    """메인 함수"""
    try:
        # 1. Scripthash 변환 테스트
        test_scripthash_conversion()

        # 2. Electrum 서버로 실제 조회 테스트
        test_electrum_balance()

        print("=" * 60)
        print("모든 테스트 완료")
        print("=" * 60)

    except KeyboardInterrupt:
        print()
        print("테스트 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
