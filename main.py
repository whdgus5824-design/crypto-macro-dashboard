"""
경제/크립토 자동화 메인 스크립트 - GitHub Actions 호환 버전
Binance 제거 (GitHub 서버 IP 차단됨)
FACT 수집 + ANALYSIS 분석을 한 번에 실행합니다 (완전 무료).

실행:
  python main.py

결과:
  data/2026-08-24.json (FACT)
  data/2026-08-24_analysis.md (ANALYSIS)
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# 수집 모듈
import requests

# 분석 모듈 - Google Gemini
import google.generativeai as genai

# Notion API
from notion_client import Client

load_dotenv()

FRED_API_KEY = os.environ.get("FRED_API_KEY")
GEMINI_API_KEY = os.environ.get("GOOGLE_GENERATIVEAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
ANALYSIS_MODEL = "gemini-3.5-flash-lite"

# Notion 클라이언트
notion_client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# ============================= 공통 유틸 =============================

def _get(url, params=None, timeout=10):
    """공통 GET 요청"""
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[WARN] 요청 실패: {url} -> {e}")
        return None


def _fred_latest(series_id):
    """FRED 최신값"""
    if not FRED_API_KEY:
        print("[WARN] FRED_API_KEY가 설정되지 않았습니다")
        return None
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    data = _get(FRED_BASE, params=params)
    if not data or "observations" not in data or not data["observations"]:
        return None
    obs = data["observations"][0]
    return {"date": obs["date"], "value": obs["value"]}


def _get_alpha_vantage_quote(symbol):
    """Alpha Vantage Global Quote API로 최신 가격 조회"""
    if not ALPHA_VANTAGE_API_KEY:
        return None
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    data = _get(ALPHA_VANTAGE_BASE, params=params)
    if not data or "Global Quote" not in data:
        return None
    quote = data["Global Quote"]
    if not quote or "05. price" not in quote:
        return None
    return {
        "price": float(quote.get("05. price", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
        "timestamp": quote.get("07. latest trading day", "N/A"),
    }


# ============================= FACT 수집 =============================

def collect_macro():
    macro_data = {
        "fed_funds_rate": _fred_latest("FEDFUNDS"),
        "treasury_2y": _fred_latest("DGS2"),
        "treasury_10y": _fred_latest("DGS10"),
        "fred_dollar_index": _fred_latest("DTWEXBGS"),
        "cpi": _fred_latest("CPIAUCSL"),
        "pce": _fred_latest("PCEPI"),
        "wti": _fred_latest("DCOILWTICO"),
        "gdp": _fred_latest("GDP"),
        "unemployment": _fred_latest("UNRATE"),
        "nonfarm_payroll": _fred_latest("PAYEMS"),
    }
    
    dxy_quote = _get_alpha_vantage_quote("DXY")
    if dxy_quote:
        macro_data["ice_dxy"] = dxy_quote
    else:
        macro_data["ice_dxy"] = None
    
    return macro_data


def collect_liquidity():
    stablecoin_supply = _get("https://stablecoins.llama.fi/stablecoins", params={"includePrices": "true"})
    total_stablecoin_mcap = None
    if stablecoin_supply and "peggedAssets" in stablecoin_supply:
        try:
            total_stablecoin_mcap = sum(
                a["circulating"].get("peggedUSD", 0)
                for a in stablecoin_supply["peggedAssets"]
                if "circulating" in a
            )
        except Exception as e:
            print(f"[WARN] 스테이블코인 합산 실패: {e}")

    return {
        "m2_us": _fred_latest("M2SL"),
        "fed_balance_sheet": _fred_latest("WALCL"),
        "tga": _fred_latest("WTREGEN"),
        "rrp": _fred_latest("RRPONTSYD"),
        "stablecoin_total_supply_usd": total_stablecoin_mcap,
        "global_m2": None,
    }


def collect_crypto(coins=("bitcoin", "ethereum")):
    ids = ",".join(coins)
    price_data = _get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true", "include_24hr_vol": "true"},
    )
    global_data = _get("https://api.coingecko.com/api/v3/global")

    result = {"prices": price_data or {}}
    if global_data and "data" in global_data:
        g = global_data["data"]
        result["btc_dominance_pct"] = g.get("market_cap_percentage", {}).get("btc")
        result["eth_dominance_pct"] = g.get("market_cap_percentage", {}).get("eth")
        result["total_market_cap_usd"] = g.get("total_market_cap", {}).get("usd")
        result["total_volume_usd"] = g.get("total_volume", {}).get("usd")
    return result


def collect_onchain():
    tvl = _get("https://api.llama.fi/v2/historicalChainTvl")
    latest_tvl = tvl[-1] if tvl else None

    dex_volume = _get("https://api.llama.fi/overview/dexs", params={"excludeTotalDataChart": "true"})
    fees = _get("https://api.llama.fi/overview/fees", params={"excludeTotalDataChart": "true"})

    return {
        "defi_tvl_usd": latest_tvl.get("tvl") if latest_tvl else None,
        "dex_volume_24h_usd": dex_volume.get("total24h") if dex_volume else None,
        "fees_24h_usd": fees.get("total24h") if fees else None,
    }


def collect_all():
    print("📊 FACT 데이터 수집 중...")
    result = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "macro": collect_macro(),
        "liquidity": collect_liquidity(),
        "crypto": collect_crypto(),
        "onchain": collect_onchain(),
        "note": "Binance Futures 데이터는 GitHub Actions 호환성을 위해 제외됨"
    }
    print("✅ FACT 수집 완료")
    return result


def save_fact(result, out_dir="data"):
    os.makedirs(out_dir, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join(out_dir, f"{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"💾 FACT 저장: {path}")
    return path


# ============================= ANALYSIS 분석 =============================

SYSTEM_PROMPT = """당신은 거시경제/크립토 데이터를 해석하는 분석가입니다.
반드시 아래 원칙을 지키세요.

