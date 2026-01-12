# Claude Project Rules

## Language
- 모든 답변은 한국어로 작성한다.
- 코드/로그/에러 메시지는 원문 유지, 설명은 한국어로 한다.

## Writing / UI Guidelines
1) 이모지를 사용하지 말고 아이콘을 사용할 것
   - 텍스트에서 이모지 금지
   - UI에서는 아이콘 컴포넌트(예: lucide-react) 사용

2) **중첩된 카드뷰는 사용하지 말 것 (CRITICAL)**
   - Card 내부에 Card 중첩 금지
   - 섹션 분리는 divider/heading/spacing/background로 처리
   - 레이아웃 깊이는 최대 2단계까지만 허용

3) **심플한 디자인 유지 (CRITICAL)**
   - 웹 UI에 너무 많은 텍스트 설명 표시 금지
   - 긴 설명문, 상세 가이드는 최소화
   - 필요한 정보만 간결하게 표시
   - 상세 정보는 툴팁/모달로 숨김 처리
   - "Less is more" 원칙

4) **모바일 친화적인 레이아웃으로 적용할 것 (CRITICAL)**
   - Mobile-first 레이아웃 원칙
   - 작은 화면 가독성/터치 타깃 최우선
   - **모바일 좌우 padding은 최소한으로 설정** (예: px-2 또는 px-4)
   - 항상 UI 업데이트 시 모바일에서 어떻게 보일지 고려

   **사용자 요청 확인 (CRITICAL)**:
   - 사용자의 UI 요청이 웹에만 한정되어 너무 디테일하면 반드시 되물을 것
   - 질문 예시: "이렇게 업데이트하면 모바일에서 레이아웃이 깨질 수 있는데 괜찮나요?"
   - 모바일 호환성을 사용자에게 확인받고 진행

5) 시간/날짜는 항상 한국 시간(Asia/Seoul)을 기준으로 판단한다.

6) fallback 더미 값 주입으로 흐름을 숨기지 말 것
   - 디버깅을 어렵게 하므로 기본/더미 값으로 덮어쓰지 않는다.
   - 문제가 발생하면 에러 메시지를 명확히 노출한다.

7) 사용자 작업에는 성공/실패 메시지를 항상 노출할 것
   - 저장/추가/삭제/새로고침 등 주요 액션의 결과를 명확히 표시한다.

## Workflow
- 코드 수정 후 항상:
  1) 테스트 실행 → PASS/FAIL 확인
  2) FAIL이면 수정 후 재테스트
  3) PASS면 `git add` → `git commit` 수행
  4) `git push`는 사용자가 명시적으로 요청할 때만 수행

## Database & API Synchronization (CRITICAL)
**스키마와 API는 항상 함께 업데이트되어야 한다.**

- 데이터베이스 스키마가 변경되면 반드시 관련 API도 함께 업데이트해야 함
- CRUD 기능 개발/수정 시 스키마와 API를 항상 같이 취급할 것
- 스키마만 업데이트하고 API를 업데이트하지 않으면 불일치가 발생함

**예시**:
- 스키마에 새 필드 추가 → API response model에도 필드 추가
- 스키마에서 필드 제거 → API에서도 해당 필드 제거
- 스키마 필드 타입 변경 → API validation/serialization 로직도 변경

**체크리스트**:
1. 스키마 변경 시 영향받는 모든 API 엔드포인트 확인
2. Pydantic 모델 (request/response) 업데이트
3. API 문서 (Swagger) 자동 반영 확인
4. 테스트 코드 업데이트

## Backend Configuration (CRITICAL)

### Allowed Hosts & CORS
백엔드 개발 시 다음 설정을 필수로 적용해야 한다:

1. **Allowed Hosts**: 모든 호스트 허용 (`*`)
2. **CORS Origin**: CORS origin 에러가 발생하지 않도록 설정

