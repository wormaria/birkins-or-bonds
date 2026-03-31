"""
visualizations.py — High-quality editorial charts for the Birkins or Bonds report.

Style: Bloomberg meets Vogue — clean, authoritative, minimal decoration.
Color palette: Finance-inspired with luxury accents.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
IMG_DIR = Path(__file__).resolve().parent.parent / "images"

# ═══════════════════════════════════════════════════════════════════════════════
# Design system — "Bloomberg meets Vogue"
# ═══════════════════════════════════════════════════════════════════════════════

# Custom palette — finance + luxury
COLORS = {
    "sp500":       "#1B474D",   # Dark teal — institutional
    "birkin":      "#C4883A",   # Gold — luxury, Hermès orange-adjacent
    "balenciaga":  "#6B4C8A",   # Purple — avant-garde
    "paddington":  "#A84B2F",   # Terra/rust — vintage warmth
    "accent":      "#20808D",   # Teal accent
    "bg":          "#FAFAF7",   # Warm white
    "grid":        "#E8E6E1",   # Subtle grid
    "text":        "#28251D",   # Near-black
    "muted":       "#8A8882",   # Muted text
}

ASSET_LABELS = {
    "sp500": "S&P 500",
    "birkin": "Hermès Birkin",
    "balenciaga": "Balenciaga City",
    "paddington": "Chloé Paddington",
}

ASSET_ORDER = ["sp500", "birkin", "balenciaga", "paddington"]


def setup_style():
    """Configure matplotlib for editorial-quality output."""
    plt.rcParams.update({
        "figure.facecolor": COLORS["bg"],
        "axes.facecolor": COLORS["bg"],
        "axes.edgecolor": COLORS["grid"],
        "axes.labelcolor": COLORS["text"],
        "axes.titlecolor": COLORS["text"],
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "text.color": COLORS["text"],
        "grid.color": COLORS["grid"],
        "grid.alpha": 0.6,
        "grid.linewidth": 0.5,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "figure.dpi": 150,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.facecolor": COLORS["bg"],
    })


def add_branding(fig, subtitle=""):
    """Add subtle branding to figure."""
    fig.text(0.99, 0.01, "birkins-or-bonds", fontsize=8,
             color=COLORS["muted"], ha="right", va="bottom",
             fontstyle="italic", alpha=0.6)
    if subtitle:
        fig.text(0.01, 0.01, subtitle, fontsize=8,
                 color=COLORS["muted"], ha="left", va="bottom", alpha=0.6)


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 1: Normalized growth curves (base = 100)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_normalized_growth(monthly, save=True):
    """Normalized growth of $100 invested in each asset."""
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 6.5))

    for asset in ASSET_ORDER:
        prices = monthly[asset].dropna()
        normalized = (prices / prices.iloc[0]) * 100
        lw = 2.8 if asset == "birkin" else 2.0
        alpha = 1.0 if asset in ["sp500", "birkin"] else 0.75
        ax.plot(normalized.index, normalized, color=COLORS[asset],
                linewidth=lw, label=ASSET_LABELS[asset], alpha=alpha)

    ax.set_title("Growth of $100 Invested (2005–2025)", fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Portfolio Value ($)", fontsize=12)
    ax.axhline(y=100, color=COLORS["muted"], linestyle="--", linewidth=0.8, alpha=0.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax.legend(loc="upper left", frameon=False, fontsize=11)
    ax.grid(True, axis="y", alpha=0.4)
    ax.set_xlim(monthly.index.min(), monthly.index.max())
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    add_branding(fig, "Source: Yahoo Finance, Knight Frank KFLII, resale platform data")

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "01_normalized_growth.png")
    plt.close()
    print("  ✓ Normalized growth chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 2: Annual returns bar chart
# ═══════════════════════════════════════════════════════════════════════════════

def plot_annual_returns(annual, save=True):
    """Grouped bar chart of annual returns."""
    setup_style()
    returns = annual[ASSET_ORDER].pct_change().dropna()

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(returns))
    width = 0.2

    for i, asset in enumerate(ASSET_ORDER):
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, returns[asset] * 100, width,
                      color=COLORS[asset], label=ASSET_LABELS[asset], alpha=0.85)

    ax.set_title("Annual Returns by Asset Class", fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Return (%)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(returns.index.astype(int), rotation=45, ha="right")
    ax.axhline(y=0, color=COLORS["text"], linewidth=0.8)
    ax.legend(loc="upper left", frameon=False, fontsize=10, ncol=2)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    add_branding(fig)

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "02_annual_returns.png")
    plt.close()
    print("  ✓ Annual returns chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 3: Rolling 12-month returns
# ═══════════════════════════════════════════════════════════════════════════════

def plot_rolling_returns(monthly, window=12, save=True):
    """Rolling 1-year returns for each asset."""
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    for asset in ASSET_ORDER:
        rolling = monthly[asset].pct_change(window).dropna() * 100
        lw = 2.2 if asset in ["sp500", "birkin"] else 1.5
        ax.plot(rolling.index, rolling, color=COLORS[asset],
                linewidth=lw, label=ASSET_LABELS[asset],
                alpha=0.9 if asset in ["sp500", "birkin"] else 0.65)

    ax.set_title("Rolling 12-Month Returns", fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Trailing 12M Return (%)", fontsize=12)
    ax.axhline(y=0, color=COLORS["text"], linewidth=0.8, alpha=0.5)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(monthly.index.min(), monthly.index.max())
    add_branding(fig)

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "03_rolling_returns.png")
    plt.close()
    print("  ✓ Rolling returns chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 4: Drawdown chart
# ═══════════════════════════════════════════════════════════════════════════════

def plot_drawdowns(monthly, save=True):
    """Drawdown from peak for each asset."""
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    for asset in ASSET_ORDER:
        prices = monthly[asset].dropna()
        cummax = prices.cummax()
        dd = ((prices - cummax) / cummax) * 100
        ax.fill_between(dd.index, dd, 0, color=COLORS[asset], alpha=0.15)
        ax.plot(dd.index, dd, color=COLORS[asset], linewidth=1.5,
                label=ASSET_LABELS[asset], alpha=0.8)

    ax.set_title("Drawdown from Peak", fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Drawdown (%)", fontsize=12)
    ax.legend(loc="lower left", frameon=False, fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(monthly.index.min(), monthly.index.max())
    add_branding(fig)

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "04_drawdowns.png")
    plt.close()
    print("  ✓ Drawdown chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 5: Correlation heatmap
# ═══════════════════════════════════════════════════════════════════════════════

def plot_correlation_heatmap(monthly, save=True):
    """Correlation heatmap of monthly returns."""
    setup_style()
    returns = monthly[ASSET_ORDER].pct_change().dropna()
    corr = returns.corr()

    labels = [ASSET_LABELS[a] for a in ASSET_ORDER]

    fig, ax = plt.subplots(figsize=(8, 7))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0, vmin=-1, vmax=1,
                annot=True, fmt=".2f", linewidths=2, linecolor=COLORS["bg"],
                xticklabels=labels, yticklabels=labels,
                cbar_kws={"shrink": 0.8, "label": "Correlation"},
                annot_kws={"size": 13, "weight": "bold"}, ax=ax)

    ax.set_title("Return Correlations (Monthly)", fontsize=18, fontweight="bold", pad=15)
    ax.tick_params(labelsize=11)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    add_branding(fig)

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "05_correlation_heatmap.png")
    plt.close()
    print("  ✓ Correlation heatmap")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 6: Summary stats dashboard
# ═══════════════════════════════════════════════════════════════════════════════

def plot_summary_dashboard(stats_df, save=True):
    """KPI-style dashboard comparing key metrics."""
    setup_style()
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    fig.suptitle("Performance Dashboard (2005–2025)", fontsize=20,
                 fontweight="bold", y=1.02)

    metrics = [
        ("cagr", "CAGR", "{:.1%}"),
        ("volatility", "Annualized Volatility", "{:.1%}"),
        ("sharpe", "Sharpe Ratio", "{:.2f}"),
        ("max_drawdown", "Max Drawdown", "{:.1%}"),
    ]

    for ax, (metric, title, fmt) in zip(axes, metrics):
        values = [stats_df.loc[a, metric] for a in ASSET_ORDER]
        colors = [COLORS[a] for a in ASSET_ORDER]
        labels = [ASSET_LABELS[a].replace(" ", "\n") for a in ASSET_ORDER]

        bars = ax.barh(range(len(ASSET_ORDER)), values, color=colors, alpha=0.85,
                       height=0.6)

        for i, (bar, val) in enumerate(zip(bars, values)):
            x_pos = bar.get_width()
            ha = "left" if x_pos >= 0 else "right"
            offset = abs(max(values) - min(values)) * 0.05
            if x_pos >= 0:
                x_pos += offset
            else:
                x_pos -= offset
            ax.text(x_pos, i, fmt.format(val), va="center", ha=ha,
                    fontsize=11, fontweight="bold", color=COLORS["text"])

        ax.set_yticks(range(len(ASSET_ORDER)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        ax.axvline(x=0, color=COLORS["text"], linewidth=0.5)
        ax.grid(True, axis="x", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.invert_yaxis()

    add_branding(fig)
    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "06_summary_dashboard.png")
    plt.close()
    print("  ✓ Summary dashboard")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 7: Portfolio simulation
# ═══════════════════════════════════════════════════════════════════════════════

def plot_portfolio_simulation(monthly, save=True):
    """Portfolio growth simulation."""
    from src.analysis import simulate_portfolios
    setup_style()

    port_results, _ = simulate_portfolios(monthly)

    fig, ax = plt.subplots(figsize=(12, 6.5))

    port_colors = ["#1B474D", "#C4883A", "#20808D", "#A84B2F"]

    for (name, res), color in zip(port_results.items(), port_colors):
        cum = res["cumulative"]
        lw = 2.5 if "60/40" in name else 1.8
        ax.plot(cum.index, cum, color=color, linewidth=lw,
                label=f"{name}  (CAGR {res['cagr']:.1%})", alpha=0.9)

    ax.set_title("Portfolio Simulations: Growth of $100",
                 fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Portfolio Value ($)", fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax.axhline(y=100, color=COLORS["muted"], linestyle="--", linewidth=0.8, alpha=0.4)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(monthly.index.min(), monthly.index.max())
    add_branding(fig, "Rebalanced monthly | RF = 2.5%")

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "07_portfolio_simulation.png")
    plt.close()
    print("  ✓ Portfolio simulation chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 8: CPI-adjusted real returns
# ═══════════════════════════════════════════════════════════════════════════════

def plot_real_returns(annual, save=True):
    """Inflation-adjusted (real) growth comparison."""
    setup_style()
    cpi = annual["cpi"]
    deflator = cpi / cpi.iloc[0]

    fig, ax = plt.subplots(figsize=(12, 6))

    for asset in ASSET_ORDER:
        real_price = annual[asset] / deflator
        normalized = (real_price / real_price.iloc[0]) * 100
        lw = 2.5 if asset in ["sp500", "birkin"] else 1.8
        ax.plot(annual.index, normalized, color=COLORS[asset],
                linewidth=lw, label=ASSET_LABELS[asset],
                marker="o", markersize=4, alpha=0.9)

    ax.set_title("Inflation-Adjusted Growth of $100 (Real Returns)",
                 fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Real Value (2005 dollars)", fontsize=12)
    ax.axhline(y=100, color=COLORS["muted"], linestyle="--", linewidth=0.8, alpha=0.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax.legend(loc="upper left", frameon=False, fontsize=11)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    add_branding(fig, "Deflated by US CPI (1983=100) | Source: Federal Reserve Bank of Minneapolis")

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "08_real_returns.png")
    plt.close()
    print("  ✓ Real returns chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 9: Rolling volatility
# ═══════════════════════════════════════════════════════════════════════════════

def plot_rolling_volatility(monthly, window=12, save=True):
    """Rolling 12-month annualized volatility."""
    setup_style()
    fig, ax = plt.subplots(figsize=(12, 6))

    returns = monthly[ASSET_ORDER].pct_change().dropna()

    for asset in ASSET_ORDER:
        rolling_vol = returns[asset].rolling(window).std() * np.sqrt(12) * 100
        lw = 2.2 if asset in ["sp500", "birkin"] else 1.5
        ax.plot(rolling_vol.index, rolling_vol, color=COLORS[asset],
                linewidth=lw, label=ASSET_LABELS[asset],
                alpha=0.9 if asset in ["sp500", "birkin"] else 0.65)

    ax.set_title("Rolling 12-Month Annualized Volatility",
                 fontsize=18, fontweight="bold", pad=15)
    ax.set_ylabel("Volatility (%)", fontsize=12)
    ax.legend(loc="upper right", frameon=False, fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(monthly.index.min(), monthly.index.max())
    add_branding(fig)

    plt.tight_layout()
    if save:
        fig.savefig(IMG_DIR / "09_rolling_volatility.png")
    plt.close()
    print("  ✓ Rolling volatility chart")


# ═══════════════════════════════════════════════════════════════════════════════
# Generate all charts
# ═══════════════════════════════════════════════════════════════════════════════

def generate_all_charts():
    """Generate all visualization outputs."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    monthly = pd.read_csv(DATA_DIR / "monthly_prices.csv",
                          index_col="date", parse_dates=True)
    annual = pd.read_csv(DATA_DIR / "annual_prices.csv", index_col="year")

    # Compute stats for dashboard
    from src.analysis import compute_summary_stats
    stats = compute_summary_stats(monthly, annual)

    print("\n🎨 Generating visualizations...")
    plot_normalized_growth(monthly)
    plot_annual_returns(annual)
    plot_rolling_returns(monthly)
    plot_drawdowns(monthly)
    plot_correlation_heatmap(monthly)
    plot_summary_dashboard(stats)
    plot_portfolio_simulation(monthly)
    plot_real_returns(annual)
    plot_rolling_volatility(monthly)
    print("\n✅ All charts generated in /images/")


if __name__ == "__main__":
    generate_all_charts()
