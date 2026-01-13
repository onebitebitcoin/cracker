"""Database configuration and session management"""
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# SQLite3 연결 URL
DATABASE_URL = "sqlite:///./bitcoin_analysis.db"

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # FastAPI용
    poolclass=StaticPool,  # 단일 연결 풀
    echo=False  # SQL 로그 출력 (개발 시 True로 변경 가능)
)

# PRAGMA 설정
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """SQLite3 PRAGMA 설정"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA cache_size = -64000")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.close()
    logger.info("SQLite3 PRAGMA 설정 완료")

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()

# 의존성 주입
def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화"""
    logger.info("데이터베이스 테이블 생성 시작")
    Base.metadata.create_all(bind=engine)
    logger.info("데이터베이스 테이블 생성 완료")
