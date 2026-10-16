"""
Streamlit Multi-Page Application - Dedicated Beginner-Friendly User Guide
Curated for The Stock Valuation Radar (@theinvestingdean)
"""

import os
import base64
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Terminology & User Guide · Valuation Radar",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

def render_guide_image(filename, caption):
    # Check assets/ first, then fall back to root directory
    assets_path = os.path.join("assets", filename)
    if os.path.exists(assets_path):
        target_path = assets_path
    elif os.path.exists(filename):
        target_path = filename
    else:
        target_path = None

    if target_path:
        with open(target_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            
        # Pure HTML rendering completely bypasses Streamlit's fullscreen button
        html_img = f"""
        <div style="margin: 1rem 0;">
            <img src="data:image/png;base64,{encoded_string}" style="max-width: 320px; width: 100%; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size: 0.85rem; color: #64748B; margin-top: 8px; font-weight: 500;">
                {caption}
            </div>
        </div>
        """
        st.markdown(html_img, unsafe_allow_html=True)
    else:
        st.info(f"📸 Placeholder: Add `{filename}` to display here.")

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
section[data-testid="stSidebar"] .guide-btn {
    width: 100%;
    justify-content: center;
    box-sizing: border-box;
}

/* 1. Apply the dotted background to the entire app view */
[data-testid="stAppViewContainer"] {
    background-color: #FAFAFA !important;
    background-image: radial-gradient(#E2E8F0 1px, transparent 1px) !important;
    background-size: 20px 20px !important;
}

/* 2. Ensure the new bordered containers have a solid white background to stand out against the dots */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    margin-bottom: 1.5rem !important;
}

/* 3. Aggressively force hide ALL Streamlit image fullscreen buttons */
button[title="View fullscreen"],
[data-testid="StyledFullScreenButton"],
.stImage button {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* 4. Universal Badge & Pill Wrap Protection */
.guide-badge-buy, .guide-badge-dca, .guide-badge-wait,
.badge-green, .badge-amber, .badge-red, .badge-yellow,
.alloc-badge-green, .alloc-badge-amber, .alloc-badge-red, .alloc-badge-yellow,
span[style*="border-radius"] {
    white-space: nowrap !important;
    display: inline-block !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        """
        <a href="/" target="_self" class="guide-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            <span>Back to Valuation Dashboard</span>
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

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


# ── Section 1: How to Think About Investing ──
with st.container(border=True):
    st.markdown(
        """
## 1. How to Think About Investing

### Buying Stocks on Sale
Imagine your favorite trainers or gaming console. You wouldn't want to buy them when the price is at an all-time peak and everyone is hyping them up. You want to buy them when they go on sale!

The stock market works the exact same way:
- **The Mistake Most People Make:** They get excited and buy when prices have skyrocketed (FOMO - Fear Of Missing Out). Then, when prices drop, they panic and sell.
- **The Smart Way to Invest:** Keep calm, look for top-quality companies, and buy them when they are discounted.

**Dollar-Cost Averaging (DCA):** This means investing a set amount of money regularly (like once a month), no matter what the market is doing. The Valuation Radar helps you know when a stock is on sale so you can make the most of your money.
""",
        unsafe_allow_html=True,
    )


# ── Section 2: The Traffic Light System & Market Overview ──
overview_visual_html = """
<style>
.guide-section-box {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 18px 20px;
  margin-top: 18px;
  margin-bottom: 20px;
}
.guide-sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}
.guide-sub-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.05rem;
  font-weight: 800;
  color: #0F172A;
  letter-spacing: -0.01em;
}
.guide-sub-badge {
  font-size: 0.72rem;
  font-weight: 700;
  color: #854D0E;
  background-color: #FEF9C3;
  border: 1px solid #FDE047;
  padding: 2px 8px;
  border-radius: 9999px;
  white-space: nowrap;
}
.guide-bar-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
  margin-bottom: 14px;
}
.guide-bar-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 12px 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.guide-bar-card-green { border-left: 4px solid #16A34A; }
.guide-bar-card-amber { border-left: 4px solid #F59E0B; }
.guide-bar-card-red   { border-left: 4px solid #DC2626; }

.guide-pill-green {
  background: #DCFCE7;
  color: #15803D;
  border: 1px solid #16A34A;
  font-weight: 800;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
  text-transform: uppercase;
}
.guide-pill-amber {
  background: #FEF3C7;
  color: #B45309;
  border: 1px solid #FCD34D;
  font-weight: 800;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
  text-transform: uppercase;
}
.guide-pill-red {
  background: #FEE2E2;
  color: #DC2626;
  border: 1px solid #FCA5A5;
  font-weight: 800;
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
  text-transform: uppercase;
}

.guide-toggle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
  margin-top: 10px;
}
.guide-toggle-item {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 10px 12px;
}

.guide-exec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 14px;
}
.guide-exec-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 14px 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.guide-exec-card-yellow { border-left: 4px solid #EAB308; }
.guide-exec-card-green  { border-left: 4px solid #10B981; }
.guide-exec-card-red    { border-left: 4px solid #EF4444; }
.guide-exec-card-indigo { border-left: 4px solid #6366F1; }
</style>

<!-- Part 1: Horizontal Bar Chart -->
<div class="guide-section-box">
  <div class="guide-sub-header">
    <div class="guide-sub-title">
      <span>📊</span>
      <span>Price vs. Average Horizontal Bar Chart</span>
    </div>
    <span class="guide-sub-badge">Green at Top • Sorted by Value</span>
  </div>
  <div style="font-size: 0.86rem; color: #475569; line-height: 1.45;">
    At the top of the dashboard, the horizontal bar chart ranks every watched stock from best discount to most overextended:
  </div>

  <div class="guide-bar-list">
    <!-- Green -->
    <div class="guide-bar-card guide-bar-card-green">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="guide-pill-green">Top of Chart</span>
          <span class="badge-green" style="font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">● BUY ZONE</span>
          <span style="font-weight: 700; color: #15803D; font-size: 0.88rem;">Green Bars (Prime Accumulation)</span>
        </div>
        <span style="font-size: 0.74rem; font-weight: 700; color: #15803D; background: #F0FDF4; border: 1px dashed #86EFAC; padding: 2px 7px; border-radius: 4px;">&lt; -5% below average</span>
      </div>
      <div style="font-size: 0.82rem; color: #334155; line-height: 1.45;">
        <b>Deep Discounts:</b> Highlights assets currently trading at the deepest discounts below their historical baseline. The top of the chart is where you hunt for high-conviction value entries.
      </div>
    </div>

    <!-- Amber -->
    <div class="guide-bar-card guide-bar-card-amber">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="guide-pill-amber">Middle</span>
          <span class="badge-amber" style="font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">● STANDARD DCA</span>
          <span style="font-weight: 700; color: #B45309; font-size: 0.88rem;">Amber Bars (Fair-Value Mean)</span>
        </div>
        <span style="font-size: 0.74rem; font-weight: 700; color: #B45309; background: #FFFBEB; border: 1px dashed #FDE68A; padding: 2px 7px; border-radius: 4px;">-5% to +10% average</span>
      </div>
      <div style="font-size: 0.82rem; color: #334155; line-height: 1.45;">
        <b>Routine Scheduled DCA:</b> Assets trading right around their fair-value average. Great for steady monthly accumulation without overpaying.
      </div>
    </div>

    <!-- Red -->
    <div class="guide-bar-card guide-bar-card-red">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="guide-pill-red">Bottom</span>
          <span class="badge-red" style="font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">● WAIT FOR PULLBACK</span>
          <span style="font-weight: 700; color: #DC2626; font-size: 0.88rem;">Red Bars (Overextended)</span>
        </div>
        <span style="font-size: 0.74rem; font-weight: 700; color: #DC2626; background: #FEF2F2; border: 1px dashed #FECACA; padding: 2px 7px; border-radius: 4px;">&gt; +10% above average</span>
      </div>
      <div style="font-size: 0.82rem; color: #334155; line-height: 1.45;">
        <b>Wait for Pullback:</b> Assets stretched furthest into overextended territory. Elevated risk of short-term retracement—exercise discipline and wait for mean reversion.
      </div>
    </div>
  </div>

  <!-- Timeframe Toggle Box -->
  <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px; margin-top: 10px;">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px; margin-bottom: 6px;">
      <div style="display: flex; align-items: center; gap: 6px;">
        <span style="font-size: 1rem;">🔄</span>
        <span style="font-weight: 700; color: #0F172A; font-size: 0.86rem;">Master Timeframe Switch (Sidebar)</span>
      </div>
      <span style="font-size: 0.72rem; color: #64748B;">Toggle dynamically adapts all chart baselines</span>
    </div>
    <div class="guide-toggle-grid">
      <div class="guide-toggle-item">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
          <span style="font-weight: 700; color: #1E293B; font-size: 0.82rem;">⚡ 90-Day View:</span>
          <span style="font-size: 0.70rem; font-weight: 700; color: #4338CA; background: #EEF2FF; border: 1px solid #C7D2FE; padding: 1px 6px; border-radius: 4px;">Tactical Dips</span>
        </div>
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
          Use for tactical short-term dips, post-earnings pullbacks, and swing accumulation opportunities.
        </div>
      </div>
      <div class="guide-toggle-item">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
          <span style="font-weight: 700; color: #1E293B; font-size: 0.82rem;">📈 1-Year View:</span>
          <span style="font-size: 0.70rem; font-weight: 700; color: #065F46; background: #ECFDF5; border: 1px solid #A7F3D0; padding: 1px 6px; border-radius: 4px;">Macro Cycles</span>
        </div>
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
          Use for macro cyclical discounts on long-term compounders across an entire 52-week trading cycle.
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Part 2: Executive Market Highlights -->
<div class="guide-section-box" style="margin-top: 20px;">
  <div class="guide-sub-header">
    <div class="guide-sub-title">
      <span>📰</span>
      <span>Executive Market Highlights</span>
    </div>
    <span class="guide-sub-badge">Instant 4-Card Briefing</span>
  </div>
  <div style="font-size: 0.86rem; color: #475569; line-height: 1.45;">
    Directly below the chart, a 4-card executive briefing gives you an instant bird's-eye view of broader market conditions:
  </div>

  <div class="guide-exec-grid">
    <!-- Card 1: Basket Breadth -->
    <div class="guide-exec-card guide-exec-card-yellow">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
          <span style="font-size: 0.70rem; font-weight: 800; color: #854D0E; text-transform: uppercase; letter-spacing: 0.05em;">Basket Breadth</span>
          <span style="font-size: 0.95rem;">🌐</span>
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">Market Euphoria vs. Health</div>
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
          The percentage of tracked assets trading stretched above average. Identifies whether the broader market has a bullish or defensive bias.
        </div>
      </div>
      <div style="font-size: 0.72rem; font-weight: 600; color: #854D0E; margin-top: 10px; padding-top: 6px; border-top: 1px dashed #E2E8F0;">
        • Overheating & risk diagnostic
      </div>
    </div>

    <!-- Card 2: Top Value Opportunities -->
    <div class="guide-exec-card guide-exec-card-green">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
          <span style="font-size: 0.70rem; font-weight: 800; color: #047857; text-transform: uppercase; letter-spacing: 0.05em;">Top Value Ops</span>
          <span style="font-size: 0.95rem;">💎</span>
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">Deepest Corridor Discounts</div>
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
          Spotlights the 4 deepest corridor discounts available right now across your radar. Your prime candidates for capital deployment.
        </div>
      </div>
      <div style="font-size: 0.72rem; font-weight: 600; color: #047857; margin-top: 10px; padding-top: 6px; border-top: 1px dashed #E2E8F0;">
        • Prime accumulation targets
      </div>
    </div>

    <!-- Card 3: Most Overextended -->
    <div class="guide-exec-card guide-exec-card-red">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
          <span style="font-size: 0.70rem; font-weight: 800; color: #B91C1C; text-transform: uppercase; letter-spacing: 0.05em;">Most Overextended</span>
          <span style="font-size: 0.95rem;">⚠️</span>
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">Caution Required</div>
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
          The stocks trading furthest above normal value. Warns you against chasing green candles when risk of a pullback is elevated.
        </div>
      </div>
      <div style="font-size: 0.72rem; font-weight: 600; color: #B91C1C; margin-top: 10px; padding-top: 6px; border-top: 1px dashed #E2E8F0;">
        • Avoid buying at peak hype
      </div>
    </div>

    <!-- Card 4: Recent Tactical Signals -->
    <div class="guide-exec-card guide-exec-card-indigo">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
          <span style="font-size: 0.70rem; font-weight: 800; color: #4338CA; text-transform: uppercase; letter-spacing: 0.05em;">Tactical Signals</span>
          <span style="font-size: 0.95rem;">🚨</span>
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">Live Triggers (Last 7 Days)</div>
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
          Live alerts whenever a stock enters <b>Tier 1 (Standard DCA)</b>, <b>Tier 2 (Deeply Oversold)</b>, or <b>Tier 3 (Capitulation)</b> within the last 7 days.
        </div>
      </div>
      <div style="font-size: 0.72rem; font-weight: 600; color: #4338CA; margin-top: 10px; padding-top: 6px; border-top: 1px dashed #E2E8F0;">
        • Timely dip notifications
      </div>
    </div>
  </div>
</div>
"""

with st.container(border=True):
    st.markdown(
        """
## 2. The Traffic Light System & Market Overview

Every stock on your dashboard has a simple color status that tells you how its current price compares to its normal historical average:

| Status | What It Looks Like | What It Means in Plain English | What You Should Do |
| :--- | :---: | :--- | :--- |
| **Buy Zone** | <span class="guide-badge-buy">🟢 BUY ZONE</span> | Price is **more than 5% below** its normal average | **Prime buying time!** The stock is on sale. A great time to add to your investments. |
| **Standard DCA** | <span class="guide-badge-dca">🟡 STANDARD DCA</span> | Price is **between 5% below and 10% above** average | **Fair price.** Continue with your normal scheduled investments as usual. |
| **Wait for Pullback** | <span class="guide-badge-wait">🔴 WAIT FOR PULLBACK</span> | Price is **more than 10% above** its normal average | **Expensive!** The stock is stretched high. Be patient and wait for the price to cool down before buying. |
""",
        unsafe_allow_html=True,
    )
    st.html(overview_visual_html)


# ── Section 3: Smart DCA Allocator & Tranche Calculator ──
alloc_guide_html = """
<style>
.alloc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 24px;
}
.alloc-card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.alloc-step {
  font-size: 0.78rem;
  font-weight: 800;
  color: #854D0E;
  background-color: #FEF9C3;
  border: 1px solid #FDE047;
  padding: 2px 8px;
  border-radius: 9999px;
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  width: fit-content;
}
.alloc-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0F172A;
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}
.alloc-text {
  font-size: 0.90rem;
  color: #334155;
  line-height: 1.55;
}
.alloc-badge-green, .alloc-badge-amber, .alloc-badge-red, .alloc-badge-yellow {
  display: inline-block !important;
  white-space: nowrap !important;
  padding: 2px 7px;
  border-radius: 5px;
  font-weight: 700;
  font-size: 0.78rem;
  line-height: 1.25;
  vertical-align: middle;
}
.alloc-badge-green { background-color: #DCFCE7; color: #15803D; border: 1px solid #16A34A; }
.alloc-badge-amber { background-color: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; }
.alloc-badge-red { background-color: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; }
.alloc-badge-yellow { background-color: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; }
</style>

<div class="alloc-grid">
  <div class="alloc-card">
    <div>
      <div class="alloc-step">Step 1</div>
      <div class="alloc-title">💷 Set Budget & Dry Powder</div>
      <div class="alloc-text">
        Enter the cash amount you want to invest (e.g., <b>£500</b>) and pick your currency (<b>£</b>, <b>$</b>, <b>€</b>).<br><br>
        <b>Choose your strategy:</b><br>
        • <b>100% Fully Deployed:</b><br>
        Invests your entire budget today.<br><br>
        • <b>Hold 25% Dry Powder:</b><br>
        Deploys 75% now and reserves 25% cash for rare <span class="alloc-badge-amber">-2.2σ Deep Dips</span> or <span class="alloc-badge-red">-3.0σ Panics</span>.
      </div>
    </div>
  </div>

  <div class="alloc-card">
    <div>
      <div class="alloc-step">Step 2</div>
      <div class="alloc-title">🎯 Pick Your Targets (Caveat Filter)</div>
      <div class="alloc-text">
        Choose <b>only</b> the specific assets you wish to accumulate right now. All other watched stocks are ignored.<br><br>
        <b>Quick Presets:</b><br>
        • <span class="alloc-badge-yellow">⚡ Top 3 Conviction</span><br>
        Instantly selects your top 3 bargain opportunities.<br><br>
        • <span class="alloc-badge-yellow">🟢 All Buy Zone</span><br>
        Selects all stocks in discounted territory.
      </div>
    </div>
  </div>

  <div class="alloc-card">
    <div>
      <div class="alloc-step">Step 3</div>
      <div class="alloc-title">⚖️ Dynamic Tranche Weighting</div>
      <div class="alloc-text">
        Money is <b>not</b> divided evenly. The calculator weights every pound based on discount and quality:<br><br>
        • <span class="alloc-badge-green">● Buy Zone</span> stocks with <span class="alloc-badge-green">Score 7.5+</span> receive a <b>1.6x boosted Tranche 2</b> allocation.<br><br>
        • <span class="alloc-badge-amber">● Standard DCA</span> stocks receive routine scheduled Tranche 1 tranches.
      </div>
    </div>
  </div>

  <div class="alloc-card">
    <div>
      <div class="alloc-step">Step 4</div>
      <div class="alloc-title">🛡️ Valuation Guardrail (Strict Protection)</div>
      <div class="alloc-text">
        Active by default. Automatically allocates <b>£0.00 (0.0% / 0 shares)</b> to protect your capital:<br><br>
        • <span class="alloc-badge-red">Score &lt; 4.5</span> (Low Conviction)<br>
        • <span class="alloc-badge-red">● Wait for Pullback</span> (+1.5σ Overextended)<br><br>
        <b>100% of your capital</b> is redirected into genuine bargains at the top. Toggle off anytime to force a token buy.
      </div>
    </div>
  </div>
</div>
"""

alloc_table_html = """
<div style="overflow-x: auto; margin-top: 14px; border: 1.5px solid #E2E8F0; border-radius: 10px; background: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
  <div style="background-color: #F8FAFC; padding: 10px 14px; border-bottom: 1.5px solid #E2E8F0; font-size: 0.85rem; font-weight: 800; color: #0F172A; display: flex; justify-content: space-between; align-items: center;">
    <span>📋 Visual Example: £500 Budget Allocation with Valuation Guardrail Active</span>
    <span style="font-size: 0.72rem; font-weight: 700; color: #15803D; background-color: #DCFCE7; border: 1px solid #16A34A; padding: 2px 8px; border-radius: 6px;">🛡️ 3 Approved · 2 Protected</span>
  </div>
  <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.84rem;">
    <thead>
      <tr style="background-color: #F8FAFC; border-bottom: 2px solid #E2E8F0; font-size: 0.74rem; color: #475569; text-transform: uppercase; letter-spacing: 0.04em;">
        <th style="padding: 10px 12px;">Asset</th>
        <th style="padding: 10px 8px;">Status</th>
        <th style="padding: 10px 8px;">Conviction</th>
        <th style="padding: 10px 8px; text-align: right;">Weight</th>
        <th style="padding: 10px 8px; text-align: right;">Cash Allocation</th>
        <th style="padding: 10px 8px; text-align: right;">Est. Shares</th>
        <th style="padding: 10px 12px;">Execution Strategy</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid #F1F5F9;">
        <td style="padding: 10px 12px; font-weight: 700; color: #0F172A;">NVDA<br><span style="font-weight: 400; font-size: 0.74rem; color: #64748B;">NVIDIA</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">● Standard DCA</span></td>
        <td style="padding: 10px 8px;"><span style="background: #DCFCE7; color: #15803D; border: 1px solid #16A34A; padding: 2px 7px; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">⚡ 8.5 / 10</span></td>
        <td style="padding: 10px 8px; text-align: right; font-weight: 700; color: #1E293B;">43.3%</td>
        <td style="padding: 10px 8px; text-align: right; font-weight: 800; color: #0F172A; font-size: 0.92rem;">£216.72</td>
        <td style="padding: 10px 8px; text-align: right; color: #475569; font-weight: 600;">~1.00 shs</td>
        <td style="padding: 10px 12px; font-size: 0.78rem; color: #334155;"><b>Tranche 1:</b> Routine DCA schedule</td>
      </tr>
      <tr style="border-bottom: 1px solid #F1F5F9;">
        <td style="padding: 10px 12px; font-weight: 700; color: #0F172A;">AMZN<br><span style="font-weight: 400; font-size: 0.74rem; color: #64748B;">Amazon.com</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">● Standard DCA</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">⚡ 7.1 / 10</span></td>
        <td style="padding: 10px 8px; text-align: right; font-weight: 700; color: #1E293B;">33.7%</td>
        <td style="padding: 10px 8px; text-align: right; font-weight: 800; color: #0F172A; font-size: 0.92rem;">£168.45</td>
        <td style="padding: 10px 8px; text-align: right; color: #475569; font-weight: 600;">~0.66 shs</td>
        <td style="padding: 10px 12px; font-size: 0.78rem; color: #334155;"><b>Tranche 1:</b> Routine DCA schedule</td>
      </tr>
      <tr style="border-bottom: 1px solid #F1F5F9;">
        <td style="padding: 10px 12px; font-weight: 700; color: #0F172A;">GOOG<br><span style="font-weight: 400; font-size: 0.74rem; color: #64748B;">Alphabet</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">● Standard DCA</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">⚡ 5.4 / 10</span></td>
        <td style="padding: 10px 8px; text-align: right; font-weight: 700; color: #1E293B;">23.0%</td>
        <td style="padding: 10px 8px; text-align: right; font-weight: 800; color: #0F172A; font-size: 0.92rem;">£114.83</td>
        <td style="padding: 10px 8px; text-align: right; color: #475569; font-weight: 600;">~0.33 shs</td>
        <td style="padding: 10px 12px; font-size: 0.78rem; color: #334155;"><b>Tranche 1:</b> Routine DCA schedule</td>
      </tr>
      <tr style="border-bottom: 1px solid #F1F5F9; background-color: #FFFDFD;">
        <td style="padding: 10px 12px; font-weight: 700; color: #0F172A;">META<br><span style="font-weight: 400; font-size: 0.74rem; color: #64748B;">Meta Platforms</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">● Wait for Pullback</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">⚡ 5.1 / 10</span></td>
        <td style="padding: 10px 8px; text-align: right; color: #94A3B8; font-weight: 500;">0.0%</td>
        <td style="padding: 10px 8px; text-align: right; color: #94A3B8; font-weight: 600;">£0.00</td>
        <td style="padding: 10px 8px; text-align: right; color: #94A3B8; font-weight: 500;">0.00 shs</td>
        <td style="padding: 10px 12px; font-size: 0.78rem; color: #DC2626;"><span style="font-weight: 700;">🛑 Hold Off:</span> Overextended (+1.5σ). Wait for pullback before buying.</td>
      </tr>
      <tr style="border-bottom: 1px solid #F1F5F9; background-color: #FFFDFD;">
        <td style="padding: 10px 12px; font-weight: 700; color: #0F172A;">TSLA<br><span style="font-weight: 400; font-size: 0.74rem; color: #64748B;">Tesla</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; padding: 2px 7px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;">● Standard DCA</span></td>
        <td style="padding: 10px 8px;"><span style="background: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; padding: 2px 7px; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">⚡ 3.9 / 10</span></td>
        <td style="padding: 10px 8px; text-align: right; color: #94A3B8; font-weight: 500;">0.0%</td>
        <td style="padding: 10px 8px; text-align: right; color: #94A3B8; font-weight: 600;">£0.00</td>
        <td style="padding: 10px 8px; text-align: right; color: #94A3B8; font-weight: 500;">0.00 shs</td>
        <td style="padding: 10px 12px; font-size: 0.78rem; color: #DC2626;"><span style="font-weight: 700;">🛑 Hold Off:</span> Low Conviction (3.9 &lt; 4.5). Wait for setup to improve.</td>
      </tr>
    </tbody>
  </table>
</div>
"""

with st.container(border=True):
    st.markdown(
        """
<div style="background: linear-gradient(135deg, #FDE047 0%, #FACC15 100%); border: 1.5px solid #EAB308; border-radius: 12px; padding: 14px 20px; color: #1F2937; display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
  <div style="display: flex; align-items: center; gap: 10px;">
    <span style="font-size: 1.4rem;">🎯</span>
    <span style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.01em;">3. Smart DCA Allocator & Tranche Calculator</span>
  </div>
  <span style="font-size: 0.75rem; font-weight: 800; color: #854D0E; background-color: #FEF9C3; border: 1px solid #FDE047; padding: 3px 10px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">Capital Deployment Engine</span>
</div>

Instead of guessing how much money to invest into each stock every month, the **Smart DCA Allocator** does the math for you. It translates your custom cash budget into an exact, disciplined purchase plan based on **Valuation Corridors** and **⚡ Radar Conviction Scores**.
""",
        unsafe_allow_html=True,
    )
    st.html(alloc_guide_html)
    st.html(alloc_table_html)


# ── Section 4: Stock Card Metrics & The ⚡ Radar Conviction Score ──
with st.container(border=True):
    st.markdown(
        """
## 4. Stock Card Metrics & The ⚡ Radar Conviction Score

Every stock card synthesizes real-time technical stretch, growth-adjusted valuation, and Wall Street institutional sentiment into simple, actionable visual metrics.

### ⚡ Radar Conviction Score (1.0 to 10.0)

Positioned prominently in the top-right header of each stock card, the composite **Radar Conviction Score** gives you an instant quantitative snapshot of each opportunity from **1.0 to 10.0**:

* **7.5 – 10.0** <span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 700; border: 1px solid #16A34A;">⚡ Score: 8.5 / 10</span> **High Conviction — Prime buying opportunity!** High-conviction alignment across standard deviation discount, attractive PEG growth valuation, and strong Wall Street analyst backing.
* **4.5 – 7.4** <span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 700; border: 1px solid #FCD34D;">⚡ Score: 6.0 / 10</span> **Moderate / Watch — Fair price or mixed signals.** Good for your regular scheduled dollar-cost averaging (DCA), but wait for dips before making outsized purchases.
* **1.0 – 4.4** <span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 700; border: 1px solid #FCA5A5;">⚡ Score: 3.2 / 10</span> **Low Conviction / Avoid — Stretched or expensive.** Warns that a stock is technically overbought, has an expensive PEG multiple, or lacks analyst upside. Be patient and wait for a pullback.

<div style="background-color: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 12px; padding: 18px 20px; margin-top: 18px; margin-bottom: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px;">
    <div style="display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 1.2rem;">⚡</span>
      <span style="font-weight: 800; font-size: 0.98rem; color: #0F172A;">How the Conviction Score is Calculated (Card Metrics Breakdown)</span>
    </div>
    <span style="background-color: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; padding: 3px 10px; border-radius: 9999px; font-weight: 800; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em;">Composite Formula</span>
  </div>
  <p style="font-size: 0.86rem; color: #475569; margin-bottom: 14px; line-height: 1.5;">
    Hovering over the <b>⚡ Score</b> badge on any stock card reveals its live mathematical breakdown. The score is quantitatively computed from <b>four core metrics</b> displayed directly across the card:
  </p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
    <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 12px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 800; font-size: 0.86rem; color: #0F172A;">📏 Standard Deviation</span>
        <span style="background: #DCFCE7; color: #15803D; border: 1px solid #16A34A; padding: 1px 7px; border-radius: 4px; font-weight: 800; font-size: 0.74rem;">40% Weight</span>
      </div>
      <div style="font-size: 0.80rem; color: #64748B; line-height: 1.45;">Measures 50-day price stretch. Rewards stocks trading deep in oversold discount territory below average.</div>
    </div>
    <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 12px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 800; font-size: 0.86rem; color: #0F172A;">🚀 2Y Forward PEG</span>
        <span style="background: #DCFCE7; color: #15803D; border: 1px solid #16A34A; padding: 1px 7px; border-radius: 4px; font-weight: 800; font-size: 0.74rem;">30% Weight</span>
      </div>
      <div style="font-size: 0.80rem; color: #64748B; line-height: 1.45;">Compares valuation to projected profit growth. Rewards companies growing faster than their price (&lt; 1.0).</div>
    </div>
    <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 12px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 800; font-size: 0.86rem; color: #0F172A;">🎯 12M Analyst Target</span>
        <span style="background: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; padding: 1px 7px; border-radius: 4px; font-weight: 800; font-size: 0.74rem;">15% Weight</span>
      </div>
      <div style="font-size: 0.80rem; color: #64748B; line-height: 1.45;">Tracks 12-month Wall Street price targets. Rewards high projected upside percentage.</div>
    </div>
    <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 12px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-weight: 800; font-size: 0.86rem; color: #0F172A;">🏛️ Wall Street Consensus</span>
        <span style="background: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; padding: 1px 7px; border-radius: 4px; font-weight: 800; font-size: 0.74rem;">15% Weight</span>
      </div>
      <div style="font-size: 0.80rem; color: #64748B; line-height: 1.45;">Aggregates institutional analyst ratings (1.0 to 5.0 scale). Rewards unanimous "Strong Buy" backing.</div>
    </div>
  </div>
</div>

---

### 💵 Stock Price & Daily Performance
- **Stock Price:** The current live price of a single share of the stock.
- **Daily Performance:** Real-time gain or loss and percentage change during the trading session (e.g. `+$2.30 (+1.5%)` or `-$4.61 (-1.29%)`).

---

### 📅 YTD Return (Year-to-Date)
- **Definition:** The profit or loss the stock has made since January 1st of the current year.
- **<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Green Badge</span>:** The stock has gained value this year.
- **<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Red Badge</span>:** The stock has lost value this year.
""",
        unsafe_allow_html=True,
    )
    render_guide_image("guide_ytd.png", "YTD Return Metric")

    st.markdown(
        """
---

### 🏔️ Distance to All-Time High (ATH)
- **Definition:** The highest price the stock has ever reached in its history.
- **What the colors tell you:**
  - **<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Red (Near ATH)</span>:** The stock is trading very close to its record highs. Proceed with caution, as it is relatively expensive.
  - **<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Amber (Moderate Pullback)</span>:** The stock has pulled back from its highs, offering a standard dip.
  - **<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Green (Deep Discount)</span>:** The stock is significantly below its record highs, offering a wide margin of safety and a cheaper entry price.
""",
        unsafe_allow_html=True,
    )
    render_guide_image("guide_ath.png", "Distance to ATH Metric")

    st.markdown(
        """
---

### 📏 Standard Deviation
- **Definition:** This measures how far the stock's price has stretched away from its normal **baseline average**.
- **How to read the score:**
  - **-1.2 or lower** (<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Oversold</span>): The stock is **oversold** below its normal average (a good buying opportunity).
  - **Between -1.2 and +1.2** (<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Neutral</span>): The stock is trading right within its **normal average range**.
  - **+1.2 or higher** (<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Overbought</span>): The stock is **overbought** and may soon drop back down.
""",
        unsafe_allow_html=True,
    )
    render_guide_image("guide_zscore.png", "Standard Deviation Metric")

    st.markdown(
        """
---

### ⚖️ Forward P/E & Fair Value
- **Forward P/E Ratio (Price-to-Earnings):** Shows how much you are paying today for every £1 or $1 the company is **expected to make in profit over the next 12 months**.
  - **Under 20.0** (<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Attractive</span>): The stock is cheap relative to its expected earnings.
  - **Between 20.0 and 35.0** (<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Moderate</span>): The stock is fairly priced or trades at a standard growth premium.
  - **Over 35.0** (<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">High Multiple</span>): The stock is expensive. The market has very high expectations for its future.
- **Fair Value Corridor:** The stock's normal average price over the last 90 days or 1 year. Upside shows how much the stock could rise to return back to this normal average.
""",
        unsafe_allow_html=True,
    )
    render_guide_image("guide_pe.png", "Forward P/E Metric")

    st.markdown(
        """
---

### 🚀 2-Year Forward PEG Ratio
- **What it is:** This compares the price of the stock to how fast its profits are expected to grow over the next 2 years.
- **How to read the score:**
  - **Under 1.0 (<span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">Great Value</span>):** The company's profits are growing faster than its price. A true bargain!
  - **Between 1.0 and 1.75 (<span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">Fair Value</span>):** The stock is fairly priced for its expected growth.
  - **Over 1.75 (<span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">Expensive</span>):** The stock is pricey. It expects perfection, making it vulnerable to drops if growth slows down.
""",
        unsafe_allow_html=True,
    )
    render_guide_image("guide_peg.png", "PEG Ratio Metric")

    st.markdown(
        """
---

### 🏛️ Wall Street Consensus & Analyst Score

* **12-Month Analyst Target:** What professional Wall Street researchers predict the stock will be worth one year from now, showing the potential percentage gain or loss.
* **Definition:** The aggregated consensus rating compiled from institutional equity research analysts (e.g., Goldman Sachs, Morgan Stanley, JPMorgan) actively covering the stock.
* **How the 1.0 to 5.0 Score Works (Lower is Better):**
  * **1.0 - 1.5** <span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 4px; font-weight: 700; border: 1px solid #16A34A;">Strong Buy</span>: Overwhelming institutional conviction; analysts forecast significant outperformance.
  * **1.6 - 2.5** <span style="background-color: #F0FDF4; color: #16A34A; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #86EFAC;">Buy</span>: General bullish bias across covering investment banks.
  * **2.6 - 3.5** <span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #FCD34D;">Hold</span>: Neutral outlook; analysts expect the stock to perform in line with the broader market.
  * **3.6 - 5.0** <span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 4px; font-weight: 600; border: 1px solid #FCA5A5;">Sell / Underperform</span>: Rare bearish rating; analysts recommend trimming or exiting positions.
* **How to Use with the Radar:** Look for confluence. When high-quality stocks enter the **Buy Zone (-1.5σ to -2.2σ)** while maintaining a **Strong Buy** or **Buy** rating, it confirms that institutional long-term conviction remains intact despite short-term price drops.
""",
        unsafe_allow_html=True,
    )
    render_guide_image("guide_consensus.png", "Wall Street Consensus Metric")


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
        (-1.5, "#22C55E", "dash", "-1.5σ Line: Tier 1 (Standard DCA)"),
        (-2.2, "#F59E0B", "dash", "-2.2σ Line: Tier 2 (Deeply Oversold)"),
        (-3.0, "#DC2626", "dash", "-3.0σ Line: Tier 3 (Capitulation)"),
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
        text="<b>🟢 TIER 1: STANDARD DCA</b><br>Crosses -1.5σ",
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
        text="<b>🟡 TIER 2: DEEPLY OVERSOLD</b><br>Wick touches -2.2σ",
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
        text="<b>🔴 TIER 3: CAPITULATION</b><br>Intraday wick to -3.0σ",
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
            title="Valuation Deviation (Standard Deviation)",
            fixedrange=True,
        ),
        showlegend=False,
    )

    return fig


# ── Section 5: Valuation Corridors & The Dip-Buying System ──
with st.container(border=True):
    st.markdown(
        """
## 5. Valuation Corridors & The Dip-Buying System

Stocks naturally move up and down around their historical average price:
- **Median Line (Middle):** The stock's normal average price where it usually trades.
- When market dips or temporary bad news push the price below this average, it creates clear, discounted buying zones.
""",
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        render_corridor_simulation(),
        use_container_width=True,
        config={
            "staticPlot": True,
            "displayModeBar": False
        }
    )

    st.markdown(
        """
### The Three Buying Tiers

| Buying Tier & Dashboard Badge | Where Price Sits on the Chart | What It Means | What to Do |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Standard Dip)**<br><span style="background-color: #DCFCE7; color: #15803D; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #16A34A;">🟢 Standard DCA</span> | Price touches the **-1.5 line** | The stock is slightly discounted below its normal average. | Good time for your regular scheduled DCA purchase. |
| **Tier 2 (Deep Dip)**<br><span style="background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCD34D;">🟡 Deeply Oversold</span> | Price reaches the **-2.0 or -2.2 line** | The stock is heavily discounted. | Great value! Consider investing double your normal amount. |
| **Tier 3 (Extreme Panic)**<br><span style="background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; border: 1px solid #FCA5A5;">🔴 Capitulation</span> | Price drops to the **-3.0 line** | The stock has experienced a severe crash or market panic. | Rare generational bargain. Maximum buying opportunity. |

### How to Confirm a Bounce Before Buying (2-Step Takeaway)
To avoid catching a falling knife, let the market prove it has bottomed:
1. **Look for a Bottom Wick:** The price dropped during the day, but strong buyers quickly pushed it back up before the close.
2. **Wait for a Green Day:** Let the stock finish the day higher than it opened. This proves buyers have fully taken back control.
""",
        unsafe_allow_html=True,
    )


# ── Section 6: Step-by-Step: How to Evaluate Any Stock ──
eval_html = """
<style>
.eval-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 16px;
  margin-bottom: 24px;
}
.eval-card {
  background-color: #FFFFFF;
  border: 1.5px solid #E2E8F0;
  border-radius: 12px;
  padding: 18px 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.eval-step {
  font-size: 0.78rem;
  font-weight: 800;
  color: #854D0E;
  background-color: #FEF9C3;
  border: 1px solid #FDE047;
  padding: 2px 8px;
  border-radius: 9999px;
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  width: fit-content;
}
.eval-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0F172A;
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}
.eval-text {
  font-size: 0.90rem;
  color: #334155;
  line-height: 1.55;
}
.badge-green, .badge-amber, .badge-red, .badge-yellow {
  display: inline-block !important;
  white-space: nowrap !important;
  padding: 2px 7px;
  border-radius: 5px;
  font-weight: 700;
  font-size: 0.78rem;
  line-height: 1.25;
  vertical-align: middle;
}
.badge-green { background-color: #DCFCE7; color: #15803D; border: 1px solid #16A34A; }
.badge-amber { background-color: #FEF3C7; color: #D97706; border: 1px solid #FCD34D; }
.badge-red { background-color: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; }
.badge-yellow { background-color: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; }
</style>

<div class="eval-grid">
  <div class="eval-card">
    <div>
      <div class="eval-step">Step 1</div>
      <div class="eval-title">⚡ The Quick Filter (Conviction Score)</div>
      <div class="eval-text">
        Glance at the <b>Radar Conviction Score</b> in the top right of the stock card:<br><br>
        • <span class="badge-green">⚡ 7.5 – 10.0</span> <b>High Conviction:</b><br>
        Prime value setup. High priority for capital.<br><br>
        • <span class="badge-amber">⚡ 4.5 – 7.4</span> <b>Moderate:</b><br>
        Fair price. Good for standard scheduled DCA.<br><br>
        • <span class="badge-red">⚡ 1.0 – 4.4</span> <b>Low Conviction:</b><br>
        Stretched or weak. Be patient and wait.<br><br>
        <i>💡 Beginner rule: If it's not green or amber, pause and wait for a better entry!</i>
      </div>
    </div>
  </div>

  <div class="eval-card">
    <div>
      <div class="eval-step">Step 2</div>
      <div class="eval-title">🎯 The "When" (Valuation Corridor)</div>
      <div class="eval-text">
        Check the <b>Standard Deviation</b> and Status Badge:<br><br>
        • <span class="badge-red">● Wait for Pullback</span> <b>(+1.5σ)</b><br>
        <b>Avoid:</b> Price is stretched. Wait for the hype to cool down.<br><br>
        • <span class="badge-green">● Buy Zone</span> <b>(-1.5σ)</b><br>
        <b>Accumulate:</b> Discounted dip. Prime entry for scheduled DCA.<br><br>
        • <span class="badge-amber">🟡 Deeply Oversold</span> <b>(-2.2σ)</b><br>
        • <span class="badge-red">🔴 Capitulation</span> <b>(-3.0σ)</b><br>
        <b>Rare bargains:</b> Generational panic. Maximum buying opportunity.
      </div>
    </div>
  </div>

  <div class="eval-card">
    <div>
      <div class="eval-step">Step 3</div>
      <div class="eval-title">⚖️ The "Why" (Fundamental Backing)</div>
      <div class="eval-text">
        Confirm company quality supports the discount:<br><br>
        • <b>2-Year Forward PEG Ratio:</b><br>
        Seek <span class="badge-green">&lt; 1.0 Undervalued</span> or <span class="badge-amber">1.0 – 1.75 Fair Value</span>.<br>
        Avoid <span class="badge-red">&gt; 1.75 High Multiple</span>.<br><br>
        • <b>Wall Street Consensus:</b><br>
        Look for institutional backing rated <span class="badge-green">Strong Buy</span> or <span class="badge-green">Buy</span> with solid positive <b>12-Month Target Upside</b>.
      </div>
    </div>
  </div>

  <div class="eval-card">
    <div>
      <div class="eval-step">Step 4</div>
      <div class="eval-title">💷 The "Action" (Smart DCA Allocator)</div>
      <div class="eval-text">
        Eliminate guesswork and emotion from position sizing:<br><br>
        • Open the <b>Smart DCA Allocator</b> (Section 3).<br><br>
        • Enter your cash budget (e.g. £500) and pick your targets.<br><br>
        • The engine auto-weights your cash, gives a <b>1.6x boost</b> to Buy Zone bargains, and relies on the <span class="badge-green">🛡️ Valuation Guardrail</span> to assign <b>£0.00</b> to overextended or low-conviction assets.
      </div>
    </div>
  </div>
</div>
"""

with st.container(border=True):
    st.markdown(
        """
## 6. Step-by-Step: How to Evaluate Any Stock

With the composite **⚡ Radar Conviction Score (1.0 to 10.0)**, evaluating any stock on your radar takes under 30 seconds. Whether you are a beginner or an intermediate investor, follow this 4-step framework before placing any order:
""",
        unsafe_allow_html=True,
    )
    st.html(eval_html)


# ── Section 7: Helpful Dashboard Tools ──
with st.container(border=True):
    st.markdown(
        """
## 7. Helpful Dashboard Tools

- 🔍 **Quick Find Bar:** Type any stock ticker (or select from the dropdown) in the Quick Find bar to jump straight to its card without scrolling through your entire radar.
- ⛶ **Interactive Full-Screen Charts:** Tap the **Expand** button under any chart or click the chart's fullscreen icon to open an interactive full-screen modal with mobile pinch-to-zoom and crosshair hover details.
""",
        unsafe_allow_html=True,
    )


# ── Section 8: Frequently Asked Questions (FAQ) ──
with st.container(border=True):
    st.markdown(
        """
## 8. Frequently Asked Questions (FAQ)

**Q: What are the main US stock market hours?**
* All times are in **UK Time**: The official US market is open from **2:30 PM to 9:00 PM (UK Time)**. Before 2:30 PM is pre-market, and after 9:00 PM is post-market.

**Q: Why does the Smart DCA Allocator give £0.00 to some of my selected stocks?**
* This is the **🛡️ Valuation Guardrail** in action. If a stock currently has a Low Conviction Score (< 4.5) or is overextended in *Wait for Pullback*, the system protects your cash by giving it £0.00 and redirecting 100% of those funds into your highest-conviction bargain assets. If you ever want to force a token buy anyway, simply toggle off the Guardrail at the top of the calculator.

**Q: Why does a stock say "Wait for Pullback" if Wall Street rates it a "Strong Buy"?**
* Wall Street analyst targets look out **12 months into the future**, whereas the Valuation Radar tracks **current price stretch over 50 days**. Even if a company has great long-term prospects, buying when price is overextended (+1.5σ or higher) increases your risk of suffering a short-term correction. Be patient and wait for the pullback.

**Q: What should I do if a stock triggers "Capitulation (-3.0σ)"?**
* Capitulation (-3.0σ) is a rare, generational buying opportunity caused by severe panic selling or market corrections. However, never dump your entire cash reserve at once. Scale in with your first tranche, and look for daily price stabilization before deploying further capital.

**Q: Should I use the 90-Day or 1-Year timeframe toggle on the bar chart?**
* Use **90-Day** for tactical, swing-style dip buying (capturing quick earnings pullbacks and monthly dips). Use **1-Year** for macro DCA accumulation into secular long-term winners at major cyclical discounts.

**Q: Should I stop investing if a stock is in "Wait for Pullback"?**
* If you invest automatically every month for the next 10+ years, sticking to your routine is fine. But do not dump big lumps of cash into a stock while it is red. Wait for it to pull back into Standard DCA or the Buy Zone.

**Q: How often does the market data update?**
* Live prices refresh automatically. You can click the **"Refresh Market Data"** button in the sidebar anytime to synchronize the freshest numbers from the exchange.
""",
        unsafe_allow_html=True,
    )
