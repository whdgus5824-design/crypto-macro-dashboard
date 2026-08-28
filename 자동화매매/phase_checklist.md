# 투자 자동화 프로젝트 - Phase별 체크리스트

---

## 📍 PHASE 1: 설계 (Week 1-2)

### Week 1: 투자 원칙 + 시스템 설계

#### 1.1 투자 원칙 명문화
```
배종현님의 투자 원칙 (필수)
├─ Rule 1: 거시경제 판단
├─ Rule 2: BTC 추세 판단  
├─ Rule 3: 거래량 조건
├─ Rule 4: OI/Funding 과열 체크
├─ Rule 5: RSI 과매수 체크
├─ Rule 6: 손절 기준
└─ Rule 7: 포지션 집중도 관리
```

**작업**
- [ ] 기존 Notion의 투자 원칙 섹션 검토
- [ ] 각 규칙을 Python 함수로 변환할 수 있는 형태로 명문화
- [ ] 예시: `if macro_regime == "RISK_OFF": aggressive_buy = False`
- [ ] 산출물: `📄 INVESTMENT_RULES.md`

#### 1.2 데이터 구조 설계
```python
# 필요한 데이터 타입별 항목 정의

Stock:
  ticker, name, price, volume, 
  EMA20, EMA50, RSI, MACD,
  volume_change, score, reason

Crypto:
  symbol, price, volume,
  EMA20, EMA50, RSI, MACD,
  OI, Funding, 거래량, score, reason

Macro:
  BTC_price, ETH_price,
  BTC_dominance, DXY, 금리, M2, 
  Risk_regime (ON/OFF)
```

**작업**
- [ ] Pandas DataFrame 구조 설계
- [ ] 각 데이터의 계산 방식 명시
- [ ] 산출물: `📄 DATA_SCHEMA.md`

#### 1.3 종목 필터 조건 정의

**주식 필터 3단계**
```
1단계 (기초)
  ├─ 거래대금: 상위 200종목
  ├─ 시가총액: 최소 1,000억
  ├─ 거래량 증가: 20일 평균 대비 150% 이상
  └─ 목표: 2,000 → 500종목

2단계 (기술적)
  ├─ EMA20 > EMA50
  ├─ RSI: 40 ~ 70
  ├─ MACD: 골든크로스
  └─ 목표: 500 → 50종목

3단계 (최종 점수)
  ├─ 조건 통과 + 점수 80점 이상
  └─ 목표: 50 → 10~15종목 추천
```

**크립토 필터 3단계**
```
시장 필터
  ├─ BTC 추세: 상승/중립/하락
  ├─ BTC Dominance
  ├─ TOTAL/TOTAL2
  ├─ DXY, M2, 금리
  └─ 경제 Risk Regime

코인 필터
  ├─ 거래량 순위
  ├─ RSI, MACD, EMA
  ├─ OI 증가율
  ├─ Funding Rate
  └─ Liquidation 수준

최종 점수
  ├─ 80점 이상 추천
  └─ 배종현 규칙 통과
```

**작업**
- [ ] 각 필터 조건의 임계값 결정
- [ ] 과거 데이터로 필터 유효성 검증
- [ ] 산출물: `📄 FILTER_CONDITIONS.md`

#### 1.4 점수 시스템 설계
```
100점 만점 배분

시장 환경      20점
  ├─ Risk Regime (ON/OFF)
  ├─ 거시경제 상태
  └─ 유동성

추세           20점
  ├─ EMA / SMA
  ├─ 고점/저점 돌파
  └─ 추세선

거래량         15점
  ├─ 거래량 증가율
  ├─ 거래량 이동평균
  └─ 거래량 돌파

모멘텀         15점
  ├─ RSI
  ├─ MACD
  └─ Stochastic

기술지표       10점
  ├─ 볼린저밴드
  ├─ ATR
  └─ CCI

수급           10점
  ├─ OI (크립토)
  ├─ 미결제약정
  └─ Long/Short 비율

변동성          5점
  ├─ 표준편차
  ├─ ATR
  └─ 변동성 지수

리스크          5점
  ├─ Funding 수준
  ├─ Liquidation
  └─ 규칙 위반 체크

───────────────────
총점           100점
```

**등급 기준**
- A+ (90~100): 강력 추천
- A (80~89): 추천
- B (70~79): 중립
- C (60~69): 관망
- 관망 (<60): 신규진입 금지

**작업**
- [ ] 각 점수 계산 함수 설계
- [ ] 점수 가중치 검증
- [ ] 산출물: `📄 SCORING_SYSTEM.md`

