# 투자 자동화 시스템 - 즉시 실행 액션 플랜
**Week 1 (8월 26-30일) 프리-런칭**

---

## 🚀 우선순위 TOP 5 (3일 내 완료)

### 1️⃣ 투자 원칙 명문화 (2시간)

**배경**: 이 프로젝트의 핵심  
**방법**: 기존 Notion의 투자 원칙 섹션을 코드 형태로 재작성  

**작업**
```
현재 Notion에서:
"📋 경제·투자 MASTER" 
  └─ "투자 원칙" 섹션 검토

변환 형태:
Rule 1: 거시경제 판단
  조건: macro_regime == "RISK_OFF"
  처리: aggressive_buy = False
  적용 위치: 점수 엔진 (시장 환경 점수)
  
Rule 2: BTC 추세 판단  
  조건: btc_trend == "DOWNTREND"
  처리: altcoin_weight = 50% (기본값 70%)
  적용 위치: 크립토 스캐너
  
... (총 7개까지)
```

**산출물**
- `📄 INVESTMENT_RULES_v1.md`
  ```markdown
  # 배종현 투자 원칙
  
  ## Rule 1: 거시경제 Risk OFF
  - 조건: DXY > X, 금리 > Y, M2 < Z
  - 처리: 공격적 매수 금지 (점수 -20점)
  - 우선순위: ⭐⭐⭐
  
  ## Rule 2: BTC 하락 추세
  ...
  ```

**체크리스트**
- [ ] 기존 Notion 투자 원칙 섹션 읽기
- [ ] 7가지 규칙 먼저 식별
- [ ] 각 규칙의 "조건", "처리", "위치" 정의
- [ ] INVESTMENT_RULES_v1.md 작성
- [ ] 이 문서를 GitHub에 commit

---

### 2️⃣ 증권사 선택 및 API 신청 (30분 신청 + 1-3일 대기)

**배경**: API 데이터 가져오기가 전체 파이프라인의 시작  
**권장**: **한국투자증권 (KIS)** 선택

**왜 KIS인가?**
| 항목 | KIS | 키움 |
|------|-----|------|
| REST API | ✅ | ⚠️ 신규 |
| WebSocket | ✅ | ❌ |
| 개발 문서 | ✅ 상세 | ⚠️ 부족 |
| 시장 데이터 | ✅ 충분 | ✅ |
| 커뮤니티 | ✅ | ⚠️ |
| 초기 추천도 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**작업**
```
Step 1: KIS Developers 가입
  → https://www.ls-sec.co.kr/kor/main/main.do
  → "개발자 센터" 찾기
  → API 신청

Step 2: API 신청 정보 준비
  회사명: 개인
  용도: 개인 투자 시스템
  이메일: (보유 이메일)
  전화번호: (휴대폰)
  
Step 3: 신청서 제출
  → API 키 발급 대기 (1-3일)

Step 4: 발급받은 정보 보관
  KIS_API_KEY: xxxxx
  KIS_API_SECRET: xxxxx
  → .env 파일에 저장 (나중에)

Step 5: (신청되면) 데모 계좌로 로그인 테스트
```

**산출물**
- KIS API Key & Secret
- 데모 계좌 접근 확인

**병렬 작업**
- 업비트 API도 미리 신청
  → https://upbit.com/developers
  → "API 키 관리" 에서 신청
  → 즉시 발급됨 (KIS보다 빠름)

**체크리스트**
- [ ] KIS Developers 가입
- [ ] API 신청
- [ ] 업비트 API도 신청
- [ ] 발급받은 키를 노트에 임시 저장 (나중에 .env로)

---

### 3️⃣ Python 개발 환경 설정 (1시간)

**배경**: 코딩을 시작하기 위한 기본 환경  
**OS별 명령어**

#### macOS / Linux
```bash
# 1. Python 버전 확인 (3.10 이상 필요)
python3 --version
# Python 3.10.0 이상이어야 함

# 2. 프로젝트 폴더 생성
mkdir -p ~/Projects/investment-system
cd ~/Projects/investment-system

# 3. 가상환경 생성
python3 -m venv venv

# 4. 가상환경 활성화
source venv/bin/activate
# (프롬프트가 (venv) 로 시작되면 성공)

# 5. pip 업그레이드
pip install --upgrade pip

# 6. 라이브러리 설치 (나중에 전체 requirements.txt 사용)
# 지금은 기본만
pip install pandas numpy requests
```

