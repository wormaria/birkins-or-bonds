"""
analysis.py — Full quantitative analysis of luxury handbags vs. equities.

Metrics computed:
  - CAGR (compound annual growth rate)
  - Annualized volatility
  - Sharpe ratio (using 10-year Treasury yield as risk-free rate)
  - Maximum drawdown
  - Correlation matrix
  - Rolling returns (1-year, 3-year)
  - CPI-adjusted (real) returns
  - Portfolio simulations (60/40 stocks/bags)
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Risk-free rate: approximate average 10-year Treasury yield 2005-2025
RISK_FREE_RATE = 0.025

ASSET_LABELS = {
    "sp500": "S&P 500",
    "birkin": "Hermès Birkin",
    "balenciaga": "Balenciaga City",
    "paddington": "Chloé Paddington",
}

ASSET_ORDER = ["sp500", "birkin", "balenciaga", "paddington"]


# ═══════════════════════════════════════════════════════════════════════════════
# Core metrics
# ═══════════════════════════════════════════════════════════════════════════════

def cagr(series):
    """Compound annual growth rate from first to last value."""
    start, end = series.dropna().iloc[0], series.dropna().iloc[-1]
    n_years = len(series.dropna()) - 1
    if n_years <= 0 or start <= 0:
        return np.nan
    return (end / start) ** (1 / n_years) - 1


def annualized_volatility(returns):
    """Annualized standard deviation of returns."""
    return returns.std() * np.sqrt(12)  # monthly returns → annualized


def sharpe_ratio(returns, rf=RISK_FREE_RATE):
    """Annualized Sharpe ratio."""
    excess = returns.mean() * 12 - rf
    vol = annualized_volatility(returns)
    if vol == 0:
        return np.nan
    return excess / vol


def max_drawdown(prices):
    """Maximum drawdown (peak-to-trough decline)."""
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    return drawdown.min()


def rolling_returns(prices, window_months=12):
    """Rolling annualized returns."""
    return prices.pct_change(window_months).dropna()


# ═══════════════════════════════════════════════════════════════════════════════
# Full analysis
# ═══════════════════════════════════════════════════════════════════════════════

def load_data():
    """Load the monthly and annual datasets."""
    monthly = pd.read_csv(DATA_DIR / "monthly_prices.csv", index_col="date", parse_dates=True)
    annual = pd.read_csv(DATA_DIR / "annual_prices.csv", index_col="year")
    return monthly, annual


def compute_summary_stats(monthly, annual):
    """Compute summary statistics for all assets."""
    assets = ASSET_ORDER
    monthly_returns = monthly[assets].pct_change().dropna()

    stats = {}
    for asset in assets:
        prices = monthly[asset].dropna()
        rets = monthly_returns[asset].dropna()
        annual_prices = annual[asset].dropna()

        stats[asset] = {
            "label": ASSET_LABELS[asset],
            "start_price": annual_prices.iloc[0],
            "end_price": annual_prices.iloc[-1],
            "cagr": cagr(annual_prices),
            "volatility": annualized_volatility(rets),
            "sharpe": sharpe_ratio(rets),
            "max_drawdown": max_drawdown(prices),
            "total_return": (annual_prices.iloc[-1] / annual_prices.iloc[0]) - 1,
        }

    return pd.DataFrame(stats).T


def compute_real_returns(annual):
    """Compute CPI-adjusted (real) returns."""
    cpi = annual["cpi"]
    deflator = cpi / cpi.iloc[0]  # normalize CPI to base year

    real = pd.DataFrame(index=annual.index)
    for asset in ASSET_ORDER:
        real[asset] = annual[asset] / deflator

    return real


def compute_correlation_matrix(monthly):
    """Correlation matrix of monthly returns."""
    returns = monthly[ASSET_ORDER].pct_change().dropna()
    return returns.corr()


def compute_rolling_returns(monthly, window=12):
    """Compute rolling 1-year returns for each asset."""
    rolling = pd.DataFrame(index=monthly.index)
    for asset in ASSET_ORDER:
        rolling[asset] = rolling_returns(monthly[asset], window)
    return rolling


def compute_drawdown_series(monthly):
    """Compute drawdown time series for each asset."""
    dd = pd.DataFrame(index=monthly.index)
    for asset in ASSET_ORDER:
        prices = monthly[asset]
        cummax = prices.cummax()
        dd[asset] = (prices - cummax) / cummax
    return dd


def compute_normalized_growth(monthly, base=100):
    """Normalize all assets to base=100 at start."""
    norm = pd.DataFrame(index=monthly.index)
    for asset in ASSET_ORDER:
        prices = monthly[asset].dropna()
        norm[asset] = (prices / prices.iloc[0]) * base
    return norm


# ═══════════════════════════════════════════════════════════════════════════════
# Portfolio simulation
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_portfolios(monthly):
    """
    Simulate portfolio allocations:
      1. 100% S&P 500
      2. 60% S&P 500 / 40% Birkin
      3. Equal-weight all four assets
      4. 50% S&P 500 / 25% Birkin / 25% Paddington
    """
    returns = monthly[ASSET_ORDER].pct_change().dropna()

    portfolios = {
        "100% S&P 500": {"sp500": 1.0},
        "60/40 Stocks–Birkin": {"sp500": 0.6, "birkin": 0.4},
        "Equal Weight": {a: 0.25 for a in ASSET_ORDER},
        "50/25/25 Mix": {"sp500": 0.5, "birkin": 0.25, "paddington": 0.25},
    }

    results = {}
    for name, weights in portfolios.items():
        port_returns = sum(returns[a] * w for a, w in weights.items())
        cumulative = (1 + port_returns).cumprod() * 100
        results[name] = {
            "cumulative": cumulative,
            "cagr": (cumulative.iloc[-1] / 100) ** (12 / len(cumulative)) - 1,
            "volatility": port_returns.std() * np.sqrt(12),
            "sharpe": (port_returns.mean() * 12 - RISK_FREE_RATE) / (port_returns.std() * np.sqrt(12)),
            "max_drawdown": max_drawdown(cumulative),
        }

    return results, portfolios


def run_full_analysis():
    """Run the complete analysis pipeline and save results."""
    monthly, annual = load_data()

    print("=" * 60)
    print("BIRKINS OR BONDS — FULL ANALYSIS")
    print("=" * 60)

    # Summary stats
    stats = compute_summary_stats(monthly, annual)
    print("\n📊 Summary Statistics (2005–2025)")
    print("-" * 60)
    for _, row in stats.iterrows():
        print(f"\n  {row['label']}")
        print(f"    CAGR:           {row['cagr']:.1%}")
        print(f"    Volatility:     {row['volatility']:.1%}")
        print(f"    Sharpe Ratio:   {row['sharpe']:.2f}")
        print(f"    Max Drawdown:   {row['max_drawdown']:.1%}")
        print(f"    Total Return:   {row['total_return']:.0%}")

    # Correlation
    corr = compute_correlation_matrix(monthly)
    print("\n📈 Correlation Matrix (monthly returns)")
    print("-" * 60)
    print(corr.round(3).to_string())

    # Portfolio simulation
    port_results, _ = simulate_portfolios(monthly)
    print("\n💼 Portfolio Simulations")
    print("-" * 60)
    for name, res in port_results.items():
        print(f"\n  {name}")
        print(f"    CAGR:         {res['cagr']:.1%}")
        print(f"    Volatility:   {res['volatility']:.1%}")
        print(f"    Sharpe:       {res['sharpe']:.2f}")
        print(f"    Max DD:       {res['max_drawdown']:.1%}")

    # Save stats
    stats.to_csv(DATA_DIR / "summary_statistics.csv")
    corr.to_csv(DATA_DIR / "correlation_matrix.csv")

    # Real returns
    real = compute_real_returns(annual)
    real.to_csv(DATA_DIR / "real_returns_cpi_adjusted.csv")

    print("\n✅ Analysis complete. Results saved to /data/")
    return stats, corr, port_results


if __name__ == "__main__":
    run_full_analysis()
