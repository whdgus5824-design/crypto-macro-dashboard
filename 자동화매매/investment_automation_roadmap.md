# 투자 자동화 시스템 통합 로드맵
**배종현 · 2026년 9월 목표**

---

## 📋 핵심 전략 (문서 분석 요약)

### 1. 설계 원칙: "AI가 주문하지 않는다"
```
❌ 나쁜 구조
AI 판단 → 자동 매수

✅ 좋은 구조
데이터 → 조건 필터 → 점수 평가 → 전략 판단 → 위험관리 → 주문 실행
```

### 2. 통합 시스템 구조
```
        [ 경제/거시 데이터 ]
               │
               ▼
         [ MARKET REGIME ]
         경제 상황 판단
         Risk ON / OFF
               │
    ┌──────────┴──────────┐
    ▼                     ▼
[주식 엔진]          [크립토 엔진]
    │                     │
 증권사 API            Upbit API
    │                     ▼
종목 스캐너          코인 스캐너
    │                     │
 종목 점수화          코인 점수화
    │                     │
    └──────────┬──────────┘
               ▼
        [ 투자 점수 엔진 ]
               │
    ┌──────────┴──────────┐
    ▼                     ▼
 매매신호              관망 대기
    │
    ▼
[ Risk Manager ]
    │
    ▼
[ 주문 실행 ]
```

### 3. 4가지 메인 프로젝트
| 프로젝트 | 목표 | 산출물 |
|---------|------|--------|
| **A. Market Data Engine** | 모든 데이터 수집/통합 | SQLite/PostgreSQL DB |
| **B. Investment Scanner** | 조건 필터링 + 점수화 | 일일 종목 추천 리스트 |
| **C. Trading Engine** | 매매신호 + 위험관리 | 자동주문 모듈 |
| **D. AI Assistant** | 시장 해석 + 리포팅 | 일일 투자 리포트 |

**개발 순서: A → B → C → D**

---

## 🎯 현재 상황 분석

### 이미 완성된 부분
- ✅ 경제 대시보드 기본 구조
- ✅ Binance Futures API 연결 경험
- ✅ 크립토 5개 페르소나 정의
- ✅ Notion 마스터 보드 레이아웃

### 새로 구축할 부분
- 🔴 증권사 API 연결 (KIS / 키움)
- 🔴 업비트 API 체계적 연결
- 🔴 통합 데이터베이스 구조
- 🔴 종목/코인 점수 엔진
- 🔴 백테스트 시스템
- 🔴 주문 실행 및 위험관리

---

## 📅 9주 개발 로드맵 (9월 목표)

### Phase 1: 기초 설계 (주 1~2)

#### Week 1: 설계 문서 작성
**주요 작업**
- [ ] 투자 원칙 코드화 (배종현님의 규칙 5~7개)
  - 예: "Risk OFF이면 공격적 매수 금지"
  - 예: "OI 급증 + Funding 과열이면 추격매수 금지"
- [ ] 종목 필터 조건 정의
  - 주식: 거래대금, 시가총액, 기술적 지표 조합
  - 크립토: BTC 추세, 유동성, OI, Funding 등
- [ ] 점수표 시스템 설계
  ```
  총 100점 배분
  - 시장 환경: 20점
  - 추세: 20점
  - 거래량: 15점
  - 모멘텀: 15점
  - 기술지표: 10점
  - 수급: 10점
  - 변동성: 5점
  - 리스크: 5점
  ```
- [ ] 데이터베이스 스키마 설계
- [ ] API 목록 및 호출 순서 정의

**산출물**
- `📄 Investment_Rules.md` (투자 원칙 코드 스펙)
- `📄 Filter_Conditions.md` (필터 상세 정의)
- `📄 Scoring_System.md` (점수 배분표)
- `📄 Database_Schema.sql` (DB 설계)

#### Week 2: 기술 스택 및 환경 설정
**주요 작업**
- [ ] 증권사 선택 (KIS vs 키움) → KIS 추천
  - KIS 선택 사유: REST + WebSocket, 충분한 API, 개발자 커뮤니티
- [ ] API 키 발급
  - 한국투자증권 KIS API 신청
  - 업비트 API 신청
