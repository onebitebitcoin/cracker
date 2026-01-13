"""Helper functions"""
import re
from typing import Optional


def is_valid_bitcoin_address(address: str) -> bool:
    """Validate Bitcoin address format (simplified)"""
    if not address:
        return False

    # Bech32 (bc1...)
    if address.startswith('bc1'):
        return len(address) >= 42 and len(address) <= 62

    # Legacy (1...)
    if address.startswith('1'):
        return len(address) >= 26 and len(address) <= 35

    # P2SH (3...)
    if address.startswith('3'):
        return len(address) >= 26 and len(address) <= 35

    return False


def is_valid_txid(txid: str) -> bool:
    """Validate transaction ID format"""
    if not txid:
        return False

    # Transaction ID is 64 character hex string
    return bool(re.match(r'^[a-fA-F0-9]{64}$', txid))


def shorten_address(address: str, prefix_len: int = 10, suffix_len: int = 6) -> str:
    """Shorten Bitcoin address for display"""
    if len(address) <= prefix_len + suffix_len:
        return address
    return f"{address[:prefix_len]}...{address[-suffix_len:]}"


def shorten_txid(txid: str, prefix_len: int = 10) -> str:
    """Shorten transaction ID for display"""
    if len(txid) <= prefix_len:
        return txid
    return f"{txid[:prefix_len]}..."


def format_btc_amount(amount: float, decimals: int = 8) -> str:
    """Format BTC amount with proper decimals"""
    return f"{amount:.{decimals}f}".rstrip('0').rstrip('.')


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)
