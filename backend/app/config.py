"""
Application Configuration
환경 변수 및 설정 관리
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Database
    database_url: str = Field(
        default="sqlite:///./bitcoin_analysis.db",
        alias="DATABASE_URL"
    )

    # Bitcoin RPC
    bitcoin_rpc_host: str = Field(
        default="localhost",
        alias="BITCOIN_RPC_HOST"
    )
    bitcoin_rpc_port: int = Field(
        default=8332,
        alias="BITCOIN_RPC_PORT"
    )
    bitcoin_rpc_user: str = Field(
        default="",
        alias="BITCOIN_RPC_USER"
    )
    bitcoin_rpc_password: str = Field(
        default="",
        alias="BITCOIN_RPC_PASSWORD"
    )
    bitcoin_rpc_use_ssl: bool = Field(
        default=False,
        alias="BITCOIN_RPC_USE_SSL"
    )

    # Redis
    redis_url: Optional[str] = Field(
        default=None,
        alias="REDIS_URL"
    )

    # Application
    secret_key: str = Field(
        default="dev_secret_key",
        alias="SECRET_KEY"
    )
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL"
    )
    environment: str = Field(
        default="development",
        alias="ENVIRONMENT"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # .env 파일의 추가 필드 무시


# 싱글톤 설정 인스턴스
settings = Settings()
