"""
data_collection.py — Collect and construct all asset time series.

Data sources:
  - S&P 500: Yahoo Finance (^GSPC, monthly close)
  - US Aggregate Bond Index: Yahoo Finance (AGG ETF, monthly close)
  - Hermès Birkin 35 Togo: Constructed from retail prices, Knight Frank KFLII
    handbag index data, auction records (Christie's, Sotheby's), and resale
    platform benchmarks (Rebag, Fashionphile, Bernstein Research).
  - Balenciaga City Classic: Constructed from retail price history and resale
    platform depreciation curves.
  - Chloé Paddington: Constructed from retail launch price (2005), resale
    platform current listings, and trend-driven demand cycles.
  - US CPI: Federal Reserve Bank of Minneapolis / FRED (1983=100 basis).

Methodology notes:
  Luxury handbag "prices" are mid-market resale estimates — the price a bag in
  very good condition would fetch on a major authenticated resale platform.
  These are NOT transaction-level data (which are proprietary). The time series
  are constructed using:
    1. Known retail prices at launch / annual Hermès price increases
    2. Knight Frank Luxury Investment Index (KFLII) handbag component returns
    3. Auction house realized prices for benchmark models
    4. Resale platform premium/discount to retail ratios (Bernstein Research)
    5. Expert commentary and market reports

  IMPORTANT — Volatility caveat:
    Handbag prices are interpolated between annual anchor points, which
    mechanically suppresses month-to-month variance. The reported volatility
    figures for handbags (especially the Birkin's 2.4%) are artifacts of
    smooth interpolation, NOT evidence of genuinely low price variance.
    Real transaction-level data — if it were available — would almost
    certainly show higher volatility. All Sharpe ratios and volatility
    comparisons should be interpreted with this caveat in mind.

  All assumptions are documented inline. This is a proxy dataset — see the
  report's Data Limitations section for a full discussion.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
import json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ═══════════════════════════════════════════════════════════════════════════════
# S&P 500 — Real market data via Yahoo Finance
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_sp500(start="2000-01-01", end="2025-12-31"):
    """Download S&P 500 index monthly close prices from Yahoo Finance."""
    spy = yf.download("^GSPC", start=start, end=end, interval="1mo", progress=False)
    if spy.empty:
        spy = yf.download("SPY", start=start, end=end, interval="1mo", progress=False)
    spy = spy[["Close"]].copy()
    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.get_level_values(0)
    spy.columns = ["sp500"]
    spy.index = spy.index.to_period("M").to_timestamp()
    spy = spy[~spy.index.duplicated(keep="first")]
    return spy


# ═══════════════════════════════════════════════════════════════════════════════
# US Aggregate Bond Index (AGG) — Real market data via Yahoo Finance
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_bonds(start="2003-01-01", end="2025-12-31"):
    """
    Download iShares Core US Aggregate Bond ETF (AGG) monthly close prices.
    AGG inception: Sep 2003. This is the standard benchmark for US investment-
    grade bonds (Treasuries + corporates + MBS).
    """
    agg = yf.download("AGG", start=start, end=end, interval="1mo", progress=False)
    if agg.empty:
        raise RuntimeError("Failed to download AGG bond data from Yahoo Finance")
    agg = agg[["Close"]].copy()
    if isinstance(agg.columns, pd.MultiIndex):
        agg.columns = agg.columns.get_level_values(0)
    agg.columns = ["bonds"]
    agg.index = agg.index.to_period("M").to_timestamp()
    agg = agg[~agg.index.duplicated(keep="first")]
    return agg


# ═══════════════════════════════════════════════════════════════════════════════
# US CPI — Inflation adjustment
# ═══════════════════════════════════════════════════════════════════════════════

def build_cpi_series():
    """
    Build annual CPI index (1983=100) from Fed Minneapolis data.
    Source: https://www.minneapolisfed.org/about-us/monetary-policy/
            inflation-calculator/consumer-price-index-1913-
    """
    cpi_data = {
        2000: 172.2, 2001: 177.1, 2002: 179.9, 2003: 184.0, 2004: 188.9,
        2005: 195.3, 2006: 201.6, 2007: 207.3, 2008: 215.3, 2009: 214.5,
        2010: 218.1, 2011: 224.9, 2012: 229.6, 2013: 233.0, 2014: 236.7,
        2015: 237.0, 2016: 240.0, 2017: 245.1, 2018: 251.1, 2019: 255.7,
        2020: 258.8, 2021: 271.0, 2022: 292.7, 2023: 304.7, 2024: 313.7,
        2025: 321.9,
    }
    cpi = pd.Series(cpi_data, name="cpi")
    cpi.index.name = "year"
    return cpi


# ═══════════════════════════════════════════════════════════════════════════════
# Hermès Birkin 35 Togo — Proxy time series
# ═══════════════════════════════════════════════════════════════════════════════

def build_birkin_series():
    """
    Construct annual mid-market resale price for Hermès Birkin 35 in Togo
    leather (black or neutral), very good condition.

    Key data points anchoring the curve:
      - 2000: Retail ~$5,500 (Hermès list), resale at ~1.0× retail = $5,500
      - 2005: Retail ~$6,500; secondary market emerging, resale ~$6,200
      - 2008: Pre-GFC peak in luxury spending; resale ~$7,800
      - 2009: GFC dip; resale ~$7,000
      - 2010-2012: Recovery; growing awareness of Birkin as investment
      - 2013: Retail ~$10,900; secondary premium growing (1.1-1.2×)
      - 2015: Retail $9,400 (Hermès sources); resale premium ~1.3× = $12,200
      - 2017: Christie's sells Himalaya Birkin for $386K (ultra-rare);
              standard B35 resale ~$14,500; retail ~$10,800
      - 2018-2019: Knight Frank KFLII handbag index: +13% (Q4'18-Q4'19);
              Hermès bags doubled over 10yr (108% per KFLII)
      - 2020: KFLII handbags +17% in 2020 (Knight Frank Wealth Report 2021)
      - 2021: Pandemic luxury boom; resale premium peaks at ~2.0× retail
      - 2022: Peak resale premium 2.2× retail (Bernstein Research);
              retail ~$10,800 → resale ~$23,800
      - 2023: Cooling begins; premium drops to ~1.8× (Bernstein).
              Market softness driven by post-pandemic normalization,
              Gen Z aspirational demand cooling, and increased supply
              of bags entering the secondary market.
      - 2024: KFLII handbags +2.8% but premium compressing to ~1.5×;
              retail ~$12,400 → resale ~$18,600. Bernstein Secondhand
              Pricing Tracker shows continued decline from 2022 peak.
      - 2025: Premium ~1.4× (Bernstein Dec 2025); retail $13,500 →
              resale ~$18,900. Jane Birkin's original bag sells for
              $10M at Sotheby's (record), but standard resale market
              is materially softer than 2021-2022 peak.

    Between anchor points, values are interpolated using the KFLII annual
    returns where available, with smoothing to avoid discontinuities.
    """
    birkin_resale = {
        2000: 5500,
        2001: 5600,
        2002: 5700,
        2003: 5900,
        2004: 6100,
        2005: 6200,
        2006: 6500,
        2007: 7200,
        2008: 7800,
        2009: 7000,   # GFC
        2010: 7600,
        2011: 8500,
        2012: 9800,
        2013: 11200,
        2014: 12000,
        2015: 12200,
        2016: 13000,
        2017: 14500,
        2018: 15800,
        2019: 17900,  # +13% KFLII
        2020: 20900,  # +17% KFLII
        2021: 23200,  # pandemic boom
        2022: 23800,  # peak (2.2× retail per Bernstein)
        2023: 21500,  # correction (1.8×)
        2024: 18600,  # KFLII +2.8% but premium compressing (1.5×)
        2025: 18900,  # 1.4× retail (Bernstein Dec 2025)
    }
    return pd.Series(birkin_resale, name="birkin")


# ═══════════════════════════════════════════════════════════════════════════════
# Balenciaga City Classic — Proxy time series
# ═══════════════════════════════════════════════════════════════════════════════

def build_balenciaga_series():
    """
    Construct annual mid-market resale price for Balenciaga Classic City
    (medium, lambskin), very good condition.

    Key data points:
      - 2003: Launched by Nicolas Ghesquière; retail ~$995
      - 2005: "It bag" status peaks; resale at or above retail ~$1,100
      - 2007: Pre-crisis luxury boom; resale ~$1,300
      - 2009: GFC dip + fashion cycle moving on; ~$900
      - 2012: Still relevant but no longer "hot"; retail rises to ~$1,545
              but resale drops below retail ~$1,200
      - 2015: Ghesquière departs (2012), Demna arrives (2015);
              City bag deprioritized; resale ~$800
      - 2018: Demna's Triple S era; City is "old Balenciaga"; resale ~$650
      - 2020: Vintage resurgence begins; slight uptick ~$600
      - 2022: Pandemic vintage boom lifts all bags; ~$750
      - 2023: Balenciaga brand crisis (Nov 2022 campaign); resale dips ~$600
      - 2024-2025: Nostalgia / Y2K revival driving renewed interest; ~$700-800

    The Balenciaga City is a case study in fashion-cycle depreciation:
    trendy bags spike then mean-revert, unlike Hermès which maintains scarcity.
    """
    balenciaga_resale = {
        2003: 995,
        2004: 1050,
        2005: 1100,
        2006: 1250,
        2007: 1300,
        2008: 1150,
        2009: 900,
        2010: 950,
        2011: 1050,
        2012: 1200,
        2013: 1150,
        2014: 1000,
        2015: 800,
        2016: 750,
        2017: 700,
        2018: 650,
        2019: 620,
        2020: 600,
        2021: 680,
        2022: 750,
        2023: 600,
        2024: 700,
        2025: 800,
    }
    return pd.Series(balenciaga_resale, name="balenciaga")


# ═══════════════════════════════════════════════════════════════════════════════
# Chloé Paddington — Proxy time series
# ═══════════════════════════════════════════════════════════════════════════════

def build_paddington_series():
    """
    Construct annual mid-market resale price for Chloé Paddington (medium,
    grained leather with signature padlock), very good condition.

    Key data points:
      - 2005: Launch year — retail $1,400; waitlists worldwide; resale at
              or above retail ~$1,500
      - 2006: Peak "It bag" status; resale ~$1,350
      - 2007: Fashion cycle moving to other bags; ~$1,100
      - 2008: GFC + declining relevance; ~$800
      - 2010: Firmly in "past trend" territory; ~$500
      - 2013: Deep secondary market discount; ~$350
      - 2015: Bottomed out; ~$250
      - 2018: Early vintage interest; ~$280
      - 2020: Y2K/2000s nostalgia wave begins; ~$350
      - 2022: Strong vintage revival (TikTok, archive fashion); ~$500
      - 2024: Chloé relaunches Paddington for resort 2025 at $2,750
              (adjusted for inflation ≈ $2,378 in 2005 dollars);
              vintage originals spike ~$800
      - 2025: Continued revival; vintage resale ~$1,100

    The Paddington illustrates the "smile curve" — high at launch, deep
    trough during irrelevance, then recovery driven by nostalgia and reissue.
    """
    paddington_resale = {
        2005: 1500,
        2006: 1350,
        2007: 1100,
        2008: 800,
        2009: 600,
        2010: 500,
        2011: 420,
        2012: 380,
        2013: 350,
        2014: 300,
        2015: 250,
        2016: 240,
        2017: 250,
        2018: 280,
        2019: 300,
        2020: 350,
        2021: 420,
        2022: 500,
        2023: 650,
        2024: 800,
        2025: 1100,
    }
    return pd.Series(paddington_resale, name="paddington")


# ═══════════════════════════════════════════════════════════════════════════════
# Assemble unified dataset
# ═══════════════════════════════════════════════════════════════════════════════

def build_annual_dataset():
    """
    Build a unified annual dataset with all assets and CPI.
    All prices are year-end values (or annual averages for bags).
    """
    # S&P 500 — take December close each year
    sp500_monthly = fetch_sp500("2000-01-01", "2025-12-31")
    sp500_annual = sp500_monthly.groupby(sp500_monthly.index.year).last()
    sp500_annual.index.name = "year"

    # Bonds (AGG) — take December close each year
    bonds_monthly = fetch_bonds("2003-01-01", "2025-12-31")
    bonds_annual = bonds_monthly.groupby(bonds_monthly.index.year).last()
    bonds_annual.index.name = "year"

    # Handbags
    birkin = build_birkin_series()
    balenciaga = build_balenciaga_series()
    paddington = build_paddington_series()
    cpi = build_cpi_series()

    # Combine
    df = pd.DataFrame({
        "sp500": sp500_annual["sp500"],
        "bonds": bonds_annual["bonds"],
        "birkin": birkin,
        "balenciaga": balenciaga,
        "paddington": paddington,
        "cpi": cpi,
    })

    # Common date range (2005-2025 has all five assets)
    df = df.loc[2005:2025].copy()
    df.index.name = "year"

    return df


def build_monthly_dataset():
    """
    Build monthly time series. For handbags, linearly interpolate
    between annual anchor points to create smooth monthly curves.

    NOTE: This interpolation mechanically suppresses volatility. The
    reported monthly standard deviations for handbags are lower bounds,
    not true measures of price variance. See report for discussion.
    """
    annual = build_annual_dataset()

    # Create monthly index
    months = pd.date_range("2005-01-01", "2025-12-01", freq="MS")

    # S&P 500 — real monthly data
    sp500 = fetch_sp500("2005-01-01", "2025-12-31")
    sp500 = sp500.reindex(months, method="ffill")

    # Bonds (AGG) — real monthly data
    bonds = fetch_bonds("2005-01-01", "2025-12-31")
    bonds = bonds.reindex(months, method="ffill")

    # Interpolate handbags to monthly
    bag_cols = ["birkin", "balenciaga", "paddington"]
    annual_dates = pd.to_datetime([f"{y}-06-01" for y in annual.index])
    bags_annual = annual[bag_cols].copy()
    bags_annual.index = annual_dates

    bags_monthly = bags_annual.reindex(months).interpolate(method="time")
    bags_monthly = bags_monthly.ffill().bfill()

    # CPI — interpolate
    cpi_annual = annual[["cpi"]].copy()
    cpi_annual.index = pd.to_datetime([f"{y}-06-01" for y in annual.index])
    cpi_monthly = cpi_annual.reindex(months).interpolate(method="time")
    cpi_monthly = cpi_monthly.ffill().bfill()

    # Combine
    df = pd.concat([sp500, bonds, bags_monthly, cpi_monthly], axis=1)
    df.index.name = "date"

    return df


def save_datasets():
    """Save both annual and monthly datasets to CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    annual = build_annual_dataset()
    annual.to_csv(DATA_DIR / "annual_prices.csv")
    print(f"Saved annual dataset: {len(annual)} rows, {list(annual.columns)}")

    monthly = build_monthly_dataset()
    monthly.to_csv(DATA_DIR / "monthly_prices.csv")
    print(f"Saved monthly dataset: {len(monthly)} rows, {list(monthly.columns)}")

    # Save metadata
    meta = {
        "description": "Birkins or Bonds — Asset price data",
        "assets": {
            "sp500": "S&P 500 Index (real data via Yahoo Finance)",
            "bonds": "iShares US Aggregate Bond ETF / AGG (real data via Yahoo Finance)",
            "birkin": "Hermès Birkin 35 Togo mid-market resale (proxy)",
            "balenciaga": "Balenciaga Classic City mid-market resale (proxy)",
            "paddington": "Chloé Paddington mid-market resale (proxy)",
        },
        "cpi_source": "Federal Reserve Bank of Minneapolis (1983=100)",
        "date_range": "2005-2025",
        "methodology": (
            "Handbag prices are constructed proxy series based on Knight Frank "
            "KFLII data, auction house records, resale platform benchmarks, "
            "and retail price histories. Monthly values are linearly interpolated "
            "between annual anchors, which mechanically suppresses volatility. "
            "See report for full methodology and caveats."
        ),
    }
    with open(DATA_DIR / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("Saved metadata.json")

    return annual, monthly


if __name__ == "__main__":
    annual, monthly = save_datasets()
    print("\n=== Annual Dataset ===")
    print(annual)
