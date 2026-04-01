<div align="center">

# 👜 Birkins or Bonds

### An Empirical Analysis of Luxury Handbags as Alternative Investment Assets

*Do Hermès Birkins outperform the S&P 500 — or even a plain bond index — on a risk-adjusted basis?*
*Spoiler: the headline numbers are misleading.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data](https://img.shields.io/badge/Data-2005--2025-orange)](data/)

</div>

---

## The Thesis

In July 2025, Jane Birkin's original Hermès bag sold at Sotheby's Paris for **$10 million** — a 9,900% return on the ~$100,000 paid in 2000. Headlines declared luxury handbags the ultimate alternative investment.

But by the time of that sale, the broader Birkin resale market had been cooling for three years. Average resale premiums fell from 2.2× retail in 2022 to 1.4× by late 2025 — a 21% decline from peak.

This project subjects the "Birkins as investments" thesis to rigorous quantitative analysis, benchmarking three iconic luxury handbag models against both the **S&P 500** and the **US Aggregate Bond Index (AGG)** over 20 years (2005–2025):

| Asset | What It Represents |
|-------|-------------------|
| **S&P 500** | Traditional equity markets |
| **US Agg Bond (AGG)** | Fixed income benchmark |
| **Hermès Birkin 35** | The "blue chip" of luxury — scarcity-driven, iconic |
| **Balenciaga City** | The "growth stock" that crashed — trend-driven, volatile |
| **Chloé Paddington** | The "meme stock" arc — hype → crash → nostalgia revival |

---

## Key Findings

<table>
<tr>
<td width="50%">

### 📊 Performance Summary (2005–2025)

| Metric | S&P 500 | US Agg Bond | Birkin (Gross) | Birkin (Net 25%) |
|--------|---------|-------------|----------------|------------------|
| **CAGR** | 8.9% | 3.1% | 5.7% | **4.2%** |
| **Volatility** | 14.8% | 4.6% | 2.4%* | 2.4%* |
| **Sharpe** | 0.47 | 0.13 | 1.21 | **0.73** |
| **Max Drawdown** | −52.6% | −17.2% | −21.8% | −21.8% |

*\*Handbag volatility is artificially suppressed by interpolation between annual data points.*

</td>
<td width="50%">

### 💡 Key Insights

- **Transaction costs are devastating** — a 25% round-trip cost cuts the Birkin's Sharpe from 1.21 to 0.73 and CAGR from 5.7% to 4.2%
- **The low-volatility story is a data artifact** — interpolation between annual anchor points mechanically suppresses variance
- **Birkin still beats bonds after fees** — 4.2% vs. 3.1% CAGR, but bonds are liquid, income-generating, and infinitely divisible
- **Not all luxury bags appreciate** — Balenciaga and Paddington both lost money over 20 years
- **The market is softening** — Birkin resale premiums fell 36% from 2022 to 2025

</td>
</tr>
</table>

---

## Visualizations

### Growth of $100 Invested
![Normalized Growth](images/01_normalized_growth.png)
*The S&P 500 wins on absolute returns ($548 vs. $305), but the Birkin's path is remarkably smooth — a consequence of interpolated proxy data, not genuine low volatility. Bonds (AGG, dashed) provide the fixed-income benchmark.*

### Performance Dashboard
![Dashboard](images/06_summary_dashboard.png)

### Drawdown from Peak
![Drawdowns](images/04_drawdowns.png)
*The Paddington's 84% drawdown illustrates the danger of fashion-cycle risk.*

### Correlation Heatmap
![Correlations](images/05_correlation_heatmap.png)
*Birkin returns are essentially uncorrelated with equities (0.06) and bonds (0.05) — driven by scarcity and culture, not economic cycles.*

### Portfolio Simulations (Annual Rebalancing)
![Portfolios](images/07_portfolio_simulation.png)
*A 60/40 stocks–Birkin allocation shows a Sharpe of 0.61, but this assumes annual rebalancing of an illiquid asset with no transaction cost deduction — the real-world advantage is far smaller.*

### Inflation-Adjusted Returns
![Real Returns](images/08_real_returns.png)

---

## The Bottom Line

| Question | Answer |
|----------|--------|
| Are Birkins better than bonds? | **Barely** — 4.2% net CAGR vs. 3.1%, but bonds are liquid, pay coupons, and require no expertise |
| Are Birkins better than stocks? | **No** — S&P 500 delivers 8.9% CAGR with no transaction friction |
| Are luxury bags good investments? | **Only Hermès** — without artificial scarcity, bags are depreciating goods |
| Should you build a handbag portfolio? | **No** — the theoretical diversification math is real, but practical barriers are prohibitive |

---

## Project Structure

```
birkins-or-bonds/
├── README.md
├── requirements.txt
├── LICENSE
├── src/
│   ├── __init__.py
│   ├── main.py              # Full pipeline runner
│   ├── data_collection.py   # Data fetching & proxy construction (incl. AGG bonds)
│   ├── analysis.py          # Quantitative analysis (gross & net-of-fee metrics)
│   ├── visualizations.py    # Chart generation (all charts include bonds benchmark)
│   └── generate_report.py   # PDF report builder
├── data/
│   ├── annual_prices.csv
│   ├── monthly_prices.csv
│   ├── summary_statistics.csv
│   ├── correlation_matrix.csv
│   ├── real_returns_cpi_adjusted.csv
│   └── metadata.json
├── images/                   # All generated charts
├── reports/
│   ├── birkins_or_bonds.qmd  # Quarto source
│   └── birkins_or_bonds_report.pdf
└── notebooks/                # Exploration notebooks
```

---

## How to Run

```bash
# Clone the repository
git clone https://github.com/wormaria/birkins-or-bonds.git
cd birkins-or-bonds

# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (data → analysis → charts)
python -m src.main

# Generate the PDF report
python -m src.generate_report
```

---

## Data & Methodology

### S&P 500
Real market data from Yahoo Finance (`^GSPC` index), monthly close prices.

### US Aggregate Bond Index
Real market data from Yahoo Finance (`AGG` ETF), monthly close prices. Note: price return understates true bond performance because it excludes coupon income.

### Luxury Handbags
Proxy time series constructed from:
- **Knight Frank Luxury Investment Index (KFLII)** handbag component — the standard benchmark for collectible handbag returns
- **Bernstein Research** Secondhand Pricing Tracker — tracks Birkin/Kelly resale premium to retail ratio
- **Auction house records** — Christie's, Sotheby's realized prices for benchmark models
- **Resale platform data** — Fashionphile, Rebag, Vestiaire Collective market benchmarks
- **Retail price histories** — Hermès annual price lists, brand archives

Each data point is documented in `src/data_collection.py` with source attribution.

### Critical Data Caveat
Handbag prices are **linearly interpolated between annual anchor points**. This mechanically suppresses month-to-month volatility. The Birkin's 2.4% annualized volatility — and the resulting Sharpe ratio of 1.21 — are partially artifacts of this data construction, not evidence of genuinely low price variance.

### Transaction Costs
The report presents both **gross** and **net-of-fee** metrics. A 25% round-trip cost (typical auction friction) is applied for net figures. Portfolio simulations do **not** deduct transaction costs from Birkin rebalancing trades.

### Inflation Adjustment
US CPI data from the Federal Reserve Bank of Minneapolis (1983=100 basis).

### Limitations
- **Survivorship bias** — only bags in good condition are resold
- **Illiquidity** — selling takes 2–8 weeks; not reflected in volatility metrics
- **Selection bias** — we track iconic bags, not a random sample
- **No income** — bags pay no dividends; S&P and AGG returns exclude dividends/coupons for comparability
- **2022–2025 resale softness** — the market is in a correction that may not be over

---

## Analysis Includes

- [x] CAGR (compound annual growth rate) — gross and net of 25% transaction costs
- [x] Annualized volatility (with interpolation caveat)
- [x] Sharpe ratio (RF = 2.5%) — gross and net of fees
- [x] Maximum drawdown
- [x] Correlation matrix (including bonds)
- [x] Rolling 12-month returns
- [x] Rolling 12-month volatility
- [x] CPI-adjusted (real) returns
- [x] Portfolio simulations (4 allocations, **annual rebalancing**)
- [x] Annual returns comparison
- [x] 2022–2025 resale market correction analysis

---

## Built With

- **pandas** / **numpy** — data processing & numerical computation
- **matplotlib** / **seaborn** — visualization
- **yfinance** — S&P 500 and AGG market data
- **scipy** — statistical methods
- **ReportLab** — PDF report generation

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
<i>The Birkin is less an investment thesis and more a case study in the economics of scarcity and cultural capital. The numbers are interesting. The practical barriers are prohibitive.</i>
</div>
