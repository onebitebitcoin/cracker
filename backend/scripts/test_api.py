#!/usr/bin/env python3
"""
API 엔드포인트 테스트 스크립트
"""
import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"

# 테스트 주소 (잘 알려진 Bitcoin 주소)
# 1) Satoshi의 Genesis block 주소
TEST_ADDRESSES = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis
    "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",  # Binance cold wallet (활동이 많음)
    "1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ",  # 활동이 많은 주소
]


def print_header(title):
    """헤더 출력"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def print_result(success, message, data=None):
    """결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{status}: {message}")
    if data:
        print(f"데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()


def test_server_health():
    """서버 상태 확인"""
    print_header("서버 상태 확인")

    try:
        # 루트 엔드포인트 접근
        response = requests.get("http://localhost:8000/", timeout=5)

        if response.status_code == 200:
            print_result(True, "서버가 실행 중입니다")
            return True
        else:
            print_result(False, f"서버 응답 오류: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_result(False, "서버에 연결할 수 없습니다. Backend 서버를 먼저 실행하세요.")
        print("실행 방법: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_result(False, f"예상치 못한 에러: {str(e)}")
        return False


def test_get_address(address):
    """주소 조회 테스트"""
    print_header(f"주소 조회: {address}")

    try:
        url = f"{BASE_URL}/addresses/{address}"
        print(f"요청 URL: {url}")

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print_result(True, "주소 정보 조회 성공")
            print(f"주소: {data.get('address')}")
            print(f"잔액: {data.get('balance')} BTC")
            print(f"확인된 잔액: {data.get('confirmed_balance')} BTC")
            print(f"미확인 잔액: {data.get('unconfirmed_balance')} BTC")
            print(f"트랜잭션 수: {data.get('tx_count')}")
            print(f"데이터 출처: {data.get('source')}")
            return True, data
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False, None

    except Exception as e:
        print_result(False, f"에러 발생: {str(e)}")
        return False, None


def test_get_address_transactions(address, limit=10):
    """주소 트랜잭션 히스토리 조회 테스트"""
    print_header(f"트랜잭션 히스토리 조회: {address}")

    try:
        url = f"{BASE_URL}/addresses/{address}/transactions"
        params = {"limit": limit, "offset": 0}
        print(f"요청 URL: {url}")
        print(f"파라미터: {params}")

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print_result(True, "트랜잭션 히스토리 조회 성공")
            print(f"전체 트랜잭션 수: {data.get('total')}")
            print(f"현재 페이지: {data.get('page')}/{data.get('total_pages')}")
            print(f"페이지 크기: {data.get('page_size')}")

            transactions = data.get('data', [])
            print(f"\n최근 트랜잭션 {len(transactions)}개:")
            for i, tx in enumerate(transactions[:5], 1):
                print(f"  {i}. TXID: {tx.get('txid')}")
                print(f"     블록 높이: {tx.get('block_height')}")

            return True, data
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False, None

    except Exception as e:
        print_result(False, f"에러 발생: {str(e)}")
        return False, None


def test_api_docs():
    """API 문서 접근 테스트"""
    print_header("API 문서 확인")

    try:
        url = "http://localhost:8000/docs"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print_result(True, "API 문서 접근 가능")
            print(f"URL: {url}")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False

    except Exception as e:
        print_result(False, f"에러 발생: {str(e)}")
        return False


def main():
    """메인 함수"""

    print("=" * 60)
    print("  Bitcoin Cracker - API 테스트")
    print("=" * 60)

    # 1. 서버 상태 확인
    if not test_server_health():
        return

    # 2. API 문서 확인
    test_api_docs()

    # 3. 주소 조회 테스트
    for i, address in enumerate(TEST_ADDRESSES[:2], 1):  # 처음 2개만 테스트
        print()
        print(f"[테스트 {i}/{2}]")

        # 주소 정보 조회
        success, addr_data = test_get_address(address)

        if success:
            time.sleep(1)  # API 부하 방지

            # 트랜잭션 히스토리 조회
            if addr_data and addr_data.get('tx_count', 0) > 0:
                test_get_address_transactions(address, limit=5)
                time.sleep(1)

    # 완료
    print()
    print("=" * 60)
    print("  모든 테스트 완료")
    print("=" * 60)
    print()
    print("추가 테스트:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")


if __name__ == "__main__":
    main()