#### Windows (PowerShell)
```powershell
# 1. Python 버전 확인
python --version

# 2. 프로젝트 폴더 생성
mkdir "C:\Users\YourName\Projects\investment-system"
cd "C:\Users\YourName\Projects\investment-system"

# 3. 가상환경 생성
python -m venv venv

# 4. 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 5. pip 업그레이드
python -m pip install --upgrade pip

# 6. 라이브러리 설치
pip install pandas numpy requests
```

**체크리스트**
- [ ] Python 3.10+ 설치 확인
- [ ] 프로젝트 폴더 생성
- [ ] 가상환경 생성 및 활성화
- [ ] pip 업그레이드
- [ ] 기본 라이브러리 설치
- [ ] `python3 -c "import pandas; print(pandas.__version__)"` 실행 후 버전 나오면 성공

---

### 4️⃣ GitHub 저장소 초기화 (30분)

**배경**: 코드 관리 + 안전한 저장소  

**작업**

#### GitHub에서
```
1. https://github.com/new 접속
2. Repository name: "investment-system"
3. Description: "Crypto + Stock Investment Automation System"
4. Public (또는 Private)
5. "Initialize this repository" 체크 해제
6. Create repository
```

#### 로컬에서
```bash
# 프로젝트 폴더에서 (가상환경 활성화 상태)
git init
git config user.name "배종현"
git config user.email "your.email@example.com"

# GitHub의 저장소 URL 연결
git remote add origin https://github.com/YOUR_USERNAME/investment-system.git

# .gitignore 생성
echo "
.env
.venv
venv/
__pycache__/
*.pyc
*.db
*.log
.DS_Store
.idea/
.vscode/
node_modules/
" > .gitignore

# README.md 생성
echo "
# Investment System

Crypto + Stock Investment Automation

## Quick Start

\`\`\`bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\Activate on Windows
pip install -r requirements.txt
\`\`\`
" > README.md

# 첫 커밋
git add .
git commit -m "Initial project setup"
git branch -M main
git push -u origin main
```

**체크리스트**
- [ ] GitHub 저장소 생성
- [ ] 로컬 git 초기화
- [ ] .gitignore 생성
- [ ] README.md 생성
- [ ] 첫 커밋
- [ ] GitHub에서 코드 확인

---

### 5️⃣ 프로젝트 폴더 구조 생성 (30분)

**배경**: 나중에 파일이 많아졌을 때 정리가 쉽도록  

#### 명령어 (한번에)
```bash
# (가상환경 활성화 상태에서)

# 모든 폴더 생성
mkdir -p config data brokers indicators scanners strategies backtest execution integrations scheduler tests logs

# 각 폴더에 __init__.py 생성
touch config/__init__.py
touch data/__init__.py
touch brokers/__init__.py
touch indicators/__init__.py
touch scanners/__init__.py
touch strategies/__init__.py
touch backtest/__init__.py
touch execution/__init__.py
touch integrations/__init__.py
touch scheduler/__init__.py
touch tests/__init__.py

# .env 템플릿 생성 (API 키 안전 보관용)
echo "
# KIS (한국투자증권)
KIS_API_KEY=
KIS_API_SECRET=

# Upbit
UPBIT_API_KEY=
UPBIT_API_SECRET=

# Notion (나중에)
NOTION_TOKEN=

# 기타 설정
DEBUG=True
" > .env

# 최상위 Python 파일들
touch main.py
touch config/settings.py
touch config/constants.py

echo "✅ 프로젝트 구조 생성 완료"
ls -la  # 폴더 목록 확인
```

**최종 구조**
```
investment-system/
├── .env                    # API 키 (절대 커밋 금지)
├── .gitignore
├── README.md
├── main.py                 # 진입점
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── constants.py
│
├── data/
│   └── __init__.py
│
├── brokers/
│   └── __init__.py
│
├── indicators/
│   └── __init__.py
│
├── scanners/
│   └── __init__.py
│
├── strategies/
│   └── __init__.py
│
├── backtest/
│   └── __init__.py
│
├── execution/
│   └── __init__.py
│
├── integrations/
│   └── __init__.py
│
├── scheduler/
│   └── __init__.py
│
├── tests/
│   └── __init__.py
│
└── logs/
    └── .gitkeep
```

**체크리스트**
- [ ] 모든 폴더 생성
- [ ] 각 __init__.py 생성
- [ ] .env 생성
- [ ] main.py, config 파일 생성
- [ ] `git add .` → `git commit -m "Add project structure"`

---

## 📅 이 주 타임라인

