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

# ─────────────────────────────────────────────
# DEFAULT CURATED BASKET (@theinvestingdean)
# Edit this dictionary anytime to customize the default stocks shown to all visitors:
# ─────────────────────────────────────────────
DEFAULT_TICKERS = {
    # Equities
    "NVDA":    "NVIDIA",
    "AAPL":    "Apple",
    "MSFT":    "Microsoft",
    "TSLA":    "Tesla",
    "GOOGL":   "Alphabet",
    # ETFs & Funds
    "VUAG.L":  "Vanguard S&P 500 (Acc)",
    "VWRP.L":  "Vanguard All-World (Acc)",
}
TICKERS = DEFAULT_TICKERS

# Backend ticker routing mapping (e.g. resolve SMSN.L to London IOB SMSN.IL ~5,110 USD)
TICKER_FETCH_MAPPING = {
    "SMSN.L": "SMSN.IL",
}

# Tickers where we always fall back to MA corridor (ETFs with no P/E)
MA_FALLBACK_TICKERS = {"SMGB.L", "SPCX", "VUAG.L", "VWRP.L"}

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

PAGE_BG      = "#F8FAFC"       # Clean slate off-white canvas
CARD_BG      = "#FFFFFF"       # Pure white cards
GRID_COLOR   = "#F1F5F9"       # Thin light-gray grid lines
TEXT_DARK    = "#0F172A"       # Dark slate for headings / primary text
MUTED_SLATE  = "#64748B"       # Crisp slate for secondary labels
BORDER_COLOR = "#E2E8F0"       # Subtle card borders
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
        /* ── Base canvas ── */
        .stApp {{
            background-color: {PAGE_BG};
            color: {TEXT_DARK};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid {BORDER_COLOR};
        }}

        /* ── Distinct Stock Card Container ── */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #FFFFFF !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
            padding: 14px 14px !important;
            margin-bottom: 20px !important;
        }}

        /* ── Uniform Responsive KPI Mini-Boxes ── */
        .kpi-mini-box {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 8px 10px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
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
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            line-height: 1.2;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
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
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 10px 14px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
            min-height: 84px;
        }}
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {{
            color: {MUTED_SLATE} !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
            color: {TEXT_DARK} !important;
            font-size: 1.35rem !important;
            font-weight: 700 !important;
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
            display: inline-block;
            text-decoration: none !important;
            box-shadow: 0 1px 2px rgba(234, 179, 8, 0.20) !important;
            transition: all 0.2s ease-in-out;
        }}
        a.dean-badge:hover {{
            background-color: #FACC15 !important;
            color: #111827 !important;
            border-color: #CA8A04 !important;
            box-shadow: 0 2px 4px rgba(234, 179, 8, 0.30);
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

        /* ── Segmented Control (90-Day vs 1-Year Timeframe Toggle) ── */
        div[data-testid="stSegmentedControl"] {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
        }}
        div[data-testid="stSegmentedControl"] > div {{
            background-color: #F8FAFC !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            padding: 2px !important;
            gap: 2px !important;
        }}
        div[data-testid="stSegmentedControl"] button {{
            border-radius: 6px !important;
            font-size: 0.80rem !important;
            font-weight: 600 !important;
            color: #475569 !important;
            border: none !important;
            padding: 4px 12px !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stSegmentedControl"] button:hover {{
            color: #0F172A !important;
            background-color: #E2E8F0 !important;
        }}
        div[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
            background-color: #FDE047 !important;
            color: #1F2937 !important;
            font-weight: 800 !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
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
        .expand-chart-btn {{
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
        .expand-chart-btn:hover {{
            background-color: #FEF08A !important;
            color: #1F2937 !important;
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
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stVerticalBlockBorderWrapper"]) {{
                flex-direction: column !important;
                display: flex !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stVerticalBlockBorderWrapper"]) > div[data-testid="column"] {{
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 14px !important;
            }}
            /* Clean edge padding on mobile phones for maximum chart width */
            .block-container {{
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
                padding-top: 1.25rem !important;
                padding-bottom: 2rem !important;
            }}
            /* Card inner padding */
            div[data-testid="stVerticalBlockBorderWrapper"] {{
                padding: 10px 8px !important;
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

            /* ── Maintain Mobile Restriction: Completely Hide Fullscreen Expand Button on Mobile ── */
            .dean-modebar-fs-btn,
            .modebar-btn.dean-modebar-fs-btn,
            div[data-testid="stPlotlyChart"] .modebar-container,
            div[data-testid="stPlotlyChart"] .modebar,
            div[data-testid="stPlotlyChart"] div[data-testid="stElementToolbar"],
            div[data-testid="stElementToolbar"],
            [data-testid="stElementToolbarButton"],
            .expand-chart-btn {{
                display: none !important;
                visibility: hidden !important;
                pointer-events: none !important;
                width: 0 !important;
                height: 0 !important;
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
) -> str:
    """
    Generate side-by-side / stacked badges for regular daily session and extended-hours trading.
    Preserves official regular session change and displays secondary badge for pre/post-market
    with percentage and absolute price, e.g. Pre: +0.3% ($3.12).
    """
    # 1. Regular session badge
    reg_badge = ""
    if reg_pct is not None and not np.isnan(reg_pct):
        if reg_pct > 0.05:
            bg_r = "#DCFCE7"
            col_r = "#15803D"
            lbl_r = f"▲ +{reg_pct:.1f}%"
        elif reg_pct < -0.05:
            bg_r = "#FEE2E2"
            col_r = "#B91C1C"
            lbl_r = f"▼ {reg_pct:.1f}%"
        else:
            bg_r = "#F1F5F9"
            col_r = "#64748B"
            lbl_r = "0.0%"
        reg_badge = f'<span style="font-size: 0.64rem; font-weight: 700; background-color: {bg_r}; color: {col_r}; padding: 1px 5px; border-radius: 9999px; line-height: 1.1; white-space: nowrap;">{lbl_r}</span>'

    # 2. Extended-hours badge (pre-market or post-market)
    ext_badge = ""
    if ext_label and ext_pct is not None and not np.isnan(ext_pct) and abs(float(ext_pct)) >= 0.005:
        if ext_pct > 0.05:
            bg_e = "#DCFCE7"
            col_e = "#15803D"
            bdr_e = "#A7F3D0"
        elif ext_pct < -0.05:
            bg_e = "#FEE2E2"
            col_e = "#B91C1C"
            bdr_e = "#FECACA"
        else:
            bg_e = "#F1F5F9"
            col_e = "#64748B"
            bdr_e = "#E2E8F0"

        price_part = f" ({ccy_sym}{ext_price:.2f})" if ext_price is not None and not np.isnan(ext_price) and ext_price > 0 else ""
        lbl_e = f"{ext_label}: {ext_pct:+.1f}%{price_part}"
        ext_badge = f'<span style="font-size: 0.60rem; font-weight: 600; background-color: {bg_e}; color: {col_e}; border: 1px solid {bdr_e}; padding: 1px 4px; border-radius: 9999px; line-height: 1.1; white-space: nowrap;">{lbl_e}</span>'

    if reg_badge and ext_badge:
        return f'<div style="display: inline-flex; flex-direction: column; align-items: flex-end; gap: 2px; margin-left: auto; max-width: 100%; flex-shrink: 1;">{reg_badge}{ext_badge}</div>'
    elif reg_badge:
        return f'<div style="display: inline-flex; align-items: center; margin-left: auto; max-width: 100%; flex-shrink: 1;">{reg_badge}</div>'
    elif ext_badge:
        return f'<div style="display: inline-flex; align-items: center; margin-left: auto; max-width: 100%; flex-shrink: 1;">{ext_badge}</div>'
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
    subtext: str,
    badge_text: str | None = None,
    badge_class: str | None = None,
    val_color: str = "#0F172A",
    subtext_color: str = "#64748B",
    inline_badge_html: str | None = None,
) -> str:
    """Generate standardized, uniform KPI mini-box HTML."""
    badge_html = ""
    if badge_text and badge_class:
        badge_html = f'<span class="metric-badge {badge_class}" style="white-space: nowrap;">{badge_text}</span>'

    inline_html = f"{inline_badge_html}" if inline_badge_html else ""

    return f"""
    <div class="kpi-mini-box">
      <div class="kpi-mini-header">
        <span class="kpi-mini-title" title="{title}">{title}</span>
        {badge_html}
      </div>
      <div class="kpi-mini-value" style="color: {val_color};">
        <span style="font-variant-numeric: tabular-nums; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{value}</span>{inline_html}
      </div>
      <div class="kpi-mini-subtext" style="color: {subtext_color};" title="{subtext}">{subtext}</div>
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
            "ext_price":      None,
            "peg_2y":        None,
            "cagr_2y_pct":   None,
            "is_etf":        False,
            "is_ucits":      False,
            "ter":           None,
            "aum":           None,
            "fund_family":   None,
            "fwd_pe":        None,
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
            "ext_price":      None,
            "peg_2y":        None,
            "cagr_2y_pct":   None,
            "is_etf":        False,
            "is_ucits":      False,
            "ter":           None,
            "aum":           None,
            "fund_family":   None,
            "fwd_pe":        None,
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

    # Bollinger Bands (20-day SMA, ±1.5σ and ±2.0σ)
    BB_WIN = 20
    bb_mid = hist_full["Close"].rolling(BB_WIN, min_periods=5).mean()
    bb_std = hist_full["Close"].rolling(BB_WIN, min_periods=5).std()
    hist_full["BB_mid"]  = bb_mid
    hist_full["BB_hi2"]  = bb_mid + 2.0 * bb_std   # Outer Upper (+2.0σ)
    hist_full["BB_hi15"] = bb_mid + 1.5 * bb_std   # Inner Upper (+1.5σ)
    hist_full["BB_lo15"] = bb_mid - 1.5 * bb_std   # Inner Lower (-1.5σ)
    hist_full["BB_lo2"]  = bb_mid - 2.0 * bb_std   # Outer Lower (-2.0σ)

    # 14-day Wilder RSI
    hist_full["RSI14"] = calculate_wilder_rsi(hist_full["Close"], period=14)

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
    pre_chg = info.get("preMarketChangePercent")
    post_chg = info.get("postMarketChangePercent")
    prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

    # If reg_chg is not provided directly, calculate vs previous close
    if reg_chg is None:
        if prev_close and isinstance(prev_close, (int, float)) and prev_close > 0 and current_price:
            reg_chg = ((current_price / float(prev_close)) - 1.0) * 100.0
        elif len(hist_full) >= 2:
            pc = float(hist_full["Close"].iloc[-2])
            if pc > 0 and current_price:
                reg_chg = ((current_price / pc) - 1.0) * 100.0

    reg_perf_pct = float(reg_chg) if reg_chg is not None and not np.isnan(reg_chg) else None

    # Extended-hours trading prints (never overwrites regular session daily performance)
    ext_perf_pct = None
    ext_label = None
    ext_price = None
    pre_price = info.get("preMarketPrice")
    post_price = info.get("postMarketPrice")

    if market_state == "PRE" and pre_chg is not None and not np.isnan(pre_chg):
        ext_label = "Pre"
        ext_perf_pct = float(pre_chg)
        ext_price = float(pre_price) if pre_price is not None and not np.isnan(pre_price) else None
    elif post_chg is not None and not np.isnan(post_chg) and abs(float(post_chg)) >= 0.005:
        ext_label = "Post"
        ext_perf_pct = float(post_chg)
        ext_price = float(post_price) if post_price is not None and not np.isnan(post_price) else None

    # ── ETF Detection (quoteType == 'ETF' or tickers like SMGB.L, SPCX, VUAG.L, VWRP.L) ──
    quote_type = str(info.get("quoteType", "")).upper()
    is_etf = (
        quote_type in {"ETF", "MUTUALFUND"}
        or ticker in {"SMGB.L", "SPCX", "VUAG.L", "VWRP.L"}
        or "ETF" in str(info.get("shortName", "")).upper()
        or "ETF" in str(info.get("longName", "")).upper()
        or "ETF" in default_name.upper()
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

    # ── 2-Year Forward EPS CAGR and 2Y PEG Ratio Calculation (Alor-Jo Methodology) ──
    # Suppressed for ETFs to eliminate misleading 'Growth Negative / N/A' tiles
    peg_2y = None
    cagr_2y_pct = None

    if not is_etf:
        ee = getattr(obj, "earnings_estimate", None)
        eps_0y = None
        eps_1y = None
        if ee is not None and isinstance(ee, pd.DataFrame) and not ee.empty:
            try:
                if "0y" in ee.index and "avg" in ee.columns:
                    eps_0y = float(ee.loc["0y", "avg"])
                if "+1y" in ee.index and "avg" in ee.columns:
                    eps_1y = float(ee.loc["+1y", "avg"])
            except Exception:
                pass

        if gdr_mult != 1.0:
            if eps_0y is not None:
                eps_0y = eps_0y / gdr_mult
            if eps_1y is not None:
                eps_1y = eps_1y / gdr_mult

        eps_ntm = eps_0y or info.get("epsCurrentYear") or (eps if not fwd_eps else None)
        eps_target = eps_1y or fwd_eps

        if (
            eps_ntm is not None
            and eps_target is not None
            and isinstance(eps_ntm, (int, float))
            and isinstance(eps_target, (int, float))
            and eps_ntm > 0
            and eps_target > eps_ntm
        ):
            cagr_2y = (eps_target / eps_ntm) ** 0.5 - 1.0
            cagr_2y_pct = cagr_2y * 100.0

            if fwd_pe is not None and isinstance(fwd_pe, (int, float)) and fwd_pe > 0 and cagr_2y_pct > 0:
                peg_2y = fwd_pe / cagr_2y_pct
    else:
        fwd_pe = None
        fwd_eps = None

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

    result = {
        "ticker":         ticker,
        "name":           display_name,
        "shortName":      info.get("shortName") or display_name,
        "longName":       info.get("longName") or display_name,
        "hist":           hist_recent,
        "info":           info,
        "eps":            eps,
        "pe_mode":        pe_ok,
        "currency":       info.get("currency", "USD"),
        "next_earnings":  next_earnings,
        "current_price":  current_price,
        "ath":            ath,
        "dist_ath":       dist_ath,
        "reg_perf_pct":   reg_perf_pct,
        "ext_perf_pct":   ext_perf_pct,
        "ext_label":      ext_label,
        "ext_price":      ext_price,
        "perf_pct":       reg_perf_pct,
        "perf_ext_label": ext_label,
        "peg_2y":         peg_2y,
        "cagr_2y_pct":    cagr_2y_pct,
        "is_etf":         is_etf,
        "is_ucits":       is_ucits,
        "ter":            ter,
        "aum":            aum,
        "fund_family":    fund_family,
        "fwd_pe":         fwd_pe,
        "error":          None,
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


def make_market_highlights_banner_html(visible_data: dict, timeframe: str = "90-Day") -> str:
    """
    Render Executive Market Highlights Banner directly below top chart and KPI counters.
    Displays:
      • Basket Breadth (% of tracked assets trading above active corridor median)
      • Top Value Opportunities (2 tickers at deepest discounts / lowest Z-Scores)
      • Most Overextended (2 tickers trading furthest above upper corridor boundary / highest Z-Scores)
    """
    if not visible_data:
        return ""

    total_count = len(visible_data)
    count_overstretched = 0
    count_above_zero = 0
    items = []

    for tk, d in visible_data.items():
        if d.get("error"):
            continue
        hist = d.get("hist", pd.DataFrame())

        # Z-score based on timeframe: use 1Y (Z252) or 90D/50D (Z50)
        if timeframe == "1-Year" and "Z252" in hist.columns:
            z_series = hist["Z252"].dropna()
        else:
            z_col = "Z50" if "Z50" in hist.columns else ("Z16" if "Z16" in hist.columns else None)
            z_series = hist[z_col].dropna() if z_col else pd.Series(dtype=float)

        z_val = float(z_series.iloc[-1]) if len(z_series) else np.nan
        if np.isnan(z_val):
            z_val = d.get("z_1y" if timeframe == "1-Year" else "z_90d", np.nan)

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
            "z": z_val,
            "diff": pct_diff,
        })

    overstretched_pct = (count_overstretched / total_count * 100.0) if total_count > 0 else 0.0

    # Top Value Opportunities (lowest Z-Scores)
    valid_z = [x for x in items if not np.isnan(x["z"])]
    valid_z_sorted = sorted(valid_z, key=lambda x: x["z"])
    top_value = valid_z_sorted[:2]

    # Most Overextended (highest Z-Scores)
    top_overextended = sorted(valid_z, key=lambda x: x["z"], reverse=True)[:2]

    val_snippets = []
    for item in top_value:
        tk = item["ticker"]
        z = item["z"]
        diff = item["diff"]
        val_snippets.append(
            f'<div style="margin-top: 6px; display: flex; align-items: center; justify-content: space-between;">'
            f'  <div><b style="color: #0F172A; font-size: 0.95rem;">{tk}</b> <span class="metric-badge badge-attractive" style="margin-left: 4px;">{z:+.2f}σ</span></div>'
            f'  <span style="font-size: 0.78rem; color: #047857; font-weight: 600;">{diff:+.1f}% vs Med</span>'
            f'</div>'
        )
    val_html = "".join(val_snippets) if val_snippets else '<div style="color: #64748B; font-size: 0.85rem;">None</div>'

    over_snippets = []
    for item in top_overextended:
        tk = item["ticker"]
        z = item["z"]
        diff = item["diff"]
        over_snippets.append(
            f'<div style="margin-top: 6px; display: flex; align-items: center; justify-content: space-between;">'
            f'  <div><b style="color: #0F172A; font-size: 0.95rem;">{tk}</b> <span class="metric-badge badge-overvalued" style="margin-left: 4px;">{z:+.2f}σ</span></div>'
            f'  <span style="font-size: 0.78rem; color: #B91C1C; font-weight: 600;">{diff:+.1f}% vs Med</span>'
            f'</div>'
        )
    over_html = "".join(over_snippets) if over_snippets else '<div style="color: #64748B; font-size: 0.85rem;">None</div>'

    breadth_desc = "Overbought Skew" if count_above_zero >= (total_count * 0.6) else ("Oversold Skew" if count_above_zero <= (total_count * 0.4) else "Neutral Balance")
    framework_badge_lbl = "1Y Corridor Framework" if timeframe == "1-Year" else "90D Corridor Framework"

    return f"""
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #EAB308; border-radius: 10px; padding: 14px 18px; margin: 16px 0 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #F1F5F9;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 1.05rem; font-weight: 800; color: #0F172A; letter-spacing: -0.01em;">Executive Market Highlights</span>
          <span style="font-size: 0.72rem; font-weight: 700; color: #854D0E; background-color: #FEF9C3; border: 1px solid #FDE047; padding: 2px 8px; border-radius: 9999px;">{framework_badge_lbl}</span>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px;">
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Basket Breadth</div>
            <div style="font-size: 0.92rem; color: #0F172A; font-weight: 600; line-height: 1.4;">
              <b>{count_overstretched} of {total_count}</b> tracked assets (<b>{overstretched_pct:.0f}%</b>) are in overstretched territory (&gt; +5% above median), with <b>{count_above_zero}</b> trading on the expensive side of fair value.
            </div>
          </div>
          <div style="font-size: 0.78rem; color: #854D0E; font-weight: 600; margin-top: 6px;">• Bias: {breadth_desc}</div>
        </div>
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px;">
          <div style="font-size: 0.72rem; font-weight: 700; color: #047857; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Top Value Opportunities</div>
          {val_html}
        </div>
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 14px;">
          <div style="font-size: 0.72rem; font-weight: 700; color: #B91C1C; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Most Overextended</div>
          {over_html}
        </div>
      </div>
    </div>
    """


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
      • Horizontal top-left legend (y=1.12, x=0)
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

    # ── Tight Y-axis autoscale ──
    all_s = [price, bb_hi2, bb_lo2, ma50]
    if show_ma200:
        all_s.append(ma200)
    comb = pd.concat([s for s in all_s if len(s)]).dropna()
    if len(comb):
        ymin = comb.quantile(0.005)
        ymax = comb.quantile(0.995)
        pad = (ymax - ymin) * 0.06
        y_range = [max(0.0, ymin - pad), ymax + pad]
    else:
        y_range = None

    # ── Plotly Layout (Consolidated: Per-Card Legends Hidden) ──
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor="#FFFFFF",
        font=dict(color=TEXT_DARK, size=11),
        showlegend=False,
        margin=dict(l=38, r=12, t=18, b=26),
        xaxis=dict(
            gridcolor=GRID_COLOR, showgrid=True, zeroline=False,
            color=MUTED_SLATE, linecolor=BORDER_COLOR,
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
        f"{timeframe_label} Fair Value {x['unit']}: {x['mid']:.2f}<br>vs Corridor Median: {x['pct']:+.1f}%"
        for x in items
    ]

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
        textposition="outside",
        textfont=dict(size=10, color=TEXT_DARK, family="monospace"),
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
            title=f"% Above / Below {timeframe_label} Corridor Median",
            gridcolor=GRID_COLOR,
            zeroline=False,
            color=MUTED_SLATE,
            linecolor=BORDER_COLOR,
            autorange=True,
            fixedrange=True,
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            color=TEXT_DARK,
            linecolor=BORDER_COLOR,
            autorange="reversed",
            categoryorder="array",
            categoryarray=labels,
            fixedrange=True,
        ),
        margin=dict(l=80, r=45, t=20, b=40),
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
if "val_timeframe" not in st.session_state:
    if query_timeframe in ["90-Day", "1-Year"]:
        st.session_state["val_timeframe"] = query_timeframe
    else:
        st.session_state["val_timeframe"] = "90-Day"

# ─────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────
with st.sidebar:
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
    cols_per_row = st.selectbox("Columns per Row", [1, 2, 3], index=1)

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
        '<a href="https://www.instagram.com/theinvestingdean" target="_blank" rel="noopener noreferrer" class="dean-badge" style="font-size: 0.70rem; padding: 1px 7px;">@theinvestingdean</a>'
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
        <h1 style="color: #0F172A; font-size: 2.1rem; font-weight: 800; margin: 0; padding: 0; letter-spacing: -0.025em; line-height: 1.2;">
          The Stock Valuation Radar
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 6px; margin-bottom: 0;">
          Know when quality stocks enter the Buy Zone, Standard DCA, or Wait for Pullback • <a href="https://www.instagram.com/theinvestingdean" target="_blank" rel="noopener noreferrer" class="dean-badge">@theinvestingdean</a>
        </p>
      </div>
      <div style="display: flex; align-items: center; gap: 7px; background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 9999px; padding: 6px 14px; margin-top: 4px;">
        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10B981;"></span>
        <span style="color: #065F46; font-size: 13px; font-weight: 600; letter-spacing: 0.02em;">Live Market Data</span>
      </div>
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

# ── 4. Price Valuation vs Corridor Median (Top Chart & Timeframe Toggle) ──
col_title, col_toggle = st.columns([3, 1], vertical_alignment="center")
with col_toggle:
    val_timeframe = st.segmented_control(
        "Valuation Corridor Timeframe",
        options=["90-Day", "1-Year"],
        default=st.session_state.get("val_timeframe", "90-Day"),
        selection_mode="single",
        label_visibility="collapsed",
        key="val_timeframe",
    )
    if not val_timeframe:
        val_timeframe = "90-Day"
        st.session_state["val_timeframe"] = "90-Day"

with col_title:
    if val_timeframe == "1-Year":
        st.markdown("### 1-Year Price Valuation vs Corridor Median")
        st.caption("Measures how far each stock has moved above or below its 1-year fair value baseline (~252 trading days). Green bars highlight Buy Zone discounts; amber represents Standard DCA; red indicates Wait for Pullback.")
    else:
        st.markdown("### 90-Day Price Valuation vs Corridor Median")
        st.caption("Measures how far each stock has moved above or below its 90-day fair value baseline. Green bars highlight Buy Zone discounts; amber represents Standard DCA; red indicates Wait for Pullback.")

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
k2.metric("Buy Zone", counts["Buy Zone"])
k3.metric("Standard DCA", counts["Standard DCA"])
k4.metric("Wait for Pullback", counts["Wait for Pullback"])

# ── Executive Market Highlights Banner ──
if visible:
    st.html(make_market_highlights_banner_html(visible, timeframe=val_timeframe))

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
            # Wrap each stock's entire module in a clearly defined card container
            with st.container(border=True):
                # ── Safe Header Display ──
                safe_name = d.get("shortName") or d.get("longName") or d.get("name") or tk
                is_etf = d.get("is_etf", False)
                is_ucits = d.get("is_ucits", False)

                asset_badge_html = ""
                if is_etf:
                    badge_lbl = "Asset Type: UCITS ETF" if is_ucits else "Asset Type: ETF"
                    asset_badge_html = f'<span class="badge" style="background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; font-size: 0.70rem; margin-left: 6px;">{badge_lbl}</span>'

                header_html = f"""
                <div id="card-{tk}" class="stock-card-container">
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

                # ── Box 1: Price with % vs SMA 50 & Dual Performance Display ──
                ma50_val = hist_df[f"MA{MA_SHORT}"].dropna() if f"MA{MA_SHORT}" in hist_df.columns else pd.Series(dtype=float)
                if len(ma50_val):
                    sma50_last = float(ma50_val.iloc[-1])
                    pct_vs_ma  = (price_now / sma50_last - 1.0) * 100.0
                    subtext_p  = f"{pct_vs_ma:+.1f}% vs SMA 50"
                    sub_color_p = "#047857" if pct_vs_ma >= 0 else "#B91C1C"
                else:
                    subtext_p = "vs SMA 50 N/A"
                    sub_color_p = MUTED_SLATE

                dual_perf_html = make_dual_perf_pill_html(
                    d.get("reg_perf_pct"),
                    d.get("ext_perf_pct"),
                    d.get("ext_label"),
                    d.get("ext_price"),
                    ccy_sym,
                )

                box1_html = make_metric_tile_html(
                    title=f"Price ({ccy})",
                    value=f"{price_now:.2f}",
                    subtext=subtext_p,
                    val_color=TEXT_DARK,
                    subtext_color=sub_color_p,
                    inline_badge_html=dual_perf_html,
                )

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
                    title="Distance to ATH",
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
                    title="Std Dev (50 Days)",
                    value=z50_str,
                    subtext="50-Day Z-Score",
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
                    fwd_pe_str = f"{fwd_pe:.1f}" if isinstance(fwd_pe, (int, float)) and fwd_pe > 0 else "N/A"

                    box4_html = make_metric_tile_html(
                        title="Forward P/E",
                        value=fwd_pe_str,
                        subtext="NTM Multiple",
                        val_color=TEXT_DARK,
                        subtext_color=MUTED_SLATE,
                    )

                    # Single Stock: 2Y PEG Ratio
                    peg_2y = d.get("peg_2y")
                    cagr_pct = d.get("cagr_2y_pct")
                    if peg_2y is not None and not np.isnan(peg_2y) and peg_2y > 0:
                        peg_2y_str = f"{peg_2y:.2f}"
                        peg_subtext = f"2Y CAGR: {cagr_pct:+.1f}%" if cagr_pct else "2Y Forward PEG"
                    else:
                        peg_2y_str = "N/A"
                        peg_subtext = "Growth Negative / N/A"

                    box5_html = make_metric_tile_html(
                        title="2Y PEG Ratio",
                        value=peg_2y_str,
                        subtext=peg_subtext,
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

                # ── Standardized 6-Box Grid (Uniform Mini-Boxes) ──
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

                # ── Detail Bollinger & Trend Chart (With Fullscreen Toolbar & Modebar) ──
                if show_charts:
                    chart_bar_html = """
                    <div style="margin-top: 10px; margin-bottom: 4px; padding: 2px 2px;">
                      <span style="font-size: 0.70rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">Trend & Valuation Corridor</span>
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
                      <span class="dean-badge" style="font-size: 0.65rem; padding: 1px 6px;">@theinvestingdean</span>
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

        row = {
            "Ticker": tk,
            "Name": safe_name,
            "Status": status,
            "Price": round(d.get("current_price", np.nan), 2),
            "Distance to ATH": f"{dist_v:+.1f}%" if not np.isnan(dist_v) else "—",
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
          <div id="dean-modal-overlay" style="position: fixed; inset: 0; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(4px); z-index: 9999999; display: flex; align-items: center; justify-content: center; padding: 16px;">
            <div id="dean-modal-card" style="background: #FFFFFF; border-radius: 12px; width: 96vw; max-width: 1440px; max-height: 94vh; display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); border: 1px solid #E2E8F0; overflow: hidden;">
              <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-bottom: 1px solid #F1F5F9; background: #FAFBFD;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span id="dean-modal-title" style="font-size: 1.35rem; font-weight: 800; color: #0F172A;"></span>
                  <span id="dean-modal-subtitle" style="font-size: 0.90rem; color: #64748B; font-weight: 500;"></span>
                  <span style="font-size: 0.70rem; font-weight: 700; color: #1F2937; background: #FDE047; border: 1px solid #EAB308; padding: 2px 8px; border-radius: 9999px;">Interactive Full-Screen View</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <button id="dean-modal-reset-btn" onclick="(window.parent.deanRefocus||window.deanRefocus||function(){{}})('modal')" style="background: #FEF08A; border: 1px solid #EAB308; border-radius: 6px; padding: 6px 14px; font-weight: 700; color: #1F2937; cursor: pointer; font-size: 0.78rem; display: flex; align-items: center; gap: 4px;">↺ Refocus View</button>
                  <button id="dean-modal-close-btn" onclick="(window.parent.deanCloseModal||window.deanCloseModal||function(){{}})()" style="background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 14px; font-weight: 700; color: #334155; cursor: pointer; font-size: 0.78rem;">✕ Close</button>
                </div>
              </div>
              <div id="dean-modal-plot-container" style="padding: 12px 18px 18px 18px; flex: 1 1 auto; min-height: 540px; width: 100%; max-width: 100%; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden;"></div>
            </div>
          </div>
          <style>
            #dean-modal-plot-container .js-plotly-plot,
            #dean-modal-plot-container .plot-container,
            #dean-modal-plot-container .svg-container,
            #dean-modal-plot-container .main-svg {
              width: 100% !important;
              max-width: 100% !important;
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

    // Force high-contrast dark charcoal text and close icons on all sidebar filter tags
    function enforceTagContrast() {
      const tags = pDoc.querySelectorAll('[data-tag], span[data-tag], .e1kig3hy3, [data-baseweb="tag"]');
      tags.forEach(tag => {
        tag.style.setProperty('background-color', '#FDE047', 'important');
        tag.style.setProperty('border', '1px solid #EAB308', 'important');
        tag.style.setProperty('color', '#1F2937', 'important');
        tag.style.setProperty('-webkit-text-fill-color', '#1F2937', 'important');

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
      });
    }

    enforceTagContrast();

    if (!pDoc.__dean_tag_observer && pWin.MutationObserver) {
      try {
        const obs = new pWin.MutationObserver(function() {
          enforceTagContrast();
        });
        obs.observe(pDoc.body, { childList: true, subtree: true });
        pDoc.__dean_tag_observer = obs;
      } catch(e) {}
    }

    function getCardWrapper(ticker) {
      const marker = pDoc.getElementById('card-' + ticker) || document.getElementById('card-' + ticker);
      if (!marker) return null;

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
      // Maintain Mobile Full-Screen Restriction: prevent screen takeover UX issues on mobile
      if ((pWin && pWin.innerWidth <= 768) || window.innerWidth <= 768) {
        return;
      }

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

          // Enable zoom and pan strictly inside the expanded modal
          if (cloneLayout.xaxis) {
            cloneLayout.xaxis.fixedrange = false;
            cloneLayout.xaxis.autorange = true;
          }
          if (cloneLayout.yaxis) {
            cloneLayout.yaxis.fixedrange = false;
            cloneLayout.yaxis.autorange = true;
          }
          cloneLayout.dragmode = 'zoom';

          cloneLayout.height = Math.max(540, Math.min(pWin.innerHeight * 0.74, 680));
          cloneLayout.margin = { l: 60, r: 24, t: 36, b: 48 };
          cloneLayout.showlegend = true;
          cloneLayout.legend = { orientation: 'h', y: 1.12, x: 0 };
          cloneLayout.paper_bgcolor = '#FFFFFF';
          cloneLayout.plot_bgcolor = '#FFFFFF';

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
            modeBarButtons: [['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d']],
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

        // Maintain Mobile Full-Screen Restriction: do not open modal on mobile screens (<= 768px)
        if ((pWin && pWin.innerWidth <= 768) || window.innerWidth <= 768) return;

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

    // ── Expand Chart Button Click (Multi-layer guarantee) ──
    pDoc.addEventListener('click', function(e) {
      const expandBtn = e.target.closest('.expand-chart-btn');
      if (!expandBtn) return;
      e.preventDefault();
      e.stopPropagation();

      const ticker = expandBtn.getAttribute('data-ticker') || '';
      const card = expandBtn.closest('[data-testid="stVerticalBlockBorderWrapper"]') || getCardWrapper(ticker);
      const origPlot = card ? card.querySelector('.js-plotly-plot') : null;
      openModalForPlot(origPlot, ticker);
    }, true);

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
