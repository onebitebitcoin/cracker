"""Graph generation service"""
from typing import List, Dict, Set
from ..schemas.common import GraphNode, GraphEdge, GraphData
from ..utils.logger import logger


class GraphService:
    """Service for generating graph data"""

    @staticmethod
    def generate_address_graph(
        address: str,
        transactions: List[Dict],
        depth: int = 3
    ) -> GraphData:
        """
        Generate graph data for an address and its connections

        Args:
            address: Starting address
            transactions: List of transactions
            depth: Maximum depth for traversal

        Returns:
            GraphData with nodes and edges
        """
        logger.info(f"주소 그래프 생성: {address}, depth={depth}")

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        visited_addresses: Set[str] = set()
        visited_txs: Set[str] = set()

        # Add starting address node
        nodes.append(GraphNode(
            id=address,
            type="address",
            label=address[:10] + "...",
            cluster_id=None
        ))
        visited_addresses.add(address)

        # Process transactions
        for tx in transactions[:50]:  # Limit to 50 transactions for performance
            txid = tx.get('txid')
            if not txid or txid in visited_txs:
                continue

            visited_txs.add(txid)

            # Add transaction node
            nodes.append(GraphNode(
                id=txid,
                type="transaction",
                label=txid[:10] + "...",
            ))

            # Add edges for inputs
            for inp in tx.get('inputs', []):
                inp_addr = inp.get('address')
                if not inp_addr:
                    continue

                # Add input address node if not visited
                if inp_addr not in visited_addresses:
                    nodes.append(GraphNode(
                        id=inp_addr,
                        type="address",
                        label=inp_addr[:10] + "...",
                    ))
                    visited_addresses.add(inp_addr)

                # Add edge from address to transaction
                edges.append(GraphEdge(
                    source=inp_addr,
                    target=txid,
                    amount=inp.get('amount', 0),
                    timestamp=tx.get('timestamp')
                ))

            # Add edges for outputs
            for out in tx.get('outputs', []):
                out_addr = out.get('address')
                if not out_addr:
                    continue

                # Add output address node if not visited
                if out_addr not in visited_addresses:
                    nodes.append(GraphNode(
                        id=out_addr,
                        type="address",
                        label=out_addr[:10] + "...",
                    ))
                    visited_addresses.add(out_addr)

                # Add edge from transaction to address
                edges.append(GraphEdge(
                    source=txid,
                    target=out_addr,
                    amount=out.get('amount', 0),
                    timestamp=tx.get('timestamp')
                ))

        logger.info(f"그래프 생성 완료: {len(nodes)}개 노드, {len(edges)}개 엣지")
        return GraphData(nodes=nodes, edges=edges)

    @staticmethod
    def generate_cluster_graph(
        cluster_id: str,
        addresses: List[Dict],
        transactions: List[Dict]
    ) -> GraphData:
        """
        Generate graph data for a cluster

        Args:
            cluster_id: Cluster ID
            addresses: List of addresses in cluster
            transactions: List of transactions

        Returns:
            GraphData with nodes and edges
        """
        logger.info(f"클러스터 그래프 생성: {cluster_id}")

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # Add address nodes
        for addr in addresses[:100]:  # Limit to 100 addresses
            nodes.append(GraphNode(
                id=addr.get('address'),
                type="address",
                label=addr.get('address', '')[:10] + "...",
                balance=addr.get('balance', 0),
                cluster_id=cluster_id
            ))

        # Add transaction edges between addresses
        address_set = {addr.get('address') for addr in addresses}

        for tx in transactions[:200]:  # Limit transactions
            txid = tx.get('txid')
            inputs = tx.get('inputs', [])
            outputs = tx.get('outputs', [])

            # Find inputs and outputs in this cluster
            cluster_inputs = [inp for inp in inputs if inp.get('address') in address_set]
            cluster_outputs = [out for out in outputs if out.get('address') in address_set]

            # Create edges between addresses via transactions
            for inp in cluster_inputs:
                for out in cluster_outputs:
                    if inp.get('address') != out.get('address'):
                        edges.append(GraphEdge(
                            source=inp.get('address'),
                            target=out.get('address'),
                            amount=out.get('amount', 0),
                            timestamp=tx.get('timestamp')
                        ))

        logger.info(f"클러스터 그래프 완료: {len(nodes)}개 노드, {len(edges)}개 엣지")
        return GraphData(nodes=nodes, edges=edges)
