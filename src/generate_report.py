"""
generate_report.py — Generate a polished PDF research report.

Style: Hedge fund research memo / sell-side report aesthetic.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors

PROJ_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = PROJ_DIR / "images"
REPORT_DIR = PROJ_DIR / "reports"

# ═══════════════════════════════════════════════════════════════════════════════
# Colors
# ═══════════════════════════════════════════════════════════════════════════════

DARK = HexColor("#1B1B1B")
TEAL = HexColor("#1B474D")
GOLD = HexColor("#C4883A")
MUTED = HexColor("#6B6B6B")
LIGHT_BG = HexColor("#F7F6F2")
BORDER = HexColor("#D4D1CA")
WHITE = HexColor("#FFFFFF")


def build_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=28, leading=34,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"],
        fontName="Helvetica", fontSize=13, leading=18,
        textColor=MUTED, alignment=TA_LEFT, spaceAfter=24
    ))
    styles.add(ParagraphStyle(
        "SectionHead", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=16, leading=22,
        textColor=TEAL, spaceBefore=24, spaceAfter=10,
        borderWidth=0, borderPadding=0
    ))
    styles.add(ParagraphStyle(
        "SubHead", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, leading=16,
        textColor=DARK, spaceBefore=14, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        "BodyText2", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        "Callout", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=16,
        textColor=TEAL, alignment=TA_LEFT, spaceAfter=8,
        leftIndent=12, borderWidth=0
    ))
    styles.add(ParagraphStyle(
        "Caption", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=16
    ))
    styles.add(ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=MUTED, alignment=TA_CENTER
    ))
    return styles


def make_table(data, col_widths=None):
    """Create a styled data table."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def add_chart(elements, filename, caption, styles, width=6.5*inch):
    """Add a chart image with caption."""
    img_path = IMG_DIR / filename
    if img_path.exists():
        img = Image(str(img_path), width=width, height=width * 0.55)
        elements.append(img)
        elements.append(Paragraph(caption, styles["Caption"]))
    else:
        elements.append(Paragraph(f"[Chart not found: {filename}]", styles["Caption"]))


