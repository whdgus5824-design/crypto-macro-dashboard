"""
경제/크립토 일일 데이터 수집기
- FRED, CoinGecko, Binance, DefiLlama에서 FACT 데이터를 수집한다.
- 이 스크립트는 판단/분석을 하지 않는다. 순수하게 숫자만 가져온다.
  (분석(ANALYSIS)은 다음 단계에서 별도 로직/AI로 처리)

실행 전 준비:
  pip install -r requirements.txt
  .env 파일에 FRED_API_KEY=본인키 를 넣어둘 것

실행:
  python collector.py
"""

import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.environ.get("FRED_API_KEY")
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# ----------------------------------------------------------------------
# 공통 유틸
# ----------------------------------------------------------------------

def _get(url, params=None, timeout=10):
    """공통 GET 요청 래퍼. 실패해도 전체 스크립트가 죽지 않게 예외를 잡아서 None 반환."""
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[WARN] 요청 실패: {url} -> {e}")
        return None


def _fred_latest(series_id):
    """FRED 시계열의 가장 최근 관측값 1개를 가져온다."""
    if not FRED_API_KEY:
        print("[WARN] FRED_API_KEY가 설정되지 않았습니다 (.env 확인)")
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


# ----------------------------------------------------------------------
# ① 거시경제
# ----------------------------------------------------------------------

def collect_macro():
    return {
        "fed_funds_rate": _fred_latest("FEDFUNDS"),   # Fed 기준금리
        "treasury_2y": _fred_latest("DGS2"),          # 미국 2Y
        "treasury_10y": _fred_latest("DGS10"),        # 미국 10Y
        "dxy": _fred_latest("DTWEXBGS"),               # 달러인덱스(광의)
        "cpi": _fred_latest("CPIAUCSL"),               # CPI
        "pce": _fred_latest("PCEPI"),                  # PCE
        "wti": _fred_latest("DCOILWTICO"),             # WTI 유가
        "gdp": _fred_latest("GDP"),                    # GDP
        "unemployment": _fred_latest("UNRATE"),        # 실업률
        "nonfarm_payroll": _fred_latest("PAYEMS"),     # 비농업고용
    }


# ----------------------------------------------------------------------
# ② 유동성
# ----------------------------------------------------------------------

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
        "m2_us": _fred_latest("M2SL"),                 # 미국 M2
        "fed_balance_sheet": _fred_latest("WALCL"),    # Fed 대차대조표
        "tga": _fred_latest("WTREGEN"),                # 재무부 TGA
        "rrp": _fred_latest("RRPONTSYD"),              # 역레포
        "stablecoin_total_supply_usd": total_stablecoin_mcap,
        "global_m2": None,  # 공식 API 없음 - 수동 취합 필요 (별도 논의)
    }


# ----------------------------------------------------------------------
# ③ 크립토 (시세/시가총액)
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# ④ 선물시장 (Binance 공개 API - 키 불필요)
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# ⑤ 온체인 (DefiLlama - 키 불필요)
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# 전체 실행
# ----------------------------------------------------------------------

def collect_all():
    print("수집 시작...")
    result = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "macro": collect_macro(),
        "liquidity": collect_liquidity(),
        "crypto": collect_crypto(),
        "futures_btc": collect_futures("BTCUSDT"),
        "futures_eth": collect_futures("ETHUSDT"),
        "onchain": collect_onchain(),
    }
    print("수집 완료.")
    return result


def save_result(result, out_dir="data"):
    os.makedirs(out_dir, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join(out_dir, f"{date_str}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {path}")
    return path


if __name__ == "__main__":
    data = collect_all()
    save_result(data)
    print(json.dumps(data, ensure_ascii=False, indent=2))
