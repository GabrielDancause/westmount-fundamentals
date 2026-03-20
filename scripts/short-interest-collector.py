#!/usr/bin/env python3
"""
Short Interest Data Collector for Westmount Fundamentals
=========================================================
Collects short interest data, calculates Squeeze Scores, and generates
JSON files for the short interest study page.

Data sources:
- yfinance: short interest, short % of float, days to cover, prices
- SEC EDGAR: Fails-to-Deliver data

Output:
- src/data/short-interest/current.json          — live table data
- src/data/short-interest/historical-outcomes.json — scatter plot data
- src/data/short-interest/sector-breakdown.json  — sector chart
- src/data/short-interest/snapshots/YYYY-MM-DD.json — monthly snapshots

Usage:
    python3 scripts/short-interest-collector.py [--backfill-months 12]
"""

import json
import os
import sys
import time
import zipfile
import io
import csv
from datetime import datetime, timedelta
from pathlib import Path

import yfinance as yf
import pandas as pd

# --- Config ---
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "src" / "data" / "short-interest"
SNAPSHOT_DIR = DATA_DIR / "snapshots"

# S&P 500 tickers — we'll fetch the list dynamically
SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# GICS Sector mapping (yfinance provides this per-ticker)
SQUEEZE_WEIGHTS = {
    "short_pct_float": 30,   # 0-30 pts
    "days_to_cover": 20,     # 0-20 pts
    "momentum": 20,          # 0-20 pts
    "ftd_ratio": 15,         # 0-15 pts
    "inst_ownership_chg": 15 # 0-15 pts
}

# Rate limiting
BATCH_SIZE = 20
BATCH_DELAY = 2  # seconds between batches


def get_sp500_tickers():
    """Fetch S&P 500 ticker list from Wikipedia."""
    try:
        tables = pd.read_html(SP500_URL)
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
        print(f"  Fetched {len(tickers)} S&P 500 tickers")
        return tickers
    except Exception as e:
        print(f"  WARNING: Could not fetch S&P 500 list: {e}")
        print(f"  Falling back to hardcoded top 100 most-shorted tickers")
        return get_fallback_tickers()


def get_fallback_tickers():
    """Fallback list of commonly shorted / high-profile tickers."""
    return [
        # Meme / heavily shorted
        "GME", "AMC", "BBBY", "CVNA", "UPST", "MARA", "RIOT", "COIN",
        "SOUN", "IONQ", "RKLB", "AFRM", "SOFI", "HOOD", "PLTR", "SNOW",
        # Large cap tech
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "NFLX",
        # Biotech (high short interest sector)
        "MRNA", "BNTX", "SGEN", "BIIB", "REGN", "VRTX", "ILMN", "CRSP",
        "RXRX", "IOVA", "BEAM", "NTLA",
        # Energy / EV
        "LCID", "RIVN", "NIO", "XPEV", "FCEL", "PLUG", "ENPH", "SEDG",
        # Retail / Consumer
        "DG", "DLTR", "BBWI", "GPS", "M", "KSS", "PARA", "WBD",
        # Real estate / Finance
        "MPW", "NYCB", "PBF", "SFM", "TRUP",
        # Other high short interest
        "ASTS", "APLD", "CLSK", "GNPX", "SMCI", "AI", "JOBY", "DNA",
        "OPEN", "SKLZ", "WISH", "CLOV", "SPCE", "BYND",
    ]


