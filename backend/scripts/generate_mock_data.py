"""Mock Bitcoin data generator"""
import random
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class MockDataGenerator:
    """Bitcoin mock data generator"""

    def __init__(self, num_addresses: int = 80, num_transactions: int = 250, num_clusters: int = 15):
        self.num_addresses = num_addresses
        self.num_transactions = num_transactions
        self.num_clusters = num_clusters
        self.addresses = []
        self.clusters = []
        self.transactions = []

    def generate_bitcoin_address(self) -> str:
        """Generate a fake Bitcoin Bech32 address"""
        # bc1q + 39 random hex characters
        random_hex = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=39))
        return f"bc1q{random_hex}"

    def generate_txid(self) -> str:
        """Generate a fake transaction ID"""
        return hashlib.sha256(str(random.random()).encode()).hexdigest()

    def generate_clusters(self) -> List[Dict]:
        """Generate cluster data"""
        clusters = []
        now = datetime.utcnow()

        for i in range(self.num_clusters):
            cluster_id = str(uuid.uuid4())
            first_seen = (now - timedelta(days=random.randint(30, 365))).isoformat()
            last_seen = (now - timedelta(days=random.randint(0, 30))).isoformat()

            cluster = {
                'id': cluster_id,
                'label': f'Cluster {chr(65 + i)}',  # Cluster A, B, C...
                'address_count': 0,  # Will be calculated later
                'total_balance': 0.0,
                'total_received': 0.0,
                'total_sent': 0.0,
                'tx_count': 0,
                'first_seen': first_seen,
                'last_seen': last_seen,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            clusters.append(cluster)

        self.clusters = clusters
        return clusters

    def generate_addresses(self) -> List[Dict]:
        """Generate address data"""
        addresses = []
        now = datetime.utcnow()

        # Ensure all clusters have at least one address
        cluster_indices = list(range(len(self.clusters)))
        random.shuffle(cluster_indices)

        for i in range(self.num_addresses):
            address = self.generate_bitcoin_address()

            # Assign to cluster (some addresses belong to clusters, some don't)
            if i < len(self.clusters):
                # First N addresses get assigned to clusters (one per cluster)
                cluster_id = self.clusters[cluster_indices[i]]['id']
            elif random.random() < 0.7:  # 70% chance to belong to a cluster
                cluster_id = random.choice(self.clusters)['id']
            else:
                cluster_id = None

            balance = round(random.uniform(0.001, 10.0), 8)
            total_received = round(balance + random.uniform(0, 50.0), 8)
            total_sent = round(total_received - balance, 8)
            tx_count = random.randint(1, 100)

            first_seen = (now - timedelta(days=random.randint(30, 365))).isoformat()
            last_seen = (now - timedelta(days=random.randint(0, 30))).isoformat()

            addr_data = {
                'address': address,
                'cluster_id': cluster_id,
                'balance': balance,
                'total_received': total_received,
                'total_sent': total_sent,
                'tx_count': tx_count,
                'first_seen': first_seen,
                'last_seen': last_seen,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            addresses.append(addr_data)

            # Update cluster stats
            if cluster_id:
                for cluster in self.clusters:
                    if cluster['id'] == cluster_id:
                        cluster['address_count'] += 1
                        cluster['total_balance'] += balance
                        cluster['total_received'] += total_received
                        cluster['total_sent'] += total_sent
                        cluster['tx_count'] += tx_count
                        break

        self.addresses = addresses
        return addresses

    def generate_transactions(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Generate transaction data with inputs and outputs"""
        transactions = []
        inputs = []
        outputs = []
        now = datetime.utcnow()

        for i in range(self.num_transactions):
            txid = self.generate_txid()
            block_height = 850000 + i
            block_hash = hashlib.sha256(f"block{block_height}".encode()).hexdigest()
            timestamp = (now - timedelta(days=random.randint(0, 365))).isoformat()

            # Random number of inputs/outputs
            num_inputs = random.randint(1, 4)
            num_outputs = random.randint(1, 3)

            # Generate inputs (from existing addresses)
            total_input = 0.0
            tx_inputs = []
            input_addresses = random.sample(self.addresses, min(num_inputs, len(self.addresses)))

            for idx, addr_data in enumerate(input_addresses):
                amount = round(random.uniform(0.1, 5.0), 8)
                total_input += amount

                tx_input = {
                    'txid': txid,
                    'vout_index': idx,
                    'prev_txid': self.generate_txid(),
                    'prev_vout': random.randint(0, 2),
                    'address': addr_data['address'],
                    'amount': amount,
                    'script_sig': f"scriptsig_{random.randint(1000, 9999)}",
                    'sequence': 4294967295
                }
                tx_inputs.append(tx_input)

            # Generate outputs (to existing addresses)
            fee = round(random.uniform(0.0001, 0.001), 8)
            total_output = total_input - fee
            remaining_output = total_output
            tx_outputs = []
            output_addresses = random.sample(self.addresses, min(num_outputs, len(self.addresses)))

            for idx, addr_data in enumerate(output_addresses):
                if idx == num_outputs - 1:
                    # Last output gets remaining amount
                    amount = remaining_output
                else:
                    amount = round(random.uniform(0.1, remaining_output * 0.8), 8)
                    remaining_output -= amount

                tx_output = {
                    'txid': txid,
                    'vout': idx,
                    'address': addr_data['address'],
                    'amount': amount,
                    'script_pubkey': f"scriptpubkey_{random.randint(1000, 9999)}",
                    'spent': random.choice([0, 1]),
                    'spent_in_txid': self.generate_txid() if random.random() < 0.5 else None
                }
                tx_outputs.append(tx_output)

            # Create transaction
            transaction = {
                'txid': txid,
                'block_height': block_height,
                'block_hash': block_hash,
                'timestamp': timestamp,
                'fee': fee,
                'size': random.randint(200, 500),
                'input_count': num_inputs,
                'output_count': num_outputs,
                'total_input': round(total_input, 8),
                'total_output': round(total_output, 8),
                'created_at': now.isoformat()
            }

            transactions.append(transaction)
            inputs.extend(tx_inputs)
            outputs.extend(tx_outputs)

        self.transactions = transactions
        return transactions, inputs, outputs

    def generate_cluster_edges(self) -> List[Dict]:
        """Generate cluster edges (relationships between clusters)"""
        edges = []
        now = datetime.utcnow()

        # Create some edges between clusters
        num_edges = random.randint(5, 15)

        for _ in range(num_edges):
            source = random.choice(self.clusters)
            target = random.choice([c for c in self.clusters if c['id'] != source['id']])

            if not target:
                continue

            tx_count = random.randint(1, 20)
            total_amount = round(random.uniform(0.1, 100.0), 8)
            first_tx = (now - timedelta(days=random.randint(30, 365))).isoformat()
            last_tx = (now - timedelta(days=random.randint(0, 30))).isoformat()

            edge = {
                'source_cluster_id': source['id'],
                'target_cluster_id': target['id'],
                'tx_count': tx_count,
                'total_amount': total_amount,
                'first_tx_timestamp': first_tx,
                'last_tx_timestamp': last_tx
            }
            edges.append(edge)

        return edges

    def generate_all(self) -> Dict:
        """Generate all mock data"""
        print(f"클러스터 {self.num_clusters}개 생성 중...")
        clusters = self.generate_clusters()

        print(f"주소 {self.num_addresses}개 생성 중...")
        addresses = self.generate_addresses()

        print(f"트랜잭션 {self.num_transactions}개 생성 중...")
        transactions, inputs, outputs = self.generate_transactions()

        print("클러스터 관계 생성 중...")
        cluster_edges = self.generate_cluster_edges()

        print("Mock 데이터 생성 완료!")
        print(f"  - 클러스터: {len(clusters)}개")
        print(f"  - 주소: {len(addresses)}개")
        print(f"  - 트랜잭션: {len(transactions)}개")
        print(f"  - 트랜잭션 입력: {len(inputs)}개")
        print(f"  - 트랜잭션 출력: {len(outputs)}개")
        print(f"  - 클러스터 관계: {len(cluster_edges)}개")

        return {
            'clusters': clusters,
            'addresses': addresses,
            'transactions': transactions,
            'transaction_inputs': inputs,
            'transaction_outputs': outputs,
            'cluster_edges': cluster_edges
        }


if __name__ == "__main__":
    generator = MockDataGenerator()
    data = generator.generate_all()
