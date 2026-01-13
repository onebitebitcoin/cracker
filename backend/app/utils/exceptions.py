"""Custom exceptions"""


class BitcoinCrackerException(Exception):
    """Base exception for Bitcoin Cracker"""
    pass


class AddressNotFoundException(BitcoinCrackerException):
    """Address not found in database"""
    pass


class TransactionNotFoundException(BitcoinCrackerException):
    """Transaction not found in database"""
    pass


class ClusterNotFoundException(BitcoinCrackerException):
    """Cluster not found in database"""
    pass


class InvalidAddressFormatException(BitcoinCrackerException):
    """Invalid Bitcoin address format"""
    pass


class InvalidTransactionIdException(BitcoinCrackerException):
    """Invalid transaction ID format"""
    pass