def fetch_short_interest_batch(tickers):
    """Fetch short interest data for a batch of tickers."""
    results = []
    total = len(tickers)

    for i in range(0, total, BATCH_SIZE):
        batch = tickers[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch {batch_num}/{total_batches}: {batch[0]}..{batch[-1]}")

        for ticker_symbol in batch:
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info

                if not info or 'shortPercentOfFloat' not in info:
                    continue

                short_pct = info.get('shortPercentOfFloat', 0)
                if short_pct is None or short_pct == 0:
                    continue

                # Get price history for momentum calc
                hist = ticker.history(period="3mo")
                if hist.empty or len(hist) < 20:
                    continue

                current_price = hist['Close'].iloc[-1]
                price_1mo_ago = hist['Close'].iloc[-min(21, len(hist))]
                price_3mo_ago = hist['Close'].iloc[0]

                momentum_1m = ((current_price - price_1mo_ago) / price_1mo_ago) * 100
                momentum_3m = ((current_price - price_3mo_ago) / price_3mo_ago) * 100

                record = {
                    "ticker": ticker_symbol,
                    "company": info.get('longName', info.get('shortName', ticker_symbol)),
                    "sector": info.get('sector', 'Unknown'),
                    "industry": info.get('industry', 'Unknown'),
                    "marketCap": info.get('marketCap', 0),
                    "currentPrice": round(current_price, 2),
                    "shortPercentOfFloat": round(short_pct * 100, 2) if short_pct < 1 else round(short_pct, 2),
                    "sharesShort": info.get('sharesShort', 0),
                    "sharesShortPriorMonth": info.get('sharesShortPriorMonth', 0),
                    "shortRatio": info.get('shortRatio', 0),  # days to cover
                    "sharesOutstanding": info.get('sharesOutstanding', 0),
                    "floatShares": info.get('floatShares', 0),
                    "institutionalOwnership": round((info.get('heldPercentInstitutions', 0) or 0) * 100, 2),
                    "momentum1m": round(momentum_1m, 2),
                    "momentum3m": round(momentum_3m, 2),
                    "beta": info.get('beta', None),
                    "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', 0),
                    "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', 0),
                    "dateCollected": datetime.now().strftime("%Y-%m-%d"),
                }

                # Normalize short % (yfinance sometimes returns as decimal, sometimes as %)
                if record["shortPercentOfFloat"] > 100:
                    record["shortPercentOfFloat"] = round(record["shortPercentOfFloat"] / 100, 2)

                results.append(record)

            except Exception as e:
                # Silently skip problematic tickers
                pass

        # Rate limiting between batches
        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    return results


def calculate_squeeze_scores(stocks):
    """Calculate proprietary Squeeze Score (0-100) for each stock."""
    if not stocks:
        return stocks

    # Get max values for normalization
    max_short_pct = max(s["shortPercentOfFloat"] for s in stocks) or 1
    max_days_cover = max(s["shortRatio"] for s in stocks) or 1

    for stock in stocks:
        score = 0

        # Short % of float (0-30 pts) — higher = more squeeze potential
        short_pct_norm = min(stock["shortPercentOfFloat"] / max(max_short_pct, 40), 1)
        score += short_pct_norm * SQUEEZE_WEIGHTS["short_pct_float"]

        # Days to cover (0-20 pts) — higher = harder for shorts to exit
        dtc_norm = min(stock["shortRatio"] / max(max_days_cover, 10), 1)
        score += dtc_norm * SQUEEZE_WEIGHTS["days_to_cover"]

        # Price momentum (0-20 pts) — rising price + high short = squeeze setup
        # Positive momentum = more squeeze potential
        mom_score = 0
        if stock["momentum1m"] > 0:
            mom_score += min(stock["momentum1m"] / 30, 1) * 10  # up to 10 pts for 1m
        if stock["momentum3m"] > 0:
            mom_score += min(stock["momentum3m"] / 50, 1) * 10  # up to 10 pts for 3m
        score += mom_score

        # Short interest change (0-15 pts) — rising short interest = more bearish bets
        if stock["sharesShort"] and stock["sharesShortPriorMonth"]:
            prior = stock["sharesShortPriorMonth"]
            if prior > 0:
                si_change = (stock["sharesShort"] - prior) / prior
                # Rising short interest = bears are piling in (contrarian bullish)
                if si_change > 0:
                    score += min(si_change / 0.3, 1) * SQUEEZE_WEIGHTS["ftd_ratio"]

        # Institutional ownership change proxy (0-15 pts)
        # High institutional ownership = smart money, potential support
        inst_own = stock.get("institutionalOwnership", 0)
        if inst_own > 50:
            score += min((inst_own - 50) / 40, 1) * SQUEEZE_WEIGHTS["inst_ownership_chg"]

        stock["squeezeScore"] = round(score, 1)

        # Rating label
        if score >= 70:
            stock["squeezeRating"] = "High"
        elif score >= 45:
            stock["squeezeRating"] = "Moderate"
        elif score >= 25:
            stock["squeezeRating"] = "Low"
        else:
            stock["squeezeRating"] = "Minimal"

    return stocks


def calculate_sector_breakdown(stocks):
    """Calculate average short interest by sector."""
    sector_data = {}
    for stock in stocks:
        sector = stock["sector"]
        if sector not in sector_data:
            sector_data[sector] = {"stocks": [], "short_pcts": [], "count": 0}
        sector_data[sector]["stocks"].append(stock["ticker"])
        sector_data[sector]["short_pcts"].append(stock["shortPercentOfFloat"])
        sector_data[sector]["count"] += 1

    breakdown = []
    for sector, data in sorted(sector_data.items()):
        avg_short = sum(data["short_pcts"]) / len(data["short_pcts"])
        max_short = max(data["short_pcts"])
        most_shorted = data["stocks"][data["short_pcts"].index(max_short)]
        breakdown.append({
            "sector": sector,
            "avgShortPercent": round(avg_short, 2),
            "maxShortPercent": round(max_short, 2),
            "mostShortedTicker": most_shorted,
            "stockCount": data["count"],
        })

    # Sort by avg short interest descending
    breakdown.sort(key=lambda x: x["avgShortPercent"], reverse=True)
    return breakdown


def build_historical_outcomes(snapshots_dir):
    """Build historical outcomes from saved snapshots.
    For each snapshot, look at what happened to heavily shorted stocks
    in the following 1/3/6/12 months."""
    outcomes = []
    snapshot_files = sorted(snapshots_dir.glob("*.json"))

    if not snapshot_files:
        print("  No historical snapshots found — will accumulate over time")
        return outcomes

    print(f"  Processing {len(snapshot_files)} historical snapshots...")

    for snap_file in snapshot_files:
        snap_date_str = snap_file.stem
        try:
            snap_date = datetime.strptime(snap_date_str, "%Y-%m-%d")
        except ValueError:
            continue

        with open(snap_file) as f:
            snap_data = json.load(f)

        # Only process heavily shorted stocks (>10% of float)
        heavily_shorted = [s for s in snap_data if s.get("shortPercentOfFloat", 0) > 10]

        for stock in heavily_shorted:
            ticker = stock["ticker"]

            # Get forward returns
            try:
                end_date = min(snap_date + timedelta(days=365), datetime.now())
                hist = yf.Ticker(ticker).history(
                    start=snap_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d")
                )
                if hist.empty or len(hist) < 20:
                    continue

                base_price = hist['Close'].iloc[0]

                def get_return(days):
                    idx = min(days, len(hist) - 1)
                    if idx < days * 0.8:  # not enough data
                        return None
                    return round(((hist['Close'].iloc[idx] - base_price) / base_price) * 100, 2)

                outcome = {
                    "ticker": ticker,
                    "snapshotDate": snap_date_str,
                    "shortPercentOfFloat": stock["shortPercentOfFloat"],
                    "sector": stock.get("sector", "Unknown"),
                    "return1m": get_return(21),
                    "return3m": get_return(63),
                    "return6m": get_return(126),
                    "return12m": get_return(252),
                }
                outcomes.append(outcome)

            except Exception:
                continue

    print(f"  Generated {len(outcomes)} historical outcome records")
    return outcomes


def fetch_sec_ftd_data():
    """Download latest SEC Fails-to-Deliver data."""
    import urllib.request

    now = datetime.now()
    # Try current month first half, then last month second half
    attempts = []
    for month_offset in range(0, 3):
        d = now - timedelta(days=30 * month_offset)
        year = d.strftime("%Y")
        month = d.strftime("%m")
        attempts.append(f"cnsfails{year}{month}b.zip")
        attempts.append(f"cnsfails{year}{month}a.zip")

    base_url = "https://www.sec.gov/files/data/fails-deliver-data/"

    for filename in attempts:
        url = base_url + filename
        try:
            print(f"  Trying SEC FTD: {filename}...")
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Research; westmountfundamentals.com)'
            })
            response = urllib.request.urlopen(req, timeout=30)
            data = response.read()

            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for name in zf.namelist():
                    if name.endswith('.txt') or name.endswith('.csv'):
                        with zf.open(name) as f:
                            content = f.read().decode('utf-8', errors='replace')
                            reader = csv.DictReader(content.splitlines(), delimiter='|')
                            ftd_records = []
                            for row in reader:
                                try:
                                    ftd_records.append({
                                        "date": row.get("SETTLEMENT DATE", ""),
                                        "ticker": row.get("SYMBOL", ""),
                                        "failQuantity": int(row.get("QUANTITY (FAILS)", 0)),
                                        "price": float(row.get("PRICE", 0)),
                                    })
                                except (ValueError, TypeError):
                                    continue

                            print(f"  Loaded {len(ftd_records)} FTD records from {filename}")
                            return ftd_records

        except Exception as e:
            continue

    print("  WARNING: Could not fetch SEC FTD data")
    return []


