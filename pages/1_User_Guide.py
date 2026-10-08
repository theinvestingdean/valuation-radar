"""
Streamlit Multi-Page Application - Dedicated Beginner-Friendly User Guide
Curated for The Stock Valuation Radar (@theinvestingdean)
"""

import os
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Terminology & User Guide · Valuation Radar",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Main Header ---
st.markdown("""
<style>
/* Hide native Streamlit multipage sidebar navigation */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Signature Yellow Pill Guide Buttons */
.guide-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: #FDE047;
    color: #1F2937 !important;
    font-weight: 700;
    font-size: 14px;
    padding: 8px 16px;
    border-radius: 8px;
    text-decoration: none !important;
    border: 1px solid #EAB308;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
    cursor: pointer;
}
.guide-btn:hover {
    background-color: #FACC15;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
    text-decoration: none !important;
    color: #1F2937 !important;
}
</style>
""", unsafe_allow_html=True)

header_html = """
<div style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 32px; margin-top: 8px;">
    <div style="display: flex; align-items: center; gap: 14px;">
        <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; filter: drop-shadow(0px 2px 3px rgba(99,102,241,0.2));">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
        <h1 style="margin: 0; padding: 0; font-size: 2.5rem; font-weight: 800; color: #0F172A; letter-spacing: -0.015em;">Terminology & User Guide</h1>
    </div>
    <p style="color: #64748B; font-size: 1.05rem; margin-top: 8px; margin-bottom: 16px; line-height: 1.5;">
      A simple, beginner-friendly guide to understanding the dashboard, spotting great buying opportunities, and investing with confidence.
    </p>
    <div>
        <a href="/" target="_self" class="guide-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            <span>Back to Valuation Dashboard</span>
        </a>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ── Section 1 & 2 Markdown ──
st.markdown(
    """
<div class="guide-container">

---

## 1. How to Think About Investing

### Buying Stocks on Sale
Imagine your favorite trainers or gaming console. You wouldn't want to buy them when the price is at an all-time peak and everyone is hyping them up. You want to buy them when they go on sale!

The stock market works the exact same way:
- **The Mistake Most People Make:** They get excited and buy when prices have skyrocketed (FOMO - Fear Of Missing Out). Then, when prices drop, they panic and sell.
- **The Smart Way to Invest:** Keep calm, look for top-quality companies, and buy them when they are discounted.

**Dollar-Cost Averaging (DCA):** This means investing a set amount of money regularly (like once a month), no matter what the market is doing. The Valuation Radar helps you know when a stock is on sale so you can make the most of your money.

---

## 2. The Traffic Light System

Every stock on your dashboard has a simple color status that tells you how its current price compares to its normal historical average:

| Status | What It Looks Like | What It Means in Plain English | What You Should Do |
| :--- | :---: | :--- | :--- |
| **Buy Zone** | <span class="guide-badge-buy">🟢 BUY ZONE</span> | Price is **more than 5% below** its normal average | **Prime buying time!** The stock is on sale. A great time to add to your investments. |
| **Standard DCA** | <span class="guide-badge-dca">🟡 STANDARD DCA</span> | Price is **between 5% below and 10% above** average | **Fair price.** Continue with your normal scheduled investments as usual. |
| **Wait for Pullback** | <span class="guide-badge-wait">🔴 WAIT FOR PULLBACK</span> | Price is **more than 10% above** its normal average | **Expensive!** The stock is stretched high. Be patient and wait for the price to cool down before buying. |

> **Tip:** You can switch between the **90-Day Average** (short-term swings) and the **1-Year Average** (long-term trend) using the toggle button at the top of the main dashboard.

---

## 3. Stock Card Metrics Made Simple

Every stock card shows key figures that give you the full story behind the price. Here is what each one means:

### 💵 Price & Market Hours (UK Time)
- **Stock Price:** The current price of a single share of the stock.
- **Daily Performance:** How much money and percentage the stock went up or down during normal market hours.  
  *Example:* `+$2.30 (+1.5%) at market close` or `-$4.61 (-1.29%) at market close`.
- **UK Market Hours to Remember:**
  - **Standard Market Hours:** **2:30 PM to 9:00 PM (UK Time)** — This is when the main US stock exchanges are open.
  - **Pre-Market:** **Before 2:30 PM (UK Time)** — Early trading before the official market opens.
  - **Post-Market:** **After 9:00 PM (UK Time)** — Late trading after the official market closes.

---