- [ ] Python 프로젝트 구조 생성
  ```
  investment-system/
  ├── config/
  │   ├── settings.py
  │   └── secrets.env
  ├── data/
  │   ├── stocks/
  │   ├── crypto/
  │   └── macro/
  ├── brokers/
  │   ├── kis_broker.py
  │   └── upbit_broker.py
  ├── indicators/
  ├── scanners/
  ├── strategies/
  ├── risk/
  ├── backtest/
  ├── execution/
  └── main.py
  ```
- [ ] 가상환경 + 라이브러리 설치
  ```
  pandas, numpy, ta-lib(또는 pandas-ta)
  requests, websocket-client
  sqlite3 / sqlalchemy
  ```
- [ ] GitHub 저장소 + .env 설정

**산출물**
- Python 프로젝트 구조
- requirements.txt
- config 템플릿

---

### Phase 2: 데이터 엔진 구축 (주 3~4)

#### Week 3: API 연결 - 증권사
**주요 작업**
- [ ] KIS API 학습 및 테스트
  ```python
  kis.get_price("005930")           # 삼성전자 현재가
  kis.get_ohlcv("005930")           # OHLCV 데이터
  kis.get_orderbook("005930")       # 호가
  kis.get_balance()                 # 잔고
  kis.get_daily_rank()              # 일일 상승/하락 순위
  ```
- [ ] KIS Broker 래퍼 클래스 작성
  ```python
  class KISBroker:
      def get_price(self, ticker)
      def get_ohlcv(self, ticker, period)
      def get_balance(self)
      def get_top_movers(self, n=20)
  ```
- [ ] 에러 처리 및 재시도 로직
- [ ] 로깅 시스템 구축

**산출물**
- `kis_broker.py` (KIS API 래퍼)
- `kis_test.py` (테스트 코드)

#### Week 4: API 연결 - 업비트 + 데이터베이스
**주요 작업**
- [ ] 업비트 API 학습 및 테스트
  - Quotation API (시세, OHLCV, 호가)
  - Exchange API (주문, 잔고)
  - WebSocket (실시간 데이터)
- [ ] Upbit Broker 래퍼 클래스 작성
- [ ] SQLite 데이터베이스 설계 및 생성
  ```sql
  -- 주식 데이터
  CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    date DATE,
    open REAL, high REAL, low REAL, close REAL,
    volume INTEGER,
    created_at TIMESTAMP
  );

  -- 암호화폐 데이터
  CREATE TABLE crypto_prices (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    date DATE,
    open REAL, high REAL, low REAL, close REAL,
    volume REAL,
    created_at TIMESTAMP
  );

  -- 거시경제 데이터
  CREATE TABLE macro_data (
    id INTEGER PRIMARY KEY,
    indicator TEXT,
    date DATE,
    value REAL,
    created_at TIMESTAMP
  );

  -- 거래 기록
  CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    asset_type TEXT,
    ticker TEXT,
    signal_type TEXT,
    score REAL,
    order_price REAL,
    created_at TIMESTAMP
  );
  ```
- [ ] Data Manager 클래스 (데이터 저장/조회)

**산출물**
- `upbit_broker.py` (업비트 API 래퍼)
- `data_manager.py` (DB 관리)
- `database.db` 초기화

---

### Phase 3: 스캐너 + 점수 엔진 (주 5~6)

#### Week 5: 종목 스캐너 (주식 + 크립토)
**주요 작업**
- [ ] 기술적 지표 라이브러리 구축
  ```python
  indicators/
  ├── trend.py (EMA, SMA, 추세)
  ├── momentum.py (RSI, MACD, Stochastic)
  ├── volume.py (거래량 지표)
  └── volatility.py (BB, ATR, 변동성)
  ```
- [ ] 주식 스캐너 1단계: 기초 필터
  - 거래대금 상위 (예: 상위 200종목)
  - 시가총액 조건
  - 거래량 증가율
  ```python
  class StockScanner:
      def filter_by_volume_increase(self, pct=1.5)
      def filter_by_price_action(self, pct=2)
      def filter_by_market_cap(self, min_cap=1000)
      def run_first_filter(self) -> DataFrame
  ```
- [ ] 주식 스캐너 2단계: 기술적 조건
  - EMA20 > EMA50
  - RSI 40~70
  - MACD 골든크로스
  - 거래량 증가
