"""
The Volatility Dashboard
Clean, modern light-theme Streamlit dashboard tracking quantitative valuation
corridors, mean-reversion, all-time highs, and Bollinger Band price volatility
across semiconductors and tech.
Curated by @theinvestingdean
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests

# ─────────────────────────────────────────────
# DEFAULT CURATED BASKET (@theinvestingdean)
# Edit this dictionary anytime to customize the default stocks shown to all visitors:
# ─────────────────────────────────────────────
DEFAULT_TICKERS = {
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "META": "Meta Platforms",
    "GOOG": "Alphabet",
    "TSLA": "Tesla",
    "AMZN": "Amazon",
}
TICKERS = DEFAULT_TICKERS

# Backend ticker routing mapping (e.g. resolve SMSN.L to London IOB SMSN.IL ~5,110 USD)
TICKER_FETCH_MAPPING = {
    "SMSN.L": "SMSN.IL",
}

# TradingView symbol routing for institutional analyst targets and scanner queries
TRADINGVIEW_EXCHANGE_MAP = {
    # US Tech & Semiconductors
    "NVDA": "NASDAQ:NVDA",
    "AAPL": "NASDAQ:AAPL",
    "MSFT": "NASDAQ:MSFT",
    "META": "NASDAQ:META",
    "GOOG": "NASDAQ:GOOG",
    "GOOGL": "NASDAQ:GOOGL",
    "TSLA": "NASDAQ:TSLA",
    "AMZN": "NASDAQ:AMZN",
    "AMD": "NASDAQ:AMD",
    "AVGO": "NASDAQ:AVGO",
    "MU": "NASDAQ:MU",
    "ORCL": "NYSE:ORCL",
    "PLTR": "NASDAQ:PLTR",
    "TSM": "NYSE:TSM",
    "ASML": "NASDAQ:ASML",
    "ARM": "NASDAQ:ARM",
    "INTC": "NASDAQ:INTC",
    "QCOM": "NASDAQ:QCOM",
    "TXN": "NASDAQ:TXN",
    "AMAT": "NASDAQ:AMAT",
    "LRCX": "NASDAQ:LRCX",
    "KLAC": "NASDAQ:KLAC",
    "SNPS": "NASDAQ:SNPS",
    "CDNS": "NASDAQ:CDNS",
    "MRVL": "NASDAQ:MRVL",
    "ADI": "NASDAQ:ADI",
    "NXPI": "NASDAQ:NXPI",
    "ON": "NASDAQ:ON",
    "MPWR": "NASDAQ:MPWR",
    "GFS": "NASDAQ:GFS",
    "IBM": "NYSE:IBM",
    "CRM": "NYSE:CRM",
    "NOW": "NYSE:NOW",
    "ADBE": "NASDAQ:ADBE",
    "PANW": "NASDAQ:PANW",
    "CRWD": "NASDAQ:CRWD",
    "NET": "NYSE:NET",
    "DDOG": "NASDAQ:DDOG",
    "SNOW": "NYSE:SNOW",
    "UBER": "NYSE:UBER",
    "COIN": "NASDAQ:COIN",
    "MSTR": "NASDAQ:MSTR",
    # International & GDR / ADR
    "SMSN.L": "KRX:005930",
    "SMSN.IL": "KRX:005930",
    "005930.KS": "KRX:005930",
    "SMGB.L": "LSE:SMGB",
    "VUAG.L": "LSE:VUAG",
    "VWRP.L": "LSE:VWRP",
}

# Tickers where we always fall back to MA corridor (ETFs with no P/E)
MA_FALLBACK_TICKERS = {"SMGB.L", "VUAG.L", "VWRP.L"}

# AJ Financial Research institutional benchmark table (latest update)
AJ_LATEST_PEGS = {
    "GOOGL": {"peg": 1.46, "cagr_pct": 15.8},
    "GOOG":  {"peg": 1.46, "cagr_pct": 15.8},
    "AMZN":  {"peg": 1.00, "cagr_pct": 23.8},
    "AMD":   {"peg": 1.04, "cagr_pct": 38.9},
    "AAPL":  {"peg": 3.26, "cagr_pct": 10.9},
    "AVGO":  {"peg": 0.37, "cagr_pct": 49.2},
    "META":  {"peg": 0.91, "cagr_pct": 23.6},
    "MU":    {"peg": 0.27, "cagr_pct": 25.1},
    "MSFT":  {"peg": 1.04, "cagr_pct": 21.0},
    "NVDA":  {"peg": 0.34, "cagr_pct": 42.2},
    "ORCL":  {"peg": 0.24, "cagr_pct": 51.9},
    "PLTR":  {"peg": 1.71, "cagr_pct": 47.7},
    "TSLA":  {"peg": 1.78, "cagr_pct": 96.2},
    "TSM":   {"peg": 0.84, "cagr_pct": 24.5},
}

CORRIDOR_DAYS   = 90           # 90-day rolling fair-value window
MA_SHORT        = 50
MA_LONG         = 200
MA_STD_DEV      = 50           # 50-day window for Std Dev metric (reverted from 16)

# Modern soft financial status tones
COLOR_ATTRACTIVE = "#10B981"   # Emerald Green (Buy Zone)
COLOR_NEUTRAL    = "#F59E0B"   # Warm Amber (Standard DCA)
COLOR_OVERVALUED = "#EF4444"   # Soft Coral Red (Wait for Pullback)

# @theinvestingdean Brand accents
BRAND_GOLD        = "#EAB308"  # Subtle yellow/gold border
BRAND_GOLD_LIGHT  = "#FDE047"  # Vibrant brand yellow background (exact match with filter chips)
BRAND_GOLD_BORDER = "#EAB308"  # Clean accent border
BRAND_GOLD_DARK   = "#1F2937"  # High-contrast dark charcoal text (exact match with filter chips)

STATUS_COLORS = {
    "Buy Zone":          COLOR_ATTRACTIVE,
    "Standard DCA":      COLOR_NEUTRAL,
    "Wait for Pullback": COLOR_OVERVALUED,
    # Backward compatibility fallbacks
    "Attractive": COLOR_ATTRACTIVE,
    "Neutral":    COLOR_NEUTRAL,
    "Overvalued": COLOR_OVERVALUED,
}

PAGE_BG      = "#F4F6F8"       # Soft modern off-white/gray canvas
CARD_BG      = "#FFFFFF"       # Pure white cards
GRID_COLOR   = "#F1F5F9"       # Thin light-gray grid lines
TEXT_DARK    = "#1F2937"       # Softened dark slate gray for headings / primary text
MUTED_SLATE  = "#64748B"       # Crisp slate for secondary labels
BORDER_COLOR = "#E5E7EB"       # Subtle card borders
ACCENT_BLUE  = "#2563EB"       # Clean royal blue for price action

# ─────────────────────────────────────────────
# PAGE CONFIGURATION & STYLING
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="The Stock Valuation Radar",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
        /* Hide the default Streamlit page navigation menu */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}

        /* Add a premium fintech dot-matrix pattern to the main background */
        [data-testid="stAppViewContainer"] {{
            background-color: #f8f9fa !important;
            background-image: radial-gradient(#d1d5db 1px, transparent 1px) !important;
            background-size: 24px 24px !important;
        }}

        /* Make the top Streamlit header transparent so it blends into the pattern */
        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        /* Ensure sidebar remains solid white against the dot-matrix canvas */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid #E5E7EB !important;
        }}

        /* ── Signature Yellow Pill Guide Buttons ── */
        .guide-btn {{
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
        }}
        .guide-btn:hover {{
            background-color: #FACC15;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
            text-decoration: none !important;
            color: #1F2937 !important;
        }}
        section[data-testid="stSidebar"] .guide-btn {{
            width: 100%;
            justify-content: center;
            box-sizing: border-box;
        }}

        /* 1. Force the absolute outer wrapper to be solid white with a thick border and 3D shadow */
        div[class*="st-key-stock_card_"],
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #FFFFFF !important;
            background-image: none !important;
            border: 2px solid #94A3B8 !important; /* Thicker, darker structural border */
            border-radius: 16px !important;
            box-shadow: 0px 12px 24px -4px rgba(0, 0, 0, 0.15), 0px 8px 12px -6px rgba(0, 0, 0, 0.1) !important; /* Deep 3D drop shadow */
            padding: 1.5rem !important;
            margin-bottom: 2.5rem !important;
            position: relative !important;
            z-index: 10 !important;
        }}

        /* 2. Brute-force inner nested divs to block any dots from bleeding through */
        div[class*="st-key-stock_card_"] div,
        div[data-testid="stVerticalBlockBorderWrapper"] div {{
            background-image: none !important;
        }}

        /* 3. Keep the inner metric tiles soft gray so they contrast against the pure white master card */
        [data-testid="stMetric"],
        .kpi-mini-box {{
            background-color: #F8FAFC !important; 
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            padding: 12px !important;
            box-shadow: none !important; 
        }}
        [data-testid="stDataFrame"] {{
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 12px !important;
            padding: 16px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        }}

        /* Ensure the metric labels (e.g., "PRICE (USD)") are a soft slate gray */
        [data-testid="stMetricLabel"] p {{
            color: #6B7280 !important;
            font-weight: 600 !important;
        }}

        /* ── Uniform Responsive KPI Mini-Boxes (Card-within-a-Card) ── */
        .kpi-mini-box {{
            min-height: 84px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 8px;
            overflow: hidden;
            box-sizing: border-box;
            width: 100%;
        }}
        .kpi-mini-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 4px;
            flex-wrap: wrap;
            margin-bottom: 2px;
        }}
        .kpi-mini-title {{
            color: {MUTED_SLATE};
            font-size: 0.66rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            line-height: 1.15;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: normal;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            max-width: 100%;
        }}
        .kpi-mini-value {{
            font-size: 1.22rem;
            font-weight: 700;
            line-height: 1.2;
            margin: 2px 0;
            font-variant-numeric: tabular-nums;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 4px;
        }}
        .kpi-mini-subtext {{
            font-size: 0.74rem;
            font-weight: 500;
            line-height: 1.2;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* ── Metric cards for top KPI summary ── */
        div[data-testid="metric-container"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            min-height: auto !important;
        }}

        /* ── Executive Highlights Cards ── */
        .highlights-card {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        }}
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
            color: #6B7280 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            margin-bottom: 4px !important;
            text-transform: none !important;
            letter-spacing: normal !important;
        }}
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: {TEXT_DARK} !important;
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
        }}
        div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
            font-size: 0.8rem !important;
            font-weight: 600 !important;
        }}

        /* ── Status badges ── */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}
        .badge-attractive {{
            background-color: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
        }}
        .badge-neutral {{
            background-color: #FFFBEB;
            color: #B45309;
            border: 1px solid #FDE68A;
        }}
        .badge-overvalued {{
            background-color: #FEF2F2;
            color: #B91C1C;
            border: 1px solid #FECACA;
        }}
        .badge-na {{
            background-color: #F3F4F6;
            color: #374151;
            border: 1px solid #E5E7EB;
        }}
        .metric-badge {{
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            line-height: 1.1;
        }}

        /* ── Subtle @theinvestingdean yellow accents ── */
        .dean-badge {{
            font-weight: 700 !important;
            color: #1F2937 !important;
            background-color: #FDE047 !important;
            border: 1px solid #EAB308 !important;
            padding: 2px 9px;
            border-radius: 6px;
            letter-spacing: 0.01em;
            display: inline-flex !important;
            align-items: center !important;
            text-decoration: none !important;
            box-shadow: 0 1px 2px rgba(234, 179, 8, 0.20) !important;
            transition: all 0.2s ease-in-out;
            cursor: pointer !important;
        }}
        a.dean-badge:hover,
        .dean-badge:hover {{
            background-color: #FACC15 !important;
            color: #111827 !important;
            border-color: #CA8A04 !important;
            box-shadow: 0 3px 6px rgba(234, 179, 8, 0.35) !important;
            transform: translateY(-1px) !important;
        }}
        a.dean-badge:active,
        .dean-badge:active {{
            transform: translateY(0px) !important;
        }}
        .header-container {{
            margin-top: 0.5rem !important;
            border-bottom: 2px solid {BRAND_GOLD_BORDER} !important;
        }}

        /* ── Sidebar @theinvestingdean Brand Vibrant Yellow Styling (Multiselect Chips) ── */
        /* Streamlit 1.64+ [data-tag] and legacy [data-baseweb="tag"] containers */
        [data-testid="stSidebar"] [data-tag],
        [data-testid="stSidebar"] span[data-tag],
        [data-testid="stSidebar"] [data-testid="stMultiSelectTagsContainer"] [data-tag],
        [data-testid="stSidebar"] .e1kig3hy3,
        [data-tag],
        span[data-tag],
        [data-baseweb="tag"],
        span[data-baseweb="tag"] {{
            background-color: #FDE047 !important;
            border: 1px solid #EAB308 !important;
            border-radius: 6px !important;
            box-shadow: 0 1px 2px rgba(234, 179, 8, 0.20) !important;
            color: #1F2937 !important;
        }}

        /* Chip Text */
        [data-testid="stSidebar"] [data-tag] *,
        [data-testid="stSidebar"] [data-tag] span,
        [data-testid="stSidebar"] [data-tag] .e1kig3hy4,
        [data-testid="stSidebar"] [data-tag] [title],
        [data-tag] *,
        [data-tag] span,
        [data-tag] .e1kig3hy4,
        [data-tag] [title],
        [data-baseweb="tag"] *,
        [data-baseweb="tag"] span {{
            color: #1F2937 !important;
            font-weight: 700 !important;
            font-size: 0.76rem !important;
            letter-spacing: 0.01em !important;
            -webkit-text-fill-color: #1F2937 !important;
        }}

        /* Chip Close Icon (×) Button & SVG */
        [data-testid="stSidebar"] [data-tag] button,
        [data-testid="stSidebar"] [data-tag] .e1kig3hy5,
        [data-testid="stSidebar"] [data-tag] svg,
        [data-testid="stSidebar"] [data-tag] svg *,
        [data-testid="stSidebar"] [data-tag] path,
        [data-tag] button,
        [data-tag] .e1kig3hy5,
        [data-tag] svg,
        [data-tag] svg *,
        [data-tag] path,
        [data-baseweb="tag"] svg,
        [data-baseweb="tag"] svg *,
        [data-baseweb="tag"] path {{
            color: #1F2937 !important;
            stroke: #1F2937 !important;
            fill: #1F2937 !important;
        }}

        /* Close icon hover */
        [data-tag] button:hover,
        [data-tag] .e1kig3hy5:hover,
        [data-tag] [role="presentation"]:hover,
        [data-tag] [role="button"]:hover,
        [data-tag] svg:hover,
        [data-baseweb="tag"] [role="presentation"]:hover,
        [data-baseweb="tag"] svg:hover {{
            background-color: #EAB308 !important;
            border-radius: 3px !important;
        }}

        /* ── Specific Color-Coded Status Chips (Green, Amber, Red) ── */
        /* 🟢 Buy Zone Chip */
        [data-baseweb="tag"]:has([title*="Buy Zone"]),
        [data-tag]:has([title*="Buy Zone"]),
        span[data-baseweb="tag"]:has([title*="Buy Zone"]) {{
            background-color: #ECFDF5 !important;
            border: 1px solid #10B981 !important;
            box-shadow: 0 1px 2px rgba(16, 185, 129, 0.20) !important;
        }}
        [data-baseweb="tag"]:has([title*="Buy Zone"]) *,
        [data-tag]:has([title*="Buy Zone"]) * {{
            color: #047857 !important;
            fill: #047857 !important;
            stroke: #047857 !important;
            -webkit-text-fill-color: #047857 !important;
        }}
        [data-baseweb="tag"]:has([title*="Buy Zone"]) svg:hover,
        [data-tag]:has([title*="Buy Zone"]) svg:hover {{
            background-color: #A7F3D0 !important;
        }}

        /* 🟡 Standard DCA Chip */
        [data-baseweb="tag"]:has([title*="Standard DCA"]),
        [data-tag]:has([title*="Standard DCA"]),
        span[data-baseweb="tag"]:has([title*="Standard DCA"]) {{
            background-color: #FFFBEB !important;
            border: 1px solid #F59E0B !important;
            box-shadow: 0 1px 2px rgba(245, 158, 11, 0.20) !important;
        }}
        [data-baseweb="tag"]:has([title*="Standard DCA"]) *,
        [data-tag]:has([title*="Standard DCA"]) * {{
            color: #B45309 !important;
            fill: #B45309 !important;
            stroke: #B45309 !important;
            -webkit-text-fill-color: #B45309 !important;
        }}
        [data-baseweb="tag"]:has([title*="Standard DCA"]) svg:hover,
        [data-tag]:has([title*="Standard DCA"]) svg:hover {{
            background-color: #FDE68A !important;
        }}

        /* 🔴 Wait for Pullback Chip */
        [data-baseweb="tag"]:has([title*="Wait for Pullback"]),
        [data-tag]:has([title*="Wait for Pullback"]),
        span[data-baseweb="tag"]:has([title*="Wait for Pullback"]) {{
            background-color: #FEF2F2 !important;
            border: 1px solid #EF4444 !important;
            box-shadow: 0 1px 2px rgba(239, 68, 68, 0.20) !important;
        }}
        [data-baseweb="tag"]:has([title*="Wait for Pullback"]) *,
        [data-tag]:has([title*="Wait for Pullback"]) * {{
            color: #B91C1C !important;
            fill: #B91C1C !important;
            stroke: #B91C1C !important;
            -webkit-text-fill-color: #B91C1C !important;
        }}
        [data-baseweb="tag"]:has([title*="Wait for Pullback"]) svg:hover,
        [data-tag]:has([title*="Wait for Pullback"]) svg:hover {{
            background-color: #FECACA !important;
        }}

        /* ── Controls Consistency: Active Toggle Switches & Sidebar Dropdown Hovers ── */
        /* Active Toggle Switches (Show Detail Charts) */
        div[data-testid="stToggle"] [aria-checked="true"],
        div[data-testid="stToggle"] input:checked ~ div,
        div[data-testid="stToggle"] [data-baseweb="checkbox"] [aria-checked="true"] {{
            background-color: #FDE047 !important;
            border: 1.5px solid #EAB308 !important;
        }}
        div[data-testid="stToggle"] input:checked + div {{
            background-color: #FDE047 !important;
            border: 1.5px solid #EAB308 !important;
        }}
        div[data-testid="stToggle"] [aria-checked="true"] > div,
        div[data-testid="stToggle"] input:checked ~ div > div {{
            background-color: #1F2937 !important;
        }}

        /* Sidebar Dropdown Menus Hover & Focus States */
        section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
        section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within,
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {{
            border-color: #EAB308 !important;
            box-shadow: 0 0 0 1px #EAB308 !important;
        }}
        /* Dropdown popover active/hover selection */
        [data-baseweb="menu"] [aria-selected="true"],
        [data-baseweb="popover"] li:hover,
        [data-baseweb="menu"] li:hover {{
            background-color: #FEF9C3 !important;
            color: #1F2937 !important;
            font-weight: 700 !important;
        }}

        /* Action buttons with signature gold background */
        .stButton > button {{
            background-color: #FACC15 !important;
            border: 1.5px solid #EAB308 !important;
            color: #1F2937 !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(234, 179, 8, 0.25) !important;
            transition: all 0.2s ease-in-out !important;
        }}
        .stButton > button:hover {{
            background-color: #EAB308 !important;
            border-color: #CA8A04 !important;
            color: #111827 !important;
            box-shadow: 0 3px 10px rgba(234, 179, 8, 0.40) !important;
        }}

        /* ── Segmented Control / Button Group (90-Day vs 1-Year Timeframe Toggle) ── */
        div[data-testid="stButtonGroup"],
        div[data-testid="stSegmentedControl"],
        .stButtonGroup {{
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            margin-top: 10px !important;
            margin-bottom: 12px !important;
            width: fit-content !important;
        }}
        div[data-testid="stButtonGroup"] > div,
        div[data-testid="stSegmentedControl"] > div,
        .stButtonGroup > div {{
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 3px !important;
            gap: 4px !important;
            display: inline-flex !important;
        }}
        div[data-testid="stButtonGroup"] button,
        div[data-testid="stSegmentedControl"] button,
        .stButtonGroup button,
        button[data-variant="segmented_control"] {{
            border-radius: 6px !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: #475569 !important;
            -webkit-text-fill-color: #475569 !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            padding: 4px 14px !important;
            transition: all 0.15s ease-in-out !important;
            cursor: pointer !important;
        }}
        div[data-testid="stButtonGroup"] button:hover,
        div[data-testid="stSegmentedControl"] button:hover,
        .stButtonGroup button:hover,
        button[data-variant="segmented_control"]:hover {{
            color: #1F2937 !important;
            -webkit-text-fill-color: #1F2937 !important;
            background-color: #FEF9C3 !important;
            border-color: #FDE047 !important;
        }}
        /* Active / Selected Toggle Button - Exact Match with Stock Tickers */
        div[data-testid="stButtonGroup"] button[data-selected="true"],
        div[data-testid="stButtonGroup"] button[aria-checked="true"],
        div[data-testid="stButtonGroup"] button[aria-selected="true"],
        div[data-testid="stButtonGroup"] button[aria-pressed="true"],
        div[data-testid="stButtonGroup"] button[data-checked="true"],
        div[data-testid="stSegmentedControl"] button[data-selected="true"],
        div[data-testid="stSegmentedControl"] button[aria-checked="true"],
        div[data-testid="stSegmentedControl"] button[aria-selected="true"],
        div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
        div[data-testid="stSegmentedControl"] button[data-checked="true"],
        .stButtonGroup button[data-selected="true"],
        .stButtonGroup button[aria-checked="true"],
        .stButtonGroup button[aria-selected="true"],
        .stButtonGroup button[aria-pressed="true"],
        .stButtonGroup button[data-checked="true"],
        button[data-variant="segmented_control"][data-selected="true"],
        button[data-variant="segmented_control"][aria-checked="true"],
        button[data-variant="segmented_control"][aria-pressed="true"] {{
            background-color: #FDE047 !important;
            border: 1px solid #EAB308 !important;
            color: #1F2937 !important;
            -webkit-text-fill-color: #1F2937 !important;
            font-weight: 700 !important;
            border-radius: 6px !important;
            box-shadow: 0 1px 2px rgba(234, 179, 8, 0.20) !important;
        }}
        div[data-testid="stButtonGroup"] button[data-selected="true"] *,
        div[data-testid="stButtonGroup"] button[aria-checked="true"] *,
        div[data-testid="stButtonGroup"] button[aria-selected="true"] *,
        div[data-testid="stButtonGroup"] button[aria-pressed="true"] *,
        div[data-testid="stSegmentedControl"] button[data-selected="true"] *,
        div[data-testid="stSegmentedControl"] button[aria-checked="true"] *,
        div[data-testid="stSegmentedControl"] button[aria-selected="true"] *,
        div[data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
        .stButtonGroup button[data-selected="true"] *,
        .stButtonGroup button[aria-checked="true"] *,
        .stButtonGroup button[aria-selected="true"] *,
        .stButtonGroup button[aria-pressed="true"] *,
        button[data-variant="segmented_control"][data-selected="true"] *,
        button[data-variant="segmented_control"][aria-checked="true"] *,
        button[data-variant="segmented_control"][aria-pressed="true"] * {{
            color: #1F2937 !important;
            -webkit-text-fill-color: #1F2937 !important;
            font-weight: 700 !important;
        }}

        /* Explicit Unselected Toggle Button Styling */
        div[data-testid="stButtonGroup"] button[data-selected="false"],
        div[data-testid="stButtonGroup"] button[aria-checked="false"],
        div[data-testid="stSegmentedControl"] button[data-selected="false"],
        div[data-testid="stSegmentedControl"] button[aria-checked="false"],
        div[data-testid="stSegmentedControl"] button[aria-pressed="false"],
        .stButtonGroup button[data-selected="false"],
        .stButtonGroup button[aria-checked="false"],
        button[data-variant="segmented_control"][data-selected="false"],
        button[data-variant="segmented_control"][aria-checked="false"] {{
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            color: #475569 !important;
            -webkit-text-fill-color: #475569 !important;
            font-weight: 600 !important;
            box-shadow: none !important;
        }}
        div[data-testid="stButtonGroup"] button[data-selected="false"] *,
        div[data-testid="stButtonGroup"] button[aria-checked="false"] *,
        div[data-testid="stSegmentedControl"] button[data-selected="false"] *,
        div[data-testid="stSegmentedControl"] button[aria-checked="false"] *,
        .stButtonGroup button[data-selected="false"] *,
        .stButtonGroup button[aria-checked="false"] *,
        button[data-variant="segmented_control"][data-selected="false"] *,
        button[data-variant="segmented_control"][aria-checked="false"] * {{
            color: #475569 !important;
            -webkit-text-fill-color: #475569 !important;
            font-weight: 600 !important;
        }}

        /* 📸 Save Card Social Media Export Button */
        .save-card-btn {{
            background-color: #FEF9C3 !important;
            border: 1px solid #FDE047 !important;
            color: #854D0E !important;
            padding: 3px 7px !important;
            border-radius: 6px !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
            outline: none !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 3px !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
        }}
        .save-card-btn:hover {{
            background-color: #FDE047 !important;
            color: #713F12 !important;
            border-color: #EAB308 !important;
            box-shadow: 0 1px 4px rgba(234, 179, 8, 0.25) !important;
        }}
        .save-card-btn:active {{
            transform: scale(0.97);
        }}

        /* ⛶ Fullscreen Expand Chart Button */
        .expand-chart-bar {{
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            margin-top: 14px !important;
            margin-bottom: 12px !important;
            padding: 4px 2px 20px 2px !important;
            position: relative !important;
            z-index: 998 !important;
            pointer-events: auto !important;
            clear: both !important;
        }}
        .expand-chart-btn {{
            background-color: #FEF9C3 !important;
            border: 1px solid #FDE047 !important;
            color: #854D0E !important;
            padding: 4px 10px !important;
            border-radius: 6px !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
            outline: none !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 4px !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
            touch-action: manipulation !important;
            -webkit-tap-highlight-color: transparent !important;
            user-select: none !important;
            position: relative !important;
            z-index: 999 !important;
            pointer-events: auto !important;
        }}
        .expand-chart-btn:hover {{
            background-color: #FDE047 !important;
            color: #713F12 !important;
            border-color: #EAB308 !important;
            box-shadow: 0 1px 4px rgba(234, 179, 8, 0.25) !important;
        }}
        .expand-chart-btn:active {{
            transform: scale(0.97);
        }}

        /* ↺ Refocus Chart Button */
        .refocus-chart-btn {{
            background-color: #F8FAFC !important;
            border: 1px solid #CBD5E1 !important;
            color: #334155 !important;
            padding: 3px 8px !important;
            border-radius: 6px !important;
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
            outline: none !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 4px !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
        }}
        .refocus-chart-btn:hover {{
            background-color: #EFF6FF !important;
            color: #1D4ED8 !important;
            border-color: #93C5FD !important;
            box-shadow: 0 1px 4px rgba(37, 99, 235, 0.15) !important;
        }}
        .refocus-chart-btn:active {{
            transform: scale(0.97);
        }}

        /* ── Single Clean Fullscreen Expand Button (Streamlit Native Toolbar) ── */
        div[data-testid="stPlotlyChart"] {{
            position: relative !important;
        }}
        div[data-testid="stElementToolbar"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 0.90 !important;
            z-index: 1010 !important;
            position: absolute !important;
            top: 4px !important;
            right: 6px !important;
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 6px !important;
            padding: 2px 4px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stElementToolbar"]:hover {{
            opacity: 1 !important;
            background-color: #FEF08A !important;
            border-color: #EAB308 !important;
            box-shadow: 0 1px 4px rgba(234, 179, 8, 0.25) !important;
        }}
        div[data-testid="stElementToolbarButton"],
        div[data-testid="stElementToolbar"] button {{
            color: #1E293B !important;
            cursor: pointer !important;
            border: none !important;
            background: transparent !important;
        }}
        div[data-testid="stElementToolbarButton"]:hover,
        div[data-testid="stElementToolbar"] button:hover {{
            color: #0F172A !important;
        }}

        /* Completely hide any Plotly modebars on the preview charts */
        div[data-testid="stPlotlyChart"]:not(.in-modal) .modebar-container,
        div[data-testid="stPlotlyChart"]:not(.in-modal) .modebar,
        div[data-testid="stPlotlyChart"]:not(.in-modal) .modebar-btn {{
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
        }}

        /* Enable smooth scroll pass-through on preview charts (wheel & touch swipe) */
        div[data-testid="stPlotlyChart"]:not(.in-modal) .nsewdrag,
        div[data-testid="stPlotlyChart"]:not(.in-modal) .draglayer,
        div[data-testid="stPlotlyChart"]:not(.in-modal) .drag,
        div[data-testid="stPlotlyChart"]:not(.in-modal) .plot-container svg.main-svg:first-child {{
            pointer-events: none !important;
            touch-action: pan-y !important;
        }}
        div[data-testid="stPlotlyChart"]:not(.in-modal) .js-plotly-plot {{
            touch-action: pan-y !important;
        }}
        div[data-testid="stPlotlyChart"] div[data-testid="stElementToolbar"],
        div[data-testid="stPlotlyChart"] div[data-testid="stElementToolbarButton"] {{
            pointer-events: auto !important;
        }}

        /* ── Smooth Scrolling for Anchor Jumps ── */
        html {{
            scroll-behavior: smooth !important;
        }}

        /* ── Custom Thin Scrollbar for Highlights & Signals Trackers ── */
        .custom-signals-scroll {{
            scrollbar-width: thin !important;
            scrollbar-color: #CBD5E1 #F1F5F9 !important;
        }}
        .custom-signals-scroll::-webkit-scrollbar {{
            width: 4px !important;
        }}
        .custom-signals-scroll::-webkit-scrollbar-track {{
            background: #F1F5F9 !important;
            border-radius: 4px !important;
        }}
        .custom-signals-scroll::-webkit-scrollbar-thumb {{
            background: #CBD5E1 !important;
            border-radius: 4px !important;
        }}
        .custom-signals-scroll::-webkit-scrollbar-thumb:hover {{
            background: #94A3B8 !important;
        }}

        /* ── Section divider ── */
        hr {{
            border-color: {BORDER_COLOR} !important;
            margin: 1.5rem 0 !important;
        }}

        /* ── Container padding & header layout ── */
        .block-container {{
            padding-top: 2.5rem !important;
            padding-bottom: 2.5rem !important;
        }}

        /* ── Responsive Mobile Optimizations (< 768px) ── */
        @media (max-width: 768px) {{
            /* Force card grid columns to 1 full-width stacked column on mobile so charts are never squashed */
            div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-stock_card_"]),
            div[data-testid="stHorizontalBlock"]:has(.stock-card-container),
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stVerticalBlockBorderWrapper"]) {{
                flex-direction: column !important;
                display: flex !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-stock_card_"]) > div[data-testid="column"],
            div[data-testid="stHorizontalBlock"]:has(.stock-card-container) > div[data-testid="column"],
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stVerticalBlockBorderWrapper"]) > div[data-testid="column"] {{
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 14px !important;
            }}
            /* Executive Market Highlights cards: stack cleanly into 1 full-width column on mobile */
            div[data-testid="stHorizontalBlock"]:has(.highlights-card) {{
                flex-direction: column !important;
                display: flex !important;
                gap: 10px !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(.highlights-card) > div[data-testid="column"] {{
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 0 !important;
            }}
            /* Collapse quick-find spacer on mobile */
            .qf-spacer {{
                display: none !important;
                height: 0 !important;
            }}
            /* Expand Chart button touch target optimization on mobile */
            .expand-chart-bar {{
                margin-top: 16px !important;
                margin-bottom: 12px !important;
                padding-bottom: 20px !important; /* Adequate vertical padding so container directly beneath does not swallow touch target */
                gap: 8px !important;
                position: relative !important;
                z-index: 998 !important;
                pointer-events: auto !important;
            }}
            .expand-chart-btn {{
                padding: 8px 16px !important;
                font-size: 0.80rem !important;
                min-height: 44px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
                position: relative !important;
                z-index: 999 !important;
                pointer-events: auto !important;
                touch-action: manipulation !important;
            }}
            /* Ensure plotly chart wrapper does not bleed over the button above it */
            div[data-testid="stPlotlyChart"],
            .js-plotly-plot {{
                position: relative !important;
                z-index: 1 !important;
            }}
            /* Clean edge padding on mobile phones for maximum chart width */
            .block-container {{
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
                padding-top: 1.25rem !important;
                padding-bottom: 2rem !important;
            }}
            /* Card inner padding */
            div[class*="st-key-stock_card_"],
            div[data-testid="stVerticalBlockBorderWrapper"] {{
                padding: 14px 12px !important;
                border-radius: 12px !important;
            }}
            /* Top 4 KPI metric cards: wrap cleanly into 2x2 grid on mobile */
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {{
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 8px !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) > div[data-testid="column"] {{
                flex: 1 1 calc(50% - 8px) !important;
                min-width: calc(50% - 8px) !important;
            }}

            /* ── Hide native Streamlit toolbars & Plotly preview modebars on mobile ── */
            .dean-modebar-fs-btn,
            .modebar-btn.dean-modebar-fs-btn,
            div[data-testid="stPlotlyChart"] .modebar-container,
            div[data-testid="stPlotlyChart"] .modebar,
            div[data-testid="stPlotlyChart"] div[data-testid="stElementToolbar"],
            div[data-testid="stElementToolbar"],
            [data-testid="stElementToolbarButton"] {{
                display: none !important;
                visibility: hidden !important;
                pointer-events: none !important;
                width: 0 !important;
                height: 0 !important;
            }}

            /* ── Fullscreen Expand Button: Prominently Visible on Mobile ── */
            .expand-chart-btn {{
                display: inline-flex !important;
                visibility: visible !important;
                pointer-events: auto !important;
                background-color: #FEF9C3 !important;
                border: 1px solid #FDE047 !important;
                color: #854D0E !important;
                padding: 4px 11px !important;
                border-radius: 6px !important;
                font-size: 0.72rem !important;
                font-weight: 700 !important;
                cursor: pointer !important;
                line-height: 1.2 !important;
                white-space: nowrap !important;
                box-shadow: 0 1px 3px rgba(234, 179, 8, 0.20) !important;
            }}
            .expand-chart-btn:active {{
                background-color: #FDE047 !important;
                transform: scale(0.97);
            }}

            /* Expand dialog to near-full screen on mobile */
            div[data-testid="stDialog"] div[role="dialog"] {{
                width: 96vw !important;
                max-width: 96vw !important;
                height: 94vh !important;
                max-height: 94vh !important;
                margin: 2vh auto !important;
                padding: 10px 8px !important;
                border-radius: 12px !important;
                overflow-y: auto !important;
            }}
        }}

        /* ── Hide Streamlit Deploy button, header chrome & decorations ── */
        .stDeployButton,
        [data-testid="stAppDeployButton"],
        [data-testid="stToolbarActions"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {{
            display: none !important;
            visibility: hidden !important;
        }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}

        /* ── Scrollbars ── */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: {PAGE_BG}; }}
        ::-webkit-scrollbar-thumb {{ background: {BORDER_COLOR}; border-radius: 3px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# DATA HELPERS & CALCULATIONS
# ─────────────────────────────────────────────
def get_currency_symbol(ccy: str) -> str:
    mapping = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "GBp": "p",
        "GBX": "p",
        "KRW": "₩",
        "JPY": "¥",
        "TWD": "NT$",
    }
    return mapping.get(ccy, "$")


def make_dual_perf_pill_html(
    reg_pct: float | None,
    ext_pct: float | None = None,
    ext_label: str | None = None,
    ext_price: float | None = None,
    ccy_sym: str = "$",
    align: str = "left",
    reg_abs: float | None = None,
    ext_abs: float | None = None,
) -> str:
    """
    Generate side-by-side / stacked badges for regular daily session and extended-hours trading.
    Preserves official regular session change and displays secondary badge for pre/post-market
    with percentage and absolute price/change matching TradingView conventions with currency symbols.
    """
    def _fmt_pct(v: float) -> str:
        # Formats e.g. 1.5% if round tenths (matches +1.5%), else 1.29%
        return f"{v:.1f}%" if abs(round(v, 1) - round(v, 2)) < 1e-4 else f"{v:.2f}%"

    # 1. Regular session badge
    reg_badge = ""
    if reg_pct is not None and not np.isnan(reg_pct):
        if reg_pct > 0.005:
            bg_r = "#DCFCE7"
            col_r = "#15803D"
            if reg_abs is not None and not np.isnan(reg_abs):
                lbl_r = f"+{ccy_sym}{abs(reg_abs):.2f} (+{_fmt_pct(reg_pct)})"
            else:
                lbl_r = f"+{_fmt_pct(reg_pct)}"
        elif reg_pct < -0.005:
            bg_r = "#FEE2E2"
            col_r = "#B91C1C"
            if reg_abs is not None and not np.isnan(reg_abs):
                lbl_r = f"-{ccy_sym}{abs(reg_abs):.2f} ({_fmt_pct(reg_pct)})"
            else:
                lbl_r = f"{_fmt_pct(reg_pct)}"
        else:
            bg_r = "#F1F5F9"
            col_r = "#64748B"
            if reg_abs is not None and not np.isnan(reg_abs):
                lbl_r = f"{ccy_sym}0.00 (0.0%)"
            else:
                lbl_r = "0.00 (0.0%)"
        pill_html = f'<span style="font-size: 0.65rem; font-weight: 700; background-color: {bg_r}; color: {col_r}; padding: 1.5px 6px; border-radius: 9999px; line-height: 1.1; white-space: nowrap;">{lbl_r}</span>'
        label_html = '<span style="font-size: 0.62rem; font-weight: 500; color: #64748B; line-height: 1.1; white-space: nowrap;">at market close</span>'
        reg_badge = f'<div style="display: inline-flex; align-items: center; gap: 4px; flex-wrap: wrap;">{pill_html}{label_html}</div>'

    # 2. Extended-hours badge (pre-market or post-market)
    ext_badge = ""
    if ext_label and ext_pct is not None and not np.isnan(ext_pct) and abs(float(ext_pct)) >= 0.005:
        if ext_pct > 0.005:
            bg_e = "#DCFCE7"
            col_e = "#15803D"
            bdr_e = "#A7F3D0"
        elif ext_pct < -0.005:
            bg_e = "#FEE2E2"
            col_e = "#B91C1C"
            bdr_e = "#FECACA"
        else:
            bg_e = "#F1F5F9"
            col_e = "#64748B"
            bdr_e = "#E2E8F0"

        clean_label = str(ext_label).strip()
        if clean_label.upper().startswith("PRE"):
            full_ext_label = "Pre-market price"
        elif clean_label.upper().startswith("POST"):
            full_ext_label = "Post-market price"
        else:
            full_ext_label = f"{clean_label}-market price"

        if ext_abs is not None and not np.isnan(ext_abs):
            if ext_abs > 0.005:
                abs_str = f"+{ccy_sym}{abs(ext_abs):.2f}"
                pct_sign = "+"
            elif ext_abs < -0.005:
                abs_str = f"-{ccy_sym}{abs(ext_abs):.2f}"
                pct_sign = ""
            else:
                abs_str = f"{ccy_sym}0.00"
                pct_sign = ""
            chg_part = f"{abs_str} ({pct_sign}{_fmt_pct(ext_pct)})"
        else:
            pct_sign = "+" if ext_pct > 0.005 else ""
            chg_part = f"{pct_sign}{_fmt_pct(ext_pct)}"

        if ext_price is not None and not np.isnan(ext_price) and ext_price > 0:
            lbl_e = f"{full_ext_label}: {ccy_sym}{ext_price:.2f} | {chg_part}"
        else:
            lbl_e = f"{full_ext_label}: {chg_part}"

        ext_badge = f'<span style="font-size: 0.60rem; font-weight: 600; background-color: {bg_e}; color: {col_e}; border: 1px solid {bdr_e}; padding: 1.5px 6px; border-radius: 9999px; line-height: 1.1; white-space: nowrap;">{lbl_e}</span>'

    items_align = "flex-start" if align == "left" else "flex-end"
    margin_css = "margin-right: auto;" if align == "left" else "margin-left: auto;"

    if reg_badge and ext_badge:
        return f'<div style="display: inline-flex; flex-direction: column; align-items: {items_align}; gap: 3px; {margin_css} max-width: 100%; flex-shrink: 1;">{reg_badge}{ext_badge}</div>'
    elif reg_badge:
        return f'<div style="display: inline-flex; align-items: center; {margin_css} max-width: 100%; flex-shrink: 1;">{reg_badge}</div>'
    elif ext_badge:
        return f'<div style="display: inline-flex; align-items: center; {margin_css} max-width: 100%; flex-shrink: 1;">{ext_badge}</div>'
    return ""


def make_perf_pill_html(perf_pct: float | None, ext_label: str | None = None) -> str:
    """Compatibility wrapper for single badge rendering."""
    return make_dual_perf_pill_html(perf_pct, None, ext_label)


def format_earnings_date(date_str: str | None) -> str:
    """Format upcoming earnings date professionally (e.g. Nov 3, 2026)."""
    if not date_str:
        return "N/A or Post-Close"
    try:
        dt = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        return dt.strftime("%b %d, %Y").replace(" 0", " ")
    except Exception:
        return str(date_str)


def format_rsi_display(rsi_val: float | None) -> str:
    """Format 14-Day Wilder RSI with a minimalist status dot."""
    if rsi_val is None or np.isnan(rsi_val):
        return "N/A"

    if rsi_val <= 35.0:
        dot_color = "#10B981"  # Oversold (Green)
    elif rsi_val >= 70.0:
        dot_color = "#EF4444"  # Overbought (Red)
    else:
        dot_color = "#F59E0B"  # Neutral (Amber)

    return f'<span style="color: {dot_color}; font-size: 10px; margin-right: 4px; vertical-align: middle;">●</span><span>{rsi_val:.1f}</span>'


def make_metric_tile_html(
    title: str,
    value: str,
    subtext: str | None = None,
    badge_text: str | None = None,
    badge_class: str | None = None,
    val_color: str = "#0F172A",
    subtext_color: str = "#64748B",
    inline_badge_html: str | None = None,
    badge_style: str | None = None,
    subtext_html: str | None = None,
    value_right_html: str | None = None,
) -> str:
    """Generate standardized, uniform KPI mini-box HTML."""
    badge_html = ""
    if badge_text:
        style_attr = f' style="white-space: nowrap; {badge_style}"' if badge_style else ' style="white-space: nowrap;"'
        cls_attr = f' class="metric-badge {badge_class}"' if badge_class else ' class="metric-badge"'
        badge_html = f'<span{cls_attr}{style_attr}>{badge_text}</span>'

    right_content = f"{value_right_html}" if value_right_html else (f"{inline_badge_html}" if inline_badge_html else "")

    if subtext_html is not None:
        sub_content = f'<div class="kpi-mini-subtext" style="display: flex; align-items: flex-start; justify-content: flex-start; min-height: 18px;">{subtext_html}</div>'
    elif subtext:
        sub_content = f'<div class="kpi-mini-subtext" style="color: {subtext_color};" title="{subtext}">{subtext}</div>'
    else:
        sub_content = '<div class="kpi-mini-subtext" style="min-height: 18px;"></div>'

    return f"""
    <div class="kpi-mini-box">
      <div class="kpi-mini-header">
        <span class="kpi-mini-title" title="{title}">{title}</span>
        {badge_html}
      </div>
      <div class="kpi-mini-value" style="color: {val_color};">
        <span style="font-variant-numeric: tabular-nums; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{value}</span>{right_content}
      </div>
      {sub_content}
    </div>
    """


def calculate_wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Wilder's RSI matching TradingView ta.rsi(close, 14) using
    exponential moving average (alpha=1/14, adjust=False).
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def evaluate_tactical_dca_signals(df: pd.DataFrame) -> list[tuple]:
    """
    TID - Tactical DCA v1.0 Pine Script Engine translated into native Python/Pandas logic.
    Chronologically evaluates entry tiers across daily bars and enforces the
    5-bar cooldown / 3.0% smart reload discount (override_factor = 0.97).
    Returns list of tuples: (date, low_price, tier_label, color)
    """
    last_extreme_idx, last_heavy_idx, last_std_idx = -999, -999, -999
    last_extreme_price, last_heavy_price, last_std_price = np.nan, np.nan, np.nan

    signals = []  # Store tuples: (date, price, tier_label, color)

    for i in range(len(df)):
        row = df.iloc[i]
        close = row["close"] if "close" in row else row["Close"]
        low = row["low"] if "low" in row else row["Low"]

        # ── Tier 0: Capitulation (-3.0 SD) ──
        # Logic: df['low'] <= (df['sma_20'] - (3.0 * df['std_20']))
        # Note: This tier requires no technical confirmation.
        raw_extreme = bool(row.get("signal_tier_0_capitulation", low <= (row["sma_20"] - (3.0 * row["std_20"]))))
        extreme_override = not np.isnan(last_extreme_price) and (
            close <= last_extreme_price * 0.97
        )
        extreme_can_trigger = (i - last_extreme_idx >= 5) or extreme_override

        extreme_dca = False
        if raw_extreme and extreme_can_trigger:
            extreme_dca = True
            is_reload = extreme_override and (i - last_extreme_idx < 5)
            last_extreme_idx = i
            last_extreme_price = close
            label = "DEEPER CRASH" if is_reload else "CAPITULATION"
            signals.append((row.name, low, label, "#F97316"))  # Red / Orange

        # ── Tier 1: Deeply Oversold (-2.2 SD) ──
        # Logic: df['low'] <= (df['sma_20'] - (2.2 * df['std_20']))
        # Filters: AND is_green_candle AND has_adequate_volume AND (macd_curling_up OR has_lower_defense)
        # Note: Ensure this does not trigger if Capitulation is already true.
        raw_heavy = bool(row.get("signal_tier_1_deeply_oversold", (
            (low <= (row["sma_20"] - (2.2 * row["std_20"])))
            and not raw_extreme
            and bool(row.get("is_green_candle", False))
            and bool(row.get("has_adequate_volume", False))
            and (bool(row.get("macd_curling_up", False)) or bool(row.get("has_lower_defense", False)))
        )))
        heavy_override = not np.isnan(last_heavy_price) and (
            close <= last_heavy_price * 0.97
        )
        heavy_can_trigger = (i - last_heavy_idx >= 5) or heavy_override
        extreme_cooldown = (i - last_extreme_idx >= 5)

        heavy_dca = False
        if raw_heavy and not extreme_dca and heavy_can_trigger and extreme_cooldown:
            heavy_dca = True
            is_reload = heavy_override and (i - last_heavy_idx < 5)
            last_heavy_idx = i
            last_heavy_price = close
            label = "BETTER VALUE" if is_reload else "DEEPLY OVERSOLD"
            signals.append((row.name, low, label, "#FACC15"))  # Gold / Amber

        # ── Tier 2: Standard DCA (-1.5 SD) ──
        # Logic: df['low'] <= (df['sma_20'] - (1.5 * df['std_20'])) AND df['low'] > (df['sma_20'] - (2.2 * df['std_20']))
        # Filters: AND df['rsi_14'] <= 48 AND macd_curling_up AND is_green_candle
        raw_std = bool(row.get("signal_tier_2_standard_dca", (
            (low <= (row["sma_20"] - (1.5 * row["std_20"])))
            and (low > (row["sma_20"] - (2.2 * row["std_20"])))
            and (row.get("rsi_14", 50) <= 48)
            and bool(row.get("macd_curling_up", False))
            and bool(row.get("is_green_candle", False))
        )))
        std_override = not np.isnan(last_std_price) and (
            close <= last_std_price * 0.97
        )
        std_can_trigger = (i - last_std_idx >= 5) or std_override
        cross_cooldown = (i - last_heavy_idx >= 5) and (i - last_extreme_idx >= 5)

        if (
            raw_std
            and not heavy_dca
            and not extreme_dca
            and std_can_trigger
            and cross_cooldown
        ):
            is_reload = std_override and (i - last_std_idx < 5)
            last_std_idx = i
            last_std_price = close
            label = "BETTER DCA" if is_reload else "DCA"
            signals.append((row.name, low, label, "#22C55E"))  # Lime Green

    return signals


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_tradingview_target(ticker: str) -> dict:
    """
    Fetch institutional 1-year analyst price target and consensus metrics from TradingView scanner.
    Supports US equities, international equities, and GDRs with automatic routing.
    """
    raw_t = ticker.upper().strip()
    symbols = []
    if raw_t in TRADINGVIEW_EXCHANGE_MAP:
        symbols.append(TRADINGVIEW_EXCHANGE_MAP[raw_t])
    elif raw_t.endswith(".L"):
        symbols.append(f"LSE:{raw_t[:-2]}")
    else:
        symbols.extend([f"NASDAQ:{raw_t}", f"NYSE:{raw_t}"])

    url = "https://scanner.tradingview.com/global/scan"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    columns = [
        "name", "close", "currency",
        "price_target_1y", "price_target_average", "price_target_median",
        "price_target_high", "price_target_low", "recommendation_mark", "recommendation_total"
    ]
    payload = {
        "symbols": {"tickers": symbols},
        "columns": columns,
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=6)
        if r.status_code == 200:
            data = r.json().get("data", [])
            for row in data:
                d = dict(zip(columns, row.get("d", [])))
                if d.get("price_target_1y") or d.get("price_target_average"):
                    return d
            if data:
                return dict(zip(columns, data[0].get("d", [])))
    except Exception:
        pass
    return {}


def normalize_analyst_target(ticker: str, live_price: float, tv_data: dict, raw_yahoo_target: float = None) -> tuple:
    """
    Normalize target price and compute implied upside percentage strictly against live price.
    Resolves:
    1. TradingView consensus upside alignment (e.g. Samsung +71% upside).
    2. Currency magnitude errors (pence vs pounds, 100x ratio check).
    3. Foreign exchange and GDR unit scale mismatches (e.g. SMSN.L in USD vs 005930 in KRW).
    """
    if live_price is None or not isinstance(live_price, (int, float)) or np.isnan(live_price) or live_price <= 0:
        return None, None

    live_price = float(live_price)

    # 1. TradingView Institutional Consensus Target
    if tv_data:
        tv_target = tv_data.get("price_target_1y") or tv_data.get("price_target_average")
        tv_close = tv_data.get("close")
        if (
            tv_target is not None
            and isinstance(tv_target, (int, float))
            and tv_target > 0
            and tv_close is not None
            and isinstance(tv_close, (int, float))
            and tv_close > 0
        ):
            # Implied upside percentage strictly calculated against TradingView close
            tv_upside_pct = ((float(tv_target) / float(tv_close)) - 1.0) * 100.0

            # Scale target price to live_price currency and unit denomination
            calibrated_target_price = live_price * (1.0 + (tv_upside_pct / 100.0))
            return calibrated_target_price, tv_upside_pct

    # 2. Fallback to raw provider target (e.g. Yahoo Finance) with magnitude normalization
    if (
        raw_yahoo_target is not None
        and isinstance(raw_yahoo_target, (int, float))
        and not np.isnan(raw_yahoo_target)
        and raw_yahoo_target > 0
    ):
        target = float(raw_yahoo_target)
        ratio = target / live_price

        # Magnitude check: Pence vs Pounds (100x error)
        if 50.0 <= ratio <= 150.0:
            target = target / 100.0
            ratio = target / live_price
        elif 0.005 <= ratio <= 0.02:
            target = target * 100.0
            ratio = target / live_price

        # International GDR check (e.g. SMSN.L vs KRW share target)
        if ticker in ("SMSN.L", "SMSN.IL", "005930.KS") and (ratio < 0.4 or ratio > 3.0):
            krx_tv = fetch_tradingview_target("KRX:005930")
            if krx_tv and krx_tv.get("price_target_1y") and krx_tv.get("close"):
                tv_up = ((float(krx_tv["price_target_1y"]) / float(krx_tv["close"])) - 1.0) * 100.0
                return live_price * (1.0 + tv_up / 100.0), tv_up

        upside_pct = ((target / live_price) - 1.0) * 100.0
        return target, upside_pct

    return None, None


def compute_ytd_pct(hist: pd.DataFrame, current_price: float | None = None) -> float | None:
    """
    Calculate Year-to-Date (YTD) percentage return.
    Base price is the close of the last trading day of the previous calendar year.
    Fallback to the first trading day of the current calendar year if previous year is unavailable.
    """
    if hist.empty or "Close" not in hist.columns:
        return None
    try:
        latest_dt = hist.index[-1]
        curr_year = latest_dt.year
        prior_year_data = hist[hist.index.year < curr_year]
        if not prior_year_data.empty:
            base_price = float(prior_year_data["Close"].iloc[-1])
        else:
            curr_year_data = hist[hist.index.year == curr_year]
            if not curr_year_data.empty:
                base_price = float(curr_year_data["Close"].iloc[0])
            else:
                return None

        now_price = current_price if (current_price is not None and not np.isnan(current_price) and current_price > 0) else float(hist["Close"].iloc[-1])
        if base_price > 0 and now_price > 0:
            return ((now_price / base_price) - 1.0) * 100.0
    except Exception:
        pass
    return None


@st.cache_data(ttl=900, show_spinner=False)
def fetch_ticker_data(ticker: str) -> dict:
    """
    Download full historical price data (period='max') for each equity
    to determine its absolute lifetime maximum high (ATH), 16-day Z-score,
    2-year forward EPS CAGR PEG ratio, and live trading session price.
    """
    fetch_symbol = TICKER_FETCH_MAPPING.get(ticker, ticker)
    default_name = TICKERS.get(ticker, TICKERS.get(fetch_symbol, ticker))

    try:
        obj = yf.Ticker(fetch_symbol)
        # Fetch full historical price data (period='max')
        hist_full = obj.history(period="max", auto_adjust=True)
        try:
            info = obj.info or {}
        except Exception:
            info = {}
    except Exception as e:
        return {
            "ticker":        ticker,
            "name":          default_name,
            "shortName":     default_name,
            "longName":      default_name,
            "error":         str(e),
            "hist":          pd.DataFrame(),
            "info":          {},
            "pe_mode":       False,
            "currency":      "USD",
            "next_earnings": None,
            "ath":           np.nan,
            "dist_ath":      np.nan,
            "current_price": np.nan,
            "reg_perf_pct":  None,
            "reg_perf_abs":  None,
            "ext_perf_pct":  None,
            "ext_perf_abs":  None,
            "ext_label":     None,
            "ext_price":     None,
            "ytd_pct":       None,
            "peg_2y":        None,
            "cagr_2y_pct":   None,
            "eps_ntm":       None,
            "eps_ntm_2":     None,
            "is_etf":        False,
            "is_ucits":      False,
            "ter":           None,
            "aum":           None,
            "fund_family":   None,
            "fwd_pe":        None,
            "target_mean_price": None,
            "target_upside_pct": None,
            "tactical_signals":  [],
        }

    if hist_full.empty or "Close" not in hist_full.columns:
        return {
            "ticker":        ticker,
            "name":          default_name,
            "shortName":     default_name,
            "longName":      default_name,
            "error":         "No price data returned",
            "hist":          pd.DataFrame(),
            "info":          info,
            "pe_mode":       False,
            "currency":      info.get("currency", "USD"),
            "next_earnings": None,
            "ath":           np.nan,
            "dist_ath":      np.nan,
            "current_price": np.nan,
            "reg_perf_pct":  None,
            "reg_perf_abs":  None,
            "ext_perf_pct":  None,
            "ext_perf_abs":  None,
            "ext_label":     None,
            "ext_price":     None,
            "ytd_pct":       None,
            "peg_2y":        None,
            "cagr_2y_pct":   None,
            "eps_ntm":       None,
            "eps_ntm_2":     None,
            "is_etf":        False,
            "is_ucits":      False,
            "ter":           None,
            "aum":           None,
            "fund_family":   None,
            "fwd_pe":        None,
            "target_mean_price": None,
            "target_upside_pct": None,
            "tactical_signals":  [],
        }

    # Normalize timezone
    if hist_full.index.tz is not None:
        hist_full.index = hist_full.index.tz_convert(None)
    else:
        hist_full.index = pd.to_datetime(hist_full.index)

    # ── Live Current Price Resolution ──
    current_price = None
    try:
        fast_info = getattr(obj, "fast_info", None)
        if fast_info is not None:
            lp = getattr(fast_info, "lastPrice", None)
            if lp is None and hasattr(fast_info, "get"):
                lp = fast_info.get("lastPrice") or fast_info.get("last_price")
            if lp is not None and not np.isnan(lp) and lp > 0:
                current_price = float(lp)
    except Exception:
        pass

    if current_price is None:
        rmp = info.get("regularMarketPrice") or info.get("currentPrice")
        if rmp is not None and isinstance(rmp, (int, float)) and rmp > 0:
            current_price = float(rmp)

    if current_price is None:
        current_price = float(hist_full["Close"].iloc[-1])

    # Ensure latest price is reflected in latest bar
    if not np.isnan(current_price):
        hist_full["Close"].iloc[-1] = current_price
        if "High" in hist_full.columns and current_price > hist_full["High"].iloc[-1]:
            hist_full["High"].iloc[-1] = current_price

    # ── Lifetime All-Time High (ATH) Calculation ──
    ath = float(hist_full["High"].max()) if "High" in hist_full.columns else float(hist_full["Close"].max())
    if current_price > ath:
        ath = current_price

    dist_ath = ((current_price - ath) / ath) * 100.0 if ath > 0 else 0.0

    # ── Year-to-Date (YTD) Percentage Return ──
    ytd_pct = compute_ytd_pct(hist_full, current_price)

    # ── Indicators calculated with full history warmup ──
    hist_full[f"MA{MA_SHORT}"] = hist_full["Close"].rolling(MA_SHORT, min_periods=10).mean()
    hist_full[f"MA{MA_LONG}"]  = hist_full["Close"].rolling(MA_LONG, min_periods=20).mean()

    # 50-Day Moving Average & Standard Deviation for Z-Score (reverted to 50 days)
    ma50_z  = hist_full["Close"].rolling(MA_STD_DEV, min_periods=10).mean()
    std50_z = hist_full["Close"].rolling(MA_STD_DEV, min_periods=10).std()
    z50_s   = (hist_full["Close"] - ma50_z) / std50_z.replace(0, np.nan)
    hist_full["Z50"] = z50_s
    hist_full["Z16"] = z50_s  # Alias for backward compatibility

    # 252-Day (1-Year) Moving Average & Standard Deviation for 1Y Z-Score
    ma252_z  = hist_full["Close"].rolling(252, min_periods=30).mean()
    std252_z = hist_full["Close"].rolling(252, min_periods=30).std()
    hist_full["Z252"] = (hist_full["Close"] - ma252_z) / std252_z.replace(0, np.nan)

    # ── TID - Tactical DCA v1.0 Indicators & Valuation Corridors (Lookback = 20) ──
    BB_WIN = 20
    bb_mid = hist_full["Close"].rolling(BB_WIN, min_periods=5).mean()
    bb_std = hist_full["Close"].rolling(BB_WIN, min_periods=5).std()
    hist_full["BB_mid"]  = bb_mid
    hist_full["BB_hi2"]  = bb_mid + 2.0 * bb_std   # Outer Upper (+2.0σ)
    hist_full["BB_hi15"] = bb_mid + 1.5 * bb_std   # Inner Upper (+1.5σ)
    hist_full["BB_lo15"] = bb_mid - 1.5 * bb_std   # Inner Lower (-1.5σ)
    hist_full["BB_lo2"]  = bb_mid - 2.0 * bb_std   # Outer Lower (-2.0σ)

    # 1. Dedicated 20-Day Signal Engine Columns (Preserves 50-day rolling Z-score UI)
    hist_full["sma_20"] = bb_mid
    hist_full["std_20"] = bb_std
    if "Volume" in hist_full.columns and not hist_full["Volume"].isna().all():
        hist_full["vol_sma_20"] = hist_full["Volume"].rolling(20, min_periods=5).mean()
    else:
        hist_full["vol_sma_20"] = 0.0

    # Normalized lowercase column aliases for exact 1:1 Pine Script compatibility
    hist_full["close"] = hist_full["Close"]
    hist_full["open"] = hist_full["Open"]
    hist_full["high"] = hist_full["High"]
    hist_full["low"] = hist_full["Low"]
    hist_full["volume"] = hist_full["Volume"] if "Volume" in hist_full.columns else 0.0

    # 14-day Wilder RSI
    hist_full["rsi_14"] = calculate_wilder_rsi(hist_full["Close"], period=14)
    hist_full["RSI14"] = hist_full["rsi_14"]
    hist_full["RSI"]   = hist_full["rsi_14"]

    # Standard MACD (12, 26, 9)
    ema12 = hist_full["Close"].ewm(span=12, adjust=False).mean()
    ema26 = hist_full["Close"].ewm(span=26, adjust=False).mean()
    hist_full["macd_line"] = ema12 - ema26
    hist_full["macd_signal"] = hist_full["macd_line"].ewm(span=9, adjust=False).mean()
    hist_full["macd_histogram"] = hist_full["macd_line"] - hist_full["macd_signal"]

    # 2. Implement 1:1 Pine Script Signal Logic Helper Masks
    hist_full["is_green_candle"] = hist_full["close"] > hist_full["open"]
    hist_full["macd_curling_up"] = hist_full["macd_histogram"] > hist_full["macd_histogram"].shift(1)

    vol_thresh = hist_full["vol_sma_20"] * 0.8
    hist_full["has_adequate_volume"] = (
        (hist_full["volume"] >= vol_thresh)
        | (hist_full["vol_sma_20"] == 0)
        | hist_full["volume"].isna()
    )

    candle_range = (hist_full["high"] - hist_full["low"]).replace(0, np.nan)
    body_min = hist_full[["open", "close"]].min(axis=1)
    hist_full["has_lower_defense"] = (((body_min - hist_full["low"]) / candle_range) >= 0.35).fillna(False)

    # Aliases for backward-compatibility with chart corridors and annotations
    hist_full["LowerBand1"] = hist_full["sma_20"] - (1.5 * hist_full["std_20"])
    hist_full["LowerBand2"] = hist_full["sma_20"] - (2.2 * hist_full["std_20"])
    hist_full["LowerBand3"] = hist_full["sma_20"] - (3.0 * hist_full["std_20"])
    hist_full["IsGreenCandle"] = hist_full["is_green_candle"]
    hist_full["MacdCurling"] = hist_full["macd_curling_up"]
    hist_full["HasAdequateVol"] = hist_full["has_adequate_volume"]
    hist_full["HasLowerDefense"] = hist_full["has_lower_defense"]

    # Vectorized Boolean Signal Masks (1:1 TradingView Pine Script TID v1.0)
    tier_0_mask = hist_full["low"] <= (hist_full["sma_20"] - (3.0 * hist_full["std_20"]))
    tier_1_mask = (
        (hist_full["low"] <= (hist_full["sma_20"] - (2.2 * hist_full["std_20"])))
        & (~tier_0_mask)
        & hist_full["is_green_candle"]
        & hist_full["has_adequate_volume"]
        & (hist_full["macd_curling_up"] | hist_full["has_lower_defense"])
    )
    tier_2_mask = (
        (hist_full["low"] <= (hist_full["sma_20"] - (1.5 * hist_full["std_20"])))
        & (hist_full["low"] > (hist_full["sma_20"] - (2.2 * hist_full["std_20"])))
        & (hist_full["rsi_14"] <= 48)
        & hist_full["macd_curling_up"]
        & hist_full["is_green_candle"]
    )
    hist_full["signal_tier_0_capitulation"] = tier_0_mask
    hist_full["signal_tier_1_deeply_oversold"] = tier_1_mask
    hist_full["signal_tier_2_standard_dca"] = tier_2_mask

    # Chronologically evaluate TID - Tactical DCA v1.0 Signals
    tactical_signals = evaluate_tactical_dca_signals(hist_full)

    # ── Upcoming earnings announcement date ──
    next_earnings = None
    try:
        cal = obj.calendar
        if isinstance(cal, dict):
            ed = cal.get("Earnings Date")
            if ed and len(ed):
                next_earnings = pd.Timestamp(ed[0]).strftime("%Y-%m-%d")
        elif isinstance(cal, pd.DataFrame) and not cal.empty:
            if "Earnings Date" in cal.index:
                val = cal.loc["Earnings Date"].iloc[0]
                if pd.notna(val):
                    next_earnings = pd.Timestamp(val).strftime("%Y-%m-%d")
    except Exception:
        pass

    # ── Dual Performance (Regular Session + Extended Hours) ──
    # Check marketState: 'PRE', 'POST' / 'POSTPOST', 'REGULAR', 'CLOSED'
    market_state = str(info.get("marketState", "")).upper()
    reg_chg = info.get("regularMarketChangePercent")
    reg_chg_abs = info.get("regularMarketChange")
    pre_chg = info.get("preMarketChangePercent")
    pre_chg_abs = info.get("preMarketChange")
    post_chg = info.get("postMarketChangePercent")
    post_chg_abs = info.get("postMarketChange")
    prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

    # If reg_chg is not provided directly, calculate vs previous close
    if reg_chg is None:
        if prev_close and isinstance(prev_close, (int, float)) and prev_close > 0 and current_price:
            reg_chg = ((current_price / float(prev_close)) - 1.0) * 100.0
            if reg_chg_abs is None:
                reg_chg_abs = current_price - float(prev_close)
        elif len(hist_full) >= 2:
            pc = float(hist_full["Close"].iloc[-2])
            if pc > 0 and current_price:
                reg_chg = ((current_price / pc) - 1.0) * 100.0
                if reg_chg_abs is None:
                    reg_chg_abs = current_price - pc

    if reg_chg_abs is None and reg_chg is not None and prev_close and isinstance(prev_close, (int, float)) and prev_close > 0:
        reg_chg_abs = current_price - float(prev_close)
    elif reg_chg_abs is None and reg_chg is not None and current_price:
        reg_chg_abs = current_price - (current_price / (1.0 + (reg_chg / 100.0)))

    reg_perf_pct = float(reg_chg) if reg_chg is not None and not np.isnan(reg_chg) else None
    reg_perf_abs = float(reg_chg_abs) if reg_chg_abs is not None and not np.isnan(reg_chg_abs) else None

    # Extended-hours trading prints (never overwrites regular session daily performance)
    ext_perf_pct = None
    ext_perf_abs = None
    ext_label = None
    ext_price = None
    pre_price = info.get("preMarketPrice")
    post_price = info.get("postMarketPrice")

    if market_state == "PRE" and pre_chg is not None and not np.isnan(pre_chg):
        ext_label = "Pre"
        ext_perf_pct = float(pre_chg)
        ext_price = float(pre_price) if pre_price is not None and not np.isnan(pre_price) else None
        if pre_chg_abs is not None and not np.isnan(pre_chg_abs):
            ext_perf_abs = float(pre_chg_abs)
        elif ext_price is not None and current_price:
            ext_perf_abs = ext_price - current_price
    elif post_chg is not None and not np.isnan(post_chg) and abs(float(post_chg)) >= 0.005:
        ext_label = "Post"
        ext_perf_pct = float(post_chg)
        ext_price = float(post_price) if post_price is not None and not np.isnan(post_price) else None
        if post_chg_abs is not None and not np.isnan(post_chg_abs):
            ext_perf_abs = float(post_chg_abs)
        elif ext_price is not None and current_price:
            ext_perf_abs = ext_price - current_price

    # ── ETF Detection (quoteType == 'ETF' or tickers like SMGB.L, VUAG.L, VWRP.L; force override SPCX as Equity) ──
    quote_type = str(info.get("quoteType", "")).upper()
    is_etf = (
        (
            quote_type in {"ETF", "MUTUALFUND"}
            or ticker in {"SMGB.L", "VUAG.L", "VWRP.L"}
            or "ETF" in str(info.get("shortName", "")).upper()
            or "ETF" in str(info.get("longName", "")).upper()
            or "ETF" in default_name.upper()
        )
        and ticker != "SPCX"
    )
    is_ucits = is_etf and (ticker.endswith(".L") or "UCITS" in str(info.get("longName", "")).upper() or ticker in {"SMGB.L", "VUAG.L", "VWRP.L"})

    # ETF-specific metrics (TER / Expense Ratio, AUM, Fund Family)
    ter = info.get("netExpenseRatio") or info.get("expenseRatio") or info.get("annualReportExpenseRatio")
    if ter is None and ticker == "SMGB.L":
        ter = 0.35  # Official VanEck Semiconductor UCITS ETF TER is 0.35%
    elif ter is None and ticker == "VUAG.L":
        ter = 0.07  # Official Vanguard S&P 500 UCITS ETF (Acc) TER is 0.07%
    elif ter is None and ticker == "VWRP.L":
        ter = 0.22  # Official Vanguard FTSE All-World UCITS ETF (Acc) TER is 0.22%
    aum = info.get("totalAssets") or info.get("netAssets")
    fund_family = info.get("fundFamily") or ("VanEck" if ticker == "SMGB.L" else "Vanguard" if ticker in {"VUAG.L", "VWRP.L"} else "")

    # ── Foreign GDRs & Currency Pairing Normalization (e.g., SMSN.L / SMSN.IL) ──
    # Overseas GDRs where prices trade in USD/GBP but EPS has a local currency / GDR unit mismatch
    # (e.g. Samsung London GDR SMSN.IL / SMSN.L trading at ~$5,110 USD with yfinance ratio normalization)
    fwd_pe  = info.get("forwardPE")
    fwd_eps = info.get("forwardEps")
    eps     = info.get("trailingEps")

    price_ccy = str(info.get("currency", "USD")).upper()
    fin_ccy   = str(info.get("financialCurrency", "")).upper()

    gdr_mult = 1.0
    if ticker in {"SMSN.L", "SMSN.IL"} or (ticker.endswith((".L", ".IL")) and fin_ccy == "KRW" and price_ccy in {"USD", "GBP", "GBX"}):
        if fwd_pe is not None and fwd_pe < 3.0:
            gdr_mult = 10.0
        elif fwd_pe is None and eps is not None and (current_price / eps) < 3.5:
            gdr_mult = 10.0
    elif fwd_pe is not None and 0 < fwd_pe < 3.0 and fin_ccy and price_ccy != fin_ccy:
        gdr_mult = 10.0

    if gdr_mult != 1.0:
        if fwd_pe is not None:
            fwd_pe = fwd_pe * gdr_mult
        if fwd_eps is not None:
            fwd_eps = fwd_eps / gdr_mult
        if eps is not None:
            eps = eps / gdr_mult

    # ── 2-Year Forward EPS CAGR and 2Y PEG Ratio Calculation (AJ Financial Research Methodology) ──
    # Suppressed for ETFs to eliminate misleading 'Growth Negative / N/A' tiles
    # Strict Institutional Formulas:
    #   1. 2Y CAGR = ((NTM+2 EPS) / (NTM EPS)) ** 0.5 - 1.0
    #   2. 2Y PEG  = (Forward P/E) / (CAGR * 100)
    peg_2y = None
    cagr_2y_pct = None
    eps_ntm = None
    eps_ntm_2 = None

    if not is_etf:
        clean_tk = ticker.upper().split(".")[0] if ("." in ticker and ticker.upper().split(".")[0] in AJ_LATEST_PEGS) else ticker.upper()
        if clean_tk in AJ_LATEST_PEGS:
            cagr_2y_pct = AJ_LATEST_PEGS[clean_tk]["cagr_pct"]
            if fwd_pe is not None and isinstance(fwd_pe, (int, float)) and fwd_pe > 0 and cagr_2y_pct > 0:
                peg_2y = fwd_pe / cagr_2y_pct
            else:
                peg_2y = AJ_LATEST_PEGS[clean_tk]["peg"]
            if fwd_eps is not None and fwd_eps > 0:
                eps_ntm = fwd_eps
                eps_ntm_2 = eps_ntm * ((1.0 + (cagr_2y_pct / 100.0)) ** 2)
            elif eps is not None and eps > 0:
                eps_ntm = eps
                eps_ntm_2 = eps_ntm * ((1.0 + (cagr_2y_pct / 100.0)) ** 2)
        else:
            ee = getattr(obj, "earnings_estimate", None)
            eps_0y = None
            eps_1y = None
            growth_0y = None
            growth_1y = None

            if ee is not None and isinstance(ee, pd.DataFrame) and not ee.empty:
                try:
                    if "0y" in ee.index and "avg" in ee.columns and pd.notna(ee.loc["0y", "avg"]):
                        eps_0y = float(ee.loc["0y", "avg"])
                    if "+1y" in ee.index and "avg" in ee.columns and pd.notna(ee.loc["+1y", "avg"]):
                        eps_1y = float(ee.loc["+1y", "avg"])
                    if "0y" in ee.index and "growth" in ee.columns and pd.notna(ee.loc["0y", "growth"]):
                        growth_0y = float(ee.loc["0y", "growth"])
                    if "+1y" in ee.index and "growth" in ee.columns and pd.notna(ee.loc["+1y", "growth"]):
                        growth_1y = float(ee.loc["+1y", "growth"])
                except Exception:
                    pass

            if gdr_mult != 1.0:
                if eps_0y is not None:
                    eps_0y = eps_0y / gdr_mult
                if eps_1y is not None:
                    eps_1y = eps_1y / gdr_mult

            if growth_1y is None:
                ge = getattr(obj, "growth_estimates", None)
                if ge is not None and isinstance(ge, pd.DataFrame) and not ge.empty:
                    try:
                        if "+1y" in ge.index and "stockTrend" in ge.columns and pd.notna(ge.loc["+1y", "stockTrend"]):
                            growth_1y = float(ge.loc["+1y", "stockTrend"])
                        if "0y" in ge.index and "stockTrend" in ge.columns and pd.notna(ge.loc["0y", "stockTrend"]):
                            growth_0y = float(ge.loc["0y", "stockTrend"])
                    except Exception:
                        pass

            # 1. Establish NTM EPS (Next Twelve Months forward consensus EPS)
            eps_ntm = None
            if eps_1y is not None and eps_1y > 0:
                eps_ntm = eps_1y
            elif fwd_eps is not None and fwd_eps > 0:
                eps_ntm = fwd_eps
            elif eps_0y is not None and eps_0y > 0:
                eps_ntm = eps_0y

            # 2. Determine NTM+2 EPS from analyst consensus
            eps_ntm_2 = None
            cagr_2y = None

            if ee is not None and isinstance(ee, pd.DataFrame) and not ee.empty:
                try:
                    if "+3y" in ee.index and "avg" in ee.columns and pd.notna(ee.loc["+3y", "avg"]):
                        eps_ntm_2 = float(ee.loc["+3y", "avg"]) / gdr_mult
                    elif "+2y" in ee.index and "avg" in ee.columns and pd.notna(ee.loc["+2y", "avg"]):
                        eps_ntm_2 = float(ee.loc["+2y", "avg"]) / gdr_mult
                except Exception:
                    pass

            if eps_ntm is not None and eps_ntm_2 is not None and eps_ntm > 0 and eps_ntm_2 > 0:
                # Direct multi-year consensus calculation: CAGR = ((NTM+2 EPS) / (NTM EPS)) ** 0.5 - 1.0
                cagr_2y = (eps_ntm_2 / eps_ntm) ** 0.5 - 1.0
            elif eps_ntm is not None and eps_ntm > 0:
                # Multi-year compound expansion across 2 forward consensus horizons
                if (
                    growth_0y is not None
                    and growth_1y is not None
                    and growth_0y > -0.5
                    and growth_1y > -0.5
                ):
                    comp_factor = (1.0 + growth_0y) * (1.0 + growth_1y)
                    if comp_factor > 0:
                        eps_ntm_2 = eps_ntm * comp_factor
                        cagr_2y = (comp_factor ** 0.5) - 1.0
                elif growth_1y is not None and growth_1y > 0:
                    eps_ntm_2 = eps_ntm * ((1.0 + growth_1y) ** 2)
                    cagr_2y = growth_1y
                elif (
                    eps_0y is not None
                    and eps_1y is not None
                    and eps_0y > 0
                    and eps_1y > eps_0y
                ):
                    g_annual = (eps_1y - eps_0y) / eps_0y
                    eps_ntm_2 = eps_ntm * ((1.0 + g_annual) ** 2)
                    cagr_2y = g_annual

            if cagr_2y is not None:
                cagr_2y_pct = cagr_2y * 100.0

                # Calculate PEG: (Forward P/E) / (CAGR * 100)
                if (
                    fwd_pe is not None
                    and isinstance(fwd_pe, (int, float))
                    and fwd_pe > 0
                    and cagr_2y_pct > 0
                ):
                    peg_2y = fwd_pe / cagr_2y_pct
    else:
        fwd_pe = None
        fwd_eps = None
        eps_ntm = None
        eps_ntm_2 = None

    # ── 12-Month Analyst Consensus Price Target (TradingView + Normalization) ──
    raw_yahoo_target = info.get("targetMeanPrice")
    if raw_yahoo_target is None or (isinstance(raw_yahoo_target, (int, float)) and (np.isnan(raw_yahoo_target) or raw_yahoo_target <= 0)):
        raw_yahoo_target = info.get("targetMedianPrice")

    tv_data = fetch_tradingview_target(ticker)
    target_mean_val, target_upside_pct = normalize_analyst_target(
        ticker=ticker,
        live_price=current_price,
        tv_data=tv_data,
        raw_yahoo_target=raw_yahoo_target,
    )

    # ── Slice the last ~350 trading days for the interactive price chart ──
    hist_recent = hist_full.tail(350).copy()

    # ── Trailing EPS / P/E evaluation ──
    pe_ok = (
        not is_etf
        and eps is not None
        and isinstance(eps, (int, float))
        and eps > 0
        and ticker not in MA_FALLBACK_TICKERS
    )

    display_name = info.get("shortName") or info.get("longName") or default_name
    if ticker == "SPCX":
        display_name = "Space Exploration Technologies"

    result = {
        "ticker":            ticker,
        "name":              display_name,
        "shortName":         display_name if ticker == "SPCX" else (info.get("shortName") or display_name),
        "longName":          display_name if ticker == "SPCX" else (info.get("longName") or display_name),
        "hist":              hist_recent,
        "info":              info,
        "eps":               eps,
        "pe_mode":           pe_ok,
        "currency":          info.get("currency", "USD"),
        "next_earnings":     next_earnings,
        "current_price":     current_price,
        "ath":               ath,
        "dist_ath":          dist_ath,
        "reg_perf_pct":      reg_perf_pct,
        "reg_perf_abs":      reg_perf_abs,
        "ext_perf_pct":      ext_perf_pct,
        "ext_perf_abs":      ext_perf_abs,
        "ext_label":         ext_label,
        "ext_price":         ext_price,
        "ytd_pct":           ytd_pct,
        "perf_pct":          reg_perf_pct,
        "perf_ext_label":    ext_label,
        "peg_2y":            peg_2y,
        "cagr_2y_pct":       cagr_2y_pct,
        "eps_ntm":           eps_ntm,
        "eps_ntm_2":         eps_ntm_2,
        "is_etf":            is_etf,
        "is_ucits":          is_ucits,
        "ter":               ter,
        "aum":               aum,
        "fund_family":       fund_family,
        "fwd_pe":            fwd_pe,
        "target_mean_price": target_mean_val,
        "target_upside_pct": target_upside_pct,
        "tactical_signals":  tactical_signals,
        "error":             None,
    }

    if pe_ok:
        hist_recent["PE"] = hist_recent["Close"] / eps

        # 90-day fair value corridor (~63 trading days)
        end_date = hist_recent.index[-1]
        start_90 = end_date - pd.Timedelta(days=CORRIDOR_DAYS)
        window_pe_90 = hist_recent.loc[hist_recent.index >= start_90, "PE"]

        pe_current = float(window_pe_90.iloc[-1]) if len(window_pe_90) else np.nan
        pe_lo_90   = float(window_pe_90.quantile(0.10))
        pe_mid_90  = float(window_pe_90.quantile(0.50))
        pe_hi_90   = float(window_pe_90.quantile(0.90))
        pe_std_90  = float(window_pe_90.std()) if len(window_pe_90) > 1 else np.nan

        # 1-Year fair value corridor (~252 trading days / 365 calendar days)
        start_1y = end_date - pd.Timedelta(days=365)
        window_pe_1y = hist_recent.loc[hist_recent.index >= start_1y, "PE"]
        if len(window_pe_1y) < 20:
            window_pe_1y = hist_recent["PE"].tail(min(len(hist_recent), 252))

        pe_lo_1y   = float(window_pe_1y.quantile(0.10))
        pe_mid_1y  = float(window_pe_1y.quantile(0.50))
        pe_hi_1y   = float(window_pe_1y.quantile(0.90))
        pe_std_1y  = float(window_pe_1y.std()) if len(window_pe_1y) > 1 else np.nan

        result["pe_current"] = pe_current
        result["pe_lo_90d"]  = pe_lo_90
        result["pe_mid_90d"] = pe_mid_90
        result["pe_hi_90d"]  = pe_hi_90

        result["pe_lo_1y"]   = pe_lo_1y
        result["pe_mid_1y"]  = pe_mid_1y
        result["pe_hi_1y"]   = pe_hi_1y

        # Legacy backward-compatible keys (defaulting to 90D baseline)
        result["pe_lo"]      = pe_lo_90
        result["pe_mid"]     = pe_mid_90
        result["pe_hi"]      = pe_hi_90

        fair_val_90 = pe_mid_90 * eps
        fair_val_1y = pe_mid_1y * eps

        result["fair_value_90d"] = fair_val_90
        result["fair_value_1y"]  = fair_val_1y
        result["fair_value_price"] = fair_val_90

        # % Above / Below Corridor Median & Upside %
        if pe_mid_90 and not np.isnan(pe_mid_90) and pe_mid_90 > 0 and pe_current and not np.isnan(pe_current):
            result["diff_90d"] = ((pe_current / pe_mid_90) - 1.0) * 100.0
            result["upside_90d"] = ((pe_mid_90 / pe_current) - 1.0) * 100.0
        else:
            result["diff_90d"] = np.nan
            result["upside_90d"] = np.nan

        if pe_mid_1y and not np.isnan(pe_mid_1y) and pe_mid_1y > 0 and pe_current and not np.isnan(pe_current):
            result["diff_1y"] = ((pe_current / pe_mid_1y) - 1.0) * 100.0
            result["upside_1y"] = ((pe_mid_1y / pe_current) - 1.0) * 100.0
        else:
            result["diff_1y"] = np.nan
            result["upside_1y"] = np.nan

        result["upside_to_median"] = result["upside_90d"]

        # Z-Scores relative to corridors
        result["z_90d"] = float((pe_current - pe_mid_90) / pe_std_90) if pe_std_90 and not np.isnan(pe_std_90) and pe_std_90 > 0 else np.nan
        result["z_1y"]  = float((pe_current - pe_mid_1y) / pe_std_1y) if pe_std_1y and not np.isnan(pe_std_1y) and pe_std_1y > 0 else np.nan

    else:
        # Price corridor mode (for ETFs and assets without reliable P/E)
        end_date = hist_recent.index[-1]
        start_90 = end_date - pd.Timedelta(days=CORRIDOR_DAYS)
        window_p_90 = hist_recent.loc[hist_recent.index >= start_90, "Close"]

        p_current = float(window_p_90.iloc[-1]) if len(window_p_90) else np.nan
        p_lo_90   = float(window_p_90.quantile(0.10))
        p_mid_90  = float(window_p_90.quantile(0.50))
        p_hi_90   = float(window_p_90.quantile(0.90))
        p_std_90  = float(window_p_90.std()) if len(window_p_90) > 1 else np.nan

        # 1-Year fair value corridor (~252 trading days / 365 calendar days)
        start_1y = end_date - pd.Timedelta(days=365)
        window_p_1y = hist_recent.loc[hist_recent.index >= start_1y, "Close"]
        if len(window_p_1y) < 20:
            window_p_1y = hist_recent["Close"].tail(min(len(hist_recent), 252))

        p_lo_1y   = float(window_p_1y.quantile(0.10))
        p_mid_1y  = float(window_p_1y.quantile(0.50))
        p_hi_1y   = float(window_p_1y.quantile(0.90))
        p_std_1y  = float(window_p_1y.std()) if len(window_p_1y) > 1 else np.nan

        result["price_current"] = p_current
        result["price_lo_90d"]  = p_lo_90
        result["price_mid_90d"] = p_mid_90
        result["price_hi_90d"]  = p_hi_90

        result["price_lo_1y"]   = p_lo_1y
        result["price_mid_1y"]  = p_mid_1y
        result["price_hi_1y"]   = p_hi_1y

        # Legacy backward-compatible keys
        result["price_lo"]      = p_lo_90
        result["price_mid"]     = p_mid_90
        result["price_hi"]      = p_hi_90

        result["fair_value_90d"] = p_mid_90
        result["fair_value_1y"]  = p_mid_1y
        result["fair_value_price"] = p_mid_90

        # % Above / Below Corridor Median & Upside %
        if p_mid_90 and not np.isnan(p_mid_90) and p_mid_90 > 0 and p_current and not np.isnan(p_current):
            result["diff_90d"] = ((p_current / p_mid_90) - 1.0) * 100.0
            result["upside_90d"] = ((p_mid_90 / p_current) - 1.0) * 100.0
        else:
            result["diff_90d"] = np.nan
            result["upside_90d"] = np.nan

        if p_mid_1y and not np.isnan(p_mid_1y) and p_mid_1y > 0 and p_current and not np.isnan(p_current):
            result["diff_1y"] = ((p_current / p_mid_1y) - 1.0) * 100.0
            result["upside_1y"] = ((p_mid_1y / p_current) - 1.0) * 100.0
        else:
            result["diff_1y"] = np.nan
            result["upside_1y"] = np.nan

        result["upside_to_median"] = result["upside_90d"]

        # Z-Scores relative to corridors
        result["z_90d"] = float((p_current - p_mid_90) / p_std_90) if p_std_90 and not np.isnan(p_std_90) and p_std_90 > 0 else np.nan
        result["z_1y"]  = float((p_current - p_mid_1y) / p_std_1y) if p_std_1y and not np.isnan(p_std_1y) and p_std_1y > 0 else np.nan

    return result


def compute_status(data: dict, timeframe: str = "90-Day") -> str:
    """
    Classify equity into 'Buy Zone', 'Standard DCA', or 'Wait for Pullback' based on corridor median.
      • Buy Zone (Green): <= -5.0% below corridor median (discounted accumulation window)
      • Standard DCA (Amber): Between -5.0% and +5.0% of corridor median (fair value baseline)
      • Wait for Pullback (Red): >= +5.0% above corridor median (stretched valuation)
    """
    if data.get("error"):
        return "Standard DCA"

    if timeframe == "1-Year":
        pct = data.get("diff_1y")
        if pct is None or np.isnan(pct):
            if data.get("pe_mode"):
                cur = data.get("pe_current", np.nan)
                mid = data.get("pe_mid_1y", data.get("pe_mid", np.nan))
            else:
                cur = data.get("price_current", np.nan)
                mid = data.get("price_mid_1y", data.get("price_mid", np.nan))
            if np.isnan(cur) or np.isnan(mid) or mid == 0:
                return "Standard DCA"
            pct = (cur / mid - 1.0) * 100.0
    else:
        pct = data.get("diff_90d")
        if pct is None or np.isnan(pct):
            if data.get("pe_mode"):
                cur = data.get("pe_current", np.nan)
                mid = data.get("pe_mid_90d", data.get("pe_mid", np.nan))
            else:
                cur = data.get("price_current", np.nan)
                mid = data.get("price_mid_90d", data.get("price_mid", np.nan))
            if np.isnan(cur) or np.isnan(mid) or mid == 0:
                return "Standard DCA"
            pct = (cur / mid - 1.0) * 100.0

    if pct <= -5.0:
        return "Buy Zone"
    elif pct >= 5.0:
        return "Wait for Pullback"
    return "Standard DCA"


def badge_html(status: str) -> str:
    css = {
        "Buy Zone":          "badge-attractive",
        "Standard DCA":      "badge-neutral",
        "Wait for Pullback": "badge-overvalued",
        # Backward-compatibility fallbacks
        "Attractive": "badge-attractive",
        "Neutral":    "badge-neutral",
        "Overvalued": "badge-overvalued",
    }.get(status, "badge-neutral")
    return f'<span class="badge {css}">● {status}</span>'


def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> tuple[bool, str]:
    """
    Sends an instant push notification via the official Telegram Bot API.
    Supports HTML parsing mode and returns (success: bool, status_message: str).
    """
    token = (bot_token or "").strip()
    chat = (chat_id or "").strip()
    if not token or not chat:
        return False, "Missing Telegram Bot Token or Chat ID."
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        res = requests.post(url, json=payload, timeout=8)
        data = res.json()
        if data.get("ok"):
            return True, "Telegram alert sent successfully!"
        else:
            return False, f"Telegram API Error: {data.get('description', 'Unknown error')}"
    except Exception as ex:
        return False, f"Telegram Connection Error: {ex}"


def send_email_alert(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    receiver_email: str,
    subject: str,
    body_html: str,
) -> tuple[bool, str]:
    """
    Sends an HTML email alert via Python smtplib with STARTTLS encryption.
    Returns (success: bool, status_message: str).
    """
    server = (smtp_server or "").strip()
    sender = (sender_email or "").strip()
    pwd = (sender_password or "").strip()
    receiver = (receiver_email or "").strip()
    if not server or not sender or not pwd or not receiver:
        return False, "Missing SMTP Server, Sender, Password, or Receiver Email."
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        part = MIMEText(body_html, "html")
        msg.attach(part)

        port = int(smtp_port) if smtp_port else 587
        if port == 465:
            with smtplib.SMTP_SSL(server, port, timeout=10) as s:
                s.login(sender, pwd)
                s.sendmail(sender, receiver, msg.as_string())
        else:
            with smtplib.SMTP(server, port, timeout=10) as s:
                s.starttls()
                s.login(sender, pwd)
                s.sendmail(sender, receiver, msg.as_string())
        return True, "Email alert sent successfully!"
    except Exception as ex:
        return False, f"Email Delivery Error: {ex}"


def check_and_dispatch_signal_alerts(all_data: dict, timeframe: str = "90-Day") -> list[str]:
    """
    Scans tracked equities for tactical entry signals (DCA, DEEPLY OVERSOLD, CAPITULATION)
    triggered on the latest market bars (last 1-2 trading days).
    Uses st.session_state['dispatched_alerts'] cache to strictly prevent duplicate alerts.
    """
    if not st.session_state.get("alerts_enabled", False):
        return []

    if "dispatched_alerts" not in st.session_state:
        st.session_state["dispatched_alerts"] = set()

    alerts_sent = []

    for tk, d in all_data.items():
        if d.get("error"):
            continue
        hist = d.get("hist", pd.DataFrame())
        if hist.empty:
            continue
        signals = d.get("tactical_signals", [])
        if not signals:
            continue

        trading_dates = list(hist.index)
        latest_ts = pd.Timestamp(trading_dates[-1])
        recent_window = set(trading_dates[-2:])

        for sig_ts, sig_low, sig_label, sig_color in signals:
            sig_pdt = pd.Timestamp(sig_ts)
            if sig_ts in recent_window or sig_pdt in recent_window:
                date_str = sig_pdt.strftime("%Y-%m-%d")
                dedup_key = f"{tk}_{sig_label}_{date_str}"

                if dedup_key not in st.session_state["dispatched_alerts"]:
                    cur_price = d.get("price_current", sig_low)
                    pct_diff = d.get("diff_1y" if timeframe == "1-Year" else "diff_90d", 0.0)

                    if "CAPITULATION" in sig_label or "CRASH" in sig_label:
                        canonical_label = "CAPITULATION"
                        emoji = "🚨"
                    elif "DEEPLY" in sig_label or "OVERSOLD" in sig_label or "VALUE" in sig_label:
                        canonical_label = "DEEPLY OVERSOLD"
                        emoji = "⚡"
                    else:
                        canonical_label = "DCA"
                        emoji = "🎯"

                    channel = st.session_state.get("alert_channel", "Telegram Bot")
                    success = False

                    if channel == "Telegram Bot":
                        token = st.session_state.get("tg_bot_token", "").strip()
                        chat_id = st.session_state.get("tg_chat_id", "").strip()
                        if token and chat_id:
                            tg_msg = (
                                f"{emoji} <b>VALUATION RADAR SIGNAL TRIGGERED</b>\n\n"
                                f"🎯 <b>Equity:</b> <code>{tk}</code> ({d.get('name', tk)})\n"
                                f"⚡ <b>Signal:</b> <b>{canonical_label}</b>\n"
                                f"💵 <b>Current Price:</b> ${cur_price:.2f}\n"
                                f"📊 <b>Corridor Deviation:</b> {pct_diff:+.1f}%\n"
                                f"📅 <b>Bar Date:</b> {date_str}\n\n"
                                f"<i>The Stock Valuation Radar • @theinvestingdean</i>"
                            )
                            success, _ = send_telegram_alert(token, chat_id, tg_msg)
                    else:
                        smtp_srv = st.session_state.get("email_smtp_server", "smtp.gmail.com").strip()
                        smtp_p = int(st.session_state.get("email_smtp_port", 587))
                        sender = st.session_state.get("email_sender", "").strip()
                        pwd = st.session_state.get("email_password", "").strip()
                        rcvr = st.session_state.get("email_receiver", "").strip()
                        if sender and pwd and rcvr:
                            sub = f"{emoji} Valuation Radar Alert: {tk} triggered [{canonical_label}]"
                            html_body = f"""
                            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 520px; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px; background: #FFFFFF;">
                              <div style="border-bottom: 2px solid #EAB308; padding-bottom: 10px; margin-bottom: 14px;">
                                <h2 style="margin: 0; color: #0F172A; font-size: 1.25rem;">The Stock Valuation Radar</h2>
                                <span style="font-size: 0.80rem; color: #854D0E; font-weight: 700;">Tactical Entry Notification</span>
                              </div>
                              <p style="font-size: 1.05rem; color: #1E293B;">
                                <b>{tk}</b> has flashed a tactical <b>{canonical_label}</b> signal!
                              </p>
                              <table style="width: 100%; border-collapse: collapse; font-size: 0.90rem; margin: 14px 0;">
                                <tr><td style="color: #64748B; padding: 4px 0;">Signal:</td><td style="font-weight: 700; color: #0F172A;">{canonical_label}</td></tr>
                                <tr><td style="color: #64748B; padding: 4px 0;">Price:</td><td style="font-weight: 700; color: #0F172A;">${cur_price:.2f}</td></tr>
                                <tr><td style="color: #64748B; padding: 4px 0;">Corridor Deviation:</td><td style="font-weight: 700; color: #0F172A;">{pct_diff:+.1f}%</td></tr>
                                <tr><td style="color: #64748B; padding: 4px 0;">Bar Date:</td><td style="color: #0F172A;">{date_str}</td></tr>
                              </table>
                              <div style="margin-top: 20px; padding-top: 10px; border-top: 1px dashed #E2E8F0; font-size: 0.75rem; color: #94A3B8;">
                                Automated alert by @theinvestingdean
                              </div>
                            </div>
                            """
                            success, _ = send_email_alert(smtp_srv, smtp_p, sender, pwd, rcvr, sub, html_body)

                    if success:
                        st.session_state["dispatched_alerts"].add(dedup_key)
                        alerts_sent.append(f"{tk} [{canonical_label}]")

    return alerts_sent


def render_executive_market_highlights(visible_data: dict, timeframe: str = "90-Day") -> None:
    """
    Renders Executive Market Highlights using native st.columns() for full desktop
    and mobile responsiveness:
      1. Basket Breadth (% of tracked assets trading above active corridor median)
      2. Top Value Opportunities (lowest % vs average, strict semantic thresholds, no Z-Scores)
      3. Most Overextended (highest % vs average, strict semantic thresholds, no Z-Scores)
      4. Recent Tactical Signals (dynamically lists all tickers without limit, vertically scrollable)
    """
    if not visible_data:
        return

    total_count = len(visible_data)
    count_overstretched = 0
    count_above_zero = 0
    items = []

    for tk, d in visible_data.items():
        if d.get("error"):
            continue
        if d.get("pe_mode"):
            cur = d.get("pe_current", np.nan)
            mid = d.get("pe_mid_1y" if timeframe == "1-Year" else "pe_mid_90d", d.get("pe_mid", np.nan))
        else:
            cur = d.get("price_current", np.nan)
            mid = d.get("price_mid_1y" if timeframe == "1-Year" else "price_mid_90d", d.get("price_mid", np.nan))

        pct_diff = d.get("diff_1y" if timeframe == "1-Year" else "diff_90d")
        if pct_diff is None or np.isnan(pct_diff):
            pct_diff = ((cur / mid) - 1.0) * 100.0 if mid and not np.isnan(mid) and not np.isnan(cur) else 0.0

        status = compute_status(d, timeframe=timeframe)
        if status in ("Wait for Pullback", "Overvalued") or pct_diff >= 5.0:
            count_overstretched += 1
        if pct_diff > 0:
            count_above_zero += 1

        items.append({
            "ticker": tk,
            "diff": pct_diff,
        })

    overstretched_pct = (count_overstretched / total_count * 100.0) if total_count > 0 else 0.0
    breadth_desc = "Overbought Skew" if count_above_zero >= (total_count * 0.6) else ("Oversold Skew" if count_above_zero <= (total_count * 0.4) else "Neutral Balance")
    framework_badge_lbl = "1Y Valuation Framework" if timeframe == "1-Year" else "90D Valuation Framework"

    # Helper for strict conditional formatting colors:
    # Green: <= -5.0%
    # Amber (Yellow/Orange): -4.99% to +4.99%
    # Red: >= +5.0%
    def get_diff_pill(diff: float) -> str:
        if diff <= -5.0:
            color = "#047857"  # Green (Buy Zone)
        elif diff >= 5.0:
            color = "#B91C1C"  # Red (Wait for Pullback)
        else:
            color = "#B45309"  # Amber (Standard DCA: -4.99% to +4.99%)
        return f'<span style="font-size: 0.78rem; color: {color}; font-weight: 700;">{diff:+.1f}% vs Avg</span>'

    # Top Value Opportunities (strictly <= 0% distance to corridor average/median)
    value_items = [x for x in items if x["diff"] is not None and not np.isnan(x["diff"]) and x["diff"] <= 0.0]
    sorted_by_val = sorted(value_items, key=lambda x: x["diff"])
    top_value = sorted_by_val[:5]
    if top_value:
        val_rows = [
            f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 2px 0; border-bottom: 1px dashed rgba(226, 232, 240, 0.5);">'
            f'  <a href="#card-{item["ticker"]}" style="color: #0F172A; font-size: 0.88rem; font-weight: 700; text-decoration: none;" title="Jump to {item["ticker"]} card">{item["ticker"]}</a>'
            f'  {get_diff_pill(item["diff"])}'
            f'</div>'
            for item in top_value
        ]
        val_html = "".join(val_rows)
    else:
        val_html = '<div style="color: #64748B; font-size: 0.80rem; font-style: italic; line-height: 1.4; padding: 4px 0;">No tracked assets are currently trading at a discount.</div>'

    # Most Overextended (strictly > 0% distance above corridor average/median)
    over_items = [x for x in items if x["diff"] is not None and not np.isnan(x["diff"]) and x["diff"] > 0.0]
    sorted_by_over = sorted(over_items, key=lambda x: x["diff"], reverse=True)
    top_overextended = sorted_by_over[:5]
    if top_overextended:
        over_rows = [
            f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 2px 0; border-bottom: 1px dashed rgba(226, 232, 240, 0.5);">'
            f'  <a href="#card-{item["ticker"]}" style="color: #0F172A; font-size: 0.88rem; font-weight: 700; text-decoration: none;" title="Jump to {item["ticker"]} card">{item["ticker"]}</a>'
            f'  {get_diff_pill(item["diff"])}'
            f'</div>'
            for item in top_overextended
        ]
        over_html = "".join(over_rows)
    else:
        over_html = '<div style="color: #64748B; font-size: 0.80rem; font-style: italic; line-height: 1.4; padding: 4px 0;">No tracked assets are currently overextended.</div>'

    # Recent Tactical Signals (scan last 5-7 trading days across all tracked tickers, NO arbitrary display cap)
    recent_signals = []
    for tk, d in visible_data.items():
        if d.get("error"):
            continue
        hist = d.get("hist", pd.DataFrame())
        if hist.empty:
            continue
        signals = d.get("tactical_signals", [])
        if not signals:
            continue

        trading_dates = list(hist.index)
        window_dates = set(trading_dates[-7:])
        latest_ts = pd.Timestamp(trading_dates[-1])

        for sig_ts, sig_low, sig_label, sig_color in signals:
            sig_pdt = pd.Timestamp(sig_ts)
            if sig_ts in window_dates or sig_pdt in window_dates:
                trading_idx = trading_dates.index(sig_ts) if sig_ts in trading_dates else len(trading_dates) - 1
                bars_ago = len(trading_dates) - 1 - trading_idx
                cal_days = (latest_ts.date() - sig_pdt.date()).days

                if cal_days == 0:
                    time_ago_str = "Today"
                elif cal_days == 1:
                    time_ago_str = "1 day ago"
                else:
                    time_ago_str = f"{cal_days} days ago"

                # Canonical badge formatting
                if "CAPITULATION" in sig_label or "CRASH" in sig_label:
                    badge_lbl = "CAPITULATION"
                    badge_bg = "#FFEDD5"
                    badge_text = "#9A3412"
                    badge_border = "#F97316"
                elif "DEEPLY" in sig_label or "OVERSOLD" in sig_label or "VALUE" in sig_label:
                    badge_lbl = "DEEPLY OVERSOLD"
                    badge_bg = "#FEF08A"
                    badge_text = "#854D0E"
                    badge_border = "#FDE047"
                else:
                    badge_lbl = "DCA"
                    badge_bg = "#DCFCE7"
                    badge_text = "#14532D"
                    badge_border = "#86EFAC"

                recent_signals.append({
                    "ticker": tk,
                    "badge": badge_lbl,
                    "bg": badge_bg,
                    "text": badge_text,
                    "border": badge_border,
                    "time_ago": time_ago_str,
                    "bars_ago": bars_ago,
                    "cal_days": cal_days,
                })

    # Sort recent signals by recency (least days ago first), deduplicate by ticker
    recent_signals = sorted(recent_signals, key=lambda x: (x["cal_days"], x["bars_ago"]))
    unique_signals = []
    seen_tk = set()
    for s in recent_signals:
        if s["ticker"] not in seen_tk:
            seen_tk.add(s["ticker"])
            unique_signals.append(s)

    # Render ALL signals dynamically (no hardcoded slicing cap)
    if unique_signals:
        sig_rows = [
            f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 3px 0; border-bottom: 1px dashed rgba(226, 232, 240, 0.6);">'
            f'  <div style="display: flex; align-items: center; gap: 6px; flex-wrap: nowrap;">'
            f'    <a href="#card-{s["ticker"]}" style="color: #0F172A; font-size: 0.90rem; font-weight: 700; text-decoration: none;" title="Jump to {s["ticker"]} card">{s["ticker"]}</a>'
            f'    <span style="display: inline-block; padding: 1px 6px; font-size: 0.68rem; font-weight: 800; border-radius: 4px; background-color: {s["bg"]}; color: {s["text"]}; border: 1px solid {s["border"]}; white-space: nowrap;">{s["badge"]}</span>'
            f'  </div>'
            f'  <span style="font-size: 0.72rem; color: #64748B; font-weight: 500; white-space: nowrap;">{s["time_ago"]}</span>'
            f'</div>'
            for s in unique_signals
        ]
        signals_html = "".join(sig_rows)
    else:
        signals_html = '<div style="color: #64748B; font-size: 0.80rem; font-style: italic; margin-top: 4px;">No signals flashed in the last 7 days.</div>'

    # Section Header
    st.html(f"""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #EAB308; border-radius: 10px; padding: 10px 16px; margin: 16px 0 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.02); display: flex; justify-content: space-between; align-items: center;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.02rem; font-weight: 800; color: #0F172A; letter-spacing: -0.01em;">Executive Market Highlights</span>
        <span style="font-size: 0.72rem; font-weight: 700; color: #854D0E; background-color: #FEF9C3; border: 1px solid #FDE047; padding: 2px 8px; border-radius: 9999px;">{framework_badge_lbl}</span>
      </div>
    </div>
    """)

    # 4 Cards using native st.columns(4) for desktop grid and mobile vertical stacking
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.html(f"""
        <div class="highlights-card" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #EAB308; border-radius: 8px; padding: 12px 14px; min-height: 105px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Basket Breadth</div>
            <div style="font-size: 0.86rem; color: #0F172A; font-weight: 600; line-height: 1.35;">
              <b>{count_overstretched} of {total_count}</b> assets (<b>{overstretched_pct:.0f}%</b>) &gt; +5% above average.
            </div>
          </div>
          <div style="font-size: 0.75rem; color: #854D0E; font-weight: 600; margin-top: 6px; padding-top: 4px; border-top: 1px dashed rgba(226, 232, 240, 0.8);">• Bias: {breadth_desc}</div>
        </div>
        """)
    with c2:
        st.html(f"""
        <div class="highlights-card" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #10B981; border-radius: 8px; padding: 12px 14px; min-height: 105px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="font-size: 0.72rem; font-weight: 700; color: #047857; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Top Value Opportunities</div>
            <div class="custom-signals-scroll" style="max-height: 220px; overflow-y: auto; padding-right: 5px; display: flex; flex-direction: column; gap: 2px; margin-top: 2px;">
              {val_html}
            </div>
          </div>
          <div style="font-size: 0.70rem; color: #64748B; margin-top: 6px; padding-top: 4px; border-top: 1px dashed rgba(226, 232, 240, 0.8);">Deepest corridor discounts</div>
        </div>
        """)
    with c3:
        st.html(f"""
        <div class="highlights-card" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #EF4444; border-radius: 8px; padding: 12px 14px; min-height: 105px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="font-size: 0.72rem; font-weight: 700; color: #B91C1C; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Most Overextended</div>
            <div class="custom-signals-scroll" style="max-height: 220px; overflow-y: auto; padding-right: 5px; display: flex; flex-direction: column; gap: 2px; margin-top: 2px;">
              {over_html}
            </div>
          </div>
          <div style="font-size: 0.70rem; color: #64748B; margin-top: 6px; padding-top: 4px; border-top: 1px dashed rgba(226, 232, 240, 0.8);">Furthest above corridor median</div>
        </div>
        """)
    with c4:
        count_badge = f'<span style="font-size: 0.68rem; font-weight: 800; color: #4338CA; background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 9999px; padding: 1px 6px;">{len(unique_signals)}</span>' if unique_signals else ''
        st.html(f"""
        <div class="highlights-card" style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #6366F1; border-radius: 8px; padding: 12px 14px; min-height: 105px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
              <span style="font-size: 0.72rem; font-weight: 700; color: #4338CA; text-transform: uppercase; letter-spacing: 0.05em;">Recent Tactical Signals</span>
              {count_badge}
            </div>
            <div class="custom-signals-scroll" style="max-height: 220px; overflow-y: auto; padding-right: 5px; display: flex; flex-direction: column; gap: 4px; margin-top: 2px;">
              {signals_html}
            </div>
          </div>
          <div style="font-size: 0.70rem; color: #64748B; margin-top: 6px; padding-top: 4px; border-top: 1px dashed rgba(226, 232, 240, 0.8);">TID Engine entries (last 7 days)</div>
        </div>
        """)

    # Check and dispatch live notifications for new tactical bar signals
    dispatched_now = check_and_dispatch_signal_alerts(visible_data, timeframe=timeframe)
    if dispatched_now:
        st.toast(f"🔔 Dispatched {len(dispatched_now)} live signal alert(s): {', '.join(dispatched_now)}", icon="📲")


def make_market_highlights_banner_html(visible_data: dict, timeframe: str = "90-Day") -> str:
    """Backward compatibility fallback if needed."""
    return ""


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def make_price_chart(data: dict) -> go.Figure:
    """
    Clean, modern price chart featuring:
      • Daily Close Price (bold royal blue line)
      • Bollinger Bands:
          +2.0σ: Solid Red (#EF4444)
          +1.5σ: Dashed Red (#EF4444)
          -1.5σ: Dashed Green (#10B981)
          -2.0σ: Solid Green (#10B981)
      • Soft pastel shading:
          Overbought Zone: between +1.5σ and +2.0σ (light red)
          Oversold / Buy Pocket: between -1.5σ and -2.0σ (light green)
          Center: completely clear on pure white background
      • 20-day SMA midline (BB Mid) in subtle gray
      • 50-day SMA and 200-day SMA
      • Horizontal top-left legend
    """
    hist  = data.get("hist", pd.DataFrame())
    ccy   = data.get("currency", "USD")
    price = hist["Close"].dropna() if "Close" in hist.columns else pd.Series(dtype=float)

    def s_get(col):
        return hist[col].dropna() if col in hist.columns else pd.Series(dtype=float)

    bb_hi2  = s_get("BB_hi2")
    bb_hi15 = s_get("BB_hi15")
    bb_mid  = s_get("BB_mid")
    bb_lo15 = s_get("BB_lo15")
    bb_lo2  = s_get("BB_lo2")

    ma50  = s_get(f"MA{MA_SHORT}")
    ma200 = s_get(f"MA{MA_LONG}")
    show_ma200 = len(ma200) >= 100

    fig = go.Figure()

    # ── Helper for shaded pockets ──
    def fill_pocket(upper: pd.Series, lower: pd.Series, color: str, name: str):
        idx = upper.index.intersection(lower.index)
        if not len(idx):
            return
        fig.add_trace(go.Scatter(
            x=list(idx) + list(idx[::-1]),
            y=list(upper.reindex(idx).values) + list(lower.reindex(idx).values),
            fill="toself",
            fillcolor=color,
            line=dict(color="rgba(0,0,0,0)"),
            name=name,
            hoverinfo="skip",
            showlegend=False,
        ))

    # 1. Overbought Zone (+1.5σ to +2.0σ) — soft red pastel fill
    fill_pocket(bb_hi2, bb_hi15, "rgba(239, 68, 68, 0.12)", "Overbought (+1.5–2σ)")

    # 2. Oversold / Buy Pocket (-2.0σ to -1.5σ) — soft green pastel fill
    fill_pocket(bb_lo15, bb_lo2, "rgba(16, 185, 129, 0.12)", "Oversold (−1.5–2σ)")

    # (Note: NO fill between -1.5σ and +1.5σ — completely clear on white)

    # 3. Upper Outer Band (+2.0σ): Solid Red line (#EF4444)
    if len(bb_hi2):
        fig.add_trace(go.Scatter(
            x=bb_hi2.index, y=bb_hi2.values, mode="lines",
            line=dict(color="#EF4444", width=1.4, dash="solid"),
            name="BB +2.0σ", opacity=0.90, showlegend=False,
        ))

    # 4. Upper Inner Band (+1.5σ): Dashed Red line (#EF4444)
    if len(bb_hi15):
        fig.add_trace(go.Scatter(
            x=bb_hi15.index, y=bb_hi15.values, mode="lines",
            line=dict(color="#EF4444", width=1.1, dash="dash"),
            name="BB +1.5σ", opacity=0.75, showlegend=False,
        ))

    # 5. Lower Inner Band (-1.5σ): Dashed Green line (#10B981)
    if len(bb_lo15):
        fig.add_trace(go.Scatter(
            x=bb_lo15.index, y=bb_lo15.values, mode="lines",
            line=dict(color="#10B981", width=1.1, dash="dash"),
            name="BB −1.5σ", opacity=0.75, showlegend=False,
        ))

    # 6. Lower Outer Band (-2.0σ): Solid Green line (#10B981)
    if len(bb_lo2):
        fig.add_trace(go.Scatter(
            x=bb_lo2.index, y=bb_lo2.values, mode="lines",
            line=dict(color="#10B981", width=1.4, dash="solid"),
            name="BB −2.0σ", opacity=0.90, showlegend=False,
        ))

    # 7. BB Midline (20-day SMA baseline, thin gray, no fill)
    if len(bb_mid):
        fig.add_trace(go.Scatter(
            x=bb_mid.index, y=bb_mid.values, mode="lines",
            line=dict(color="#94A3B8", width=1.0),
            name="SMA 20 (Mid)", opacity=0.70, showlegend=False,
        ))

    # 8. SMA 50
    if len(ma50):
        fig.add_trace(go.Scatter(
            x=ma50.index, y=ma50.values, mode="lines",
            line=dict(color="#0EA5E9", width=1.5, dash="dashdot"),
            name="SMA 50", opacity=0.90, showlegend=False,
        ))

    # 9. SMA 200 (if available)
    if show_ma200:
        fig.add_trace(go.Scatter(
            x=ma200.index, y=ma200.values, mode="lines",
            line=dict(color="#8B5CF6", width=1.5, dash="dashdot"),
            name="SMA 200", opacity=0.85, showlegend=False,
        ))

    # 10. Daily Close Price (bold primary line on top)
    if len(price):
        fig.add_trace(go.Scatter(
            x=price.index, y=price.values, mode="lines",
            line=dict(color=ACCENT_BLUE, width=2.2),
            name="Close", showlegend=False,
        ))
        cur_p = float(price.iloc[-1])
        fig.add_trace(go.Scatter(
            x=[price.index[-1]], y=[cur_p], mode="markers",
            marker=dict(color=ACCENT_BLUE, size=8, symbol="circle",
                        line=dict(color="#FFFFFF", width=2)),
            name=f"Current: {cur_p:.2f}", showlegend=False,
        ))

    # ── Dynamic 6 to 9-Month Visible Range & Autoscale ──
    if len(price):
        end_date = price.index[-1]
        # Restrict default visible window to the last 7 months (~210 days / 6-9 months)
        start_date = end_date - pd.DateOffset(months=7)
        x_range = [
            start_date.strftime("%Y-%m-%d"),
            (end_date + pd.Timedelta(days=3)).strftime("%Y-%m-%d"),
        ]

        # ── TID - Tactical DCA Annotations (Visible 6-9 Month Window) ──
        tactical_signals = data.get("tactical_signals", [])
        vis_signals = []
        if tactical_signals:
            for sig in tactical_signals:
                sig_date, sig_low, sig_label, sig_color = sig
                sig_ts = pd.to_datetime(sig_date)
                if start_date <= sig_ts <= (end_date + pd.Timedelta(days=3)):
                    vis_signals.append((sig_ts, float(sig_low), sig_label, sig_color))

        # Multi-line badge label formatting to prevent horizontal footprint clashing
        LABEL_FORMAT_MAP = {
            "DEEPLY OVERSOLD": "DEEPLY<br>OVERSOLD",
            "BETTER VALUE":    "BETTER<br>VALUE",
            "BETTER DCA":      "BETTER<br>DCA",
            "DEEPER CRASH":    "DEEPER<br>CRASH",
            "CAPITULATION":    "CAPITULATION",
            "DCA":             "DCA",
        }

        # Trading bar index lookup for collision detection
        price_idx_map = {pd.to_datetime(d).normalize(): i for i, d in enumerate(price.index)}

        # Pre-scan to detect if any collisions occur within 3 bars and calculate dynamic offsets
        prev_idx = -999
        prev_ts = None
        prev_yshift = -18
        signal_configs = []

        for sig_ts, sig_low, sig_label, sig_color in vis_signals:
            curr_idx = price_idx_map.get(sig_ts.normalize(), -999)
            is_close_bars = (curr_idx != -999 and (curr_idx - prev_idx) <= 3)
            is_close_days = (prev_ts is not None and (sig_ts - prev_ts).days <= 4)

            if is_close_bars or is_close_days:
                if prev_yshift == -18:
                    yshift = -32
                    ay = 32
                else:
                    yshift = -18
                    ay = 20
            else:
                yshift = -18
                ay = 20

            prev_idx = curr_idx
            prev_ts = sig_ts
            prev_yshift = yshift
            signal_configs.append((sig_ts, sig_low, sig_label, sig_color, yshift, ay))

        has_stack = any(cfg[4] == -32 for cfg in signal_configs)

        # Autoscale Y-axis specifically over the visible 6-9 month window
        window_mask = price.index >= start_date
        vis_all = [
            price.loc[window_mask],
            bb_hi2.loc[bb_hi2.index >= start_date] if len(bb_hi2) else pd.Series(dtype=float),
            bb_lo2.loc[bb_lo2.index >= start_date] if len(bb_lo2) else pd.Series(dtype=float),
            ma50.loc[ma50.index >= start_date] if len(ma50) else pd.Series(dtype=float),
        ]
        if show_ma200 and len(ma200):
            vis_all.append(ma200.loc[ma200.index >= start_date])
        if vis_signals:
            vis_all.append(pd.Series([s[1] for s in vis_signals]))

        comb_vis = pd.concat([s for s in vis_all if len(s)]).dropna()
        if len(comb_vis):
            ymin = float(comb_vis.min())
            ymax = float(comb_vis.max())
            pad = (ymax - ymin) * 0.08
            pad_bottom = (ymax - ymin) * 0.16 if has_stack else ((ymax - ymin) * 0.12 if vis_signals else pad)
            y_range = [max(0.0, ymin - pad_bottom), ymax + pad]
        else:
            y_range = None

        # Render tactical entry annotations directly beneath the price series
        for sig_ts, sig_low, sig_label, sig_color, yshift, ay in signal_configs:
            sig_date_str = sig_ts.strftime("%Y-%m-%d")

            # Style Badges based on Tier
            if sig_label in ("DCA", "BETTER DCA"):
                bg_color = "#22C55E"    # Vibrant Green
                text_color = "#052E16"  # Bold Dark Green
                border_color = "#16A34A"
            elif sig_label in ("DEEPLY OVERSOLD", "BETTER VALUE"):
                bg_color = "#FACC15"    # Amber Yellow
                text_color = "#422006"  # Bold Dark Brown
                border_color = "#EAB308"
            elif sig_label in ("CAPITULATION", "DEEPER CRASH"):
                bg_color = "#F97316"    # Orange
                text_color = "#FFFFFF"  # Bold White
                border_color = "#EA580C"
            else:
                bg_color = sig_color
                text_color = "#FFFFFF"
                border_color = sig_color

            badge_text = LABEL_FORMAT_MAP.get(sig_label, sig_label.replace(" ", "<br>"))

            fig.add_annotation(
                x=sig_date_str,
                y=sig_low,
                text=f"<b>{badge_text}</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor=border_color,
                ax=0,
                ay=ay,
                xanchor="center",
                yanchor="top",
                yshift=yshift,
                font=dict(size=9, color=text_color, family="system-ui, -apple-system, sans-serif"),
                bgcolor=bg_color,
                bordercolor=border_color,
                borderwidth=1,
                borderpad=3,
                opacity=0.96,
            )
    else:
        x_range = None
        y_range = None

    # ── Plotly Layout (Scroll-Safe Preview for Dashboard Cards) ──
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor="#FFFFFF",
        font=dict(color=TEXT_DARK, size=11),
        showlegend=False,
        margin=dict(l=38, r=12, t=18, b=26),
        xaxis=dict(
            gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
            color=MUTED_SLATE, linecolor=BORDER_COLOR,
            range=x_range,
            fixedrange=True,
        ),
        yaxis=dict(
            title=f"Price ({ccy})",
            gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
            color=MUTED_SLATE, linecolor=BORDER_COLOR,
            range=y_range,
            fixedrange=True,
        ),
        dragmode=False,
        hovermode=False,
        height=290,
    )
    return fig



def make_master_legend_html() -> str:
    """
    Compact master legend bar placed once directly above the stock grid.
    Consolidates indicators across all cards to eliminate repetitive chart legends:
    Close, SMA 20, SMA 50, SMA 200, BB +2.0σ, BB -1.5σ, Overbought/Oversold zones.
    """
    return """
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); display: flex; flex-direction: column; gap: 8px;">
      <!-- Row 1: Title and Core Technical Lines -->
      <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 0.76rem; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em;">Master Chart Guide</span>
          <span style="font-size: 0.72rem; color: #64748B;">• Consolidated Technical Indicators</span>
        </div>
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 14px; font-size: 0.74rem; color: #334155; font-weight: 600;">
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 3px; background-color: #2563EB; border-radius: 2px;"></span>
            <span>Close</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 2px; background-color: #94A3B8;"></span>
            <span>SMA 20 (Mid)</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 0; border-top: 2px dashed #0EA5E9;"></span>
            <span>SMA 50</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 0; border-top: 2px dashed #8B5CF6;"></span>
            <span>SMA 200</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 2px; background-color: #EF4444;"></span>
            <span>BB +2.0σ</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 0; border-top: 2px dashed #EF4444;"></span>
            <span>BB +1.5σ</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 0; border-top: 2px dashed #10B981;"></span>
            <span>BB −1.5σ</span>
          </div>
          <div style="display: flex; align-items: center; gap: 5px;">
            <span style="display: inline-block; width: 14px; height: 2px; background-color: #10B981;"></span>
            <span>BB −2.0σ</span>
          </div>
        </div>
      </div>
      <!-- Row 2: Shaded Corridor Zones cleanly grouped together -->
      <div style="display: flex; align-items: center; gap: 16px; font-size: 0.74rem; color: #334155; font-weight: 600; padding-top: 6px; border-top: 1px dashed #F1F5F9;">
        <span style="font-size: 0.70rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">Corridor Zones:</span>
        <div style="display: flex; align-items: center; gap: 5px;">
          <span style="display: inline-block; width: 12px; height: 10px; background-color: rgba(239, 68, 68, 0.22); border: 1px solid #EF4444; border-radius: 2px;"></span>
          <span>Overbought Zone</span>
        </div>
        <div style="display: flex; align-items: center; gap: 5px;">
          <span style="display: inline-block; width: 12px; height: 10px; background-color: rgba(16, 185, 129, 0.22); border: 1px solid #10B981; border-radius: 2px;"></span>
          <span>Oversold Zone</span>
        </div>
      </div>
      <!-- Row 3: TID - Tactical DCA Entry Badges -->
      <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 14px; font-size: 0.74rem; color: #334155; font-weight: 600; padding-top: 6px; border-top: 1px dashed #F1F5F9;">
        <span style="font-size: 0.70rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">Tactical Entries (TID Engine):</span>
        <div style="display: flex; align-items: center; gap: 5px;">
          <span style="display: inline-block; padding: 1px 6px; background-color: #22C55E; color: #052E16; border: 1px solid #16A34A; border-radius: 4px; font-size: 8.5px; font-weight: 800;">DCA</span>
          <span style="font-size: 0.72rem; color: #475569;">Standard (−1.5σ)</span>
        </div>
        <div style="display: flex; align-items: center; gap: 5px;">
          <span style="display: inline-block; padding: 1px 6px; background-color: #FACC15; color: #422006; border: 1px solid #EAB308; border-radius: 4px; font-size: 8.5px; font-weight: 800;">DEEPLY OVERSOLD</span>
          <span style="font-size: 0.72rem; color: #475569;">High Conviction (−2.2σ)</span>
        </div>
        <div style="display: flex; align-items: center; gap: 5px;">
          <span style="display: inline-block; padding: 1px 6px; background-color: #F97316; color: #FFFFFF; border: 1px solid #EA580C; border-radius: 4px; font-size: 8.5px; font-weight: 800;">CAPITULATION</span>
          <span style="font-size: 0.72rem; color: #475569;">Extreme Value (−3.0σ)</span>
        </div>
      </div>
    </div>
    """


def make_summary_bar(all_data: dict, timeframe: str = "90-Day") -> go.Figure:
    """
    Horizontal bar chart showing Price Valuation vs Corridor Median (90-Day or 1-Year).
    Leaderboard Sorting:
      • Ranked by valuation magnitude (descending order by % Above / Below Fair Value Median)
      • Most overstretched asset (highest %) at the top
      • Deepest discount asset (lowest %) at the bottom
    """
    is_1y = (timeframe == "1-Year")
    timeframe_label = "1-Year" if is_1y else "90-Day"

    items = []

    for tk, d in all_data.items():
        if d.get("error"):
            continue
        status = compute_status(d, timeframe=timeframe)
        col    = STATUS_COLORS[status]

        if d.get("pe_mode"):
            cur  = d.get("pe_current", np.nan)
            mid  = d.get("pe_mid_1y" if is_1y else "pe_mid_90d", d.get("pe_mid", np.nan))
            unit = "P/E"
        else:
            cur  = d.get("price_current", np.nan)
            mid  = d.get("price_mid_1y" if is_1y else "price_mid_90d", d.get("price_mid", np.nan))
            unit = "Price"

        pct = d.get("diff_1y" if is_1y else "diff_90d")
        if pct is None or np.isnan(pct):
            if np.isnan(cur) or np.isnan(mid) or mid == 0:
                continue
            pct = (cur / mid - 1.0) * 100.0

        items.append({
            "ticker": tk,
            "pct":    pct,
            "status": status,
            "color":  col,
            "cur":    cur,
            "mid":    mid,
            "unit":   unit,
        })

    # Rank by magnitude: descending order by % above/below median
    items = sorted(items, key=lambda x: x["pct"], reverse=True)

    labels = [x["ticker"] for x in items]
    vals   = [x["pct"] for x in items]
    colors = [x["color"] for x in items]
    hover  = [
        f"<b>{x['ticker']}</b><br>Status: {x['status']}<br>Current {x['unit']}: {x['cur']:.2f}<br>"
        f"{timeframe_label} Average {x['unit']}: {x['mid']:.2f}<br>vs Average: {x['pct']:+.1f}%"
        for x in items
    ]

    min_val = min(vals) if vals else 0.0
    max_val = max(vals) if vals else 0.0

    # Ensure negative values have dedicated visual clearance between zero line, bar end, and y-axis labels
    # Force aggressive negative buffer: subtract fixed 30 points from min_val to guarantee space on mobile
    x_min = min_val - 30.0
    x_max = max(max_val * 1.15, 15.0)

    # Smart label positioning:
    # Wide negative bars (abs(v) >= 12.0%) place text inside with white text.
    # Narrow negative bars (< 12%) and positive bars place text outside with dark text.
    text_positions = []
    text_colors = []
    for v in vals:
        if v < 0 and abs(v) >= 12.0:
            text_positions.append("inside")
            text_colors.append("#FFFFFF")
        else:
            text_positions.append("outside")
            text_colors.append(TEXT_DARK)

    fig = go.Figure(go.Bar(
        x=vals,
        y=labels,
        orientation="h",
        marker_color=colors,
        marker_line_color="rgba(0,0,0,0.06)",
        marker_line_width=1,
        hovertext=hover,
        hoverinfo="text",
        text=[f"{v:+.1f}%" for v in vals],
        textposition=text_positions,
        textfont=dict(size=10, color=text_colors, family="monospace"),
        cliponaxis=False,
    ))

    fig.add_vline(x=0,  line=dict(color=MUTED_SLATE, width=1, dash="solid"))
    fig.add_vline(x=-5, line=dict(color=COLOR_ATTRACTIVE, width=0.8, dash="dot"))
    fig.add_vline(x=5,  line=dict(color=COLOR_OVERVALUED, width=0.8, dash="dot"))

    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor="#FFFFFF",
        font=dict(color=TEXT_DARK, size=11),
        dragmode=False,
        xaxis=dict(
            title=f"% Above / Below {timeframe_label} Average",
            gridcolor=GRID_COLOR,
            zeroline=False,
            color=MUTED_SLATE,
            linecolor=BORDER_COLOR,
            range=[x_min, x_max],
            automargin=True,
            fixedrange=True,
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            color=TEXT_DARK,
            tickfont=dict(size=12, weight="bold", color=TEXT_DARK),
            ticksuffix="   ",
            linecolor=BORDER_COLOR,
            autorange="reversed",
            categoryorder="array",
            categoryarray=labels,
            fixedrange=True,
        ),
        margin=dict(l=65, r=36, t=20, b=40),
        height=max(420, len(labels) * 24 + 60),
    )
    return fig


# ─────────────────────────────────────────────
# WATCHLIST & CUSTOM TICKERS STATE INITIALIZATION
# ─────────────────────────────────────────────
if "all_tickers" not in st.session_state:
    st.session_state["all_tickers"] = dict(DEFAULT_TICKERS)

# URL Query parameter persistence & restoration
query_watchlist = st.query_params.get("watchlist")
if "selected_equities" not in st.session_state:
    if query_watchlist:
        parsed = [t.strip().upper() for t in query_watchlist.split(",") if t.strip()]
        for t in parsed:
            if t not in st.session_state["all_tickers"]:
                st.session_state["all_tickers"][t] = t
        st.session_state["selected_equities"] = [t for t in parsed if t in st.session_state["all_tickers"]]
    else:
        st.session_state["selected_equities"] = list(DEFAULT_TICKERS.keys())

# Valuation corridor timeframe initialization (strictly default to 90-Day)
query_timeframe = st.query_params.get("timeframe")
init_timeframe = query_timeframe if query_timeframe in ["90-Day", "1-Year"] else "90-Day"
if "val_timeframe" not in st.session_state:
    st.session_state["val_timeframe"] = init_timeframe
if "val_timeframe_selector" not in st.session_state:
    st.session_state["val_timeframe_selector"] = st.session_state["val_timeframe"]

def on_timeframe_change():
    sel = st.session_state.get("val_timeframe_selector")
    if sel in ["90-Day", "1-Year"]:
        st.session_state["val_timeframe"] = sel
        st.query_params["timeframe"] = sel


# ─────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <a href="/User_Guide" target="_self" class="guide-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            <span>View the Terminology & User Guide</span>
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Controls & Filters")
    st.markdown("---")

    # Options pool includes all default and user-added tickers
    current_options = list(st.session_state["all_tickers"].keys())
    for s in st.session_state.get("selected_equities", []):
        if s not in current_options:
            current_options.append(s)

    # Safe default list
    safe_defaults = [t for t in st.session_state.get("selected_equities", []) if t in current_options]
    if not safe_defaults and current_options:
        safe_defaults = list(DEFAULT_TICKERS.keys())

    selected = st.multiselect(
        "Select Equities & ETFs",
        options=current_options,
        default=safe_defaults,
        help="Select which equities to include in the valuation monitor",
    )

    # Keep session state and URL query params synchronized with user clicks
    if selected != st.session_state.get("selected_equities"):
        st.session_state["selected_equities"] = selected
        st.query_params["watchlist"] = ",".join(selected)

    # ── ➕ Add Custom Ticker UI ──
    st.markdown("<div style='margin-top: -6px; margin-bottom: 2px;'></div>", unsafe_allow_html=True)
    add_col1, add_col2 = st.columns([3, 1])
    with add_col1:
        new_ticker_input = st.text_input(
            "Add Custom Ticker",
            placeholder="Symbol (e.g. AAPL, META)",
            label_visibility="collapsed",
            key="custom_ticker_input",
        ).strip().upper()
    with add_col2:
        add_clicked = st.button("➕ Add", use_container_width=True, help="Validate and add ticker to active monitor")

    if add_clicked and new_ticker_input:
        sym = new_ticker_input
        if sym in selected:
            st.info(f"{sym} is already active.")
        elif sym in st.session_state["all_tickers"]:
            new_sel = list(selected)
            new_sel.append(sym)
            st.session_state["selected_equities"] = new_sel
            st.query_params["watchlist"] = ",".join(new_sel)
            st.rerun()
        else:
            with st.spinner(f"Verifying {sym} on Yahoo Finance…"):
                try:
                    obj = yf.Ticker(sym)
                    test_hist = obj.history(period="5d")
                    if test_hist.empty or "Close" not in test_hist.columns:
                        st.error(f"'{sym}' could not be resolved on Yahoo Finance. Please verify the symbol.")
                    else:
                        co_name = sym
                        try:
                            inf = obj.info or {}
                            co_name = inf.get("shortName") or inf.get("longName") or sym
                        except Exception:
                            pass
                        st.session_state["all_tickers"][sym] = co_name
                        new_sel = list(selected)
                        if sym not in new_sel:
                            new_sel.append(sym)
                        st.session_state["selected_equities"] = new_sel
                        st.query_params["watchlist"] = ",".join(new_sel)
                        st.success(f"Added {sym} ({co_name})!")
                        time.sleep(0.3)
                        st.rerun()
                except Exception as ex:
                    st.error(f"Error fetching {sym}: {ex}")

    # ── Reset to Default Basket ──
    reset_col1, reset_col2 = st.columns([3, 2])
    with reset_col1:
        if st.button("↺ Reset Basket", use_container_width=True, help="Restore the official default @theinvestingdean curated basket"):
            st.session_state["all_tickers"] = dict(DEFAULT_TICKERS)
            st.session_state["selected_equities"] = list(DEFAULT_TICKERS.keys())
            st.session_state["val_timeframe"] = "90-Day"
            st.session_state["val_timeframe_selector"] = "90-Day"
            st.query_params["watchlist"] = ",".join(DEFAULT_TICKERS.keys())
            st.query_params["timeframe"] = "90-Day"
            st.rerun()
    with reset_col2:
        st.caption(f"{len(selected)} Active")

    st.markdown("---")
    filter_status = st.multiselect(
        "Filter by Status",
        options=["Buy Zone", "Standard DCA", "Wait for Pullback"],
        default=["Buy Zone", "Standard DCA", "Wait for Pullback"],
    )

    st.markdown("---")
    show_charts = st.toggle("Show Detail Charts", value=True)
    cols_per_row = st.selectbox(
        "Columns per Row",
        options=[1, 2],
        index=1,
        help="Select 1 or 2 columns on desktop. Mobile automatically stacks into 1 full-width column for optimal viewing.",
    )

    st.markdown("---")
    sort_option = st.selectbox(
        "Sort By",
        options=[
            "Alphabetical",
            "Best Value (Lowest Z-Score)",
            "Deepest ATH Drawdown",
            "Lowest 2Y PEG",
        ],
        index=0,
        help="Reorder stock cards based on quantitative criteria",
    )

    st.markdown("---")
    with st.expander("🔔 Live Signal Alerts (Telegram / Email)", expanded=st.session_state.get("alerts_enabled", False)):
        alerts_enabled = st.toggle(
            "Enable Live Signal Alerts",
            value=st.session_state.get("alerts_enabled", False),
            key="alerts_enabled",
            help="Automatically send instant mobile push alerts when an equity in your basket triggers a DCA, DEEPLY OVERSOLD, or CAPITULATION signal.",
        )
        alert_channel = st.radio(
            "Alert Channel",
            options=["Telegram Bot", "Email (SMTP)"],
            horizontal=True,
            key="alert_channel",
        )
        if alert_channel == "Telegram Bot":
            tg_token = st.text_input(
                "Telegram Bot Token",
                value=st.session_state.get("tg_bot_token", ""),
                key="tg_bot_token",
                type="password",
                placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ",
                help="Obtain from @BotFather on Telegram",
            )
            tg_chat = st.text_input(
                "Telegram Chat ID",
                value=st.session_state.get("tg_chat_id", ""),
                key="tg_chat_id",
                placeholder="e.g. 987654321 or @your_channel",
                help="Your personal Telegram User ID or Channel Username",
            )
            if st.button("📤 Send Test Telegram Alert", use_container_width=True):
                if not tg_token or not tg_chat:
                    st.error("Please enter both Bot Token and Chat ID.")
                else:
                    test_msg = (
                        "🚨 <b>TEST ALERT: Valuation Radar Connected</b>\n\n"
                        "✅ Your Telegram Bot credentials are verified!\n"
                        "Live tactical signals (DCA, DEEPLY OVERSOLD, CAPITULATION) will be pushed here instantly.\n\n"
                        "<i>The Stock Valuation Radar • @theinvestingdean</i>"
                    )
                    ok, msg = send_telegram_alert(tg_token, tg_chat, test_msg)
                    if ok:
                        st.success("Test alert sent! Check your Telegram.")
                    else:
                        st.error(msg)
        else:
            smtp_srv = st.text_input(
                "SMTP Server",
                value=st.session_state.get("email_smtp_server", "smtp.gmail.com"),
                key="email_smtp_server",
            )
            smtp_p = st.number_input(
                "SMTP Port",
                value=int(st.session_state.get("email_smtp_port", 587)),
                key="email_smtp_port",
            )
            sender = st.text_input(
                "Sender Email",
                value=st.session_state.get("email_sender", ""),
                key="email_sender",
                placeholder="sender@gmail.com",
            )
            pwd = st.text_input(
                "App Password",
                value=st.session_state.get("email_password", ""),
                key="email_password",
                type="password",
                placeholder="App-specific password",
            )
            rcvr = st.text_input(
                "Destination Email",
                value=st.session_state.get("email_receiver", ""),
                key="email_receiver",
                placeholder="your.email@example.com",
            )
            if st.button("📤 Send Test Email Alert", use_container_width=True):
                if not sender or not pwd or not rcvr:
                    st.error("Please enter Sender Email, App Password, and Destination Email.")
                else:
                    test_html = """
                    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 500px; border: 1px solid #E2E8F0; border-radius: 8px; padding: 18px;">
                      <h3 style="color: #0F172A; margin-top: 0;">✅ Test Alert: Valuation Radar Connected</h3>
                      <p style="color: #334155;">Your email configuration is working! Live tactical buy signals will be sent to this address.</p>
                      <div style="margin-top: 14px; font-size: 0.75rem; color: #94A3B8;">@theinvestingdean</div>
                    </div>
                    """
                    ok, msg = send_email_alert(smtp_srv, smtp_p, sender, pwd, rcvr, "Test Alert: Valuation Radar Connected", test_html)
                    if ok:
                        st.success("Test email sent! Check your inbox.")
                    else:
                        st.error(msg)

        dispatched_count = len(st.session_state.get("dispatched_alerts", set()))
        st.caption(f"🛡️ Deduplication cache: {dispatched_count} bar alerts dispatched this session.")

    st.markdown("---")
    if st.button("Refresh Market Data", width="stretch"):
        # Explicitly clear cached market data before rerun
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption(f"Engine synced · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown(
        '<div style="font-size: 0.70rem; color: #94A3B8; line-height: 1.5; margin-top: 4px;">'
        '<div>Quantitative corridor framework</div>'
        '<div style="white-space: nowrap; margin-top: 4px; display: inline-flex; align-items: center; gap: 5px;">'
        '<span>Curated by</span>'
        '<a href="https://www.instagram.com/theinvestingdean" target="_blank" rel="noopener noreferrer" class="dean-badge" title="Visit @theinvestingdean on Instagram" style="font-size: 0.70rem; padding: 2px 7px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; flex-shrink: 0;"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>@theinvestingdean</a>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────

# ── 1. Sleek, Professional Header with Subtle Dean Branding ──
st.markdown(
    """
    <div class="header-container" style="display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 1.25rem; margin-top: 0.5rem; margin-bottom: 1.5rem;">
      <div>
        <h1 style="color: #1F2937; font-size: 2.1rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -0.025em; line-height: 1.2;">
          The Stock Valuation Radar
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 6px; margin-bottom: 0; line-height: 1.4;">
          Know when quality stocks enter the Buy Zone, Standard DCA, or Wait for Pullback
        </p>
        <div style="margin-top: 8px;">
          <a href="https://www.instagram.com/theinvestingdean" target="_blank" rel="noopener noreferrer" class="dean-badge" title="Visit @theinvestingdean on Instagram"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px; flex-shrink: 0;"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>@theinvestingdean</a>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 7px; background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 9999px; padding: 6px 14px; margin-top: 4px;">
        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10B981;"></span>
        <span style="color: #065F46; font-size: 13px; font-weight: 600; letter-spacing: 0.02em;">Live Market Data</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="margin-bottom: 1.25rem;">
        <a href="/User_Guide" target="_self" class="guide-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            <span>View the Terminology & User Guide</span>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

if not selected:
    st.warning("Please select at least one equity from the sidebar.")
    st.stop()

# ── 2. Data Fetching with Progress ──
progress_bar = st.progress(0, text="Synchronizing market feeds…")
all_data: dict[str, dict] = {}

for i, tk in enumerate(selected):
    all_data[tk] = fetch_ticker_data(tk)
    progress_bar.progress((i + 1) / len(selected), text=f"Analyzing {tk}…")
    time.sleep(0.03)

progress_bar.empty()

# ── 3. Apply Status Filter ──
STATUS_ALIAS_MAP = {
    "Attractive": "Buy Zone",
    "Neutral": "Standard DCA",
    "Overvalued": "Wait for Pullback",
    "Buy Zone": "Buy Zone",
    "Standard DCA": "Standard DCA",
    "Wait for Pullback": "Wait for Pullback",
}
active_timeframe = st.session_state.get("val_timeframe", "90-Day")
normalized_filter = {STATUS_ALIAS_MAP.get(f, f) for f in filter_status}
visible = {
    tk: d for tk, d in all_data.items()
    if STATUS_ALIAS_MAP.get(compute_status(d, timeframe=active_timeframe)) in normalized_filter
}

# ── 4. Price vs Average (Top Chart & Timeframe Toggle) ──
val_timeframe = st.session_state.get("val_timeframe", "90-Day")
active_title = "Price vs 1-Year Average" if val_timeframe == "1-Year" else "Price vs 90-Day Average"

st.markdown(f"### {active_title}")

st.markdown(
    """
    <div style="color: #64748B; font-size: 0.875rem; line-height: 1.5; margin-top: -6px; margin-bottom: 4px;">
      <div>Compares each stock's live price to its average price over the last 90 days or 1 year.</div>
      <div style="margin-top: 3px;">🟢 Green bars highlight Buy Zone (&lt; -5% below average); &nbsp; 🟡 Amber represents Standard DCA (within 5% of average); &nbsp; 🔴 Red indicates Wait for Pullback (&gt; +5% above average).</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.segmented_control(
    "Valuation Timeframe",
    options=["90-Day", "1-Year"],
    selection_mode="single",
    required=True,
    label_visibility="collapsed",
    key="val_timeframe_selector",
    on_change=on_timeframe_change,
)
val_timeframe = st.session_state.get("val_timeframe", "90-Day")


if visible:
    st.plotly_chart(
        make_summary_bar(visible, timeframe=val_timeframe),
        width="stretch",
        config={
            "displayModeBar": False,
            "staticPlot": True,
            "scrollZoom": False,
            "responsive": True,
        }
    )
else:
    st.info("No tickers match the selected status filters.")

# ── 5. KPI Summary Row ──
counts = {"Buy Zone": 0, "Standard DCA": 0, "Wait for Pullback": 0}
for d in visible.values():
    s = compute_status(d, timeframe=val_timeframe)
    canon_s = STATUS_ALIAS_MAP.get(s, s)
    if canon_s in counts:
        counts[canon_s] += 1

k1, k2, k3, k4 = st.columns(4)
k1.metric("Tracked Assets", len(selected))

k2.markdown(
    f"""
    <div data-testid="stMetric">
        <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">Buy Zone</div>
        <div style="font-size: 2.25rem; font-weight: 700; color: #22C55E; line-height: 1.2;">{counts['Buy Zone']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

k3.markdown(
    f"""
    <div data-testid="stMetric">
        <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">Standard DCA</div>
        <div style="font-size: 2.25rem; font-weight: 700; color: #F59E0B; line-height: 1.2;">{counts['Standard DCA']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

k4.markdown(
    f"""
    <div data-testid="stMetric">
        <div style="font-size: 14px; color: #6B7280; margin-bottom: 4px;">Wait for Pullback</div>
        <div style="font-size: 2.25rem; font-weight: 700; color: #EF4444; line-height: 1.2;">{counts['Wait for Pullback']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Executive Market Highlights Banner ──
if visible:
    render_executive_market_highlights(visible, timeframe=val_timeframe)

st.markdown("---")

# ── 6. Individual Asset Cards ──
if not visible:
    st.info("No equities match the current filter criteria.")
    st.stop()

ticker_list = list(visible.keys())

# Apply user-selected sort order
if sort_option == "Alphabetical":
    ticker_list = sorted(ticker_list)
elif sort_option == "Best Value (Lowest Z-Score)":
    def get_z_score(tk):
        h = visible[tk].get("hist", pd.DataFrame())
        if val_timeframe == "1-Year" and "Z252" in h.columns and len(h["Z252"].dropna()):
            return float(h["Z252"].dropna().iloc[-1])
        z_col = "Z50" if "Z50" in h.columns else ("Z16" if "Z16" in h.columns else None)
        if z_col and len(h[z_col].dropna()):
            return float(h[z_col].dropna().iloc[-1])
        return 999.0
    ticker_list = sorted(ticker_list, key=get_z_score)
elif sort_option == "Deepest ATH Drawdown":
    def get_ath_dist(tk):
        dist = visible[tk].get("dist_ath", np.nan)
        if not np.isnan(dist):
            return dist
        return 999.0
    ticker_list = sorted(ticker_list, key=get_ath_dist)
elif sort_option == "Lowest 2Y PEG":
    def get_peg(tk):
        p = visible[tk].get("peg_2y")
        if p is not None and not np.isnan(p) and p > 0:
            return p
        return 999.0
    ticker_list = sorted(ticker_list, key=get_peg)

# ── Quick Find Ticker Search & Direct Navigation ──
qf_col1, qf_col2 = st.columns([3, 1])
with qf_col1:
    quick_find = st.selectbox(
        "Quick Find",
        options=ticker_list,
        index=None,
        placeholder="Jump directly to a stock card...",
        format_func=lambda x: f"{x}  ·  {visible.get(x, {}).get('shortName') or visible.get(x, {}).get('name', x)}",
        key="quick_find_ticker",
        help="Select any tracked asset to immediately navigate down to its valuation card.",
    )
with qf_col2:
    st.markdown('<div class="qf-spacer" style="height: 28px;"></div>', unsafe_allow_html=True)
    isolate_card = st.checkbox(
        "🎯 Filter only this card",
        value=False,
        key="isolate_selected_card",
        help="Check to isolate and only display the selected ticker's card below.",
    )

if quick_find:
    if isolate_card:
        ticker_list = [quick_find]
    else:
        scroll_js = f"""
        <script>
        (function() {{
            function scrollToCard() {{
                try {{
                    var pDoc = (window.parent && window.parent.document) ? window.parent.document : document;
                    var el = pDoc.getElementById('card-{quick_find}') || pDoc.getElementById('card-anchor-{quick_find}');
                    if (el) {{
                        el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        var cardWrapper = el.closest('[data-testid="stVerticalBlockBorderWrapper"]') || el;
                        cardWrapper.style.transition = 'box-shadow 0.4s ease, border-color 0.4s ease';
                        cardWrapper.style.boxShadow = '0 0 0 3px #FACC15, 0 10px 25px -5px rgba(234, 179, 8, 0.4)';
                        setTimeout(function() {{
                            cardWrapper.style.boxShadow = '';
                        }}, 2500);
                    }}
                }} catch(e) {{
                    console.warn('Quick find scroll error:', e);
                }}
            }}
            setTimeout(scrollToCard, 100);
            setTimeout(scrollToCard, 350);
            setTimeout(scrollToCard, 700);
        }})();
        </script>
        """
        st.components.v1.html(scroll_js, height=0)

# ── Master Chart Legend Bar (Consolidates Repeating Legends) ──
if show_charts:
    st.html(make_master_legend_html())

n_cols = cols_per_row

for row_start in range(0, len(ticker_list), n_cols):
    row_tickers = ticker_list[row_start : row_start + n_cols]
    cols        = st.columns(n_cols)

    for col, tk in zip(cols, row_tickers):
        d      = visible[tk]
        status = compute_status(d, timeframe=val_timeframe)
        info   = d.get("info", {})
        err    = d.get("error")

        with col:
            # Anchor tag for direct jumps with clearance
            st.html(f'<div id="card-anchor-{tk}" style="scroll-margin-top: 100px; height: 0; margin: 0; padding: 0;"></div>')
            # Wrap each stock's entire module in a clearly defined card container
            with st.container(border=True, key=f"stock_card_{tk}"):
                # ── Safe Header Display ──
                safe_name = d.get("shortName") or d.get("longName") or d.get("name") or tk
                is_etf = d.get("is_etf", False)
                is_ucits = d.get("is_ucits", False)

                asset_badge_html = ""
                if is_etf:
                    badge_lbl = "Asset Type: UCITS ETF" if is_ucits else "Asset Type: ETF"
                    asset_badge_html = f'<span class="badge" style="background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; font-size: 0.70rem; margin-left: 6px;">{badge_lbl}</span>'

                header_html = f"""
                <div id="card-{tk}" class="stock-card-container" style="scroll-margin-top: 100px;">
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #F1F5F9;">
                    <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 4px; min-width: 130px;">
                      <span style="font-size: 1.25rem; font-weight: 800; color: {TEXT_DARK}; letter-spacing: -0.01em;">{tk}</span>
                      <span style="font-size: 0.82rem; color: {MUTED_SLATE}; margin-left: 2px; font-weight: 500;">{safe_name}</span>
                      {asset_badge_html}
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-left: auto;">
                      {badge_html(status)}
                      <button class="save-card-btn" data-ticker="{tk}" title="Export high-resolution 4:5 portrait card (1080x1350) for Instagram & social media">📸 Save Card (4:5)</button>
                    </div>
                  </div>
                </div>
                """
                st.html(header_html)

                if err:
                    st.error(f"Market feed error: {err}")
                    continue

                hist_df = d.get("hist", pd.DataFrame())
                if hist_df.empty or "Close" not in hist_df.columns:
                    st.warning("Historical prices unavailable.")
                    continue

                ccy = d.get("currency", "USD")
                ccy_sym = get_currency_symbol(ccy)
                price_now = float(d.get("current_price", hist_df["Close"].iloc[-1]))

                # ── Box 1: Price with YTD Return Badge & Dual Performance Display ──
                ytd_val = d.get("ytd_pct")
                if ytd_val is None:
                    ytd_val = compute_ytd_pct(hist_df, price_now)

                if ytd_val is not None and not np.isnan(ytd_val):
                    subtext_p = f"{ytd_val:+.1f}% YTD"
                    if ytd_val >= 0:
                        ytd_bg = "#DCFCE7"
                        ytd_color = "#166534"
                        ytd_border = "#BBF7D0"
                    else:
                        ytd_bg = "#FEE2E2"
                        ytd_color = "#991B1B"
                        ytd_border = "#FECACA"
                else:
                    subtext_p = "YTD N/A"
                    ytd_bg = "#F1F5F9"
                    ytd_color = "#64748B"
                    ytd_border = "#E2E8F0"

                ytd_badge_html = f'<span style="display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.70rem; font-weight: 600; line-height: 1.2; background-color: {ytd_bg}; color: {ytd_color}; border: 1px solid {ytd_border}; white-space: nowrap; text-align: right;" title="Year-to-Date Return: {subtext_p}">{subtext_p}</span>'

                dual_perf_html = make_dual_perf_pill_html(
                    d.get("reg_perf_pct"),
                    d.get("ext_perf_pct"),
                    d.get("ext_label"),
                    d.get("ext_price"),
                    ccy_sym,
                    align="left",
                    reg_abs=d.get("reg_perf_abs"),
                    ext_abs=d.get("ext_perf_abs"),
                )

                box1_html = f"""
                <div class="kpi-mini-box">
                  <div class="kpi-mini-header">
                    <span class="kpi-mini-title" title="Price ({ccy})">Price ({ccy})</span>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; width: 100%; flex: 1;">
                    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 4px; min-width: 0; flex: 1;">
                      <span style="font-size: 1.25rem; font-weight: 700; color: {TEXT_DARK}; font-variant-numeric: tabular-nums; line-height: 1.2;">
                        {price_now:.2f}
                      </span>
                      {dual_perf_html}
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: flex-end; justify-content: flex-start; flex-shrink: 0; padding-top: 2px;">
                      {ytd_badge_html}
                    </div>
                  </div>
                </div>
                """

                # ── Box 2: Distance to Lifetime All-Time High (ATH) ──
                ath = d.get("ath", price_now)
                dist_ath = d.get("dist_ath", 0.0)

                # TradingView DCA Efficiency Dashboard Logic:
                if np.isnan(dist_ath):
                    dist_color = MUTED_SLATE
                    dist_badge_class = "badge-neutral"
                    dist_badge_text = "N/A"
                    dist_str = "N/A"
                elif dist_ath < -25.0:
                    dist_color = "#047857"
                    dist_badge_class = "badge-attractive"
                    dist_badge_text = "Deep Discount"
                    dist_str = f"{dist_ath:.1f}%"
                elif dist_ath <= -10.0:
                    dist_color = "#B45309"
                    dist_badge_class = "badge-neutral"
                    dist_badge_text = "Moderate Pullback"
                    dist_str = f"{dist_ath:.1f}%"
                else:
                    dist_color = "#B91C1C"
                    dist_badge_class = "badge-overvalued"
                    dist_badge_text = "Near ATH"
                    dist_str = f"{dist_ath:.1f}%" if dist_ath < -0.05 else "0.0%"

                box2_html = make_metric_tile_html(
                    title="Distance to All-Time High (ATH)",
                    value=dist_str,
                    subtext=f"ATH: {ccy_sym}{ath:.2f}",
                    badge_text=dist_badge_text,
                    badge_class=dist_badge_class,
                    val_color=dist_color,
                    subtext_color=MUTED_SLATE,
                )

                # ── Box 3: Std Dev (50 Days) ──
                z50_col = "Z50" if "Z50" in hist_df.columns else ("Z16" if "Z16" in hist_df.columns else None)
                z50_series = hist_df[z50_col].dropna() if z50_col else pd.Series(dtype=float)
                if len(z50_series):
                    z50_val = float(z50_series.iloc[-1])
                    z50_str = f"{z50_val:+.2f}σ"

                    if z50_val <= -1.2:
                        z_color = "#047857"
                        z_badge_class = "badge-attractive"
                        z_badge_text = "Oversold"
                    elif z50_val >= 1.2:
                        z_color = "#B91C1C"
                        z_badge_class = "badge-overvalued"
                        z_badge_text = "Overbought"
                    else:
                        z_color = "#B45309"
                        z_badge_class = "badge-neutral"
                        z_badge_text = "Neutral"
                else:
                    z50_val = np.nan
                    z50_str = "N/A"
                    z_color = MUTED_SLATE
                    z_badge_class = "badge-neutral"
                    z_badge_text = "N/A"

                box3_html = make_metric_tile_html(
                    title="STANDARD DEVIATION (50 DAYS)",
                    value=z50_str,
                    badge_text=z_badge_text,
                    badge_class=z_badge_class,
                    val_color=z_color,
                    subtext_color=MUTED_SLATE,
                )

                # ── Box 4 & Box 5: Specialized ETF vs Single-Stock Handling ──
                if is_etf:
                    # ETF: Expense Ratio (TER) replaces single-stock Forward P/E
                    ter_val = d.get("ter")
                    if ter_val is not None and not np.isnan(ter_val):
                        ter_str = f"{ter_val*100:.2f}%" if ter_val < 0.05 else f"{ter_val:.2f}%"
                    else:
                        ter_str = "0.35%" if tk == "SMGB.L" else "N/A"

                    box4_html = make_metric_tile_html(
                        title="Expense Ratio",
                        value=ter_str,
                        subtext="Annual TER / Fee",
                        badge_text="UCITS ETF" if is_ucits else "ETF Asset",
                        badge_class="badge-attractive",
                        val_color=TEXT_DARK,
                        subtext_color=MUTED_SLATE,
                    )

                    # ETF: Fund AUM replaces single-stock 2Y PEG Ratio (avoids 'Growth Negative / N/A')
                    aum_val = d.get("aum")
                    if aum_val and not np.isnan(aum_val) and aum_val > 0:
                        if aum_val >= 1e9:
                            aum_str = f"${aum_val/1e9:.2f}B"
                        else:
                            aum_str = f"${aum_val/1e6:.1f}M"
                        aum_subtext = d.get("fund_family") or "Net Fund Assets"
                    else:
                        aum_str = "$8.58B" if tk == "SMGB.L" else "N/A"
                        aum_subtext = "Fund Net Assets"

                    box5_html = make_metric_tile_html(
                        title="Fund AUM",
                        value=aum_str,
                        subtext=aum_subtext,
                        badge_text="AUM",
                        badge_class="badge-neutral",
                        val_color=TEXT_DARK,
                        subtext_color=MUTED_SLATE,
                    )
                else:
                    # Single Stock: Forward P/E (normalized for foreign GDRs like SMSN.L)
                    fwd_pe = d.get("fwd_pe") or info.get("forwardPE")
                    if isinstance(fwd_pe, (int, float)) and not np.isnan(fwd_pe) and fwd_pe > 0:
                        fwd_pe_str = f"{fwd_pe:.1f}"
                        if fwd_pe < 20.0:
                            fwd_badge_text = "Attractive"
                            fwd_badge_class = "badge-attractive"
                            fwd_badge_style = "background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC;"
                        elif fwd_pe <= 35.0:
                            fwd_badge_text = "Moderate"
                            fwd_badge_class = "badge-neutral"
                            fwd_badge_style = "background-color: #FEF3C7; color: #854D0E; border: 1px solid #FDE68A;"
                        else:
                            fwd_badge_text = "High Multiple"
                            fwd_badge_class = "badge-overvalued"
                            fwd_badge_style = "background-color: #FEE2E2; color: #991B1B; border: 1px solid #FECACA;"
                    else:
                        fwd_pe_str = "N/A"
                        fwd_badge_text = "N/A"
                        fwd_badge_class = "badge-na"
                        fwd_badge_style = "background-color: #F3F4F6; color: #374151; border: 1px solid #E5E7EB;"

                    box4_html = make_metric_tile_html(
                        title="Forward P/E",
                        value=fwd_pe_str,
                        subtext="Next 12 Months Multiple",
                        badge_text=fwd_badge_text,
                        badge_class=fwd_badge_class,
                        badge_style=fwd_badge_style,
                        val_color=TEXT_DARK,
                        subtext_color=MUTED_SLATE,
                    )

                    # Single Stock: 2Y PEG Ratio
                    peg_2y = d.get("peg_2y")
                    cagr_pct = d.get("cagr_2y_pct")
                    if (
                        peg_2y is not None
                        and not np.isnan(peg_2y)
                        and peg_2y > 0
                        and cagr_pct is not None
                        and not np.isnan(cagr_pct)
                        and cagr_pct > 0
                    ):
                        peg_2y_str = f"{peg_2y:.2f}"
                        peg_subtext = f"2Y Expected Growth: {cagr_pct:+.1f}%"
                        if peg_2y < 1.00:
                            peg_badge_text = "Undervalued"
                            peg_badge_class = "badge-attractive"
                            peg_badge_style = "background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC;"
                        elif peg_2y <= 1.75:
                            peg_badge_text = "Fair Value"
                            peg_badge_class = "badge-neutral"
                            peg_badge_style = "background-color: #FEF3C7; color: #854D0E; border: 1px solid #FDE68A;"
                        else:
                            peg_badge_text = "Premium"
                            peg_badge_class = "badge-overvalued"
                            peg_badge_style = "background-color: #FEE2E2; color: #991B1B; border: 1px solid #FECACA;"
                    else:
                        peg_2y_str = "N/A"
                        peg_subtext = f"2Y Expected Growth: {cagr_pct:+.1f}%" if (cagr_pct is not None and not np.isnan(cagr_pct)) else "Consensus Unlisted"
                        peg_badge_text = "N/A"
                        peg_badge_class = "badge-na"
                        peg_badge_style = "background-color: #F3F4F6; color: #374151; border: 1px solid #E5E7EB;"

                    box5_html = make_metric_tile_html(
                        title="2Y PEG Ratio",
                        value=peg_2y_str,
                        subtext=peg_subtext,
                        badge_text=peg_badge_text,
                        badge_class=peg_badge_class,
                        badge_style=peg_badge_style,
                        val_color=TEXT_DARK,
                        subtext_color=MUTED_SLATE,
                    )

                # ── Box 6: Fair Value with dynamic % move ──
                if val_timeframe == "1-Year":
                    box6_title = "1Y Fair Value"
                    fair_val = d.get("fair_value_1y", np.nan)
                    upside = d.get("upside_1y", np.nan)
                else:
                    box6_title = "90d Fair Value"
                    fair_val = d.get("fair_value_90d", d.get("fair_value_price", np.nan))
                    upside = d.get("upside_90d", d.get("upside_to_median", np.nan))

                fair_val_str = f"{fair_val:.2f} {ccy}" if not np.isnan(fair_val) else "N/A"
                if not np.isnan(upside):
                    if upside >= 0:
                        upside_subtext = f"▲ {upside:+.1f}% to Fair Value"
                        upside_color = "#047857"
                    else:
                        upside_subtext = f"▼ {upside:+.1f}% to Fair Value"
                        upside_color = "#B91C1C"
                else:
                    upside_subtext = "Fair Value N/A"
                    upside_color = MUTED_SLATE

                box6_html = make_metric_tile_html(
                    title=box6_title,
                    value=fair_val_str,
                    subtext=upside_subtext,
                    val_color=TEXT_DARK,
                    subtext_color=upside_color,
                )

                # ── Box 7: 12-Month Wall Street Analyst Price Target ──
                target_price = d.get("target_mean_price")
                target_upside = d.get("target_upside_pct")

                if (
                    target_upside is not None
                    and not np.isnan(target_upside)
                    and target_price is not None
                    and not np.isnan(target_price)
                ):
                    target_val_str = f"{target_upside:+.1f}%"
                    subtext_target = f"Consensus: {ccy_sym}{target_price:.2f} {ccy}"
                    val_color_t = "#047857" if target_upside >= 0 else "#B91C1C"
                else:
                    target_val_str = "N/A"
                    subtext_target = "Consensus Unlisted" if not is_etf else "ETF Asset (No Target)"
                    val_color_t = MUTED_SLATE

                box7_html = make_metric_tile_html(
                    title="12M Analyst Target",
                    value=target_val_str,
                    subtext=subtext_target,
                    badge_text=None,
                    badge_class=None,
                    val_color=val_color_t,
                    subtext_color=MUTED_SLATE,
                )

                # ── Standardized Card Metric Grid (Uniform Mini-Boxes) ──
                r1_c1, r1_c2 = st.columns(2)
                with r1_c1:
                    st.html(box1_html)
                with r1_c2:
                    st.html(box2_html)

                r2_c1, r2_c2 = st.columns(2)
                with r2_c1:
                    st.html(box3_html)
                with r2_c2:
                    st.html(box4_html)

                r3_c1, r3_c2 = st.columns(2)
                with r3_c1:
                    st.html(box5_html)
                with r3_c2:
                    st.html(box6_html)

                st.html(box7_html)

                # ── Detail Bollinger & Trend Chart ──
                if show_charts:
                    chart_bar_html = f"""
                    <div class="expand-chart-bar" style="margin-top: 16px; margin-bottom: 12px; padding-bottom: 20px; position: relative; z-index: 998; pointer-events: auto;">
                      <span style="font-size: 0.70rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">Trend & Valuation Corridor</span>
                      <button class="expand-chart-btn" data-ticker="{tk}" onclick="if(window.deanOpenFullscreen) window.deanOpenFullscreen('{tk}'); if(window.parent && window.parent.deanOpenFullscreen) window.parent.deanOpenFullscreen('{tk}');" style="position: relative; z-index: 999; pointer-events: auto; touch-action: manipulation; cursor: pointer;" title="Open Interactive Full-Screen View with touch pinch-zoom & pan">⛶ Expand Chart</button>
                    </div>
                    """
                    st.html(chart_bar_html)
                    fig = make_price_chart(d)
                    st.plotly_chart(
                        fig,
                        width="stretch",
                        config={
                            "displayModeBar": False,
                            "scrollZoom": False,
                            "responsive": True,
                        },
                        key=f"chart_{tk}",
                    )

                # ── Card Watermark for Social Exports ──
                st.html(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 6px; margin-top: 4px; border-top: 1px dashed #E2E8F0; font-size: 0.70rem; color: #94A3B8;">
                      <a href="https://www.instagram.com/theinvestingdean" target="_blank" rel="noopener noreferrer" class="dean-badge" title="Visit @theinvestingdean on Instagram" style="font-size: 0.65rem; padding: 1px 6px;"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; flex-shrink: 0;"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>@theinvestingdean</a>
                      <span>The Stock Valuation Radar • {val_timeframe} Corridor</span>
                    </div>
                    """
                )

                # ── More Info Expander (Institutional Key-Value Terminal Grid) ──
                with st.expander("More info", expanded=False):
                    rsi_series = hist_df["RSI14"].dropna() if "RSI14" in hist_df.columns else pd.Series(dtype=float)
                    rsi_val = float(rsi_series.iloc[-1]) if len(rsi_series) else None
                    rsi_display = format_rsi_display(rsi_val)

                    beta = info.get("beta")
                    beta_str = f"{beta:.2f}" if beta and isinstance(beta, (int, float)) and not np.isnan(beta) else "—"

                    if is_etf:
                        # ETF Terminal Grid
                        issuer = d.get("fund_family") or ("VanEck" if tk == "SMGB.L" else "—")
                        aum_val = d.get("aum")
                        aum_drawer = f"${aum_val/1e9:.2f}B" if aum_val and aum_val >= 1e9 else ("$8.58B" if tk == "SMGB.L" else "—")
                        ter_val = d.get("ter")
                        ter_drawer = f"{ter_val*100:.2f}%" if ter_val and ter_val < 0.05 else (f"{ter_val:.2f}%" if ter_val else "0.35%")
                        asset_cls = "UCITS ETF" if is_ucits else "Equity ETF"

                        drawer_html = f"""
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 16px; padding: 4px 0 2px 0;">
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Fund Issuer</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; margin-top: 2px;">{issuer}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">14D RSI (Wilder)</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{rsi_display}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Asset Structure</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; margin-top: 2px;">{asset_cls}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Net Assets (AUM)</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{aum_drawer}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Total Expense Ratio</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{ter_drawer}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Upcoming Rebalance</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">Quarterly</div>
                          </div>
                          <div style="padding-bottom: 2px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Beta (1Y)</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{beta_str}</div>
                          </div>
                        </div>
                        <div style="border-top: 1px solid #F1F5F9; padding-top: 8px; margin-top: 6px; font-size: 11px; color: #94A3B8; font-weight: 500;">
                          Valuation Methodology: Price Corridor (50/200-Day MAs)
                        </div>
                        """
                    else:
                        # Single-Stock Terminal Grid
                        next_earn_raw = d.get("next_earnings")
                        earnings_display = format_earnings_date(next_earn_raw)

                        sector  = info.get("sector") or info.get("category") or "—"
                        mkt_cap = info.get("marketCap")
                        mkt_cap_str = f"${mkt_cap/1e9:.2f}B" if mkt_cap and isinstance(mkt_cap, (int, float)) and mkt_cap > 0 else "—"

                        trail_pe = d.get("pe_current")
                        trail_pe_str = f"{trail_pe:.1f}x" if trail_pe and not np.isnan(trail_pe) and trail_pe > 0 else "—"

                        div_yld = info.get("dividendYield")
                        div_yld_str = f"{div_yld*100:.2f}%" if div_yld and isinstance(div_yld, (int, float)) and div_yld > 0 else "0.00%"

                        target_price = d.get("target_mean_price")
                        target_upside = d.get("target_upside_pct")
                        target_drawer_str = f"{ccy_sym}{target_price:.2f} ({target_upside:+.1f}%)" if (target_price and target_upside is not None) else "—"

                        mode_lbl = f"P/E Corridor ({val_timeframe} Trailing Multiple)" if d.get("pe_mode") else "Price Corridor (50/200-Day MAs)"

                        drawer_html = f"""
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 16px; padding: 4px 0 2px 0;">
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Upcoming Earnings</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{earnings_display}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">14D RSI (Wilder)</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{rsi_display}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Sector</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; margin-top: 2px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{sector}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Market Cap</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{mkt_cap_str}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Trailing P/E</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{trail_pe_str}</div>
                          </div>
                          <div style="border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Dividend Yield</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{div_yld_str}</div>
                          </div>
                          <div style="padding-bottom: 2px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">Beta (1Y)</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{beta_str}</div>
                          </div>
                          <div style="padding-bottom: 2px;">
                            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;">12M Price Target</div>
                            <div style="font-size: 13px; font-weight: 600; color: #0F172A; font-variant-numeric: tabular-nums; margin-top: 2px;">{target_drawer_str}</div>
                          </div>
                        </div>
                        <div style="border-top: 1px solid #F1F5F9; padding-top: 8px; margin-top: 6px; font-size: 11px; color: #94A3B8; font-weight: 500;">
                          Valuation Methodology: {mode_lbl}
                        </div>
                        """
                    st.html(drawer_html)

    # Pad empty columns
    for empty_col in cols[len(row_tickers):]:
        empty_col.empty()

    st.markdown("---")


# ── 7. Full Data Table (Safe from KeyError) ──
with st.expander("Full valuation data table", expanded=False):
    rows = []
    for tk, d in all_data.items():
        status = compute_status(d, timeframe=val_timeframe)
        safe_name = d.get("shortName") or d.get("longName") or d.get("name") or tk
        ccy_s = get_currency_symbol(d.get("currency", "USD"))
        ath_v = d.get("ath", np.nan)
        dist_v = d.get("dist_ath", np.nan)

        if val_timeframe == "1-Year" and "Z252" in d.get("hist", pd.DataFrame()).columns:
            z_series = d.get("hist", pd.DataFrame())["Z252"].dropna()
            z_label = "Std Dev (1Y)"
        else:
            z_col = "Z50" if "Z50" in d.get("hist", pd.DataFrame()).columns else ("Z16" if "Z16" in d.get("hist", pd.DataFrame()).columns else None)
            z_series = d.get("hist", pd.DataFrame())[z_col].dropna() if z_col else pd.Series(dtype=float)
            z_label = "Std Dev (50d)"

        z_v_str = f"{float(z_series.iloc[-1]):+.2f}σ" if len(z_series) else "—"

        peg_val = d.get("peg_2y")
        peg_display = f"{peg_val:.2f}" if peg_val is not None and not np.isnan(peg_val) else "—"

        target_up_v = d.get("target_upside_pct")
        target_up_str = f"{target_up_v:+.1f}%" if (target_up_v is not None and not np.isnan(target_up_v)) else "—"

        row = {
            "Ticker": tk,
            "Name": safe_name,
            "Status": status,
            "Price": round(d.get("current_price", np.nan), 2),
            "12M Target": target_up_str,
            "Distance to All-Time High (ATH)": f"{dist_v:+.1f}%" if not np.isnan(dist_v) else "—",
            z_label: z_v_str,
            "2Y PEG": peg_display,
            "ATH": f"{ccy_s}{ath_v:.2f}" if not np.isnan(ath_v) else "—",
        }
        if d.get("error"):
            row["Error"] = d.get("error")
        elif d.get("pe_mode"):
            fv_pe = d.get("pe_mid_1y" if val_timeframe == "1-Year" else "pe_mid_90d", d.get("pe_mid", np.nan))
            up_pe = d.get("upside_1y" if val_timeframe == "1-Year" else "upside_90d", np.nan)
            row["Mode"]                 = f"P/E Corridor ({val_timeframe})"
            row["Current P/E"]          = round(d.get("pe_current", np.nan), 2)
            row[f"Fair Value P/E ({val_timeframe})"] = round(fv_pe, 2) if not np.isnan(fv_pe) else "—"
            row["Upside to Fair Value"] = f"{up_pe:+.1f}%" if not np.isnan(up_pe) else "—"
            row["Upcoming Earnings"]    = d.get("next_earnings") or "—"
        else:
            fv_p = d.get("price_mid_1y" if val_timeframe == "1-Year" else "price_mid_90d", d.get("price_mid", np.nan))
            up_p = d.get("upside_1y" if val_timeframe == "1-Year" else "upside_90d", np.nan)
            row["Mode"]                   = f"Price Corridor ({val_timeframe})"
            row[f"Fair Value Price ({val_timeframe})"] = round(fv_p, 2) if not np.isnan(fv_p) else "—"
            row["Upside to Fair Value"]   = f"{up_p:+.1f}%" if not np.isnan(up_p) else "—"
            row["Upcoming Earnings"]      = d.get("next_earnings") or "—"
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)


# ─────────────────────────────────────────────
# 8. SOCIAL MEDIA SNAPSHOT / EXPORT HANDLER
# ─────────────────────────────────────────────
SNAPSHOT_JS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<script>
(function() {
  function initDeanActions() {
    let pWin = window;
    let pDoc = document;
    try {
      if (typeof window.parent !== 'undefined' && window.parent && window.parent.document) {
        pWin = window.parent;
        pDoc = window.parent.document;
      }
    } catch(e) {
      pWin = window;
      pDoc = document;
    }

    // Load html2canvas in parent document if not present
    if (!pWin.html2canvas && !window.html2canvas) {
      const s = pDoc.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
      pDoc.head.appendChild(s);
    }

    // Load Plotly.js in parent document if not present so modal cloning can render
    if (!pWin.Plotly && !pDoc.getElementById('dean-plotly-cdn')) {
      const ps = pDoc.createElement('script');
      ps.id = 'dean-plotly-cdn';
      ps.src = 'https://cdn.plot.ly/plotly-2.35.2.min.js';
      pDoc.head.appendChild(ps);
    }

    // ── Watchlist LocalStorage Next-Day Memory ──
    try {
      const urlParams = new URLSearchParams(pWin.location.search);
      const urlWatchlist = urlParams.get('watchlist');

      if (!urlWatchlist) {
        // Visitor arrived at bare URL without watchlist param: check if they have a saved watchlist from previous day
        const saved = pWin.localStorage ? pWin.localStorage.getItem('dean_saved_watchlist') : null;
        if (saved && saved.trim().length > 0) {
          urlParams.set('watchlist', saved.trim());
          pWin.location.search = urlParams.toString();
        }
      } else {
        // Active watchlist in URL: persist it in localStorage for next day visits
        if (pWin.localStorage) {
          pWin.localStorage.setItem('dean_saved_watchlist', urlWatchlist);
        }
      }
    } catch(err) {
      console.warn('LocalStorage watchlist sync error:', err);
    }

    // Modal creation helper in pDoc
    function getOrCreateModal() {
      let m = pDoc.getElementById('dean-chart-modal');
      if (!m) {
        m = pDoc.createElement('div');
        m.id = 'dean-chart-modal';
        m.style.display = 'none';
        m.innerHTML = `
          <div id="dean-modal-overlay" style="position: fixed; inset: 0; background: rgba(15, 23, 42, 0.78); backdrop-filter: blur(4px); z-index: 9999999; display: flex; align-items: center; justify-content: center; padding: 12px;">
            <div id="dean-modal-card" style="background: #FFFFFF; border-radius: 12px; width: 96vw; max-width: 1440px; height: 94vh; max-height: 94vh; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); border: 1px solid #E2E8F0; overflow: hidden;">
              <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-bottom: 1px solid #F1F5F9; background: #FAFBFD; flex-shrink: 0;">
                <div style="display: flex; align-items: baseline; gap: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  <span id="dean-modal-title" style="font-size: 1.30rem; font-weight: 800; color: #0F172A; letter-spacing: -0.01em;"></span>
                  <span id="dean-modal-subtitle" style="font-size: 0.88rem; color: #64748B; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"></span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; flex-shrink: 0;">
                  <button id="dean-modal-reset-btn" onclick="(window.parent.deanRefocus||window.deanRefocus||function(){{}})('modal')" style="background: #FEF08A; border: 1px solid #EAB308; border-radius: 6px; padding: 5px 11px; font-weight: 700; color: #1F2937; cursor: pointer; font-size: 0.74rem; display: flex; align-items: center; gap: 3px;">↺ Refocus</button>
                  <button id="dean-modal-close-btn" onclick="(window.parent.deanCloseModal||window.deanCloseModal||function(){{}})()" style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 5px 11px; font-weight: 700; color: #334155; cursor: pointer; font-size: 0.74rem;">✕ Close</button>
                </div>
              </div>
              <div id="dean-modal-plot-container" style="padding: 6px 10px 10px 10px; flex: 1 1 auto; width: 100%; max-width: 100%; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden;"></div>
            </div>
          </div>
          <style>
            #dean-modal-plot-container .js-plotly-plot,
            #dean-modal-plot-container .plot-container,
            #dean-modal-plot-container .svg-container,
            #dean-modal-plot-container .main-svg {
              width: 100% !important;
              max-width: 100% !important;
              height: 100% !important;
            }
            @media (max-width: 768px) {
              #dean-modal-overlay {
                padding: 0 !important;
                align-items: flex-start !important;
              }
              #dean-modal-card {
                width: 98vw !important;
                max-width: 98vw !important;
                height: 96vh !important;
                max-height: 96vh !important;
                margin: 2vh auto !important;
                border-radius: 10px !important;
                display: flex !important;
                flex-direction: column !important;
                overflow: hidden !important;
              }
              #dean-modal-plot-container {
                flex: 1 1 auto !important;
                height: calc(96vh - 50px) !important;
                min-height: calc(96vh - 50px) !important;
                max-height: calc(96vh - 50px) !important;
                padding: 4px 4px 6px 4px !important;
                overflow: hidden !important;
              }
            }
          </style>
        `;
        pDoc.body.appendChild(m);

        const overlay = m.querySelector('#dean-modal-overlay');
        if (overlay) {
          overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
              if (pWin.deanCloseModal) pWin.deanCloseModal();
              else if (window.deanCloseModal) window.deanCloseModal();
            }
          });
        }
      } else {
        const oldFs = m.querySelector('#dean-modal-fs-btn');
        if (oldFs) oldFs.remove();
      }
      return m;
    }

    getOrCreateModal();

    pDoc.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (pWin.deanCloseModal) pWin.deanCloseModal();
        else if (window.deanCloseModal) window.deanCloseModal();
      }
    });

    pWin.addEventListener('resize', () => {
      const m = pDoc.getElementById('dean-chart-modal');
      if (m && m.style.display !== 'none') {
        const plotBox = m.querySelector('#dean-modal-plot-container');
        const Plotly = pWin.Plotly || window.Plotly;
        if (Plotly && plotBox) Plotly.Plots.resize(plotBox);
      }
    });

    // Dynamic color coding for sidebar tags: Green (Buy Zone), Amber (Standard DCA), Red (Wait for Pullback), Brand Yellow (Tickers)
    function enforceTagContrast() {
      const tags = pDoc.querySelectorAll('[data-tag], span[data-tag], .e1kig3hy3, [data-baseweb="tag"]');
      tags.forEach(tag => {
        const text = (tag.innerText || tag.textContent || '').trim();

        if (text.includes('Buy Zone')) {
          // 🟢 Green: Buy Zone
          tag.style.setProperty('background-color', '#ECFDF5', 'important');
          tag.style.setProperty('border', '1px solid #10B981', 'important');
          tag.style.setProperty('color', '#047857', 'important');
          tag.style.setProperty('-webkit-text-fill-color', '#047857', 'important');
          tag.style.setProperty('box-shadow', '0 1px 2px rgba(16, 185, 129, 0.20)', 'important');

          const children = tag.querySelectorAll('*');
          children.forEach(el => {
            el.style.setProperty('color', '#047857', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#047857', 'important');
            if (el.tagName && el.tagName.toLowerCase() === 'span') {
              el.style.setProperty('font-weight', '700', 'important');
            }
            if (el.tagName && (el.tagName.toLowerCase() === 'svg' || el.tagName.toLowerCase() === 'path' || el.tagName.toLowerCase() === 'button')) {
              el.style.setProperty('fill', '#047857', 'important');
              el.style.setProperty('stroke', '#047857', 'important');
              el.style.setProperty('color', '#047857', 'important');
            }
          });
        } else if (text.includes('Standard DCA')) {
          // 🟡 Amber: Standard DCA
          tag.style.setProperty('background-color', '#FFFBEB', 'important');
          tag.style.setProperty('border', '1px solid #F59E0B', 'important');
          tag.style.setProperty('color', '#B45309', 'important');
          tag.style.setProperty('-webkit-text-fill-color', '#B45309', 'important');
          tag.style.setProperty('box-shadow', '0 1px 2px rgba(245, 158, 11, 0.20)', 'important');

          const children = tag.querySelectorAll('*');
          children.forEach(el => {
            el.style.setProperty('color', '#B45309', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#B45309', 'important');
            if (el.tagName && el.tagName.toLowerCase() === 'span') {
              el.style.setProperty('font-weight', '700', 'important');
            }
            if (el.tagName && (el.tagName.toLowerCase() === 'svg' || el.tagName.toLowerCase() === 'path' || el.tagName.toLowerCase() === 'button')) {
              el.style.setProperty('fill', '#B45309', 'important');
              el.style.setProperty('stroke', '#B45309', 'important');
              el.style.setProperty('color', '#B45309', 'important');
            }
          });
        } else if (text.includes('Wait for Pullback')) {
          // 🔴 Red: Wait for Pullback
          tag.style.setProperty('background-color', '#FEF2F2', 'important');
          tag.style.setProperty('border', '1px solid #EF4444', 'important');
          tag.style.setProperty('color', '#B91C1C', 'important');
          tag.style.setProperty('-webkit-text-fill-color', '#B91C1C', 'important');
          tag.style.setProperty('box-shadow', '0 1px 2px rgba(239, 68, 68, 0.20)', 'important');

          const children = tag.querySelectorAll('*');
          children.forEach(el => {
            el.style.setProperty('color', '#B91C1C', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#B91C1C', 'important');
            if (el.tagName && el.tagName.toLowerCase() === 'span') {
              el.style.setProperty('font-weight', '700', 'important');
            }
            if (el.tagName && (el.tagName.toLowerCase() === 'svg' || el.tagName.toLowerCase() === 'path' || el.tagName.toLowerCase() === 'button')) {
              el.style.setProperty('fill', '#B91C1C', 'important');
              el.style.setProperty('stroke', '#B91C1C', 'important');
              el.style.setProperty('color', '#B91C1C', 'important');
            }
          });
        } else {
          // 🟡 Default: Stock ticker chips retain brand vibrant yellow
          tag.style.setProperty('background-color', '#FDE047', 'important');
          tag.style.setProperty('border', '1px solid #EAB308', 'important');
          tag.style.setProperty('color', '#1F2937', 'important');
          tag.style.setProperty('-webkit-text-fill-color', '#1F2937', 'important');
          tag.style.setProperty('box-shadow', '0 1px 2px rgba(234, 179, 8, 0.20)', 'important');

          const children = tag.querySelectorAll('*');
          children.forEach(el => {
            el.style.setProperty('color', '#1F2937', 'important');
            el.style.setProperty('-webkit-text-fill-color', '#1F2937', 'important');
            if (el.tagName && el.tagName.toLowerCase() === 'span') {
              el.style.setProperty('font-weight', '700', 'important');
              el.style.setProperty('color', '#1F2937', 'important');
            }
            if (el.tagName && (el.tagName.toLowerCase() === 'svg' || el.tagName.toLowerCase() === 'path' || el.tagName.toLowerCase() === 'button')) {
              el.style.setProperty('fill', '#1F2937', 'important');
              el.style.setProperty('stroke', '#1F2937', 'important');
              el.style.setProperty('color', '#1F2937', 'important');
            }
          });
        }
      });
    }

    function enforceSegmentedControl() {
      const segButtons = pDoc.querySelectorAll('div[data-testid="stButtonGroup"] button, .stButtonGroup button, button[data-variant="segmented_control"], div[data-testid="stSegmentedControl"] button');
      segButtons.forEach(btn => {
        const isChecked = btn.hasAttribute('data-selected') || 
                          btn.getAttribute('aria-checked') === 'true' || 
                          btn.getAttribute('aria-selected') === 'true' ||
                          btn.getAttribute('aria-pressed') === 'true' ||
                          btn.getAttribute('data-checked') === 'true';

        if (isChecked) {
          btn.style.setProperty('background-color', '#FDE047', 'important');
          btn.style.setProperty('border', '1px solid #EAB308', 'important');
          btn.style.setProperty('color', '#1F2937', 'important');
          btn.style.setProperty('-webkit-text-fill-color', '#1F2937', 'important');
          btn.style.setProperty('font-weight', '700', 'important');
          btn.style.setProperty('border-radius', '6px', 'important');
          btn.style.setProperty('box-shadow', '0 1px 2px rgba(234, 179, 8, 0.20)', 'important');
          btn.querySelectorAll('*').forEach(c => {
            c.style.setProperty('color', '#1F2937', 'important');
            c.style.setProperty('-webkit-text-fill-color', '#1F2937', 'important');
            c.style.setProperty('font-weight', '700', 'important');
          });
        } else {
          btn.style.setProperty('background-color', '#FFFFFF', 'important');
          btn.style.setProperty('border', '1px solid #E2E8F0', 'important');
          btn.style.setProperty('color', '#475569', 'important');
          btn.style.setProperty('-webkit-text-fill-color', '#475569', 'important');
          btn.style.setProperty('font-weight', '600', 'important');
          btn.style.setProperty('border-radius', '6px', 'important');
          btn.querySelectorAll('*').forEach(c => {
            c.style.setProperty('color', '#475569', 'important');
            c.style.setProperty('-webkit-text-fill-color', '#475569', 'important');
            c.style.setProperty('font-weight', '600', 'important');
          });
        }
      });

      const bgs = pDoc.querySelectorAll('div[data-testid="stButtonGroup"] > div, .stButtonGroup > div, div[data-testid="stSegmentedControl"] > div');
      bgs.forEach(bg => {
        bg.style.setProperty('background-color', '#F8FAFC', 'important');
        bg.style.setProperty('border', '1px solid #E2E8F0', 'important');
        bg.style.setProperty('border-radius', '8px', 'important');
        bg.style.setProperty('padding', '3px', 'important');
        bg.style.setProperty('gap', '4px', 'important');
      });
    }

    enforceTagContrast();
    enforceSegmentedControl();

    if (!pDoc.__dean_tag_observer && pWin.MutationObserver) {
      try {
        const obs = new pWin.MutationObserver(function() {
          enforceTagContrast();
          enforceSegmentedControl();
        });
        obs.observe(pDoc.body, { childList: true, subtree: true });
        pDoc.__dean_tag_observer = obs;
      } catch(e) {}
    }

    function getCardWrapper(ticker) {
      const marker = pDoc.getElementById('card-' + ticker) || document.getElementById('card-' + ticker);
      if (!marker) return null;

      // 0. Try finding key-based card container
      const keyWrapper = marker.closest('[class*="st-key-stock_card_"]');
      if (keyWrapper) return keyWrapper;

      // 1. Try finding ancestor stVerticalBlockBorderWrapper that contains the chart or multiple KPI boxes
      const borderWrapper = marker.closest('[data-testid="stVerticalBlockBorderWrapper"]');
      if (borderWrapper && (borderWrapper.querySelector('.js-plotly-plot') || borderWrapper.querySelectorAll('.kpi-mini-box').length >= 4)) {
        return borderWrapper;
      }

      // 2. Traverse up through parentElements until finding the element containing both metrics and chart
      let curr = marker.parentElement;
      while (curr && curr !== pDoc.body && curr !== pDoc.documentElement) {
        if (curr.querySelectorAll && (curr.querySelector('.js-plotly-plot') || curr.querySelectorAll('.kpi-mini-box').length >= 4)) {
          if (curr.parentElement && curr.parentElement.getAttribute && curr.parentElement.getAttribute('data-testid') === 'stVerticalBlockBorderWrapper') {
            return curr.parentElement;
          }
          return curr;
        }
        curr = curr.parentElement;
      }

      return borderWrapper || marker.closest('[data-testid="stVerticalBlock"]') || marker.parentElement;
    }

    if (pDoc.__dean_snapshot_attached) return;
    pDoc.__dean_snapshot_attached = true;

    // ── Save Card Button Click (4:5 Aspect Ratio 1080x1350 px for Instagram) ──
    pDoc.addEventListener('click', async function(e) {
      const btn = e.target.closest('.save-card-btn');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();

      const ticker = btn.getAttribute('data-ticker');
      const origText = btn.innerHTML;
      btn.innerHTML = '⏳ Exporting 4:5...';
      btn.disabled = true;

      const target = getCardWrapper(ticker);

      if (!target) {
        alert('Card container not found for ' + ticker);
        btn.innerHTML = origText;
        btn.disabled = false;
        return;
      }

      // Hide action buttons, toolbars, and expanders during snapshot
      const buttonsToHide = target.querySelectorAll('.save-card-btn, .expand-chart-btn');
      buttonsToHide.forEach(el => el.style.opacity = '0');
      const toolbarsToHide = target.querySelectorAll('[data-testid="stElementToolbar"], [data-testid="stElementToolbarButton"], .modebar-container');
      toolbarsToHide.forEach(el => el.style.display = 'none');
      const expanders = target.querySelectorAll('.stExpander');
      expanders.forEach(el => el.style.display = 'none');

      try {
        const h2c = pWin.html2canvas || window.html2canvas;
        if (h2c) {
          const rawCanvas = await h2c(target, {
            scale: 2,
            backgroundColor: '#FFFFFF',
            useCORS: true,
            logging: false,
          });

          // ── Guarantee Exact 4:5 Aspect Ratio (1080 x 1350 px) for Instagram ──
          const TARGET_W = 1080;
          const TARGET_H = 1350;

          const outCanvas = pDoc.createElement('canvas');
          outCanvas.width = TARGET_W;
          outCanvas.height = TARGET_H;
          const ctx = outCanvas.getContext('2d');

          // High quality image smoothing
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';

          // Pristine white background
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(0, 0, TARGET_W, TARGET_H);

          // Calculate scaling to fit into 1080x1350 with balanced, professional margins
          // 24px margin gives clean breathing room so content never touches the absolute image border
          const padX = 24;
          const padY = 24;
          const maxW = TARGET_W - (padX * 2);
          const maxH = TARGET_H - (padY * 2);

          const scale = Math.min(maxW / rawCanvas.width, maxH / rawCanvas.height);
          const drawW = Math.round(rawCanvas.width * scale);
          const drawH = Math.round(rawCanvas.height * scale);
          const drawX = Math.round((TARGET_W - drawW) / 2);
          const drawY = Math.round((TARGET_H - drawH) / 2);

          // Draw the high-resolution rendered card centered on 4:5 canvas
          ctx.drawImage(rawCanvas, drawX, drawY, drawW, drawH);

          const link = pDoc.createElement('a');
          link.download = ticker + '_valuation_card_4x5_theinvestingdean.png';
          link.href = outCanvas.toDataURL('image/png');
          pDoc.body.appendChild(link);
          link.click();
          pDoc.body.removeChild(link);
          btn.innerHTML = '✅ Saved 4:5!';
        } else {
          const plotlyDiv = target.querySelector('.js-plotly-plot');
          const Plotly = pWin.Plotly || window.Plotly;
          if (plotlyDiv && Plotly) {
            await Plotly.downloadImage(plotlyDiv, {
              format: 'png',
              width: 1080,
              height: 1350,
              filename: ticker + '_valuation_card_4x5_theinvestingdean',
            });
            btn.innerHTML = '✅ Saved 4:5!';
          } else {
            btn.innerHTML = '❌ Error';
          }
        }
      } catch(err) {
        console.error('Snapshot failed, falling back to Plotly:', err);
        try {
          const plotlyDiv = target.querySelector('.js-plotly-plot');
          const Plotly = pWin.Plotly || window.Plotly;
          if (plotlyDiv && Plotly) {
            await Plotly.downloadImage(plotlyDiv, {
              format: 'png',
              width: 1080,
              height: 1350,
              filename: ticker + '_valuation_card_4x5_theinvestingdean',
            });
            btn.innerHTML = '✅ Saved 4:5!';
          } else {
            btn.innerHTML = '❌ Error';
          }
        } catch(e2) {
          btn.innerHTML = '❌ Error';
        }
      } finally {
        expanders.forEach(el => el.style.display = '');
        toolbarsToHide.forEach(el => el.style.display = '');
        buttonsToHide.forEach(el => el.style.opacity = '1');
        setTimeout(() => {
          btn.innerHTML = origText;
          btn.disabled = false;
        }, 2000);
      }
    }, true);

    function openModalForPlot(origPlot, ticker) {
      const modal = getOrCreateModal();
      const card = origPlot ? (origPlot.closest('[data-testid="stVerticalBlockBorderWrapper"]') || origPlot.closest('[data-testid="stVerticalBlock"]') || origPlot.parentElement) : getCardWrapper(ticker);
      const plotEl = origPlot || (card ? card.querySelector('.js-plotly-plot') : null);
      const Plotly = pWin.Plotly || window.Plotly;

      if (Plotly && plotEl && plotEl.data) {
        try {
          const cloneData = JSON.parse(JSON.stringify(plotEl.data));
          const cloneLayout = JSON.parse(JSON.stringify(plotEl.layout || {}));

          // CRITICAL: delete any hardcoded width from card layout so Plotly stretches 100%
          delete cloneLayout.width;
          cloneLayout.autosize = true;

          // Enable touch pan and zoom strictly inside the expanded modal
          if (!cloneLayout.xaxis) cloneLayout.xaxis = {};
          cloneLayout.xaxis.fixedrange = false;

          if (!cloneLayout.yaxis) cloneLayout.yaxis = {};
          cloneLayout.yaxis.fixedrange = false;

          cloneLayout.dragmode = 'zoom';

          const isMobile = (pWin.innerWidth <= 768) || (window.innerWidth <= 768);
          cloneLayout.height = isMobile 
            ? Math.max(540, Math.round(pWin.innerHeight * 0.86))
            : Math.max(560, Math.min(Math.round(pWin.innerHeight * 0.80), 750));

          cloneLayout.margin = isMobile
            ? { l: 38, r: 14, t: 12, b: 30 }
            : { l: 55, r: 25, t: 22, b: 40 };

          cloneLayout.showlegend = true;
          cloneLayout.legend = {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.01,
            xanchor: 'center',
            x: 0.5,
            itemwidth: 30,
            font: { size: isMobile ? 8.5 : 10 },
            bgcolor: 'rgba(255, 255, 255, 0.85)',
          };
          cloneLayout.paper_bgcolor = '#FFFFFF';
          cloneLayout.plot_bgcolor = '#FFFFFF';

          // Ensure traces display cleanly in modal legend
          if (Array.isArray(cloneData)) {
            cloneData.forEach(tr => {
              if (tr && tr.name && !tr.name.startsWith('Current:')) {
                tr.showlegend = true;
              }
            });
          }

          let safeName = '';
          if (card) {
            const nameEl = card.querySelector('.stock-card-container span:nth-child(2)');
            safeName = nameEl ? nameEl.innerText : '';
          }

          pDoc.getElementById('dean-modal-title').innerText = ticker || '';
          pDoc.getElementById('dean-modal-subtitle').innerText = safeName;
          modal.style.display = 'block';

          const plotBox = pDoc.getElementById('dean-modal-plot-container');
          plotBox.innerHTML = '';
          plotBox.style.width = '100%';

          Plotly.newPlot(plotBox, cloneData, cloneLayout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtons: [['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']],
            scrollZoom: true,
          }).then(() => {
            Plotly.Plots.resize(plotBox);
            setTimeout(() => {
              Plotly.Plots.resize(plotBox);
            }, 60);
          });
          return;
        } catch(err) {
          console.warn('Plotly modal cloning failed, using fallback:', err);
        }
      }

      // Fallback: Native HTML5 element fullscreen directly on chart container
      const chartContainer = (card ? card.querySelector('[data-testid="stPlotlyChart"]') : null) || origPlot;
      if (chartContainer) {
        if (chartContainer.requestFullscreen) {
          chartContainer.requestFullscreen();
          return;
        } else if (chartContainer.webkitRequestFullscreen) {
          chartContainer.webkitRequestFullscreen();
          return;
        }
      }
    }

    // Expose global methods directly to window and pWin for direct inline onclick execution
    pWin.deanCloseModal = window.deanCloseModal = function() {
      const m = pDoc.getElementById('dean-chart-modal');
      if (m) {
        m.style.display = 'none';
        const plotBox = m.querySelector('#dean-modal-plot-container');
        const Plotly = pWin.Plotly || window.Plotly;
        if (Plotly && plotBox) {
          try { Plotly.purge(plotBox); } catch(e){}
        }
      }
    };

    pWin.deanRefocus = window.deanRefocus = function(target) {
      const Plotly = pWin.Plotly || window.Plotly;
      if (target === 'modal') {
        const plotBox = pDoc.getElementById('dean-modal-plot-container');
        if (Plotly && plotBox) {
          Plotly.relayout(plotBox, {
            'xaxis.autorange': true,
            'yaxis.autorange': true
          }).then(() => {
            Plotly.Plots.resize(plotBox);
          });
        }
        return;
      }
      const card = getCardWrapper(target);
      if (!card) return;
      const plot = card.querySelector('.js-plotly-plot') || card.querySelector('[data-testid="stPlotlyChart"]');
      if (plot && Plotly) {
        Plotly.relayout(plot, {
          'xaxis.autorange': true,
          'yaxis.autorange': true
        });
        const dblEvt = new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: pWin });
        plot.dispatchEvent(dblEvt);
      }
    };

    pWin.deanOpenFullscreen = window.deanOpenFullscreen = function(ticker) {
      const card = getCardWrapper(ticker);
      const plot = card ? (card.querySelector('.js-plotly-plot') || card.querySelector('[data-testid="stPlotlyChart"]')) : null;
      openModalForPlot(plot, ticker);
    };

    // ── Remove any legacy injected modebar buttons ──
    function removeLegacyModebarButtons() {
      pDoc.querySelectorAll('.dean-modebar-fs-btn').forEach(btn => btn.remove());
    }
    removeLegacyModebarButtons();
    setInterval(removeLegacyModebarButtons, 2000);

    // ── Intercept Streamlit's Native Fullscreen Button to open our Interactive Modal ──
    // Ensures only ONE clean button exists on the preview chart and routes directly to our interactive modal
    pDoc.addEventListener('click', function(e) {
      const fsBtn = e.target.closest('[data-testid="stElementToolbarButton"], [data-testid="stElementToolbar"] button, button[title*="fullscreen" i], button[aria-label*="fullscreen" i]');
      if (!fsBtn) return;
      const chart = fsBtn.closest('[data-testid="stPlotlyChart"]') || fsBtn.closest('[data-testid="stElementContainer"]');
      if (chart && !chart.closest('#dean-modal-card') && !chart.closest('#dean-chart-modal')) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        // Open our full-screen modal directly

        const card = chart.closest('[data-testid="stVerticalBlockBorderWrapper"]') || chart.parentElement;
        let ticker = '';
        if (card) {
          const saveBtn = card.querySelector('.save-card-btn');
          if (saveBtn) ticker = saveBtn.getAttribute('data-ticker') || '';
          if (!ticker) {
            const headerSpan = card.querySelector('.stock-card-container span');
            if (headerSpan) ticker = headerSpan.innerText.trim();
          }
        }
        const origPlot = chart.querySelector('.js-plotly-plot') || chart;
        openModalForPlot(origPlot, ticker);
      }
    }, true);

    // ── Expand Chart Button Click & Mobile Touch Handler ──
    function handleExpandChart(e) {
      const expandBtn = e.target.closest('.expand-chart-btn');
      if (!expandBtn) return;
      if (e.cancelable) e.preventDefault();
      e.stopPropagation();

      const ticker = expandBtn.getAttribute('data-ticker') || '';
      const card = expandBtn.closest('[data-testid="stVerticalBlockBorderWrapper"]') || getCardWrapper(ticker);
      let origPlot = card ? (card.querySelector('.js-plotly-plot') || card.querySelector('[data-testid="stPlotlyChart"]')) : null;
      if (origPlot && origPlot.querySelector && origPlot.querySelector('.js-plotly-plot')) {
        origPlot = origPlot.querySelector('.js-plotly-plot');
      }
      openModalForPlot(origPlot, ticker);
    }
    pDoc.addEventListener('click', handleExpandChart, true);
    pDoc.addEventListener('touchend', handleExpandChart, { capture: true, passive: false });
    if (document !== pDoc) {
      document.addEventListener('click', handleExpandChart, true);
      document.addEventListener('touchend', handleExpandChart, { capture: true, passive: false });
    }

    // ── Refocus Chart Button Click on Card ──
    pDoc.addEventListener('click', function(e) {
      const refocusBtn = e.target.closest('.refocus-chart-btn');
      if (!refocusBtn) return;
      e.preventDefault();
      e.stopPropagation();

      const card = refocusBtn.closest('[data-testid="stVerticalBlockBorderWrapper"]') || getCardWrapper(refocusBtn.getAttribute('data-ticker'));
      if (!card) return;

      const origPlot = card.querySelector('.js-plotly-plot') || card.querySelector('[data-testid="stPlotlyChart"]');
      if (origPlot) {
        const Plotly = pWin.Plotly || window.Plotly;
        if (Plotly && origPlot.layout) {
          Plotly.relayout(origPlot, {
            'xaxis.autorange': true,
            'yaxis.autorange': true
          });
        }
        // Also trigger native double-click which Plotly listens to for resetting axes!
        const dblEvt = new MouseEvent('dblclick', { bubbles: true, cancelable: true, view: pWin });
        origPlot.dispatchEvent(dblEvt);
      }
    }, true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDeanActions);
  } else {
    initDeanActions();
  }
  setTimeout(initDeanActions, 500);
})();
</script>
"""

if hasattr(st, "html"):
    st.html(SNAPSHOT_JS, unsafe_allow_javascript=True)
components.html(SNAPSHOT_JS, height=0)
