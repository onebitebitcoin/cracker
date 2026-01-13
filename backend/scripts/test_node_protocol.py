#!/usr/bin/env python3
"""
Bitcoin 노드 프로토콜 확인 스크립트
"""
import socket
import json


def test_electrum_protocol(host: str, port: int):
    """Electrum 프로토콜 테스트"""
    print(f"Electrum 프로토콜 테스트: {host}:{port}")
    print("-" * 60)

    try:
        # TCP 소켓 생성
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))

        # Electrum server.version 요청
        request = {
            "id": 1,
            "method": "server.version",
            "params": ["test-client", "1.4"]
        }

        message = json.dumps(request) + "\n"
        sock.sendall(message.encode())

        # 응답 수신
        response = sock.recv(4096).decode()
        sock.close()

        print(f"요청: {request}")
        print(f"응답: {response}")
        print()

        # 응답 파싱
        response_data = json.loads(response)

        if "result" in response_data:
            print("✅ Electrum 서버입니다!")
            print(f"서버 정보: {response_data['result']}")
            return True, "electrum"
        else:
            print("❌ Electrum 서버가 아닙니다")
            return False, None

    except Exception as e:
        print(f"❌ Electrum 프로토콜 테스트 실패: {str(e)}")
        return False, None


def test_bitcoin_rpc(host: str, port: int):
    """Bitcoin Core RPC 테스트 (HTTP JSON-RPC)"""
    print(f"Bitcoin Core RPC 테스트: {host}:{port}")
    print("-" * 60)

    try:
        import requests

        # Bitcoin Core RPC 요청
        url = f"http://{host}:{port}"
        headers = {"content-type": "application/json"}
        payload = {
            "jsonrpc": "1.0",
            "id": "test",
            "method": "getblockcount",
            "params": []
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"요청: {payload}")
        print(f"응답 상태: {response.status_code}")
        print(f"응답: {response.text[:200]}")
        print()

        if response.status_code == 200:
            print("✅ Bitcoin Core RPC 서버입니다!")
            return True, "bitcoin-rpc"
        else:
            print("❌ Bitcoin Core RPC 서버가 아닙니다")
            return False, None

    except Exception as e:
        print(f"❌ Bitcoin Core RPC 테스트 실패: {str(e)}")
        return False, None


def main():
    """메인 함수"""

    host = "175.195.68.72"
    port = 50001

    print("=" * 60)
    print("Bitcoin 노드 프로토콜 확인")
    print("=" * 60)
    print(f"호스트: {host}")
    print(f"포트: {port}")
    print()
    print("=" * 60)
    print()

    # 1. Electrum 프로토콜 테스트
    success, protocol = test_electrum_protocol(host, port)
    if success:
        print()
        print("결론: Electrum 서버입니다.")
        print("Bitcoin Core RPC 연결을 사용할 수 없습니다.")
        print("Electrum 클라이언트 라이브러리를 사용해야 합니다.")
        return

    print()

    # 2. Bitcoin Core RPC 테스트
    success, protocol = test_bitcoin_rpc(host, port)
    if success:
        print()
        print("결론: Bitcoin Core RPC 서버입니다.")
        return

    print()
    print("결론: 알 수 없는 프로토콜입니다.")


if __name__ == "__main__":
    main()
