"""
analysis.py — Full quantitative analysis of luxury handbags vs. equities vs. bonds.

Metrics computed:
  - CAGR (compound annual growth rate) — gross and net of transaction costs
  - Annualized volatility (with interpolation caveat for handbags)
  - Sharpe ratio (using 10-year Treasury yield as risk-free rate)
  - Maximum drawdown
  - Correlation matrix between assets
  - Rolling returns (1-year, 3-year)
  - CPI-adjusted (real) returns
  - Portfolio simulation with ANNUAL rebalancing (not monthly — handbags
    are illiquid and cannot be rebalanced monthly)

Transaction cost assumptions for handbags:
  - Low estimate: 15% (consignment to Fashionphile/Rebag)
  - High estimate: 25% (auction house buyer's premium + seller's commission)
  These are applied as a one-time friction on total return, then annualized.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Risk-free rate: approximate average 10-year Treasury yield 2005-2025
RISK_FREE_RATE = 0.025

ASSET_LABELS = {
    "sp500": "S&P 500",
    "bonds": "US Agg Bond (AGG)",
    "birkin": "Hermès Birkin",
    "balenciaga": "Balenciaga City",
    "paddington": "Chloé Paddington",
}

ASSET_ORDER = ["sp500", "bonds", "birkin", "balenciaga", "paddington"]

# Handbag transaction cost scenarios
TXN_COST_LOW = 0.15   # 15% consignment fee
TXN_COST_HIGH = 0.25  # 25% auction round-trip


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


def cagr_net_of_fees(series, fee_rate):
    """
    CAGR net of a one-time transaction cost applied at exit.
    This models: buy at start, hold, sell at end minus commission.
    """
    start, end = series.dropna().iloc[0], series.dropna().iloc[-1]
    n_years = len(series.dropna()) - 1
    if n_years <= 0 or start <= 0:
        return np.nan
    net_end = end * (1 - fee_rate)
    return (net_end / start) ** (1 / n_years) - 1


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


def sharpe_net_of_fees(annual_prices, monthly_returns, fee_rate, rf=RISK_FREE_RATE):
    """
    Sharpe ratio adjusted for transaction costs.
    Reduces the annualized return by the amortized fee impact,
    keeps volatility unchanged.
    """
    gross_cagr = cagr(annual_prices)
    net_cagr_val = cagr_net_of_fees(annual_prices, fee_rate)
    vol = annualized_volatility(monthly_returns)
    if vol == 0:
        return np.nan
    return (net_cagr_val - rf) / vol


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
    """
    Compute summary statistics for all assets.
    Includes gross AND net-of-fee metrics for handbag assets.
    """
    assets = ASSET_ORDER
    monthly_returns = monthly[assets].pct_change().dropna()
    handbag_assets = {"birkin", "balenciaga", "paddington"}

    stats = {}
    for asset in assets:
        prices = monthly[asset].dropna()
        rets = monthly_returns[asset].dropna()
        annual_prices = annual[asset].dropna()

        row = {
            "label": ASSET_LABELS[asset],
            "start_price": annual_prices.iloc[0],
            "end_price": annual_prices.iloc[-1],
            "cagr": cagr(annual_prices),
            "volatility": annualized_volatility(rets),
            "sharpe": sharpe_ratio(rets),
            "max_drawdown": max_drawdown(prices),
            "total_return": (annual_prices.iloc[-1] / annual_prices.iloc[0]) - 1,
        }

        # Net-of-fee metrics for handbags
        if asset in handbag_assets:
            row["cagr_net_15"] = cagr_net_of_fees(annual_prices, TXN_COST_LOW)
            row["cagr_net_25"] = cagr_net_of_fees(annual_prices, TXN_COST_HIGH)
            row["sharpe_net_15"] = sharpe_net_of_fees(annual_prices, rets, TXN_COST_LOW)
            row["sharpe_net_25"] = sharpe_net_of_fees(annual_prices, rets, TXN_COST_HIGH)
        else:
            row["cagr_net_15"] = row["cagr"]  # no transaction cost for liquid assets
            row["cagr_net_25"] = row["cagr"]
            row["sharpe_net_15"] = row["sharpe"]
            row["sharpe_net_25"] = row["sharpe"]

        # Flag interpolated volatility
        row["vol_interpolated"] = asset in handbag_assets

        stats[asset] = row

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
# Portfolio simulation — ANNUAL rebalancing
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_portfolios(monthly):
    """
    Simulate portfolio allocations with ANNUAL rebalancing.

    Why annual, not monthly: the report documents that selling a Birkin
    takes 2-8 weeks. Monthly rebalancing of an illiquid asset is physically
    impossible. Annual rebalancing is the minimum realistic frequency,
    and even this is optimistic (it assumes you can execute a trade within
    a calendar year).

    Portfolios:
      1. 100% S&P 500
      2. 60% S&P 500 / 40% Bonds (traditional 60/40)
      3. 60% S&P 500 / 40% Birkin
      4. 50% S&P 500 / 25% Bonds / 25% Birkin
    """
    returns = monthly[ASSET_ORDER].pct_change().dropna()

    portfolios = {
        "100% S&P 500": {"sp500": 1.0},
        "60/40 Stocks–Bonds": {"sp500": 0.6, "bonds": 0.4},
        "60/40 Stocks–Birkin": {"sp500": 0.6, "birkin": 0.4},
        "50/25/25 Mix": {"sp500": 0.5, "bonds": 0.25, "birkin": 0.25},
    }

    results = {}
    for name, target_weights in portfolios.items():
        # Annual rebalancing: reset weights each January
        assets_in_port = list(target_weights.keys())
        weights_arr = np.array([target_weights[a] for a in assets_in_port])

        port_values = [100.0]
        current_weights = weights_arr.copy()

        for i, date in enumerate(returns.index):
            month_returns = np.array([returns.loc[date, a] for a in assets_in_port])
            # Grow each position
            grown = current_weights * (1 + month_returns)
            portfolio_value = grown.sum() / current_weights.sum() * port_values[-1]
            port_values.append(portfolio_value)

            # Update weights (drift)
            current_weights = grown / grown.sum()

            # Rebalance annually (every January)
            if date.month == 1:
                current_weights = weights_arr.copy()

        cumulative = pd.Series(port_values[1:], index=returns.index)
        n_months = len(cumulative)
        final_cagr = (cumulative.iloc[-1] / 100) ** (12 / n_months) - 1

        port_returns = cumulative.pct_change().dropna()
        port_vol = port_returns.std() * np.sqrt(12)
        port_sharpe = (port_returns.mean() * 12 - RISK_FREE_RATE) / port_vol if port_vol > 0 else np.nan

        results[name] = {
            "cumulative": cumulative,
            "cagr": final_cagr,
            "volatility": port_vol,
            "sharpe": port_sharpe,
            "max_drawdown": max_drawdown(cumulative),
        }

    return results, portfolios


def run_full_analysis():
    """Run the complete analysis pipeline and save results."""
    monthly, annual = load_data()

    print("=" * 60)
    print("BIRKINS OR BONDS — FULL ANALYSIS (v2)")
    print("=" * 60)

    # Summary stats
    stats = compute_summary_stats(monthly, annual)
    print("\n📊 Summary Statistics (2005–2025)")
    print("-" * 60)
    for _, row in stats.iterrows():
        is_bag = row.get("vol_interpolated", False)
        print(f"\n  {row['label']}")
        print(f"    CAGR (gross):     {row['cagr']:.1%}")
        if is_bag:
            print(f"    CAGR (net 15%):   {row['cagr_net_15']:.1%}")
            print(f"    CAGR (net 25%):   {row['cagr_net_25']:.1%}")
        print(f"    Volatility:       {row['volatility']:.1%}" +
              (" ⚠ interpolated" if is_bag else ""))
        print(f"    Sharpe (gross):   {row['sharpe']:.2f}")
        if is_bag:
            print(f"    Sharpe (net 15%): {row['sharpe_net_15']:.2f}")
            print(f"    Sharpe (net 25%): {row['sharpe_net_25']:.2f}")
        print(f"    Max Drawdown:     {row['max_drawdown']:.1%}")
        print(f"    Total Return:     {row['total_return']:.0%}")

    # Correlation
    corr = compute_correlation_matrix(monthly)
    print("\n📈 Correlation Matrix (monthly returns)")
    print("-" * 60)
    print(corr.round(3).to_string())

    # Portfolio simulation (annual rebalancing)
    port_results, _ = simulate_portfolios(monthly)
    print("\n💼 Portfolio Simulations (annual rebalancing)")
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