#### 1.5 데이터베이스 설계
```sql
-- 주식 가격 데이터
stocks (
  id, ticker, date, 
  open, high, low, close, volume,
  EMA20, EMA50, RSI, MACD,
  score, reason, created_at
)

-- 크립토 가격 데이터
crypto (
  id, symbol, date,
  open, high, low, close, volume,
  EMA20, EMA50, RSI, MACD, OI, Funding,
  score, reason, created_at
)

-- 거시경제
macro (
  id, date,
  BTC, ETH, BTC_dominance, DXY,
  interest_rate, M2, liquidity,
  risk_regime, created_at
)

-- 추천 종목 기록
recommendations (
  id, date, asset_type, ticker, score,
  reason, confidence, created_at
)

-- 거래 기록 (향후 자동매매용)
trades (
  id, date, asset_type, ticker, signal,
  entry_price, quantity, exit_price,
  pnl, duration, created_at
)
```

**작업**
- [ ] SQL 스키마 작성
- [ ] SQLAlchemy ORM 모델 설계
- [ ] 산출물: `📄 DATABASE_SCHEMA.sql` + `models.py`

#### 1.6 API 목록 정리

**한국투자증권 (KIS) - 필수**
- [ ] GET /uapi/domestic-stock/v1/quotations/search-info (종목 검색)
- [ ] GET /uapi/domestic-stock/v1/quotations/inquire-daily-price (일가)
- [ ] GET /uapi/domestic-stock/v1/quotations/inquire-price (현재가)
- [ ] GET /uapi/domestic-stock/v1/quotations/inquire-daily-indexation-price (지수)
- [ ] GET /uapi/domestic-stock/v1/ranking/best-brokers (거래량 순위)
- [ ] GET /uapi/domestic-stock/v1/quotations/psearch-result (투자자별 매매)
- [ ] GET /uapi/account/v1/domestic-stock/inquire-balance (잔고)

**업비트 API - 필수**
- [ ] GET /v1/candles/days (일봉)
- [ ] GET /v1/candles/minutes (분봉)
- [ ] GET /v1/ticker (현재가)
- [ ] GET /v1/orderbook (호가)
- [ ] GET /v1/trades/ticks (체결)
- [ ] GET /v1/accounts (계좌)
- [ ] POST /v1/orders (주문)
- [ ] GET /v1/orders (주문 조회)

**경제 데이터 (기존)**
- [ ] Fred API (금리)
- [ ] Yahoo Finance (지수)
- [ ] CoinGecko / CoinMarketCap (크립토)

**작업**
- [ ] 각 API 호출 순서 정의
- [ ] Rate limit 계획
- [ ] 산출물: `📄 API_LIST.md`

---

### Week 2: 기술 환경 설정

#### 2.1 증권사 선택 확정
```
KIS vs 키움 비교

KIS (한국투자증권)
✅ REST API + WebSocket 모두 지원
✅ 충분한 API 량
✅ 개발자 문서 상세
✅ 데모 계좌 쉽게 개설
❌ 일부 고급 기능 제한

키움
✅ 높은 API 자유도
❌ REST API 상대적으로 새로움
❌ 개발자 커뮤니티 작음

→ 결론: KIS 선택 (안정성 + 시간 절약)
```

**작업**
- [ ] KIS Developers 회원가입
- [ ] API 신청 (대기 시간: 1-3일)
- [ ] 데모 계좌 개설
- [ ] 시세 조회 테스트
- [ ] 산출물: API Key & Secret

#### 2.2 Python 개발 환경
```
Python 3.10 이상
+ 가상환경 (venv)
+ pip (패키지 관리)
```

**작업**
- [ ] Python 3.10+ 설치
- [ ] GitHub 저장소 생성
  ```bash
  mkdir investment-system
  cd investment-system
  git init
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```

#### 2.3 라이브러리 설치
```
# requirements.txt 작성

# 데이터 처리
pandas==2.0.0
numpy==1.24.0

# API 클라이언트
requests==2.31.0
websocket-client==1.7.0
aiohttp==3.9.0

# 데이터베이스
sqlalchemy==2.0.0
sqlite3 (내장)

# 기술적 지표
ta-lib==0.4.28
# or pandas-ta==0.3.14b0 (ta-lib 대체)

# 백테스트
pandas==2.0.0  (이미 있음)
# vectorbt==0.25.0 (선택)

# 스케줄링
apscheduler==3.10.0

# Notion 연동
notion-client==2.2.0

# 유틸리티
python-dotenv==1.0.0
pydantic==2.0.0
loguru==0.7.0

# 선택사항
streamlit==1.30.0  (대시보드)
plotly==5.18.0     (시각화)
```

**작업**
```bash
pip install -r requirements.txt
```

