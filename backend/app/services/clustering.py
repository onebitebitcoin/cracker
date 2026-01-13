"""Clustering service using Union-Find algorithm"""
from typing import Dict, List, Set
import uuid
from ..utils.logger import logger


class UnionFind:
    """Union-Find data structure for clustering"""

    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def make_set(self, address: str):
        """Create a new set for an address"""
        if address not in self.parent:
            self.parent[address] = address
            self.rank[address] = 0

    def find(self, address: str) -> str:
        """Find the root of the set containing address"""
        if address not in self.parent:
            self.make_set(address)

        if self.parent[address] != address:
            # Path compression
            self.parent[address] = self.find(self.parent[address])

        return self.parent[address]

    def union(self, addr1: str, addr2: str):
        """Union two sets"""
        root1 = self.find(addr1)
        root2 = self.find(addr2)

        if root1 == root2:
            return

        # Union by rank
        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2
        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1

    def get_clusters(self) -> Dict[str, Set[str]]:
        """Get all clusters as a dictionary of root -> addresses"""
        clusters: Dict[str, Set[str]] = {}

        for address in self.parent:
            root = self.find(address)
            if root not in clusters:
                clusters[root] = set()
            clusters[root].add(address)

        return clusters


class ClusteringService:
    """Service for clustering Bitcoin addresses"""

    @staticmethod
    def cluster_by_co_spending(transactions: List[Dict]) -> Dict[str, Set[str]]:
        """
        Cluster addresses using co-spending heuristic

        Args:
            transactions: List of transaction dictionaries with 'inputs' field

        Returns:
            Dictionary mapping cluster_id -> set of addresses
        """
        logger.info(f"Co-spending 클러스터링 시작: {len(transactions)}개 트랜잭션")

        uf = UnionFind()

        # Process each transaction
        for tx in transactions:
            inputs = tx.get('inputs', [])

            # Extract input addresses
            input_addresses = [inp.get('address') for inp in inputs if inp.get('address')]

            # If multiple inputs, they belong to the same cluster
            if len(input_addresses) >= 2:
                # Union all input addresses
                first = input_addresses[0]
                for addr in input_addresses[1:]:
                    uf.union(first, addr)

        # Get clusters
        clusters = uf.get_clusters()

        logger.info(f"클러스터링 완료: {len(clusters)}개 클러스터 생성")
        return clusters

    @staticmethod
    def assign_cluster_ids(clusters: Dict[str, Set[str]]) -> Dict[str, str]:
        """
        Assign UUID to each cluster

        Args:
            clusters: Dictionary of root -> addresses

        Returns:
            Dictionary mapping address -> cluster_id
        """
        address_to_cluster: Dict[str, str] = {}

        for root, addresses in clusters.items():
            cluster_id = str(uuid.uuid4())
            for addr in addresses:
                address_to_cluster[addr] = cluster_id

        logger.info(f"클러스터 ID 할당 완료: {len(address_to_cluster)}개 주소")
        return address_to_cluster

    @staticmethod
    def calculate_cluster_stats(cluster_id: str, addresses: List[Dict]) -> Dict:
        """
        Calculate statistics for a cluster

        Args:
            cluster_id: Cluster UUID
            addresses: List of address dictionaries

        Returns:
            Dictionary with cluster statistics
        """
        if not addresses:
            return {
                'id': cluster_id,
                'address_count': 0,
                'total_balance': 0.0,
                'total_received': 0.0,
                'total_sent': 0.0,
                'tx_count': 0
            }

        stats = {
            'id': cluster_id,
            'address_count': len(addresses),
            'total_balance': sum(addr.get('balance', 0) for addr in addresses),
            'total_received': sum(addr.get('total_received', 0) for addr in addresses),
            'total_sent': sum(addr.get('total_sent', 0) for addr in addresses),
            'tx_count': sum(addr.get('tx_count', 0) for addr in addresses)
        }

        return stats