- [ ] 주식 스캐너 3단계: 최종 점수
- [ ] 크립토 스캐너 (유사 구조)

**산출물**
- `indicators/` 폴더 (지표 함수들)
- `scanners/stock_scanner.py`
- `scanners/crypto_scanner.py`
- 일일 스캐너 결과 CSV

#### Week 6: 점수 엔진 + 배경종현 규칙 적용
**주요 작업**
- [ ] 점수 엔진 구현 (100점 기준)
  ```python
  class ScoringEngine:
      def score_market_regime(self, data) -> int    # 20점
      def score_trend(self, data) -> int            # 20점
      def score_volume(self, data) -> int           # 15점
      def score_momentum(self, data) -> int         # 15점
      def score_technicals(self, data) -> int       # 10점
      def score_supply_demand(self, data) -> int    # 10점
      def score_volatility(self, data) -> int       # 5점
      def score_risk(self, data) -> int             # 5점
      def calculate_total_score(self, data) -> dict
  ```
- [ ] 배종현님의 투자 원칙 코드화
  ```python
  class InvestmentRules:
      def check_macro_risk_off(self) -> bool
      def check_btc_downtrend(self) -> bool
      def check_oi_funding_overheated(self) -> bool
      def check_rsi_overbought(self) -> bool
      def check_position_concentration(self) -> bool
      def apply_all_rules(self, ticker, score) -> (score, reason)
  ```
- [ ] 등급 시스템 구현
  - A+: 90~100
  - A: 80~89
  - B: 70~79
  - C: 60~69
  - 관망: <60

**산출물**
- `strategies/scoring_engine.py`
- `strategies/investment_rules.py`
- 일일 추천 리스트 (CSV + JSON)

---

### Phase 4: 백테스트 + 자동화 (주 7~8)

#### Week 7: 백테스트 시스템
**주요 작업**
- [ ] 백테스트 엔진 구축
  ```python
  class BacktestEngine:
      def load_historical_data(self, ticker, start, end)
      def apply_strategy(self, data, rules)
      def simulate_trades(self)
      def calculate_metrics(self)
  ```
- [ ] 매매 신호 전략 정의
  - 매수 조건: 점수 80점 이상 + 모든 규칙 통과
  - 매도 조건: RSI > 70 또는 추세 반전
- [ ] 2021~2026년 히스토리 데이터로 테스트
- [ ] 성과 지표 분석
  - 승률, 평균수익, 최대손실, MDD, Profit Factor, Sharpe Ratio
  - **주의**: 수익률만 보지 말고 MDD도 중시

**산출물**
- `backtest/backtest_engine.py`
- `backtest/results.csv` (성과 리포트)

#### Week 8: 모의매매 시스템
**주요 작업**
- [ ] 실시간 시뮬레이터 구축
  - 실시간 데이터 수신
  - 매매 신호 생성
  - 가상 주문 처리
  - 가상 포트폴리오 추적
- [ ] 모의 거래 일지 기록
- [ ] 주 단위 성과 모니터링

**산출물**
- `execution/paper_trading.py`
- 모의매매 일일 리포트

---

### Phase 5: 최종 통합 + Notion 자동화 (주 9)

#### Week 9: 통합 + Notion 연동
**주요 작업**
- [ ] 메인 파이프라인 구축
  ```python
  # main.py
  def daily_investment_workflow():
      1. 경제 데이터 업데이트 (기존 대시보드)
      2. 주식 + 크립토 API 데이터 수집
      3. 기술적 지표 계산
      4. 스캐너 실행
      5. 점수 계산 + 규칙 적용
      6. 추천 종목 생성
      7. Notion 업데이트
      8. AI 리포트 생성
  ```
- [ ] Notion Integration 구현
  - 일일 추천 종목 자동 업로드
  - 시장 판단 자동 업데이트
  - 리포트 생성
- [ ] 스케줄러 설정 (Cron / APScheduler)
  - 평일 오전 8시 실행
  - 실시간 가격 업데이트 (시장 개장 중)
- [ ] 대시보드 UI 정리
  - Streamlit 또는 간단한 HTML
  - 종목 추천 순위표
  - 시장 판단 게이지

**산출물**
- `main.py` (전체 파이프라인)
- `integrations/notion_updater.py`
- `scheduler/daily_jobs.py`
- 최종 Notion 대시보드

