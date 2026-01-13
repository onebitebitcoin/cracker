"""Database seeding script"""
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, init_db
from app.models import Address, Transaction, TransactionInput, TransactionOutput, Cluster, ClusterEdge
from generate_mock_data import MockDataGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_database(db):
    """Clear all data from database"""
    logger.info("데이터베이스 초기화 중...")

    try:
        # Delete in correct order (respecting foreign keys)
        db.query(ClusterEdge).delete()
        db.query(TransactionInput).delete()
        db.query(TransactionOutput).delete()
        db.query(Transaction).delete()
        db.query(Address).delete()
        db.query(Cluster).delete()
        db.commit()
        logger.info("기존 데이터 삭제 완료")
    except Exception as e:
        logger.error(f"데이터 삭제 실패: {e}")
        db.rollback()
        raise


def seed_clusters(db, clusters_data):
    """Seed clusters"""
    logger.info(f"클러스터 {len(clusters_data)}개 저장 중...")

    for cluster_data in clusters_data:
        cluster = Cluster(**cluster_data)
        db.add(cluster)

    db.commit()
    logger.info("클러스터 저장 완료")


def seed_addresses(db, addresses_data):
    """Seed addresses"""
    logger.info(f"주소 {len(addresses_data)}개 저장 중...")

    for addr_data in addresses_data:
        address = Address(**addr_data)
        db.add(address)

    db.commit()
    logger.info("주소 저장 완료")


def seed_transactions(db, transactions_data, inputs_data, outputs_data):
    """Seed transactions with inputs and outputs"""
    logger.info(f"트랜잭션 {len(transactions_data)}개 저장 중...")

    # Create transactions
    for tx_data in transactions_data:
        transaction = Transaction(**tx_data)
        db.add(transaction)

    db.commit()
    logger.info("트랜잭션 저장 완료")

    # Create inputs
    logger.info(f"트랜잭션 입력 {len(inputs_data)}개 저장 중...")
    for input_data in inputs_data:
        tx_input = TransactionInput(**input_data)
        db.add(tx_input)

    db.commit()
    logger.info("트랜잭션 입력 저장 완료")

    # Create outputs
    logger.info(f"트랜잭션 출력 {len(outputs_data)}개 저장 중...")
    for output_data in outputs_data:
        tx_output = TransactionOutput(**output_data)
        db.add(tx_output)

    db.commit()
    logger.info("트랜잭션 출력 저장 완료")


def seed_cluster_edges(db, edges_data):
    """Seed cluster edges"""
    logger.info(f"클러스터 관계 {len(edges_data)}개 저장 중...")

    for edge_data in edges_data:
        edge = ClusterEdge(**edge_data)
        db.add(edge)

    db.commit()
    logger.info("클러스터 관계 저장 완료")


def seed_database(clear_existing=True):
    """Main seeding function"""
    logger.info("=== 데이터베이스 시딩 시작 ===")

    # Initialize database tables
    logger.info("데이터베이스 테이블 생성...")
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Clear existing data if requested
        if clear_existing:
            clear_database(db)

        # Generate mock data
        generator = MockDataGenerator(
            num_addresses=80,
            num_transactions=250,
            num_clusters=15
        )
        data = generator.generate_all()

        # Seed in correct order (respecting foreign keys)
        seed_clusters(db, data['clusters'])
        seed_addresses(db, data['addresses'])
        seed_transactions(db, data['transactions'], data['transaction_inputs'], data['transaction_outputs'])
        seed_cluster_edges(db, data['cluster_edges'])

        logger.info("=== 데이터베이스 시딩 완료 ===")
        logger.info(f"총 {len(data['addresses'])}개 주소, {len(data['transactions'])}개 트랜잭션, {len(data['clusters'])}개 클러스터")

        # Print some sample data
        sample_address = db.query(Address).first()
        if sample_address:
            logger.info(f"\n샘플 주소: {sample_address.address}")
            logger.info(f"  잔액: {sample_address.balance} BTC")
            logger.info(f"  클러스터 ID: {sample_address.cluster_id}")

        sample_cluster = db.query(Cluster).first()
        if sample_cluster:
            logger.info(f"\n샘플 클러스터: {sample_cluster.label}")
            logger.info(f"  주소 수: {sample_cluster.address_count}개")
            logger.info(f"  총 잔액: {sample_cluster.total_balance} BTC")

    except Exception as e:
        logger.error(f"시딩 중 오류 발생: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(clear_existing=True)