1. 입력으로 주어진 JSON 안의 숫자만 근거로 삼습니다. JSON에 없는 사실, 뉴스, 사건을 지어내지 마세요.
2. 값이 null이거나 없는 항목은 "데이터 없음"이라고 명시하고, 억지로 해석하지 마세요.
3. 반드시 [FACT] -> [ANALYSIS] 구조로 작성하세요.
   - [FACT]: 입력 JSON의 숫자를 그대로 요약 (단위, 날짜 포함)
   - [ANALYSIS]: 그 숫자가 시장에 어떤 의미인지 1~2문장, 과장 없이
4. 카테고리는 다음 4개 순서로: 거시경제 / 유동성 / 크립토 / 온체인
5. 각 카테고리는 3~5줄 이내로 짧게. 전체 응답은 A4 반 페이지를 넘기지 않습니다.
6. 확정적 예측("반드시 오른다")이나 투자 조언(매수/매도 지시)은 하지 않습니다. 해석만 제공합니다.
"""


def build_user_prompt(data: dict) -> str:
    return (
        "아래는 오늘 자동 수집된 FACT 데이터입니다. 이 데이터만 근거로 "
        "[FACT]->[ANALYSIS] 형식의 일일 리포트를 작성해주세요.\n\n"
        f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```"
    )


def analyze(data: dict) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY가 .env에 없습니다. "
            "GOOGLE_GENERATIVEAI_API_KEY 또는 GEMINI_API_KEY 를 .env에 추가하세요."
        )

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        ANALYSIS_MODEL,
        system_instruction=SYSTEM_PROMPT
    )
    response = model.generate_content(build_user_prompt(data))
    return response.text


def save_analysis(text: str, fact_json_path: str):
    out_path = fact_json_path.replace(".json", "_analysis.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"💾 ANALYSIS 저장: {out_path}")
    return out_path


# ============================= Notion 저장 =============================

def save_to_notion(fact_data: dict):
    """수집한 FACT 데이터를 Notion에 저장"""
    if not notion_client or not NOTION_DATABASE_ID:
        print("[WARN] Notion API 설정 없음. Notion 저장 건너뜀.")
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    rows_to_save = []

    # ① 거시경제
    macro = fact_data.get("macro", {})
    if macro.get("fed_funds_rate"):
        rows_to_save.append({
            "이름": "Fed 기금금리",
            "카테고리": "거시경제",
            "지표명": "FEDFUNDS",
            "현재값": float(macro["fed_funds_rate"]["value"]),
            "분석": f"기준금리 {macro['fed_funds_rate']['value']}%",
            "출처": "FRED"
        })
    
    if macro.get("treasury_10y"):
        rows_to_save.append({
            "이름": "미국 10년물 국채",
            "카테고리": "거시경제",
            "지표명": "DGS10",
            "현재값": float(macro["treasury_10y"]["value"]),
            "분석": f"10년물 {macro['treasury_10y']['value']}%",
            "출처": "FRED"
        })

    # ② 크립토
    crypto = fact_data.get("crypto", {})
    prices = crypto.get("prices", {})
    
    if prices.get("bitcoin"):
        btc = prices["bitcoin"]
        rows_to_save.append({
            "이름": "BTC",
            "카테고리": "크립토",
            "지표명": "BTC/USD",
            "현재값": btc.get("usd", 0),
            "변화율": btc.get("usd_24h_change", 0),
            "분석": f"BTC ${btc['usd']}",
            "출처": "CoinGecko"
        })

    # ③ 온체인
    onchain = fact_data.get("onchain", {})
    if onchain.get("defi_tvl_usd"):
        rows_to_save.append({
            "이름": "DeFi TVL",
            "카테고리": "온체인",
            "지표명": "DeFi TVL",
            "현재값": onchain["defi_tvl_usd"] / 1e9,
            "분석": f"DeFi TVL: ${onchain['defi_tvl_usd']/1e9:.2f}B",
            "출처": "DefiLlama"
        })

    # Notion에 저장
    print(f"📝 Notion에 {len(rows_to_save)}개 행 저장 중...")
    success_count = 0
    for row in rows_to_save:
        try:
            notion_client.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties={
                    "날짜": {"date": {"start": today}},
                    "이름": {"title": [{"text": {"content": row["이름"]}}]},
                    "카테고리": {"select": {"name": row["카테고리"]}},
                    "지표명": {"rich_text": [{"text": {"content": row["지표명"]}}]},
                    "현재값": {"number": row.get("현재값")},
                    "변화율": {"number": row.get("변화율")},
                    "분석": {"rich_text": [{"text": {"content": row["분석"]}}]},
                    "출처": {"rich_text": [{"text": {"content": row["출처"]}}]},
                }
            )
            success_count += 1
        except Exception as e:
            print(f"[WARN] Notion 저장 실패 ({row['이름']}): {e}")
    
    print(f"✅ Notion 저장 완료: {success_count}/{len(rows_to_save)}")


# ============================= 메인 실행 =============================

if __name__ == "__main__":
    print("=" * 60)
    print("📈 경제/크립토 자동화 대시보드 - 일일 리포트")
    print("(GitHub Actions 호환 버전 - Binance 제외)")
    print("=" * 60)

    try:
        # FACT 수집
        fact_data = collect_all()

        # FACT 저장
        fact_path = save_fact(fact_data)

        # ANALYSIS 생성
        print("\n🤖 ANALYSIS 생성 중...")
        analysis_text = analyze(fact_data)

        # ANALYSIS 저장
        analysis_path = save_analysis(analysis_text, fact_path)

        # Notion에 저장
        print("\n📌 Notion에 자동 저장 중...")
        save_to_notion(fact_data)

        # 최종 결과 출력
        print("\n" + "=" * 60)
        print("📋 오늘의 분석")
        print("=" * 60)
        print(analysis_text)
        print("\n" + "=" * 60)
        print(f"✨ 완료!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n[ERROR] 실행 실패: {e}")
        sys.exit(1)
