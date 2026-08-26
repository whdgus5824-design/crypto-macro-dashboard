# 📈 경제/크립토 자동화 대시보드

거시경제 지표, 유동성, 크립토 시세, 선물시장, 온체인 데이터를 매일 자동으로 수집하고 AI 분석을 생성하는 자동화 시스템입니다.

## ✨ 특징

- **📊 자동 데이터 수집**: FRED, CoinGecko, Binance, DefiLlama 등 5개 카테고리 데이터 수집
- **🤖 AI 분석**: Google Gemini를 사용한 FACT/ANALYSIS 자동 생성 (완전 무료)
- **⏰ 매일 자동 실행**: GitHub Actions로 정해진 시간에 자동 실행
- **📁 결과 저장**: 매일 생성된 JSON(FACT)과 Markdown(ANALYSIS) 파일이 GitHub에 자동 저장

## 🚀 빠른 시작

### 로컬에서 수동 실행

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. .env 파일 생성 (API 키 입력)
cp .env.example .env
# .env 파일에서 다음 3개 API 키 입력:
# - FRED_API_KEY (무료, stlouisfed.org/docs/api)
# - GOOGLE_GENERATIVEAI_API_KEY (무료, aistudio.google.com)
# - ALPHA_VANTAGE_API_KEY (무료, alphavantage.co)

# 3. 실행
python main.py
```

### GitHub Actions 자동화 설정

1. **GitHub 저장소 생성**: https://github.com/new
2. **로컬에서 푸시**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/username/crypto-macro-dashboard.git
   git push -u origin main
   ```
3. **GitHub Secrets 등록**:
   - Settings → Secrets and variables → Actions
   - 3개의 API 키를 Secret으로 추가:
     - `FRED_API_KEY`
     - `GOOGLE_GENERATIVEAI_API_KEY`
     - `ALPHA_VANTAGE_API_KEY`

4. **자동화 시작**: 매일 한국시간 오전 8시에 자동 실행됨

## 📂 구조

```
crypto-macro-dashboard/
├── main.py                          # 메인 실행 스크립트 (수집 + 분석)
├── collector.py                     # 데이터 수집 전용 (참고용)
├── requirements.txt                 # Python 패키지 목록
├── .env.example                     # 환경변수 예시
├── .gitignore
├── README.md
├── .github/
│   └── workflows/
│       └── daily-report.yml         # GitHub Actions 워크플로우
└── data/                            # 매일 생성되는 결과 폴더
    ├── 2026-08-25.json              # FACT 데이터
    └── 2026-08-25_analysis.md       # ANALYSIS 분석
```

## 📊 수집하는 데이터

### ① 거시경제 (FRED)
- Fed 기준금리, 미국채 2Y/10Y, 달러인덱스
- CPI, PCE, WTI유, GDP, 실업률, 비농업고용

### ② 유동성 (FRED + DefiLlama)
- 미국 M2, Fed 대차대조표, TGA, 역레포
- 스테이블코인 총 공급량

### ③ 크립토 (CoinGecko)
- BTC/ETH 가격, 24H 변동률
- BTC Dominance, 전체 시가총액, 거래량

### ④ 선물시장 (Binance)
- OI (미결제약정), 펀딩비, 롱숏비율
- 거래량, 24H 변동률

### ⑤ 온체인 (DefiLlama)
- DeFi TVL, DEX 거래량, 수수료

## 📋 결과 형식

### data/2026-08-25.json (FACT)
```json
{
  "collected_at_utc": "2026-08-25T23:45:00+00:00",
  "macro": { ... },
  "crypto": { ... },
  "futures_btc": { ... },
  ...
}
```

### data/2026-08-25_analysis.md (ANALYSIS)
```markdown
# 📋 오늘의 분석

## 거시경제
[FACT] 2026년 7월 기준 Fed 기금금리 3.63% ...
[ANALYSIS] 낮은 금리 환경이 리스크자산에 우호적 신호 ...

## 크립토
[FACT] BTC 가격 $78,500, 24H +1.31% ...
[ANALYSIS] 거래량 증가로 강한 추세 확인 ...
```

## 🔑 API 키 발급

| API | 링크 | 비용 | 필수 |
|-----|------|------|------|
| FRED | https://fredaccount.stlouisfed.org/login | 무료 | ✅ |
| Gemini | https://aistudio.google.com | 무료 | ✅ |
| Alpha Vantage | https://www.alphavantage.co | 무료 (선택) | ⭕ |

## ⚙️ 커스터마이징

### 실행 시간 변경

`.github/workflows/daily-report.yml`의 cron 스케줄 수정:
```yaml
on:
  schedule:
    - cron: '0 22 * * *'  # 새로운 시간 (UTC 기준)
```

### 추가 암호화폐 수집

`main.py`의 `collect_crypto()` 함수에서:
```python
def collect_crypto(coins=("bitcoin", "ethereum", "solana")):  # 추가
```

## 📝 로그 확인

GitHub 저장소의 **Actions** 탭에서:
- 매일 실행 기록 확인
- 실패 시 에러 로그 조회
- 수동으로 workflow 실행 가능

## 📞 문제 해결

**Q: 분석이 안 나와요**
- A: Gemini API 키가 올바른지 확인하세요. GitHub Secrets에 정확히 입력됐는지 확인.

**Q: 데이터가 비어있어요**
- A: FRED API 키를 확인하세요. 또는 API 요청 제한에 도달했을 수 있습니다.

**Q: 매일 실행 안 돼요**
- A: GitHub Actions 탭에서 workflow 실행 상태 확인. `*.yml` 파일 문법 오류 가능성.

## 📌 다음 단계

- [ ] 노션 API 연동 (자동 리포트 저장)
- [ ] 슬랙/디스코드 알림
- [ ] 웹 대시보드 구축
- [ ] 역사 데이터 분석

## 📄 라이선스

MIT

---

**마지막 업데이트**: 2026-08-25  
**자동화 상태**: ✅ 활성화
