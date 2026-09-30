"""
Streamlit Multi-Page Application - Dedicated Terminology & User Guide
Curated for The Stock Valuation Radar (@theinvestingdean)
"""

import streamlit as st

st.set_page_config(
    page_title="Terminology & User Guide · Valuation Radar",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Styling ──
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .guide-container {
        max-width: 960px;
        margin: 0 auto;
        font-size: 15px;
        line-height: 1.65;
        color: #1E293B;
    }
    .guide-badge-buy {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .guide-badge-dca {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .guide-badge-wait {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }
    .guide-badge-ytd-green {
        background-color: #DCFCE7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    .guide-badge-ytd-red {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
        display: inline-block;
    }
    .dean-badge {
        background: linear-gradient(135deg, #10B981, #059669);
        color: #FFFFFF !important;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        text-decoration: none !important;
        letter-spacing: 0.02em;
        display: inline-block;
        box-shadow: 0 1px 3px rgba(16, 185, 129, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar Navigation Link ──
with st.sidebar:
    try:
        st.page_link("app.py", label="Back to Valuation Radar", icon="📈")
        st.markdown("---")
    except Exception:
        pass
    st.markdown(
        """
        <div style="font-size: 0.72rem; color: #64748B; line-height: 1.5;">
            <strong>The Stock Valuation Radar</strong><br>
            Reference Guide & Terminology Documentation.<br>
            Curated by <a href="https://www.instagram.com/theinvestingdean" target="_blank" class="dean-badge" style="font-size: 0.68rem; padding: 1px 6px;">@theinvestingdean</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Top Bar Link ──
col_link, col_space = st.columns([1, 3])
with col_link:
    try:
        st.page_link("app.py", label="← Back to Valuation Radar", icon="📈")
    except Exception:
        pass

# ── Main Header ──
st.title("📚 Terminology & User Guide")
st.markdown(
    """
    <p style="color: #64748B; font-size: 15px; margin-top: -8px; margin-bottom: 24px;">
      Comprehensive documentation of formulas, valuation corridors, quantitative indicators, and tactical execution systems.
    </p>
    """,
    unsafe_allow_html=True,
)

USER_GUIDE_MARKDOWN = r"""
<div class="guide-container">

---

## 1. Executive Overview & Investment Philosophy

### The Mission: Emotion-Free, Disciplined Investing
Most retail investors suffer from two destructive behavioral biases:
1. **FOMO (Fear Of Missing Out):** Aggressively buying near market peaks when prices are extended, hype is elevated, and valuation multiples are stretched.
2. **Panic Hesitation:** Freezing or selling during natural pullbacks, exactly when high-quality businesses are on sale at an attractive margin of safety.

**The Stock Valuation Radar** eliminates emotional decision-making. By calculating objective historical moving average corridors, forward earnings growth rates, and statistical volatility bands, the Radar provides a clear, quantitative signal for when to **accumulate**, when to **hold standard DCA**, and when to **exercise patience**.

---

## 2. The Traffic Light Valuation System

Every asset on the dashboard is continuously classified into one of three primary valuation states based on its price relative to its historical moving average corridor:

| Valuation Status | Visual Signal | Mathematical Condition | Strategic Action |
| :--- | :---: | :--- | :--- |
| **Buy Zone** | <span class="guide-badge-buy">🟢 BUY ZONE</span> | **Price $\le -5.0\%$** vs Historical Average Corridor | **Prime Accumulation.** Asset is historically discounted. Increase DCA allocation or deploy tactical dip-buying tranches. |
| **Standard DCA** | <span class="guide-badge-dca">🟡 STANDARD DCA</span> | **Price between $-5.0\%$ and $+10.0\%$** vs Historical Average | **Fair Value Corridor.** Proceed with routine automated DCA schedules. No need to pause or over-allocate. |
| **Wait for Pullback** | <span class="guide-badge-wait">🔴 WAIT FOR PULLBACK</span> | **Price $> +10.0\%$** vs Historical Average Corridor | **Overextended.** Elevated multiple expansion. Pause lump-sum purchases and let cash reserves build for mean-reversion pullbacks. |

> [!TIP]
> **Active Timeframe Selection:** You can toggle the baseline between the **90-Day Moving Average** (short-to-medium term swing valuation) and the **1-Year Moving Average** (long-term structural fair value) using the timeframe toggle at the top of the main dashboard.

---

## 3. Stock Card Metrics & Glossary

Each individual stock card features standardized, uniform metric tiles designed to provide instant multi-dimensional context.

### 💵 Price (USD / Local) & Performance Context
- **Live / Delayed Price:** Displayed in the primary currency of the stock listing (e.g. USD for US equities, GBX/GBP for London listings).
- **YTD Return Badge:** Renders as a styled pill badge (<span class="guide-badge-ytd-green">YTD +18.4%</span> or <span class="guide-badge-ytd-red">YTD -4.2%</span>) representing performance since the opening session of January 1st:
  $$\text{YTD Return (\%)} = \left( \frac{\text{Current Price} - \text{Year Open Close}}{\text{Year Open Close}} \right) \times 100$$
- **Daily Performance:** Absolute dollar/currency change alongside percentage change at the official close of regular trading:
  *Example:* `+$2.30 (+1.5%) at market close` or `-$4.61 (-1.29%) at market close`.
- **Extended-Hours Trading (Pre-Market / Post-Market):** When pre-market or post-market quotes are active, the card displays the raw extended-hours price and the net move from regular close:
  *Example:* `Pre-market price: $351.60 | -$1.24 (-0.35%)`.

---

### 🏔️ Distance to All-Time High (ATH)
Measures the current drawdown from the company's highest historical closing price across its entire lifetime dataset:
$$\text{Distance to ATH (\%)} = \left( \frac{\text{Current Price} - \text{Lifetime High}}{\text{Lifetime High}} \right) \times 100$$

- **$> -10\%$ (Green):** Normal market consolidation within striking distance of record highs.
- **$-10\%$ to $-25\%$ (Amber):** Healthy market correction. Often represents an attractive entry window for blue-chip compounders.
- **$< -25\%$ (Red):** Bear market territory / deep value drawdown. Requires fundamental verification to distinguish between temporary market dislocation vs permanent business impairment.

---

### 📊 Standard Deviation (50-Day & 252-Day) / Z-Score
Quantifies how many standard deviations ($\sigma$) the current price sits above or below its 50-day Simple Moving Average:
$$Z = \frac{\text{Current Price} - \text{SMA}_{50}}{\sigma_{50}}$$

- **$Z < -1.5\sigma$:** Statistically oversold. Price is stretched unusually far below its short-term mean, creating high rebound probability.
- **$-1.5\sigma \le Z \le +1.5\sigma$:** Normal random walk distribution around trend.
- **$Z > +1.5\sigma$:** Statistically overbought. Short-term momentum is stretched.

---

### ⚖️ Trailing P/E & Historical Fair Value Corridor
- **Trailing P/E (TTM):** Current Price divided by Trailing Twelve Month diluted earnings per share.
  $$\text{Trailing P/E} = \frac{\text{Current Price}}{\text{Trailing 12-Month EPS}}$$
- **Fair Value Corridor:** The historical moving average of the stock's price or P/E over the chosen timeframe (90-Day or 1-Year).
- **Upside / Downside to Fair Value:** The percentage move required for the stock to revert to its historical mean:
  $$\text{Upside to Fair Value (\%)} = \left( \frac{\text{Fair Value Target} - \text{Current Price}}{\text{Current Price}} \right) \times 100$$
  *Positive values (Green)* show upside potential to historical fair value; *negative values (Red)* show overvaluation.

---

## 4. 2-Year Forward PEG & EPS CAGR (AJ Financial Research Methodology)

Standard trailing P/E ratios look backward and fail to account for corporate reinvestment and rapid earnings expansion. The Valuation Radar implements the **AJ Financial Research 2-Year Forward PEG framework** to benchmark growth equities against consensus expectations.

### Mathematical Formulation

1. **Forward Price-to-Earnings (NTM P/E):**
   $$\text{Forward P/E} = \frac{\text{Current Price}}{\text{Next Twelve Months Consensus EPS (NTM EPS)}}$$

2. **2-Year Forward EPS Compound Annual Growth Rate (CAGR):**
   Estimates annual earnings growth between year 1 (NTM EPS) and year 2 (NTM+2 EPS):
   $$\text{EPS CAGR}_{2Y} = \left( \frac{\text{NTM+2 EPS}}{\text{NTM EPS}} \right)^{\frac{1}{2}} - 1$$

3. **2-Year Forward PEG Ratio:**
   Normalizes the forward earnings multiple against the annual growth rate:
   $$\text{PEG}_{2Y} = \frac{\text{Forward P/E}}{\text{EPS CAGR}_{2Y} \times 100}$$

### Valuation Tiers & Interpretation
- **$< 1.0$ — Exceptional Value:** Forward earnings growth exceeds the price multiple. Rare asymmetric upside.
- **$1.0 - 1.75$ — Fair Value (GARP):** Healthy Growth-At-A-Reasonable-Price. Premium business trading at a sensible multiple.
- **$1.75 - 2.5$ — High Valuation:** Multiple is elevated relative to growth. High vulnerability to market volatility or guidance revisions.
- **$> 2.5$ — Extreme Premium:** Stock is priced for flawless execution. Significant multiple compression risk if earnings growth moderates.

---

## 5. TID - Tactical DCA v1.0 System

The **TID Tactical DCA** engine translates quantitative volatility envelopes and liquidity absorption patterns into concrete dip-buying tiers.

### Bollinger Envelopes Structure (Lookback = 20 Sessions)
The system calculates a 20-day Simple Moving Average baseline and expands three standard deviation envelopes:
- **Baseline:** 20-day Simple Moving Average (SMA 20)
- **Corridor 2 ($-1.5\sigma$):** Standard DCA Accumulation Boundary
- **Corridor 1 ($-2.2\sigma$):** Heavy DCA Accumulation Boundary
- **Corridor 0 ($-3.0\sigma$):** Capitulation / Liquidity Flush Boundary

### Execution Tiers

| Tier | Volatility Level | Trigger Mechanism | Suggested DCA Allocation |
| :--- | :--- | :--- | :--- |
| **Tier 2** | **$-1.5\sigma$ Lower Band** | Price touches or penetrates the $-1.5\sigma$ band | **$1\times$ Standard DCA Allocation.** Routine accumulation. |
| **Tier 1** | **$-2.2\sigma$ Lower Band** | Price touches or penetrates the $-2.2\sigma$ band | **$2\times$ to $3\times$ Standard Allocation.** High-conviction dip buying. |
| **Tier 0** | **$-3.0\sigma$ Lower Band** | Price reaches extreme $-3.0\sigma$ liquidity flush | **Max Tactical Deployment.** Rare panic capitulation offering generational entry prices. |

### Technical Confirmation Filters
To prevent "catching falling knives", tactical signals are reinforced with price action confirmation:
1. **Volume Absorption:** Daily trading volume $> 1.3\times$ the 20-day moving average, signaling institutional buyers absorbing supply.
2. **Lower Wick Defense:** Daily candlestick exhibiting a lower shadow $\ge 40\%$ of the total bar range, demonstrating aggressive intraday buyer support.
3. **Bullish Reversal Candle:** A green closing candle following band penetration, confirming buyer control before capital deployment.

---

## 6. ETFs vs Individual Equities

The Valuation Radar automatically recognizes Exchange-Traded Funds (ETFs) such as `VUAG.L` (Vanguard S&P 500), `VWRP.L` (Vanguard FTSE All-World), and `SMGB.L` (VanEck Semiconductor).

Because index ETFs represent diversified baskets of hundreds of companies, single-stock metrics like EPS and PEG ratios are mathematically inapplicable. The dashboard dynamically swaps these tiles for ETF-specific metrics:
- **TER (Total Expense Ratio):** The annual management fee charged by the fund manager (e.g. 0.07% for VUAG). Lower fees allow more capital to compound over decades.
- **AUM (Assets Under Management):** The total dollar size of the fund, reflecting liquidity, institutional adoption, and low tracking error risk.

---

## 7. Interactive Tools & Productivity Features

- 🔍 **Quick Find Ticker Jumper:** Type or select any stock in the Quick Find bar to immediately jump to its detailed card without manual scrolling.
- ⛶ **Expand Chart Modal:** Tap the "Expand Chart" bar beneath any chart to open a full-screen, high-resolution modal with touch-enabled pinch-to-zoom and pan.
- 🎯 **Refocus Chart Button:** Double-click or tap the "Refocus" button to instantly restore the chart view back to the optimal 6-to-9 month window.
- 📸 **Export 4:5 Social Card:** Click the camera icon on any card to export a high-contrast 4:5 visual summary ready for Instagram or Twitter.
- ⏱️ **Timeframe Toggle (90-Day vs 1-Year):** Recalibrate the entire dashboard between short-term swing fair value and 1-year structural mean reversion.

---

## 8. Frequently Asked Questions (FAQ)

**Q: Why do some prices say "at market close" while others say "Pre-market price"?**  
*A: During regular trading hours (9:30 AM – 4:00 PM EST), prices reflect official exchange trading. After the close, the dashboard displays "at market close". During extended sessions (pre-market 4:00 AM – 9:30 AM EST and after-hours 4:00 PM – 8:00 PM EST), extended-hours quotes are shown.*

**Q: Should I completely stop buying when a stock is in "Wait for Pullback"?**  
*A: If you are an automated long-term monthly DCA investor, maintaining regular scheduled contributions is fine. However, "Wait for Pullback" warns against deploying large lump-sums or chasing hype. Let tactical cash accumulate until prices revert toward Standard DCA or the Buy Zone.*

**Q: How often does the data update?**  
*A: The dashboard pulls live market data via Yahoo Finance. Click the "Refresh Market Data" button in the sidebar or reload the page anytime to synchronize the latest quotes.*

</div>
"""

st.markdown(USER_GUIDE_MARKDOWN, unsafe_allow_html=True)