def generate_pdf():
    """Generate the full PDF report."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIR / "birkins_or_bonds_report.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.85*inch,
        rightMargin=0.85*inch,
        title="Birkins or Bonds: Luxury Handbags as Alternative Investments",
        author="Perplexity Computer",
    )

    styles = build_styles()
    elements = []

    # ─── Cover / Title ───
    elements.append(Spacer(1, 0.5*inch))
    elements.append(HRFlowable(width="100%", thickness=2, color=TEAL))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Birkins or Bonds", styles["ReportTitle"]))
    elements.append(Paragraph(
        "An Empirical Analysis of Luxury Handbags as Alternative Investment Assets",
        styles["ReportSubtitle"]
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Mariah Workman  ·  March 2026", styles["Caption"]
    ))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elements.append(Spacer(1, 16))

    # ─── Executive Summary ───
    elements.append(Paragraph("Executive Summary", styles["SectionHead"]))
    elements.append(Paragraph(
        "In July 2025, Jane Birkin's original Hermès bag sold at Sotheby's Paris for over $10 million — "
        "a 9,900% return on the approximately $100,000 paid in 2000, representing a 20.3% annualized IRR.<super>1</super> "
        "This report subjects the \"Birkins as investments\" thesis to rigorous quantitative analysis, benchmarking "
        "three iconic luxury handbag models against the S&P 500 over a 20-year horizon (2005–2025).",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        "The Hermès Birkin 35 achieves a Sharpe ratio of 1.21 — 2.6× the S&P 500's 0.47 — driven by "
        "extraordinarily low volatility (2.4% annualized vs. 14.8%). Its near-zero correlation with equities "
        "(ρ = 0.06) makes it a theoretically compelling diversifier. However, the Balenciaga City and Chloé "
        "Paddington both destroyed value over the same period, demonstrating that luxury ≠ investment grade.",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        "Key finding: the Birkin's returns are a function of Hermès's deliberate supply constraint and "
        "enduring cultural capital — not a generalizable property of luxury goods.",
        styles["Callout"]
    ))

    # Footnotes for exec summary
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>1</super> '
        '<a href="https://fortune.com/2025/12/17/gen-z-reality-check-birkin-resale-prices-slump-aspirational-luxury-slowdown/" color="blue">'
        'Fortune, "Gen Z\'s reality check: Birkin resale prices slump" (Dec 2025)</a></font>',
        styles["BodyText2"]
    ))

    elements.append(PageBreak())

    # ─── Data & Methodology ───
    elements.append(Paragraph("Data & Methodology", styles["SectionHead"]))
    elements.append(Paragraph("Data Sources", styles["SubHead"]))

    source_data = [
        ["Asset", "Source", "Type"],
        ["S&P 500", "Yahoo Finance (^GSPC)", "Real market data"],
        ["Hermès Birkin 35", "Knight Frank KFLII, Bernstein, auctions", "Proxy construction"],
        ["Balenciaga City", "Retail history, Fashionphile benchmarks", "Proxy construction"],
        ["Chloé Paddington", "Retail history, resale platform listings", "Proxy construction"],
        ["US CPI", "Federal Reserve Bank of Minneapolis", "Real data"],
    ]
    elements.append(make_table(source_data, col_widths=[1.5*inch, 2.8*inch, 1.8*inch]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Proxy Construction Methodology", styles["SubHead"]))
    elements.append(Paragraph(
        "Handbag \"prices\" represent mid-market resale estimates — the price a bag in very good condition "
        "would fetch on a major authenticated resale platform. The time series are constructed by anchoring "
        "to known retail prices, applying Knight Frank KFLII handbag component returns, calibrating to "
        "auction realized prices, and adjusting for resale premium/discount ratios from Bernstein Research's "
        "Secondhand Pricing Tracker.<super>2</super> Monthly values are linearly interpolated between annual anchor points.",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>2</super> '
        '<a href="https://www.knightfrank.com/wealthreport/2020-07-31-rise-in-handbag-opulence-the-knight-frank-luxury-investment-index" color="blue">'
        'Knight Frank, "Rise in Handbag Opulence" (KFLII 2020)</a></font>',
        styles["BodyText2"]
    ))

    elements.append(Paragraph("Limitations", styles["SubHead"]))
    limitations = [
        "Survivorship bias: only bags in good condition are resold; damaged/lost bags are invisible to the data.",
        "Illiquidity: selling a handbag takes 2–8 weeks vs. milliseconds for equities.",
        "Transaction costs: resale platforms charge 15–30% commission; auction houses charge 20–25% buyer's premium. These are not reflected in reported returns.",
        "Selection bias: we track the most iconic bags, not a random sample of luxury handbags.",
        "No income: bags generate no dividends or coupons. S&P 500 returns exclude dividends for comparability.",
    ]
    for lim in limitations:
        elements.append(Paragraph(f"• {lim}", styles["BodyText2"]))

    elements.append(PageBreak())

    # ─── Results ───
    elements.append(Paragraph("Results", styles["SectionHead"]))
    elements.append(Paragraph("Performance Summary", styles["SubHead"]))

    perf_data = [
        ["Metric", "S&P 500", "Hermès Birkin", "Balenciaga City", "Chloé Paddington"],
        ["CAGR", "8.9%", "5.7%", "−1.6%", "−1.5%"],
        ["Volatility", "14.8%", "2.4%", "3.6%", "5.3%"],
        ["Sharpe Ratio", "0.47", "1.21", "−1.10", "−0.73"],
        ["Max Drawdown", "−52.6%", "−21.8%", "−53.8%", "−84.0%"],
        ["Total Return", "448%", "205%", "−27%", "−27%"],
    ]
    elements.append(make_table(perf_data, col_widths=[1.1*inch, 1.1*inch, 1.2*inch, 1.3*inch, 1.4*inch]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        "The Birkin's Sharpe ratio of 1.21 is 2.6× the S&P 500's 0.47. This is driven not by higher absolute "
        "returns but by extraordinarily low volatility (2.4% vs. 14.8%). The Birkin barely registers the 2008 "
        "financial crisis, losing only 21.8% peak-to-trough versus the S&P 500's 52.6%.<super>3</super>",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>3</super> '
        '<a href="https://www.elliman.com/insider/the-wealth-report-2025-the-great-luxury-correction" color="blue">'
        'Douglas Elliman / Knight Frank, "The Wealth Report 2025" (Feb 2025)</a></font>',
        styles["BodyText2"]
    ))

    elements.append(Spacer(1, 10))
    add_chart(elements, "01_normalized_growth.png",
              "Figure 1: Growth of $100 invested in each asset class, 2005–2025. "
              "Source: Yahoo Finance, Knight Frank KFLII, resale platform data.", styles)

    elements.append(PageBreak())
    elements.append(Paragraph("Drawdown Analysis", styles["SubHead"]))
    elements.append(Paragraph(
        "The drawdown chart reveals the Birkin's resilience during market stress. While the S&P 500 "
        "suffered a 52.6% drawdown during the GFC and periodic corrections of 20%+, the Birkin's maximum "
        "drawdown was just 21.8% — occurring not during a market crisis but during the 2022–2024 resale "
        "premium compression identified by Bernstein Research.<super>4</super>",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        "The Chloé Paddington's 84% drawdown illustrates the danger of fashion-cycle risk — a bag that "
        "was the most coveted accessory in 2005 was worth $250 by 2015.",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>4</super> '
        '<a href="https://fortune.com/2025/12/17/gen-z-reality-check-birkin-resale-prices-slump-aspirational-luxury-slowdown/" color="blue">'
        'Fortune, Bernstein Research Secondhand Pricing Tracker (Dec 2025)</a></font>',
        styles["BodyText2"]
    ))
    add_chart(elements, "04_drawdowns.png",
              "Figure 2: Peak-to-trough drawdowns for each asset, 2005–2025.", styles)

    elements.append(Paragraph("Correlation Structure", styles["SubHead"]))
    elements.append(Paragraph(
        "The Birkin's monthly return correlation with the S&P 500 is just 0.06 — essentially zero. "
        "This is consistent with the hypothesis that luxury collectible returns are driven by wealth effects, "
        "scarcity dynamics, and cultural trends rather than economic cycles. The Paddington is slightly "
        "negatively correlated with the Birkin (−0.20), suggesting that Birkin scarcity and nostalgia-driven "
        "fashion revivals operate through different mechanisms.",
        styles["BodyText2"]
    ))
    add_chart(elements, "05_correlation_heatmap.png",
              "Figure 3: Correlation matrix of monthly returns across asset classes.", styles, width=4.5*inch)

    elements.append(PageBreak())
    elements.append(Paragraph("Portfolio Simulation", styles["SubHead"]))
    elements.append(Paragraph(
        "We simulate four portfolio allocations rebalanced monthly:",
        styles["BodyText2"]
    ))

    port_data = [
        ["Portfolio", "CAGR", "Volatility", "Sharpe", "Max Drawdown"],
        ["100% S&P 500", "8.8%", "14.8%", "0.47", "−52.6%"],
        ["60/40 Stocks–Birkin", "7.7%", "9.0%", "0.60", "−35.9%"],
        ["Equal Weight (4 assets)", "3.0%", "4.4%", "0.12", "−31.0%"],
        ["50/25/25 Mix", "5.6%", "7.7%", "0.43", "−38.3%"],
    ]
    elements.append(make_table(port_data, col_widths=[1.7*inch, 0.8*inch, 0.9*inch, 0.8*inch, 1.2*inch]))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        "The 60/40 stocks–Birkin allocation delivers the best risk-adjusted outcome: Sharpe 0.60 vs. 0.47 "
        "for pure equity, with a maximum drawdown reduced from 52.6% to 35.9%. The improvement comes from "
        "the Birkin's low correlation and low volatility, which dampen portfolio-level variance without "
        "dramatically reducing returns.",
        styles["BodyText2"]
    ))
    add_chart(elements, "07_portfolio_simulation.png",
              "Figure 4: Simulated portfolio growth of $100 under different allocation strategies.", styles)

    elements.append(Paragraph("Inflation-Adjusted Returns", styles["SubHead"]))
    elements.append(Paragraph(
        "After adjusting for CPI inflation, the Birkin's real CAGR falls to approximately 3.1%, while "
        "the S&P 500 delivers ~6.3%. The Birkin preserves purchasing power; the Paddington and Balenciaga "
        "do not — their real returns are deeply negative over the period.",
        styles["BodyText2"]
    ))
    add_chart(elements, "08_real_returns.png",
              "Figure 5: Inflation-adjusted (real) growth of $100, 2005–2025. "
              "CPI source: Federal Reserve Bank of Minneapolis.", styles)

    elements.append(PageBreak())

    # ─── Discussion ───
    elements.append(Paragraph("Discussion", styles["SectionHead"]))
    elements.append(Paragraph("What Makes the Birkin Different?", styles["SubHead"]))
    elements.append(Paragraph(
        "The Birkin's performance is not a property of \"luxury handbags\" as an asset class — it is a "
        "property of Hermès's deliberate supply constraint. Five key drivers explain the asymmetry:",
        styles["BodyText2"]
    ))
    drivers = [
        "Artificial scarcity: Hermès produces a limited number of Birkins annually and requires substantial purchase history before offering one.",
        "Price inelasticity: annual retail price increases of 5–8% are absorbed by a deep, global demand pool.<super>5</super>",
        "Cultural capital: the Birkin carries social signaling value that transcends seasonal fashion cycles.",
        "Authentication infrastructure: platforms like Rebag, Fashionphile, and Vestiaire provide market liquidity and buyer trust.",
        "Wealth concentration: as global wealth concentrates, demand for Veblen goods rises faster than supply.",
    ]
    for d in drivers:
        elements.append(Paragraph(f"• {d}", styles["BodyText2"]))

    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>5</super> '
        '<a href="https://finance.yahoo.com/news/birkin-bags-double-value-5-195755262.html" color="blue">'
        'Yahoo Finance, "Birkin bags can double in value in 5 years" (Mar 2024)</a></font>',
        styles["BodyText2"]
    ))

    elements.append(Paragraph("The Fashion Cycle Trap", styles["SubHead"]))
    elements.append(Paragraph(
        "The Balenciaga City and Chloé Paddington tell the opposite story. Both were \"It bags\" that "
        "generated enormous excitement at launch but depreciated as fashion moved on. The Paddington lost "
        "84% of its peak value before nostalgia and a Chloé brand reissue partially recovered it. "
        "Trend-driven bags are consumption goods, not investment assets. Only bags with permanent brand "
        "moats — Hermès, certain Chanel classics — exhibit investment-like behavior.",
        styles["BodyText2"]
    ))

    elements.append(Paragraph("Practical Caveats", styles["SubHead"]))
    caveats = [
        "Illiquidity premium: the Birkin's returns partly compensate for illiquidity. Selling takes 2–8 weeks vs. milliseconds for equities.",
        "Transaction costs: after 15–30% resale commission, net CAGR drops to approximately 3.5–4.5%.",
        "Storage and insurance: proper storage and coverage add ~1–2% annually.",
        "No income generation: unlike dividend stocks or coupon bonds, bags produce zero cash flow.",
        "Concentration risk: a single bag is a single asset with binary fashion and condition risk.",
    ]
    for c in caveats:
        elements.append(Paragraph(f"• {c}", styles["BodyText2"]))

    # ─── Conclusion ───
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Conclusion", styles["SectionHead"]))
    elements.append(Paragraph(
        "Are Birkins better than bonds? On a risk-adjusted basis, yes — the Birkin's Sharpe ratio of 1.21 "
        "surpasses not only investment-grade bonds but most equity benchmarks. Its near-zero correlation with "
        "equities makes it a theoretically compelling portfolio diversifier.",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        "Are Birkins better than stocks? In absolute terms, no. The S&P 500's 8.9% CAGR and 448% total "
        "return significantly outpace the Birkin's 5.7% and 205%.",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        "Are luxury handbags good investments? Only if they're Hermès. The Balenciaga and Paddington data "
        "demonstrate that \"luxury\" alone does not create investment value. Without Hermès's unique supply "
        "constraint and enduring cultural capital, handbags are depreciating consumer goods.",
        styles["BodyText2"]
    ))
    elements.append(Paragraph(
        "The Birkin is less an investment thesis and more a case study in the economics of scarcity, "
        "brand, and cultural permanence. The real lesson is about diversification: uncorrelated assets "
        "with positive expected returns improve risk-adjusted outcomes, even when they carry illiquidity "
        "and transaction costs.",
        styles["Callout"]
    ))

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "Data and code: "
        '<a href="https://github.com/mariahworkman/birkins-or-bonds" color="blue">'
        "github.com/mariahworkman/birkins-or-bonds</a>",
        styles["Footer"]
    ))

    # Build
    doc.build(elements)
    print(f"✅ Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_pdf()