**FastAPI 설정 예시**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 - 모든 origin 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
```

**주의사항**:
- 개발 환경에서는 편의를 위해 모든 origin 허용
- 프로덕션 환경에서는 보안을 위해 특정 origin만 허용하도록 변경 필요

## Git
4) git commit message는 알아서 만들 것
   - 변경 내용 기반으로 명확한 메시지를 자동 생성
   - 커밋 메시지는 한국어로 작성한다.
   - 가능하면 Conventional Commits 사용
- 단, 환경 제약으로 git이 실패하면 사용자에게 원인/대안 커맨드를 안내한다.

---

## Debugging & Logging

### 로그 파일
- **Backend**: `backend/debug.log` - 모든 백엔드 동작 로그
- **Frontend**: `frontend/debug.log` - 모든 프론트엔드 동작 로그

### 로깅 필수 사항
1) **상세한 로그 기록**
   - 모든 API 요청/응답
   - 데이터베이스 쿼리
   - 사용자 인터랙션
   - 에러 및 예외 (스택 트레이스 포함)
   - 성능 메트릭 (처리 시간)

2) **로그 포맷**
   ```
   [타임스탬프] [레벨] [위치] 메시지 [데이터]
   ```

3) **로그 레벨**
   - DEBUG: 상세 디버깅 정보
   - INFO: 일반 정보
   - WARNING: 경고
   - ERROR: 에러
   - CRITICAL: 치명적 오류

### Backend (Python)
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.FileHandler('debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 사용 예시
logger.info(f"API Request: GET /api/v1/addresses/{address}")
logger.error(f"Database error: {str(e)}", exc_info=True)
```

### Frontend (JavaScript)
```javascript
// 로그 유틸리티
const logger = {
  log: (level, message, data) => {
    const timestamp = new Date().toISOString();
    const logMsg = `[${timestamp}] [${level}] ${message}`;
    console.log(logMsg, data || '');

    // localStorage에 저장
    const logs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    logs.push({ timestamp, level, message, data });
    localStorage.setItem('debug_logs', JSON.stringify(logs.slice(-1000)));
  },
  debug: (msg, data) => logger.log('DEBUG', msg, data),
  info: (msg, data) => logger.log('INFO', msg, data),
  error: (msg, data) => logger.log('ERROR', msg, data)
};

// 사용 예시
logger.info('Fetching address data', { address });
logger.error('API request failed', { error: error.message });
```

### 로그 확인
```bash
# 실시간 로그 모니터링
tail -f backend/debug.log
tail -f frontend/debug.log

# 에러만 필터링
grep ERROR backend/debug.log
```

---

## 사용자에게 에러 표시 (필수)

### 원칙
**에러 발생 시 사용자에게 웹 UI에서 자세한 에러 메시지를 보여주어야 합니다.**

### Backend
```python
from fastapi import HTTPException

@app.get("/api/v1/addresses/{address}")
async def get_address(address: str):
    try:
        result = fetch_address(address)
        return result
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

        # 개발: 상세 에러 정보 반환
        raise HTTPException(
            status_code=500,
            detail={
                "message": "주소 조회 중 오류 발생",
                "error": str(e),
                "type": type(e).__name__
            }
        )
```

### Frontend
```javascript
// 에러를 사용자에게 표시
const handleError = (error) => {
  // Toast 알림
  toast.error(
    <div>
      <div className="font-bold">{error.message}</div>
      {import.meta.env.DEV && error.details && (
        <div className="text-sm mt-1">{error.details}</div>
      )}
    </div>
  );

  logger.error('Error occurred', error);
};

// API 호출 시
try {
  const response = await fetch('/api/v1/addresses/...');
  if (!response.ok) {
    const errorData = await response.json();
    handleError(errorData.error);
  }
} catch (error) {
  handleError({ message: '네트워크 오류', details: error.message });
}
```

### 에러 표시 컴포넌트
```javascript
export const ErrorAlert = ({ error }) => (
  <div className="bg-red-50 border-l-4 border-red-500 p-4">
    <div className="font-bold">{error.message}</div>
    {import.meta.env.DEV && error.details && (
      <div className="text-sm mt-2">{error.details}</div>
    )}
  </div>
);
```

### 가이드라인
1. **명확한 메시지**: 무엇이 잘못되었는지 명확히 표시
2. **해결 방법 제시**: 사용자가 어떻게 해야 하는지 안내
3. **개발 환경 상세 정보**: 개발 시 스택 트레이스, 에러 타입 표시
4. **프로덕션 간소화**: 프로덕션에서는 민감 정보 숨김

**중요**: 문제 해결을 위해 충분히 상세한 로그를 남기고, **사용자에게도 명확한 에러 메시지를 표시**하는 것이 필수입니다.