#### 2.4 프로젝트 폴더 구조
```
investment-system/
├── .env                          # API 키 (Git 무시)
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                       # 메인 파이프라인
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # 환경설정
│   └── constants.py             # 상수 정의
│
├── data/
│   ├── __init__.py
│   ├── data_manager.py          # DB 관리
│   ├── models.py                # SQLAlchemy ORM
│   └── database.db              # SQLite (생성 후)
│
├── brokers/
│   ├── __init__.py
│   ├── kis_broker.py            # 한국투자증권
│   ├── upbit_broker.py          # 업비트
│   └── broker_base.py           # 기본 클래스
│
├── indicators/
│   ├── __init__.py
│   ├── trend.py                 # EMA, SMA 등
│   ├── momentum.py              # RSI, MACD 등
│   ├── volume.py                # 거래량 지표
│   └── volatility.py            # BB, ATR 등
│
├── scanners/
│   ├── __init__.py
│   ├── stock_scanner.py         # 주식 필터
│   └── crypto_scanner.py        # 크립토 필터
│
├── strategies/
│   ├── __init__.py
│   ├── scoring_engine.py        # 점수 계산
│   ├── investment_rules.py      # 배종현 규칙
│   └── strategy_base.py         # 기본 클래스
│
├── backtest/
│   ├── __init__.py
│   ├── backtest_engine.py       # 백테스트
│   └── results/                 # 결과 저장
│
├── execution/
│   ├── __init__.py
│   ├── risk_manager.py          # 위험관리
│   ├── order_executor.py        # 주문 실행
│   └── paper_trading.py         # 모의매매
│
├── integrations/
│   ├── __init__.py
│   ├── notion_updater.py        # Notion 동기화
│   └── news_fetcher.py          # 뉴스 수집
│
├── scheduler/
│   ├── __init__.py
│   └── daily_jobs.py            # 스케줄 관리
│
├── tests/
│   ├── __init__.py
│   ├── test_brokers.py
│   ├── test_indicators.py
│   └── test_scanners.py
│
└── logs/                         # 로그 저장 디렉토리
    └── .gitkeep
```

**작업**
```bash
# 폴더 생성
mkdir -p investment-system/{config,data,brokers,indicators,scanners,strategies,backtest,execution,integrations,scheduler,tests,logs}

# 각 폴더에 __init__.py 생성
touch investment-system/**/__init__.py

# .env 파일 생성
echo "
KIS_API_KEY=your_key_here
KIS_API_SECRET=your_secret_here
UPBIT_API_KEY=your_key_here
UPBIT_API_SECRET=your_secret_here
NOTION_TOKEN=your_token_here
" > investment-system/.env

# .gitignore
echo "
.env
.venv
venv/
__pycache__/
*.pyc
*.db
*.log
.DS_Store
" > investment-system/.gitignore
```

#### 2.5 GitHub 초기화
```bash
git add .
git commit -m "Initial project setup"
git push origin main
```

**작업**
- [ ] GitHub 저장소 생성
- [ ] README 작성 (프로젝트 설명)
- [ ] 초기 커밋

---

## 📊 PHASE 1 체크리스트 (완료 기준)

### Week 1 완료 기준
- [ ] 투자 원칙 7가지 명문화
- [ ] 데이터 구조 설계 완료
- [ ] 필터 조건 상세 정의
- [ ] 점수 시스템 완성
- [ ] 데이터베이스 스키마 확정
- [ ] API 목록 정리

**산출물 문서**
- [ ] INVESTMENT_RULES.md
- [ ] DATA_SCHEMA.md
- [ ] FILTER_CONDITIONS.md
- [ ] SCORING_SYSTEM.md
- [ ] DATABASE_SCHEMA.sql
- [ ] API_LIST.md

### Week 2 완료 기준
- [ ] KIS API 키 발급 (또는 신청)
- [ ] 업비트 API 키 발급
- [ ] Python 3.10+ 설치
- [ ] 가상환경 생성
- [ ] requirements.txt 준비
- [ ] 프로젝트 폴더 구조 생성
- [ ] GitHub 저장소 초기화
- [ ] .env 파일 설정

**산출물 코드**
- [ ] 프로젝트 폴더 구조
- [ ] requirements.txt
- [ ] .gitignore
- [ ] README.md

---

## 🚀 다음 Phase 미리보기

### PHASE 2 (Week 3-4): API 연결
```
├─ KIS Broker 클래스
├─ Upbit Broker 클래스
├─ 데이터베이스 연결
└─ 실시간 데이터 수집
```

### PHASE 3 (Week 5-6): 스캐너 + 점수
```
├─ 기술적 지표 계산
├─ 주식 스캐너
├─ 크립토 스캐너
└─ 점수 엔진
```

### PHASE 4 (Week 7-8): 검증
```
├─ 백테스트 시스템
└─ 모의매매
```

### PHASE 5 (Week 9): 통합
```
├─ Notion 자동화
├─ 스케줄러
└─ 최종 대시보드
```

---

**작성일**: 2026년 8월 26일  
**완료 목표**: 2026년 9월 9일 (Phase 1 완료)
