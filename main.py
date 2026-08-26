"""
경제/크립토 자동화 메인 스크립트 - Gemini API 버전
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

load_dotenv()

FRED_API_KEY = os.environ.get("FRED_API_KEY")
GEMINI_API_KEY = os.environ.get("GOOGLE_GENERATIVEAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
ANALYSIS_MODEL = "gemini-3.5-flash-lite"  # 최신 무료 모델

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


# ============================= FACT 수집 =============================

def _get_alpha_vantage_quote(symbol):
    """Alpha Vantage Global Quote API로 최신 가격 조회"""
    if not ALPHA_VANTAGE_API_KEY:
        print("[WARN] ALPHA_VANTAGE_API_KEY가 설정되지 않았습니다")
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
    # Alpha Vantage 데이터 형식: {"05. price": "123.45", "09. change": "1.23", ...}
    return {
        "price": float(quote.get("05. price", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
        "timestamp": quote.get("07. latest trading day", "N/A"),
    }


def collect_macro():
    macro_data = {
        "fed_funds_rate": _fred_latest("FEDFUNDS"),
        "treasury_2y": _fred_latest("DGS2"),
        "treasury_10y": _fred_latest("DGS10"),
        "fred_dollar_index": _fred_latest("DTWEXBGS"),  # 연준 광의 달러지수
        "cpi": _fred_latest("CPIAUCSL"),
        "pce": _fred_latest("PCEPI"),
        "wti": _fred_latest("DCOILWTICO"),
        "gdp": _fred_latest("GDP"),
        "unemployment": _fred_latest("UNRATE"),
        "nonfarm_payroll": _fred_latest("PAYEMS"),
    }
    
    # Alpha Vantage에서 실제 ICE DXY 추가 수집
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


def collect_futures(symbol="BTCUSDT"):
    oi = _get("https://fapi.binance.com/fapi/v1/openInterest", params={"symbol": symbol})
    funding = _get(
        "https://fapi.binance.com/fapi/v1/fundingRate",
        params={"symbol": symbol, "limit": 1},
    )
    ls_ratio = _get(
        "https://fapi.binance.com/futures/data/globalLongShortAccountRatio",
        params={"symbol": symbol, "period": "1h", "limit": 1},
    )
    ticker_24h = _get("https://fapi.binance.com/fapi/v1/ticker/24hr", params={"symbol": symbol})

    return {
        "symbol": symbol,
        "open_interest": oi.get("openInterest") if oi else None,
        "funding_rate": funding[0].get("fundingRate") if funding else None,
        "long_short_ratio": ls_ratio[0] if ls_ratio else None,
        "volume_24h": ticker_24h.get("volume") if ticker_24h else None,
        "price_change_pct_24h": ticker_24h.get("priceChangePercent") if ticker_24h else None,
    }


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
        "futures_btc": collect_futures("BTCUSDT"),
        "futures_eth": collect_futures("ETHUSDT"),
        "onchain": collect_onchain(),
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


# ============================= ANALYSIS 분석 (Gemini) =============================

SYSTEM_PROMPT = """당신은 거시경제/크립토 데이터를 해석하는 분석가입니다.
반드시 아래 원칙을 지키세요.

1. 입력으로 주어진 JSON 안의 숫자만 근거로 삼습니다. JSON에 없는 사실, 뉴스, 사건을 지어내지 마세요.
2. 값이 null이거나 없는 항목은 "데이터 없음"이라고 명시하고, 억지로 해석하지 마세요.
3. 반드시 [FACT] -> [ANALYSIS] 구조로 작성하세요.
   - [FACT]: 입력 JSON의 숫자를 그대로 요약 (단위, 날짜 포함)
   - [ANALYSIS]: 그 숫자가 시장에 어떤 의미인지 1~2문장, 과장 없이
4. 카테고리는 다음 5개 순서로: 거시경제 / 유동성 / 크립토 / 선물시장 / 온체인
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


# ============================= 메인 실행 =============================

if __name__ == "__main__":
    print("=" * 60)
    print("📈 경제/크립토 자동화 대시보드 - 일일 리포트")
    print("(Google Gemini 무료 API 사용)")
    print("=" * 60)

    # FACT 수집
    fact_data = collect_all()

    # FACT 저장
    fact_path = save_fact(fact_data)

    # ANALYSIS 생성
    print("\n🤖 ANALYSIS 생성 중...")
    try:
        analysis_text = analyze(fact_data)
    except Exception as e:
        print(f"[ERROR] 분석 생성 실패: {e}")
        sys.exit(1)

    # ANALYSIS 저장 및 출력
    analysis_path = save_analysis(analysis_text, fact_path)

    # 최종 결과 콘솔에 출력
    print("\n" + "=" * 60)
    print("📋 오늘의 분석")
    print("=" * 60)
    print(analysis_text)
    print("\n" + "=" * 60)
    print(f"✨ 완료! FACT와 ANALYSIS가 data 폴더에 저장되었습니다.")
    print("=" * 60)