### 📅 YTD Return (Year-to-Date)
- **Definition:** The profit or loss the stock has made since January 1st of the current year.
- **<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Green Badge</span>:** The stock has gained value this year.
- **<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Red Badge</span>:** The stock has lost value this year.

---

### 🏔️ Distance to All-Time High (ATH)
- **Definition:** The highest price the stock has ever reached in its history.
- **What the colors tell you:**
  - **<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Red (Near ATH)</span>:** The stock is trading very close to its record highs. Proceed with caution, as it is relatively expensive.
  - **<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Amber (Moderate Pullback)</span>:** The stock has pulled back from its highs, offering a standard dip.
  - **<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Green (Deep Discount)</span>:** The stock is significantly below its record highs, offering a wide margin of safety and a cheaper entry price.

---

### 📏 Standard Deviation (Z-Score)
- **Definition:** This measures how far the stock's price has stretched away from its normal **50-day baseline average**.
- **How to read the score:**
  - **-1.5 or lower** (<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Discounted</span>): The stock is **heavily discounted** (a good buying opportunity).
  - **Near 0** (<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Normal</span>): The stock is trading right at its **normal average**.
  - **+1.5 or higher** (<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Overstretched</span>): The stock is **overstretched** and may soon drop back down.

---

### ⚖️ Forward P/E & Fair Value
  - **Forward P/E Ratio (Price-to-Earnings):** Shows how much you are paying today for every £1 or $1 the company is **expected to make in profit over the next 12 months**.
    - **Under 20.0** (<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Attractive</span>): The stock is cheap relative to its expected earnings.
    - **Between 20.0 and 35.0** (<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Moderate</span>): The stock is fairly priced or trades at a standard growth premium.
    - **Over 35.0** (<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">High Multiple</span>): The stock is expensive. The market has very high expectations for its future.
  - **Fair Value Corridor:** The stock's normal average price over the last 90 days or 1 year. Upside shows how much the stock could rise to return back to this normal average.

---

### 🚀 2-Year Forward PEG Ratio
- **What it is:** This compares the price of the stock to how fast its profits are expected to grow over the next 2 years.
- **How to read the score:**
  - **Under 1.0 (<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Great Value</span>):** The company's profits are growing faster than its price. A true bargain!
  - **Between 1.0 and 1.75 (<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Fair Value</span>):** The stock is fairly priced for its expected growth.
  - **Over 1.75 (<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Expensive</span>):** The stock is pricey. It expects perfection, making it vulnerable to drops if growth slows down.

---

### 🎯 12-Month Analyst Target
- What professional Wall Street researchers predict the stock will be worth one year from now, showing the potential percentage gain or loss.

---

### ⚡ RSI (Momentum Gauge)
- Think of RSI like a speedometer from 0 to 100:
  - **Under 30:** <span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Oversold</span> The stock has been sold off too fast and is ready to bounce back up.
  - **Between 30 and 70:** <span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Normal</span> A calm, steady trend.
  - **Over 70:** <span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Overbought</span> The stock has rocketed up too quickly and needs to take a breather.

---

### 🏛️ Wall Street Consensus & Analyst Score

* **Definition:** The aggregated consensus rating compiled from institutional equity research analysts (e.g., Goldman Sachs, Morgan Stanley, JPMorgan) actively covering the stock.
* **How the 1.0 to 5.0 Score Works (Lower is Better):**
  * **1.0 - 1.5** <span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 4px; font-weight: 700; border: 1px solid #16A34A;">Strong Buy</span>: Overwhelming institutional conviction; analysts forecast significant outperformance.
  * **1.6 - 2.5** <span style="background-color: #F0FDF4; color: #16A34A; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #86EFAC;">Buy</span>: General bullish bias across covering investment banks.
  * **2.6 - 3.5** <span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #FCD34D;">Hold</span>: Neutral outlook; analysts expect the stock to perform in line with the broader market.
  * **3.6 - 5.0** <span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #FCA5A5;">Sell / Underperform</span>: Rare bearish rating; analysts recommend trimming or exiting positions.
* **How to Use with the Radar:** Look for confluence. When high-quality stocks enter the **Buy Zone (-1.5σ to -2.2σ)** while maintaining a **Strong Buy** or **Buy** rating, it confirms that institutional long-term conviction remains intact despite short-term price drops.

---

## 4. Valuation Corridors & The Dip-Buying System

Stocks naturally move up and down around their historical average price:
- **Median Line (Middle):** The stock's normal average price where it usually trades.
- When market dips or temporary bad news push the price below this average, it creates clear, discounted buying zones.

</div>
""",
    unsafe_allow_html=True,
)

def render_corridor_simulation():
  # 1. Base trend path (peaks at +2.3, troughs at -3.1)
  n_bars = 45
  x_steps = np.linspace(0, 2 * np.pi, n_bars)
  trend = 2.6 * np.sin(x_steps) - 0.4

  # 2. Build synthetic OHLC candles following the trend
  dates = [f"Day {i+1}" for i in range(n_bars)]
  opens, highs, lows, closes = [], [], [], []

  prev_close = trend[0] - 0.2
  for i in range(n_bars):
    op = prev_close
    # Introduce realistic daily variance around the trajectory
    cl = trend[i] + np.random.uniform(-0.15, 0.15)
    body_min, body_max = min(op, cl), max(op, cl)

    # Extra lower wick on Capitulation (near day 33) and Oversold
    lower_wick_boost = (
        0.35 if (i in [18, 19, 32, 33]) else np.random.uniform(0.05, 0.2)
    )
    hi = body_max + np.random.uniform(0.05, 0.2)
    lo = body_min - lower_wick_boost

    opens.append(op)
    closes.append(cl)
    highs.append(hi)
    lows.append(lo)
    prev_close = cl

  fig = go.Figure()

  # 3. Add Corridor Zones (Background rects)
  fig.add_hrect(
      y0=2.2,
      y1=3.8,
      fillcolor="rgba(239, 68, 68, 0.12)",
      layer="below",
      line_width=0,
  )
  fig.add_hrect(
      y0=1.5,
      y1=2.2,
      fillcolor="rgba(239, 68, 68, 0.05)",
      layer="below",
      line_width=0,
  )
  fig.add_hrect(
      y0=-1.5,
      y1=-2.2,
      fillcolor="rgba(34, 197, 94, 0.08)",
      layer="below",
      line_width=0,
  )
  fig.add_hrect(
      y0=-2.2,
      y1=-3.0,
      fillcolor="rgba(245, 158, 11, 0.10)",
      layer="below",
      line_width=0,
  )
  fig.add_hrect(
      y0=-3.0,
      y1=-4.0,
      fillcolor="rgba(239, 68, 68, 0.12)",
      layer="below",
      line_width=0,
  )

  # 4. Add Corridor Reference Lines
  corridors = [
      (2.2, "#DC2626", "dash", "+2.2σ Line (Extreme Overbought)"),
      (1.5, "#EF4444", "dash", "+1.5σ Line (Overextended / Wait)"),
      (0.0, "#64748B", "solid", "Median Line (Normal Fair Value)"),
      (-1.5, "#22C55E", "dash", "-1.5σ Line: Tier 2 (Standard DCA)"),
      (-2.2, "#F59E0B", "dash", "-2.2σ Line: Tier 1 (Deeply Oversold)"),
      (-3.0, "#DC2626", "dash", "-3.0σ Line: Tier 0 (Capitulation)"),
  ]
  for y_val, color, dash, label in corridors:
    fig.add_hline(
        y=y_val,
        line=dict(color=color, width=1.5, dash=dash),
        annotation_text=f"  {label}",
        annotation_position="right",
        annotation_font=dict(size=11, color=color, family="sans-serif"),
    )

  # 5. Plot Synthetic Candlesticks
  fig.add_trace(
      go.Candlestick(
          x=dates,
          open=opens,
          high=highs,
          low=lows,
          close=closes,
          increasing_line_color="#22C55E",
          decreasing_line_color="#EF4444",
          name="Stock Price",
      )
  )

  # 6. Retain Key Tier Callout Annotations
  fig.add_annotation(
      x=dates[11],
      y=highs[11],
      text="<b>🔴 EXTREME OVERBOUGHT</b><br>Touches +2.2σ",
      showarrow=True,
      arrowhead=2,
      arrowcolor="#DC2626",
      ax=-55,
      ay=-35,
      bgcolor="#FFFFFF",
      bordercolor="#DC2626",
      borderwidth=1.5,
      font=dict(size=10, color="#1F2937"),
  )
  fig.add_annotation(
      x=dates[24],
      y=lows[24],
      text="<b>🟢 TIER 2: STANDARD DCA</b><br>Crosses -1.5σ",
      showarrow=True,
      arrowhead=2,
      arrowcolor="#22C55E",
      ax=-50,
      ay=-35,
      bgcolor="#FFFFFF",
      bordercolor="#22C55E",
      borderwidth=1.5,
      font=dict(size=10, color="#1F2937"),
  )
  fig.add_annotation(
      x=dates[27],
      y=lows[27],
      text="<b>🟡 TIER 1: DEEPLY OVERSOLD</b><br>Wick touches -2.2σ",
      showarrow=True,
      arrowhead=2,
      arrowcolor="#F59E0B",
      ax=-60,
      ay=35,
      bgcolor="#FFFFFF",
      bordercolor="#F59E0B",
      borderwidth=1.5,
      font=dict(size=10, color="#1F2937"),
  )
  fig.add_annotation(
      x=dates[33],
      y=lows[33],
      text="<b>🟠 TIER 0: CAPITULATION</b><br>Intraday wick to -3.0σ",
      showarrow=True,
      arrowhead=2,
      arrowcolor="#DC2626",
      ax=45,
      ay=35,
      bgcolor="#FFFFFF",
      bordercolor="#DC2626",
      borderwidth=1.5,
      font=dict(size=10, color="#1F2937"),
  )

  fig.update_layout(
      height=550,
      margin=dict(l=20, r=220, t=30, b=30),
      plot_bgcolor="#FFFFFF",
      paper_bgcolor="#FFFFFF",
      dragmode=False,
      xaxis=dict(
          showgrid=True,
          gridcolor="#F1F5F9",
          showticklabels=False,
          fixedrange=True,
          rangeslider_visible=False,
      ),
      yaxis=dict(
          showgrid=True,
          gridcolor="#F1F5F9",
          zeroline=False,
          range=[-3.8, 3.2],
          title="Valuation Deviation (Z-Score)",
          fixedrange=True,
      ),
      showlegend=False,
  )

  return fig

with st.container(border=True):
    st.plotly_chart(
        render_corridor_simulation(),
        use_container_width=True,
        config={
            "staticPlot": True,
            "displayModeBar": False
        }
    )


# ── Section 4 Breakdown & Final Sections ──
st.markdown(
    """
<div class="guide-container">

### The Three Buying Tiers

| Buying Tier & Dashboard Badge | Where Price Sits on the Chart | What It Means | What to Do |
| :--- | :--- | :--- | :--- |
| **Tier 2 (Standard Dip)**<br><span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">🟢 Standard DCA</span> | Price touches the **-1.5 line** | The stock is slightly discounted below its normal average. | Good time for your regular scheduled DCA purchase. |
| **Tier 1 (Deep Dip)**<br><span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">🟡 Deeply Oversold</span> | Price reaches the **-2.0 or -2.2 line** | The stock is heavily discounted. | Great value! Consider investing double your normal amount. |
| **Tier 0 (Extreme Panic)**<br><span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">🔴 Capitulation</span> | Price drops to the **-3.0 line** | The stock has experienced a severe crash or market panic. | Rare generational bargain. Maximum buying opportunity. |

### How to Confirm a Bounce Before Buying (2-Step Takeaway)
To avoid catching a falling knife, let the market prove it has bottomed:
1. **Look for a Bottom Wick:** The price dropped during the day, but strong buyers quickly pushed it back up before the close.
2. **Wait for a Green Day:** Let the stock finish the day higher than it opened. This proves buyers have fully taken back control.

---

## 5. Helpful Dashboard Tools

- 🔍 **Quick Find:** Type any stock ticker in the Quick Find bar to jump straight to its card without scrolling.
- ⛶ **Expand Chart:** Tap the Expand button under any chart to open a full-screen view with pinch-to-zoom on your phone.
- 🎯 **Refocus Chart:** Tap Refocus to reset the chart back to the perfect 6-to-9 month view.
- 📸 **Export 4:5 Card:** Tap the camera icon on any stock card to download a clean image ready to share on Instagram or Twitter.
- ⏱️ **Timeframe Toggle:** Switch between 90-Day and 1-Year valuation averages with a single click.

---

## 6. Frequently Asked Questions (FAQ)

**Q: What are the main stock market hours?**  
*A: All times are in **UK Time**! The official US market is open from **2:30 PM to 9:00 PM (UK Time)**. Before 2:30 PM is pre-market, and after 9:00 PM is post-market.*

**Q: Should I stop investing if a stock is in "Wait for Pullback"?**  
*A: If you invest automatically every month for the next 10 years, sticking to your routine is fine. But do not dump big lumps of cash into a stock while it is red. Wait for it to pull back into Standard DCA or the Buy Zone.*

**Q: How often does the market data update?**  
*A: Live from Yahoo Finance! You can click the "Refresh Market Data" button in the sidebar anytime to synchronize the freshest numbers.*

</div>
""",
    unsafe_allow_html=True,
)
