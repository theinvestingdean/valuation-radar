"""
Streamlit Multi-Page Application - Dedicated Beginner-Friendly User Guide
Curated for The Stock Valuation Radar (@theinvestingdean)
"""

import os
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
        font-size: 16px;
        line-height: 1.7;
        color: #1E293B;
    }
    .guide-badge-buy {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .guide-badge-dca {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .guide-badge-wait {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
    }
    .guide-badge-green {
        background-color: #DCFCE7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        display: inline-block;
    }
    .guide-badge-amber {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        display: inline-block;
    }
    .guide-badge-red {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
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
            Beginner's Guide & Terminology.<br>
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
    <p style="color: #64748B; font-size: 16px; margin-top: -8px; margin-bottom: 24px;">
      A simple, beginner-friendly guide to understanding the dashboard, spotting great buying opportunities, and investing with confidence.
    </p>
    """,
    unsafe_allow_html=True,
)

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
- **<span class="guide-badge-green">Green Badge</span>:** The stock has gained value this year.
- **<span class="guide-badge-red">Red Badge</span>:** The stock has lost value this year.

---

### 🏔️ Distance to All-Time High (ATH)
- **Definition:** The highest price the stock has ever reached in its history.
- **What the colors tell you:**
  - **<span class="guide-badge-red">Red (Near ATH)</span>:** The stock is trading very close to its record highs. Proceed with caution, as it is relatively expensive.
  - **<span class="guide-badge-amber">Amber (Moderate Pullback)</span>:** The stock has pulled back from its highs, offering a standard dip.
  - **<span class="guide-badge-green">Green (Deep Discount)</span>:** The stock is significantly below its record highs, offering a wide margin of safety and a cheaper entry price.

---

### 📏 Standard Deviation (Z-Score)
- **Definition:** This measures how far the stock's price has stretched away from its normal average.
- **How to read the score:**
  - A score of **-1.5** means the stock is **heavily discounted** (a good buying opportunity).
  - A score near **0** means it is trading right at its **normal average**.
  - A score of **+1.5** means the stock is **overstretched** and may soon drop back down.

---

### 🏷️ Trailing P/E & Fair Value
- **P/E Ratio (Price-to-Earnings):** Shows how much you are paying for every £1 or $1 the company makes in profit. A lower number generally means you are getting more profit for your money.
- **Fair Value Corridor:** The stock's normal average price over the last 90 days or 1 year. Upside shows how much the stock could rise to return back to this normal average.

---

### 🚀 2-Year Forward PEG Ratio
- **What it is:** This compares the price of the stock to how fast its profits are expected to grow over the next 2 years.
- **How to read the score:**
  - **Under 1.0 (<span class="guide-badge-green">Great Value</span>):** The company's profits are growing faster than its price. A true bargain!
  - **Between 1.0 and 1.75 (<span class="guide-badge-amber">Fair Value</span>):** The stock is fairly priced for its expected growth.
  - **Over 1.75 (<span class="guide-badge-red">Expensive</span>):** The stock is pricey. It expects perfection, making it vulnerable to drops if growth slows down.

---

### 🎯 12-Month Analyst Target
- What professional Wall Street researchers predict the stock will be worth one year from now, showing the potential percentage gain or loss.

---

### ⚡ RSI (Momentum Gauge)
- Think of RSI like a speedometer from 0 to 100:
  - **Under 30 (Oversold):** The stock has been sold off too fast and is ready to bounce back up.
  - **Between 30 and 70 (Normal):** A calm, steady trend.
  - **Over 70 (Overbought):** The stock has rocketed up too quickly and needs to take a breather.

---

## 4. Valuation Corridors & The Dip-Buying System

Stocks naturally move up and down around their historical average price:
- **Median Line (Middle):** The stock's normal average price where it usually trades.
- When market dips or temporary bad news push the price below this average, it creates clear, discounted buying zones.

</div>
""",
    unsafe_allow_html=True,
)

# ── Bollinger Bands Visual Aid ──
img_candidates = ["bollinger_guide.png", "pages/bollinger_guide.png"]
img_path = next((p for p in img_candidates if os.path.exists(p)), None)

if img_path:
    st.image(img_path, caption="Visual guide to the Valuation Corridors (-1.5, -2.0, and Median)")
else:
    st.image("bollinger_guide.png", caption="Visual guide to the Valuation Corridors (-1.5, -2.0, and Median)")

# ── Section 4 Breakdown & Final Sections ──
st.markdown(
    """
<div class="guide-container">

### The Three Buying Tiers

| Buying Tier & Dashboard Badge | Where Price Sits on the Chart | What It Means | What to Do |
| :--- | :--- | :--- | :--- |
| **Tier 2 (Standard Dip)**<br><span class="guide-badge-green">🟢 Standard DCA</span> | Price touches the **-1.5 line** | The stock is slightly discounted below its normal average. | Good time for your regular scheduled DCA purchase. |
| **Tier 1 (Deep Dip)**<br><span class="guide-badge-amber">🟡 Deeply Oversold</span> | Price reaches the **-2.0 or -2.2 line** | The stock is heavily discounted. | Great value! Consider investing double your normal amount. |
| **Tier 0 (Extreme Panic)**<br><span class="guide-badge-red">🔴 Capitulation</span> | Price drops to the **-3.0 line** | The stock has experienced a severe crash or market panic. | Rare generational bargain. Maximum buying opportunity. |

### How to Confirm a Bounce Before Buying
To avoid buying while the price is still falling like a falling rock, look for these three easy clues:
1. **Volume Spike:** A huge surge in trading activity showing big funds are stepping in to buy.
2. **Long Bottom Wick:** The price dropped during the day, but strong buyers immediately pushed it back up before the close.
3. **Green Candle:** The day closes higher than it opened, proving the buyers have taken back control.

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