---

## 🛠️ 기술 스택

### Backend
- **언어**: Python 3.10+
- **API 클라이언트**: requests, websocket-client
- **데이터 처리**: pandas, numpy
- **기술적 지표**: ta-lib (또는 pandas-ta)
- **데이터베이스**: SQLite (초기) → PostgreSQL (성장)

### 자동화 & 모니터링
- **스케줄링**: APScheduler (Python 내장)
- **Notion API**: notion-client
- **로깅**: Python logging

### 초기 대시보드 (Optional)
- **Streamlit**: 빠른 프로토타이핑
- 나중에 Next.js로 업그레이드 가능

### AI (Phase 4)
- Claude API를 통한 시장 분석 요약
- 일일 리포트 자동 생성

---

## 📊 주요 산출물 (목표)

### 코드
```
investment-system/
├── 📄 README.md
├── 📄 requirements.txt
├── 🔧 config/
├── 🔧 brokers/ (KIS + Upbit)
├── 🔧 indicators/ (기술적 지표)
├── 🔧 scanners/ (종목 필터)
├── 🔧 strategies/ (점수 + 규칙)
├── 🔧 backtest/ (역사 검증)
├── 🔧 execution/ (실행)
├── 🔧 integrations/ (Notion)
└── 📄 main.py
```

### 데이터
- `database.db` (SQLite 또는 PostgreSQL)
- `daily_stocks.csv` (일일 추천 주식)
- `daily_crypto.csv` (일일 추천 코인)
- `backtest_results.csv` (백테스트 성과)

### Notion
- 📊 MASTER 대시보드 (경제 + 추천)
- 📈 STOCK 섹션 (주식 추천 일지)
- ₿ CRYPTO 섹션 (코인 추천 일지)
- 🤖 TRADING 섹션 (신호 + 성과)

---

## ⚠️ 중요한 설계 원칙

### 1️⃣ "AI가 직접 주문하지 않는다"
```
신호 발생
    ↓
위험관리 체크 (Risk Manager)
    ↓
"조건 충족?"
    ↓
주문 실행
```

### 2️⃣ 배종현님의 규칙 우선
- 거시경제 Risk OFF → 공격적 매수 금지
- BTC 하락 → 알트 비중 축소
- OI + Funding 과열 → 추격매수 금지
- RSI 과열 → 신규진입 금지
- 손절 기준 필수
- 1종목 과도한 비중 금지

### 3️⃣ 점진적 자동화
- **Phase 1-2**: 수동으로 데이터 검증
- **Phase 3**: 종목 추천 스캐너 (1차 목표)
- **Phase 4**: 백테스트 검증
- **Phase 5**: 모의매매
- **향후**: 소액 자동매매 (단계적 확대)

### 4️⃣ 보안
- API 키는 환경변수에 저장
- GitHub에 `.env` 커밋 금지
- 로컬 테스트 → 클라우드 배포 순서

---

## 🎯 성공 지표

| 주차 | 목표 | 검증 방법 |
|------|------|---------|
| 1-2 | 설계 완료 | 문서 + DB 스키마 |
| 3-4 | API 연결 | 실시간 데이터 조회 테스트 |
| 5-6 | 스캐너 + 점수 | 일일 추천 리스트 생성 |
| 7 | 백테스트 | 과거 3년 데이터 검증 |
| 8 | 모의매매 | 1주일 이상 가상 거래 |
| 9 | Notion 통합 | 자동 일일 업데이트 |

---

## 📌 다음 스텝

### 즉시 할 일 (이번 주)
1. [ ] 증권사 선택 확정 (KIS 추천)
2. [ ] KIS + 업비트 API 키 신청
3. [ ] 투자 원칙 5-7개 명문화
4. [ ] Python 프로젝트 폴더 생성
5. [ ] GitHub 저장소 초기화

### Week 1 완료 기준
- 모든 설계 문서 완성
- 데이터베이스 스키마 최종 확정
- 필터 조건 및 점수표 확정
- Python 개발 환경 준비 완료

---

**작성일**: 2026년 8월 26일  
**목표 완료일**: 2026년 9월 30일  
**1차 목표**: 일일 자동 종목 추천 시스템  
**최종 목표**: 투자 자동화 통합 플랫폼