def aggregate_ftd_by_ticker(ftd_records, tickers_set):
    """Aggregate FTD data by ticker, only for tickers we care about."""
    agg = {}
    for record in ftd_records:
        ticker = record["ticker"]
        if ticker not in tickers_set:
            continue
        if ticker not in agg:
            agg[ticker] = {"totalFails": 0, "days": 0, "maxFails": 0}
        agg[ticker]["totalFails"] += record["failQuantity"]
        agg[ticker]["days"] += 1
        agg[ticker]["maxFails"] = max(agg[ticker]["maxFails"], record["failQuantity"])

    return agg


def generate_study_stats(stocks, outcomes):
    """Generate summary statistics for the study."""
    stats = {
        "totalStocksAnalyzed": len(stocks),
        "heavilyShortedCount": len([s for s in stocks if s["shortPercentOfFloat"] > 10]),
        "avgShortPercent": round(sum(s["shortPercentOfFloat"] for s in stocks) / max(len(stocks), 1), 2),
        "maxShortPercent": round(max((s["shortPercentOfFloat"] for s in stocks), default=0), 2),
        "mostShortedTicker": max(stocks, key=lambda s: s["shortPercentOfFloat"])["ticker"] if stocks else None,
        "highSqueezeCount": len([s for s in stocks if s.get("squeezeScore", 0) >= 70]),
        "dateGenerated": datetime.now().strftime("%Y-%m-%d"),
        "dataSource": "Yahoo Finance, SEC EDGAR",
    }

    # Historical outcome stats (if we have them)
    if outcomes:
        returns_6m = [o["return6m"] for o in outcomes if o.get("return6m") is not None]
        if returns_6m:
            stats["avgReturn6m"] = round(sum(returns_6m) / len(returns_6m), 2)
            stats["medianReturn6m"] = round(sorted(returns_6m)[len(returns_6m) // 2], 2)
            stats["positiveReturn6mPct"] = round(len([r for r in returns_6m if r > 0]) / len(returns_6m) * 100, 1)
            stats["squeezePct50Plus"] = round(len([r for r in returns_6m if r > 50]) / len(returns_6m) * 100, 1)
            stats["historicalObservations"] = len(returns_6m)

    return stats


def main():
    """Main collection pipeline."""
    print("=" * 60)
    print("Short Interest Data Collector — Westmount Fundamentals")
    print("=" * 60)
    print()

    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Get ticker universe
    print("[1/6] Fetching S&P 500 tickers...")
    tickers = get_sp500_tickers()

    # Step 2: Fetch short interest data
    print(f"\n[2/6] Fetching short interest data for {len(tickers)} tickers...")
    stocks = fetch_short_interest_batch(tickers)
    print(f"  Got data for {len(stocks)} stocks with short interest > 0")

    if not stocks:
        print("ERROR: No data collected. Check network connection.")
        sys.exit(1)

    # Step 3: Fetch SEC FTD data and enrich
    print("\n[3/6] Fetching SEC Fails-to-Deliver data...")
    ftd_records = fetch_sec_ftd_data()
    if ftd_records:
        tickers_set = {s["ticker"] for s in stocks}
        ftd_agg = aggregate_ftd_by_ticker(ftd_records, tickers_set)
        for stock in stocks:
            ftd = ftd_agg.get(stock["ticker"], {})
            stock["ftdTotalFails"] = ftd.get("totalFails", 0)
            stock["ftdDays"] = ftd.get("days", 0)
            stock["ftdMaxFails"] = ftd.get("maxFails", 0)

    # Step 4: Calculate Squeeze Scores
    print("\n[4/6] Calculating Squeeze Scores...")
    stocks = calculate_squeeze_scores(stocks)

    # Sort by short % descending
    stocks.sort(key=lambda s: s["shortPercentOfFloat"], reverse=True)

    # Top 10 preview
    print("\n  Top 10 Most Shorted:")
    for i, s in enumerate(stocks[:10], 1):
        print(f"  {i:2}. {s['ticker']:6} {s['shortPercentOfFloat']:6.2f}% short | "
              f"DTC: {s['shortRatio']:4.1f} | Squeeze: {s['squeezeScore']:5.1f} ({s['squeezeRating']})")

    # Step 5: Build sector breakdown
    print("\n[5/6] Building sector breakdown...")
    sector_breakdown = calculate_sector_breakdown(stocks)

    # Step 6: Historical outcomes (from past snapshots)
    print("\n[6/6] Building historical outcomes...")
    outcomes = build_historical_outcomes(SNAPSHOT_DIR)

    # Generate summary stats
    stats = generate_study_stats(stocks, outcomes)

    # --- Write output files ---
    print("\nWriting output files...")

    # Current data (for the live table)
    current_output = {
        "meta": stats,
        "stocks": stocks,
    }
    with open(DATA_DIR / "current.json", "w") as f:
        json.dump(current_output, f, indent=2)
    print(f"  ✓ current.json ({len(stocks)} stocks)")

    # Sector breakdown
    with open(DATA_DIR / "sector-breakdown.json", "w") as f:
        json.dump(sector_breakdown, f, indent=2)
    print(f"  ✓ sector-breakdown.json ({len(sector_breakdown)} sectors)")

    # Historical outcomes
    with open(DATA_DIR / "historical-outcomes.json", "w") as f:
        json.dump(outcomes, f, indent=2)
    print(f"  ✓ historical-outcomes.json ({len(outcomes)} records)")

    # Save today's snapshot (for future historical analysis)
    today = datetime.now().strftime("%Y-%m-%d")
    with open(SNAPSHOT_DIR / f"{today}.json", "w") as f:
        json.dump(stocks, f, indent=2)
    print(f"  ✓ snapshots/{today}.json (monthly snapshot saved)")

    # Summary
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)
    print(f"  Stocks analyzed: {stats['totalStocksAnalyzed']}")
    print(f"  Heavily shorted (>10%): {stats['heavilyShortedCount']}")
    print(f"  Highest short: {stats['mostShortedTicker']} ({stats['maxShortPercent']}%)")
    print(f"  High squeeze potential: {stats['highSqueezeCount']}")
    print(f"  Data dir: {DATA_DIR}")
    print()


if __name__ == "__main__":
    main()
