#!/bin/bash

# Bitcoin Cracker - Deployment Script
# Railway를 통해 프로젝트를 배포합니다

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

echo "=========================================="
echo "Bitcoin Cracker - Deployment"
echo "=========================================="
echo ""

# 환경 설정
ENVIRONMENT=${1:-"production"}

case $ENVIRONMENT in
    "--prod"|"production")
        ENVIRONMENT="production"
        ;;
    "--staging"|"staging")
        ENVIRONMENT="staging"
        ;;
    *)
        ENVIRONMENT="production"
        ;;
esac

info "배포 환경: $ENVIRONMENT"
echo ""

# 1. Railway CLI 확인
info "1. Railway CLI 확인 중..."
if ! command -v railway &> /dev/null; then
    error "Railway CLI가 설치되어 있지 않습니다."
    echo "   설치 방법:"
    echo "   $ npm install -g @railway/cli"
    echo "   또는"
    echo "   $ brew install railway"
    exit 1
fi
success "Railway CLI 발견"

# 2. Railway 로그인 확인
echo ""
info "2. Railway 인증 확인 중..."
if ! railway whoami &> /dev/null; then
    warning "Railway에 로그인되어 있지 않습니다."
    echo "   로그인을 시작합니다..."
    railway login
fi
success "Railway 인증 완료"

# 3. 의존성 설치
echo ""
info "3. 의존성 설치 중..."
read -p "의존성을 재설치하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./install.sh
    success "의존성 설치 완료"
else
    warning "의존성 설치를 건너뜁니다."
fi

# 4. 테스트 실행
echo ""
info "4. 테스트 실행 중..."
read -p "배포 전에 테스트를 실행하시겠습니까? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    if ./test.sh; then
        success "모든 테스트 통과"
    else
        error "테스트 실패! 배포를 중단합니다."
        exit 1
    fi
else
    warning "테스트를 건너뜁니다."
fi

# 5. Frontend 빌드
echo ""
info "5. Frontend 빌드 중..."
if [ -d "frontend" ]; then
    cd frontend
    npm run build
    cd ..
    success "Frontend 빌드 완료"
else
    warning "frontend/ 디렉토리가 없습니다."
fi

# 6. Railway 프로젝트 연결
echo ""
info "6. Railway 프로젝트 연결 확인 중..."
if [ ! -f "railway.json" ]; then
    warning "Railway 프로젝트가 연결되어 있지 않습니다."
    read -p "새 프로젝트를 생성하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        railway init
    else
        error "Railway 프로젝트가 필요합니다."
        exit 1
    fi
fi
success "Railway 프로젝트 연결됨"

# 7. 환경 변수 설정
echo ""
info "7. 환경 변수 설정 중..."
if [ -f ".env" ]; then
    warning "로컬 .env 파일이 발견되었습니다."
    read -p "환경 변수를 Railway에 업로드하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # .env 파일의 각 변수를 Railway에 설정
        while IFS='=' read -r key value; do
            # 주석과 빈 줄 건너뛰기
            if [[ ! $key =~ ^# ]] && [ -n "$key" ]; then
                railway variables set "$key=$value" --environment $ENVIRONMENT
            fi
        done < .env
        success "환경 변수 업로드 완료"
    fi
else
    warning ".env 파일이 없습니다."
    echo "   Railway 대시보드에서 환경 변수를 수동으로 설정해주세요."
fi

# 8. Git 커밋 확인
echo ""
info "8. Git 상태 확인 중..."
if [ -d ".git" ]; then
    if [[ -n $(git status -s) ]]; then
        warning "커밋되지 않은 변경사항이 있습니다."
        read -p "변경사항을 커밋하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            echo "커밋 메시지를 입력하세요:"
            read -r COMMIT_MESSAGE
            git commit -m "$COMMIT_MESSAGE"
            success "커밋 완료"
        fi
    fi
else
    warning "Git 저장소가 아닙니다."
fi

# 9. Railway 배포
echo ""
info "9. Railway에 배포 중..."
echo "   환경: $ENVIRONMENT"
echo ""

railway up --environment $ENVIRONMENT

if [ $? -eq 0 ]; then
    success "배포가 완료되었습니다!"
else
    error "배포 중 오류가 발생했습니다."
    exit 1
fi

# 10. 배포 URL 표시
echo ""
info "10. 배포 정보 확인 중..."
DEPLOY_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

if [ -n "$DEPLOY_URL" ]; then
    echo ""
    echo "=========================================="
    success "배포 성공!"
    echo "=========================================="
    echo ""
    echo "배포 URL: $DEPLOY_URL"
    echo "환경: $ENVIRONMENT"
    echo ""
    echo "Railway 대시보드: https://railway.app/dashboard"
    echo ""
else
    warning "배포 URL을 가져올 수 없습니다."
    echo "   Railway 대시보드에서 확인해주세요: https://railway.app/dashboard"
fi

# 11. 로그 확인 (선택사항)
echo ""
read -p "배포 로그를 확인하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    railway logs --environment $ENVIRONMENT
fi

echo ""
success "배포 프로세스가 완료되었습니다."