```
월요일 (26일)   👈 오늘
├─ ✅ 로드맵 문서 읽기 (이 문서)
├─ ✅ 투자 원칙 명문화 시작
└─ ✅ KIS API 신청 시작

화요일 (27일)
├─ 투자 원칙 명문화 완료
├─ API 신청 (업비트까지)
├─ Python 환경 설정 완료
└─ GitHub 저장소 생성

수요일 (28일)
├─ 폴더 구조 생성
├─ 설계 문서 정리
└─ README 작성

목요일 (29일)
├─ 설계 문서 재검토
├─ API 키 발급 확인 (KIS)
└─ 환경 테스트

금요일 (30일)
├─ 전체 검토
├─ 설계 문서 최종화
└─ Week 2 준비
```

---

## 📝 Week 1 완료 체크리스트

### 코드 파일
- [ ] GitHub 저장소 생성
- [ ] .gitignore 작성
- [ ] README.md 작성
- [ ] 프로젝트 폴더 구조 완성
- [ ] config/settings.py 생성
- [ ] .env 템플릿 생성

### 설계 문서
- [ ] INVESTMENT_RULES_v1.md (투자 원칙)
- [ ] DATABASE_SCHEMA.md (DB 설계) ← 제공됨
- [ ] FILTER_CONDITIONS.md (필터) ← 제공됨
- [ ] SCORING_SYSTEM.md (점수) ← 제공됨
- [ ] API_LIST.md (API 정리) ← 제공됨

### API 준비
- [ ] KIS Developers 가입
- [ ] KIS API 신청 (발급 대기)
- [ ] Upbit API 신청 (즉시 발급)
- [ ] API 키/Secret 임시 저장

### 환경 구성
- [ ] Python 3.10+ 설치
- [ ] 가상환경 생성 + 활성화
- [ ] 기본 라이브러리 설치 (pandas, numpy, requests)
- [ ] Git 초기화 + 첫 커밋

---

## 🎯 Week 1 성공 기준

**필수 (반드시)**
- ✅ 투자 원칙 7개 명문화
- ✅ API 신청 (KIS + Upbit)
- ✅ Python 환경 구성
- ✅ GitHub 저장소 초기화
- ✅ 폴더 구조 생성

**권장 (하면 좋음)**
- ✅ 설계 문서 3개 이상 정독
- ✅ 필터/점수 시스템 초안 검토
- ✅ KIS API 문서 훑어보기

---

## 🤔 자주 물어보는 질문

### Q1: Python 버전은?
**A:** Python 3.10 이상. 3.11 또는 3.12 권장.  
확인: `python3 --version`

### Q2: Mac vs Windows 차이는?
**A:** 명령어만 다름. 프로젝트 로직은 동일.  
Mac: `source venv/bin/activate`  
Windows: `.\venv\Scripts\Activate.ps1`

### Q3: API 키가 언제 발급되나?
**A:** Upbit은 신청 즉시, KIS는 1-3일 대기.  
KIS 대기 중에도 설계 진행 가능.

### Q4: GitHub에 .env 올리면 안 되나?
**A:** **절대 금지!**  
.gitignore에 `.env` 추가 필수.  
GitHub에서 노출되면 API 키 즉시 초기화.

### Q5: 가상환경이 뭔가?
**A:** Python 프로젝트별 독립적인 라이브러리 환경.  
한 프로젝트에서 pandas 2.0 쓰고, 다른 프로젝트에서 1.0 쓸 수 있게 해줌.

### Q6: Week 1에 뭘 배포하나?
**A:** 아무것도 안 함. 설계만.  
배포는 Week 9에 (Notion 자동화).

---

## 📞 도움이 필요하면

**문제 유형별 해결**
```
Git 관련 문제
→ GitHub 공식 튜토리얼 참고

Python 환경 문제
→ python.org 공식 가이드

API 문제
→ KIS/Upbit 공식 문서 먼저

설계 질문
→ INVESTMENT_RULES_v1.md 재검토
```

---

## ✅ 최종 체크

**이 주 말에 이 상태면 성공**

```
폴더 구조
investment-system/
├── .env (생성됨)
├── .gitignore (생성됨)
├── README.md (생성됨)
├── main.py (생성됨)
└── [모든 폴더 생성됨]

GitHub
[코드가 올라있음]

문서
├── INVESTMENT_RULES_v1.md ✅
├── 제공된 설계 문서 3개 ✅
└── README.md에 링크 ✅

API
- KIS: 신청됨 (발급 대기 중)
- Upbit: 발급됨 (키 보관 중)

이 모든 것이 완료되면 Week 2에
API 연결 코딩 시작 가능!
```

---

**작성일**: 2026년 8월 26일  
**완료 기한**: 2026년 8월 30일 (금요일)  
**다음 문서**: `investment_automation_roadmap.md` (PHASE 2로 이동)

**Good luck! 🚀**
