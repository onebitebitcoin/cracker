"""
Bitcoin 유틸리티 함수
주소 변환, scripthash 생성 등
"""
import hashlib
from typing import Optional
from ..utils.logger import logger


def base58_decode(address: str) -> bytes:
    """Base58 디코딩"""
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    decoded = 0
    multi = 1
    for char in reversed(address):
        if char not in alphabet:
            raise ValueError(f"Invalid Base58 character: {char}")
        decoded += multi * alphabet.index(char)
        multi *= 58

    # 정수를 바이트로 변환
    hex_str = hex(decoded)[2:]
    if len(hex_str) % 2:
        hex_str = '0' + hex_str

    result = bytes.fromhex(hex_str)

    # 앞의 '1' 문자는 0x00 바이트를 의미
    pad = 0
    for char in address:
        if char == '1':
            pad += 1
        else:
            break

    return b'\x00' * pad + result


def bech32_decode(address: str) -> Optional[bytes]:
    """Bech32 디코딩 (간단한 구현)"""
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

    if not address.startswith('bc1') and not address.startswith('tb1'):
        return None

    # HRP와 데이터 분리
    if '1' not in address:
        return None

    hrp, data_part = address.rsplit('1', 1)

    # 데이터 부분을 5비트 값으로 변환
    data = []
    for char in data_part[:-6]:  # 마지막 6자는 체크섬
        if char not in charset:
            return None
        data.append(charset.index(char))

    # 5비트 -> 8비트 변환
    converted = []
    bits = 0
    value = 0

    for d in data[1:]:  # 첫 번째는 witness version
        value = (value << 5) | d
        bits += 5

        if bits >= 8:
            bits -= 8
            converted.append((value >> bits) & 0xff)
            value &= (1 << bits) - 1

    return bytes(converted)


def address_to_script_pubkey(address: str) -> Optional[bytes]:
    """
    Bitcoin 주소를 scriptPubKey로 변환

    Args:
        address: Bitcoin 주소

    Returns:
        scriptPubKey 바이트 또는 None
    """
    try:
        # Legacy 주소 (1로 시작 - P2PKH)
        if address.startswith('1'):
            try:
                decoded = base58_decode(address)
                # 체크섬 제거 (마지막 4바이트)
                pubkey_hash = decoded[1:-4]

                if len(pubkey_hash) != 20:
                    logger.error(f"Invalid pubkey hash length: {len(pubkey_hash)}")
                    return None

                # P2PKH scriptPubKey: OP_DUP OP_HASH160 <pubkey_hash> OP_EQUALVERIFY OP_CHECKSIG
                script = bytes([0x76, 0xa9, 0x14]) + pubkey_hash + bytes([0x88, 0xac])
                return script
            except Exception as e:
                logger.error(f"Legacy 주소 변환 실패: {e}")
                return None

        # P2SH 주소 (3로 시작)
        elif address.startswith('3'):
            try:
                decoded = base58_decode(address)
                script_hash = decoded[1:-4]

                if len(script_hash) != 20:
                    logger.error(f"Invalid script hash length: {len(script_hash)}")
                    return None

                # P2SH scriptPubKey: OP_HASH160 <script_hash> OP_EQUAL
                script = bytes([0xa9, 0x14]) + script_hash + bytes([0x87])
                return script
            except Exception as e:
                logger.error(f"P2SH 주소 변환 실패: {e}")
                return None

        # Bech32 주소 (bc1로 시작 - Segwit)
        elif address.startswith('bc1') or address.startswith('tb1'):
            try:
                witness_program = bech32_decode(address)
                if not witness_program:
                    logger.error("Bech32 디코딩 실패")
                    return None

                # Witness version (0)
                witness_version = 0

                # scriptPubKey: OP_0 <witness_program>
                script = bytes([witness_version, len(witness_program)]) + witness_program
                return script
            except Exception as e:
                logger.error(f"Bech32 주소 변환 실패: {e}")
                return None

        else:
            logger.error(f"지원하지 않는 주소 형식: {address}")
            return None

    except Exception as e:
        logger.error(f"주소 변환 중 예외 발생: {e}", exc_info=True)
        return None


def address_to_scripthash(address: str) -> Optional[str]:
    """
    Bitcoin 주소를 Electrum scripthash로 변환

    Electrum scripthash = SHA256(scriptPubKey)의 역순 hex

    Args:
        address: Bitcoin 주소

    Returns:
        scripthash (hex) 또는 None
    """
    try:
        # scriptPubKey 생성
        script = address_to_script_pubkey(address)
        if not script:
            logger.error(f"scriptPubKey 생성 실패: {address}")
            return None

        # SHA256 해시
        script_hash = hashlib.sha256(script).digest()

        # 역순으로 변환
        reversed_hash = script_hash[::-1]

        # hex 문자열로 변환
        scripthash = reversed_hash.hex()

        logger.debug(f"주소 변환: {address} -> scripthash: {scripthash}")

        return scripthash

    except Exception as e:
        logger.error(f"Scripthash 변환 실패: {address}, 에러={str(e)}", exc_info=True)
        return None
