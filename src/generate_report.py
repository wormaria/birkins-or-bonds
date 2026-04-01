"""
generate_report.py — Generate a polished PDF research report (v2).

v2 changes per review feedback:
  1. Lede addresses the 2022-2025 resale softness directly, not in footnotes
  2. Performance Summary table includes net-of-fee CAGR and Sharpe
  3. Portfolio simulation uses annual rebalancing (noted in text)
  4. Volatility caveat is explicit: interpolation suppresses variance
  5. Conclusion leads with practical limitations, theory is secondary
  6. Bonds (AGG) benchmarked throughout
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

DARK = HexColor("#1B1B1B")
TEAL = HexColor("#1B474D")
GOLD = HexColor("#C4883A")
MUTED = HexColor("#6B6B6B")
LIGHT_BG = HexColor("#F7F6F2")
BORDER = HexColor("#D4D1CA")
WHITE = HexColor("#FFFFFF")


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("ReportTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=28, leading=34,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=6))
    styles.add(ParagraphStyle("ReportSubtitle", parent=styles["Normal"],
        fontName="Helvetica", fontSize=13, leading=18,
        textColor=MUTED, alignment=TA_LEFT, spaceAfter=24))
    styles.add(ParagraphStyle("SectionHead", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=16, leading=22,
        textColor=TEAL, spaceBefore=24, spaceAfter=10))
    styles.add(ParagraphStyle("SubHead", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, leading=16,
        textColor=DARK, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("BodyText2", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, leading=15,
        textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=8))
    styles.add(ParagraphStyle("Callout", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10.5, leading=15,
        textColor=TEAL, alignment=TA_LEFT, spaceAfter=8, leftIndent=12))
    styles.add(ParagraphStyle("Caption", parent=styles["Normal"],
        fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=16))
    styles.add(ParagraphStyle("Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=MUTED, alignment=TA_CENTER))
    styles.add(ParagraphStyle("Footnote", parent=styles["Normal"],
        fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=MUTED, alignment=TA_LEFT, spaceAfter=2))
    return styles


def make_table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def add_chart(elements, filename, caption, styles, width=6.3*inch):
    img_path = IMG_DIR / filename
    if img_path.exists():
        from PIL import Image as PILImage
        with PILImage.open(str(img_path)) as pil_img:
            orig_w, orig_h = pil_img.size
        aspect = orig_h / orig_w
        img = Image(str(img_path), width=width, height=width * aspect)
        elements.append(img)
        elements.append(Paragraph(caption, styles["Caption"]))


def fn(num):
    """Superscript footnote marker."""
    return f'<super>{num}</super>'


def generate_pdf():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORT_DIR / "birkins_or_bonds_report.pdf"

    doc = SimpleDocTemplate(
        str(output_path), pagesize=letter,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        leftMargin=0.85*inch, rightMargin=0.85*inch,
        title="Birkins or Bonds: Luxury Handbags as Alternative Investments",
        author="Perplexity Computer",
    )

    styles = build_styles()
    elements = []

    # ─── Cover ───
    elements.append(Spacer(1, 0.4*inch))
    elements.append(HRFlowable(width="100%", thickness=2, color=TEAL))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Birkins or Bonds", styles["ReportTitle"]))
    elements.append(Paragraph(
        "An Empirical Analysis of Luxury Handbags as Alternative Investment Assets",
        styles["ReportSubtitle"]))
    elements.append(Paragraph("Mariah Workman  ·  March 2026", styles["Caption"]))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elements.append(Spacer(1, 14))

    # ─── Executive Summary — Issue #1: address the softness in the body ───
    elements.append(Paragraph("Executive Summary", styles["SectionHead"]))
    elements.append(Paragraph(
        f"In July 2025, Jane Birkin's original Hermès bag sold at Sotheby's Paris for over $10 million — "
        f"a 9,900% return on the ~$100,000 paid in 2000.{fn(1)} That headline obscures a more complicated "
        f"reality: by the time of that sale, the broader Birkin resale market had been cooling for three years. "
        f"According to Bernstein Research's Secondhand Pricing Tracker, the average resale premium for Birkin "
        f"and Kelly bags fell from 2.2× retail in 2022 to 1.4× by late 2025.{fn(2)} A standard Birkin 35 that "
        f"would have fetched ~$23,800 at the 2022 peak resells for ~$18,900 today — a 21% decline from the high.",
        styles["BodyText2"]))
    elements.append(Paragraph(
        "This report subjects the \"Birkins as investments\" thesis to quantitative analysis, benchmarking "
        "three luxury handbag models against both the <b>S&amp;P 500</b> and the <b>US Aggregate Bond Index (AGG)</b> "
        "over 2005–2025. We report both gross and <b>net-of-transaction-cost</b> returns, flag the data "
        "construction artifacts that inflate risk-adjusted metrics, and conclude that the practical case "
        "for handbags as portfolio diversifiers is far weaker than the theoretical one.",
        styles["BodyText2"]))
    elements.append(Paragraph(
        "Headline: the Birkin's gross Sharpe ratio of 1.21 drops to 0.73 after a 25% round-trip "
        "transaction cost — and even the gross figure is inflated by artificially smooth proxy data.",
        styles["Callout"]))

    # Footnotes
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>1</super> '
        '<a href="https://fortune.com/2025/12/17/gen-z-reality-check-birkin-resale-prices-slump-aspirational-luxury-slowdown/" color="blue">'
        'Fortune, "Gen Z\'s reality check: Birkin resale prices slump" (Dec 2025)</a></font>',
        styles["Footnote"]))
    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>2</super> '
        'Bernstein Research Secondhand Pricing Tracker, via '
        '<a href="https://fortune.com/2025/12/17/gen-z-reality-check-birkin-resale-prices-slump-aspirational-luxury-slowdown/" color="blue">'
        'Fortune (Dec 2025)</a>. Resale premium = auction price / retail cost.</font>',
        styles["Footnote"]))

    elements.append(PageBreak())

    # ─── Data & Methodology ───
    elements.append(Paragraph("Data &amp; Methodology", styles["SectionHead"]))
    elements.append(Paragraph("Data Sources", styles["SubHead"]))

    source_data = [
        ["Asset", "Source", "Type"],
        ["S&P 500", "Yahoo Finance (^GSPC)", "Real market data"],
        ["US Agg Bond (AGG)", "Yahoo Finance (AGG ETF)", "Real market data"],
        ["Hermès Birkin 35", "Knight Frank KFLII, Bernstein, auctions", "Proxy construction"],
        ["Balenciaga City", "Retail history, Fashionphile benchmarks", "Proxy construction"],
        ["Chloé Paddington", "Retail history, resale platform listings", "Proxy construction"],
        ["US CPI", "Federal Reserve Bank of Minneapolis", "Real data"],
    ]
    elements.append(make_table(source_data, col_widths=[1.3*inch, 2.6*inch, 1.5*inch]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Proxy Construction", styles["SubHead"]))
    elements.append(Paragraph(
        f"Handbag \"prices\" are mid-market resale estimates constructed by anchoring to known retail prices, "
        f"applying Knight Frank KFLII handbag component returns, calibrating to auction realized prices, and "
        f"adjusting for resale premium ratios from Bernstein Research.{fn(3)} Monthly values are linearly "
        f"interpolated between annual anchor points.",
        styles["BodyText2"]))

    # Issue #4: Volatility caveat — prominent, not buried
    elements.append(Paragraph("Critical Caveat: Interpolation Suppresses Volatility", styles["SubHead"]))
    elements.append(Paragraph(
        "Linear interpolation between annual anchor points mechanically smooths month-to-month "
        "price variation. The reported volatility figures for handbags — especially the Birkin's "
        "2.4% annualized — are <b>artifacts of this data construction</b>, not evidence of genuinely low "
        "price variance. Real transaction-level data, if it were available, would almost certainly show "
        "higher volatility. All Sharpe ratios and volatility comparisons involving handbag assets should "
        "be interpreted as lower bounds on risk, not precise measurements.",
        styles["BodyText2"]))

    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>3</super> '
        '<a href="https://www.knightfrank.com/wealthreport/2020-07-31-rise-in-handbag-opulence-the-knight-frank-luxury-investment-index" color="blue">'
        'Knight Frank, "Rise in Handbag Opulence" (KFLII 2020)</a></font>',
        styles["Footnote"]))

    elements.append(Paragraph("Other Limitations", styles["SubHead"]))
    for lim in [
        "Survivorship bias: only bags in good condition are resold; damaged/lost bags are invisible.",
        "Illiquidity: selling takes 2–8 weeks vs. milliseconds for equities or bonds.",
        "Transaction costs: 15–30% resale commission or 20–25% auction buyer's premium.",
        "Selection bias: we track iconic bags, not a random sample.",
        "No income: bags generate no dividends or coupons. S&P and AGG returns exclude "
        "dividends/coupons for comparability.",
    ]:
        elements.append(Paragraph(f"• {lim}", styles["BodyText2"]))

    elements.append(PageBreak())

    # ─── Results — Issue #2: net-of-fee metrics in the headline table ───
    elements.append(Paragraph("Results", styles["SectionHead"]))
    elements.append(Paragraph("Performance Summary — Gross and Net of Fees", styles["SubHead"]))

    perf_data = [
        ["Metric", "S&P 500", "US Agg\nBond", "Birkin\n(Gross)", "Birkin\n(Net 25%)", "Balenciaga\n(Net 25%)", "Paddington\n(Net 25%)"],
        ["CAGR", "8.9%", "3.1%", "5.7%", "4.2%", "−3.0%", "−2.9%"],
        ["Volatility*", "14.8%", "4.6%", "2.4%", "2.4%", "3.6%", "5.3%"],
        ["Sharpe", "0.47", "0.13", "1.21", "0.73", "−1.52", "−1.03"],
        ["Max Drawdown", "−52.6%", "−17.2%", "−21.8%", "−21.8%", "−53.8%", "−84.0%"],
        ["Total Return", "448%", "86%", "205%", "129%", "−45%", "−45%"],
    ]
    elements.append(make_table(perf_data,
        col_widths=[0.85*inch, 0.75*inch, 0.7*inch, 0.75*inch, 0.85*inch, 0.9*inch, 0.9*inch]))
    elements.append(Paragraph(
        "<i>*Handbag volatility is artificially low due to interpolation between annual data points. "
        "Net 25% = after deducting a 25% round-trip transaction cost (typical auction friction).</i>",
        styles["Caption"]))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"The gross Birkin Sharpe ratio of 1.21 is the number that appears in most popular press "
        f"coverage. But two adjustments materially change the picture: (1) after a 25% transaction "
        f"cost, the Sharpe falls to <b>0.73</b>; and (2) even that figure relies on a volatility "
        f"number (2.4%) that is suppressed by data smoothing. A more realistic volatility estimate "
        f"of 5–8% — still below equities — would push the net Sharpe into the 0.2–0.4 range, "
        f"roughly comparable to the S&amp;P 500.",
        styles["BodyText2"]))

    elements.append(Paragraph(
        f"The inclusion of the <b>US Aggregate Bond Index</b> directly answers the title question. "
        f"Bonds returned 3.1% CAGR with 4.6% volatility and a 17.2% maximum drawdown — a Sharpe of "
        f"0.13.{fn(4)} The Birkin beats bonds on both an absolute and risk-adjusted basis even after "
        f"fees. But bonds are liquid, income-generating, and can be bought in any size. The comparison "
        f"is not as straightforward as CAGR vs. CAGR.",
        styles["BodyText2"]))

    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>4</super> '
        'AGG total return from Yahoo Finance. Note: AGG price return understates true bond performance '
        'because it excludes coupon income. Actual total return with reinvested coupons would be higher.</font>',
        styles["Footnote"]))

    elements.append(Spacer(1, 6))
    add_chart(elements, "01_normalized_growth.png",
              "Figure 1: Growth of $100 invested in each asset class, 2005–2025. Bonds shown as dashed line. "
              "Source: Yahoo Finance, Knight Frank KFLII, resale platform data.", styles)

    # Issue #6: Birkin softness in the body
    elements.append(Paragraph("The 2022–2025 Correction", styles["SubHead"]))
    elements.append(Paragraph(
        f"The Birkin resale market peaked in 2022, when Bernstein Research reported average resale "
        f"premiums of 2.2× retail — meaning a bag purchased for $10,000 at Hermès resold for "
        f"~$22,200.{fn(5)} By late 2025, that premium had compressed to 1.4×. Several factors drove "
        f"the correction:",
        styles["BodyText2"]))
    for factor in [
        "Post-pandemic normalization of luxury demand after the 2020–2021 spending surge.",
        "Gen Z aspirational demand cooling as economic uncertainty increased.",
        "Increased secondary market supply as pandemic-era buyers liquidated.",
        "Hermès retail price increases (+44% since 2015) narrowing the arbitrage between retail and resale.",
    ]:
        elements.append(Paragraph(f"• {factor}", styles["BodyText2"]))
    elements.append(Paragraph(
        "This correction is not a data footnote — it is a structural feature of the asset class. "
        "The Birkin's 20-year track record includes multiple periods of premium compression, "
        "and the current softness should temper any extrapolation of past returns.",
        styles["BodyText2"]))

    elements.append(Paragraph(
        '<font size="7" color="#6B6B6B"><super>5</super> '
        '<a href="https://fortune.com/2025/12/17/gen-z-reality-check-birkin-resale-prices-slump-aspirational-luxury-slowdown/" color="blue">'
        'Fortune / Bernstein Research Secondhand Pricing Tracker (Dec 2025)</a></font>',
        styles["Footnote"]))

    elements.append(Paragraph("Drawdown Analysis", styles["SubHead"]))
    add_chart(elements, "04_drawdowns.png",
              "Figure 2: Peak-to-trough drawdowns for all five asset classes, 2005–2025.", styles)

    elements.append(Paragraph("Correlation Structure", styles["SubHead"]))
    elements.append(Paragraph(
        "The Birkin's monthly return correlation with the S&amp;P 500 is 0.06 and with bonds is 0.05 — "
        "essentially uncorrelated with both major asset classes. This is the theoretical basis for "
        "diversification. However, the practical value of low correlation is limited when the asset "
        "cannot be traded freely (see Discussion).",
        styles["BodyText2"]))
    add_chart(elements, "05_correlation_heatmap.png",
              "Figure 3: Correlation matrix of monthly returns across all asset classes.", styles, width=4.5*inch)

    elements.append(PageBreak())

    # Issue #3: Annual rebalancing, properly noted
    elements.append(Paragraph("Portfolio Simulation (Annual Rebalancing)", styles["SubHead"]))
    elements.append(Paragraph(
        "We simulate four allocations rebalanced <b>annually</b> (each January). Monthly rebalancing — "
        "the standard assumption in portfolio theory — is physically impossible for an asset that takes "
        "2–8 weeks to sell. Even annual rebalancing is optimistic; it assumes you can execute a handbag "
        "sale and reinvest proceeds within a calendar year.",
        styles["BodyText2"]))

    port_data = [
        ["Portfolio", "CAGR", "Volatility", "Sharpe", "Max DD"],
        ["100% S&P 500", "8.8%", "14.9%", "0.47", "−52.6%"],
        ["60/40 Stocks–Bonds", "6.8%", "9.4%", "0.48", "−31.8%"],
        ["60/40 Stocks–Birkin", "7.8%", "8.9%", "0.61", "−34.5%"],
        ["50/25/25 Mix", "6.9%", "7.7%", "0.58", "−27.8%"],
    ]
    elements.append(make_table(port_data, col_widths=[1.5*inch, 0.8*inch, 0.9*inch, 0.8*inch, 0.9*inch]))
    elements.append(Paragraph(
        "<i>Handbag transaction costs are NOT deducted from portfolio simulation returns. "
        "If a 25% round-trip cost were applied to each annual Birkin rebalancing, portfolio "
        "returns would be materially lower.</i>",
        styles["Caption"]))

    elements.append(Paragraph(
        "The 60/40 stocks–Birkin portfolio shows a Sharpe of 0.61 vs. 0.48 for the traditional "
        "stocks–bonds 60/40. But this comparison is misleading: (1) Birkin volatility is artificially "
        "low, (2) transaction costs are not deducted, and (3) annual rebalancing of an illiquid asset "
        "is impractical. A fairer comparison would add 2–3% per year in friction and use a higher "
        "volatility estimate, which would largely erase the Sharpe advantage.",
        styles["BodyText2"]))

    add_chart(elements, "07_portfolio_simulation.png",
              "Figure 4: Portfolio growth of $100 under annual rebalancing. "
              "Transaction costs not deducted from Birkin allocations.", styles)

    elements.append(PageBreak())

    # ─── Discussion ───
    elements.append(Paragraph("Discussion", styles["SectionHead"]))
    elements.append(Paragraph("What Drives Birkin Returns?", styles["SubHead"]))
    for d in [
        "Artificial scarcity: Hermès limits production and requires purchase history before offering a Birkin.",
        "Price inelasticity: annual retail increases of 5–8% are absorbed by deep global demand.",
        "Cultural permanence: the Birkin carries signaling value that transcends seasonal fashion.",
        "Authentication infrastructure: Rebag, Fashionphile, and Vestiaire provide market liquidity.",
        "Wealth concentration: demand for Veblen goods rises faster than supply as wealth concentrates.",
    ]:
        elements.append(Paragraph(f"• {d}", styles["BodyText2"]))

    elements.append(Paragraph("The Fashion Cycle Trap", styles["SubHead"]))
    elements.append(Paragraph(
        "The Balenciaga City and Chloé Paddington both lost ~27% gross (worse after fees) over 20 years. "
        "Both were iconic \"It bags\" that depreciated as fashion moved on. The Paddington lost 84% of "
        "its peak value before nostalgia partially recovered it. "
        "Trend-driven bags are consumption goods, not investment assets. Only bags with permanent brand "
        "moats — Hermès, certain Chanel classics — exhibit investment-like behavior.",
        styles["BodyText2"]))

    elements.append(PageBreak())

    # ─── Conclusion — Issue #5: lead with practical limitations ───
    elements.append(Paragraph("Conclusion", styles["SectionHead"]))

    elements.append(Paragraph("The Practical Case Is Weak", styles["SubHead"]))
    elements.append(Paragraph(
        "Despite favorable headline metrics, luxury handbags are impractical portfolio assets "
        "for most investors. The obstacles are structural, not incidental:",
        styles["BodyText2"]))
    for obs in [
        "<b>Transaction costs destroy returns.</b> A 25% round-trip cost reduces the Birkin's "
        "CAGR from 5.7% to 4.2% and its Sharpe from 1.21 to 0.73. For bags sold through auction "
        "houses (20–25% buyer's premium + seller's commission), the haircut is even larger.",
        "<b>Illiquidity is not a theoretical concern — it's a physical one.</b> You cannot rebalance "
        "a portfolio that includes a $20,000 handbag with the same frequency as one built from ETFs. "
        "Our simulation uses annual rebalancing, which is itself optimistic.",
        "<b>The low-volatility story is a data artifact.</b> Interpolating between annual anchor "
        "points mechanically suppresses variance. The Birkin's true monthly volatility is unknowable "
        "from public data but almost certainly higher than the 2.4% reported here.",
        "<b>No income.</b> Bonds pay coupons. Stocks pay dividends. Bags pay nothing. Over 20 years, "
        "foregone income compounds into a material opportunity cost.",
        "<b>Concentration risk.</b> A single bag is a single asset with binary condition and fashion risk. "
        "A diversified bond ETF holds thousands of securities.",
        "<b>The market is softening.</b> The 2022–2025 premium compression suggests the Birkin's best "
        "years may be behind it — or at least that extrapolating the 2010–2022 boom is risky.",
    ]:
        elements.append(Paragraph(f"• {obs}", styles["BodyText2"]))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("The Theoretical Case Is Real — But Narrow", styles["SubHead"]))
    elements.append(Paragraph(
        "The Birkin's near-zero correlation with equities and bonds is genuine and theoretically "
        "valuable. If transaction costs were lower, liquidity were higher, and price data were more "
        "transparent, a small Birkin allocation could improve a portfolio's efficient frontier. "
        "The 50/25/25 mix (stocks, bonds, Birkin) shows the best risk-adjusted path, with max "
        "drawdown of just 27.8% vs. 52.6% for pure equity.",
        styles["BodyText2"]))
    elements.append(Paragraph(
        "But this is a theoretical exercise. In practice, the friction costs, illiquidity, "
        "and data limitations make the Birkin more interesting as a case study in scarcity "
        "economics than as an actionable investment thesis.",
        styles["BodyText2"]))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Answering the Title Question", styles["SubHead"]))

    answer_style = ParagraphStyle("AnswerCell", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK)
    q_style = ParagraphStyle("QuestionCell", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=DARK)
    q_header = ParagraphStyle("QHeader", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=WHITE)
    a_header = ParagraphStyle("AHeader", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=WHITE)

    answer_data = [
        [Paragraph("Question", q_header), Paragraph("Answer", a_header)],
        [Paragraph("Are Birkins better than bonds?", q_style),
         Paragraph("On a gross CAGR basis, yes (5.7% vs. 3.1%). Net of 25% fees, "
         "still slightly better (4.2% vs. 3.1%). But bonds are liquid, "
         "income-generating, and infinitely divisible.", answer_style)],
        [Paragraph("Are Birkins better than stocks?", q_style),
         Paragraph("No. S&amp;P 500 delivers 8.9% CAGR with no transaction friction, "
         "full liquidity, and dividend income.", answer_style)],
        [Paragraph("Are luxury bags good investments?", q_style),
         Paragraph("Only Hermès. Balenciaga and Paddington both lost money. "
         "\"Luxury\" alone creates no investment value.", answer_style)],
    ]
    elements.append(make_table(answer_data, col_widths=[1.6*inch, 4.7*inch]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "The Birkin is less an investment thesis and more a case study in the economics of scarcity "
        "and cultural capital. The numbers are interesting. The practical barriers are prohibitive.",
        styles["Callout"]))

    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        'Data and code: '
        '<a href="https://github.com/wormaria/birkins-or-bonds" color="blue">'
        'github.com/wormaria/birkins-or-bonds</a>',
        styles["Footer"]))

    doc.build(elements)
    print(f"✅ Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_pdf()
