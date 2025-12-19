"""
Real-Time Candlestick Simulation App - V2 (Optimized)

A Streamlit application for simulating real-time NQ futures candlestick chart
with configurable playback speed, indicators, and market session awareness.

VERSION 2 IMPROVEMENTS:
- Uses st.fragment for partial reruns (reduces full page repaints)
- Uses st.empty() placeholders for surgical updates
- Optimized refresh intervals
- Better separation of static vs dynamic content

KNOWN LIMITATIONS (Streamlit Architecture):
- Still requires full component re-render on each update
- No true WebSocket streaming to update just the growing candle
- ECharts component recreated each refresh (causes flicker)

For true real-time streaming, consider: Dash, Bokeh, or custom WebSocket solution.

Usage:
    streamlit run realtime_candlestick_app_v2.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from typing import Optional, Dict, List, Tuple
import sqlite3
import time as time_module
from streamlit_echarts import st_echarts
from streamlit_autorefresh import st_autorefresh

# Import our custom modules
from data_loader import TickDataLoader, OHLCBuilder


# ==============================================================================
# CONFIGURATION & DEFAULTS
# ==============================================================================

DEFAULT_CONFIG = {
    'up_candle_color': '#26A69A',      # Green
    'down_candle_color': '#EF5350',     # Red
    'doji_candle_color': '#9E9E9E',     # Gray
    'volume_up_color': '#26A69A80',     # Green with alpha
    'volume_down_color': '#EF535080',   # Red with alpha
    'vwap_color': '#FF9800',            # Orange
    'ema9_color': '#2196F3',            # Blue
    'ema20_color': '#9C27B0',           # Purple
    'volume_avg_color': '#FFEB3B',      # Yellow
    'grid_color': '#333333',
    'text_color': '#FFFFFF',
    'background_color': '#1E1E1E',
    'max_visible_candles': 100,
    'default_timeframe': '1m',
    'default_speed': 1.0,
}

SESSIONS = {
    'premarket': {'start': time(4, 0), 'end': time(9, 30), 'label': 'Pre-Market', 'color': '#FFA500'},
    'rth': {'start': time(9, 30), 'end': time(16, 0), 'label': 'Regular Hours', 'color': '#4CAF50'},
    'afterhours': {'start': time(16, 0), 'end': time(20, 0), 'label': 'After Hours', 'color': '#9C27B0'},
}

JUMP_OPTIONS = [
    ('1 Min', timedelta(minutes=1)),
    ('5 Min', timedelta(minutes=5)),
    ('30 Min', timedelta(minutes=30)),
    ('60 Min', timedelta(minutes=60)),
    ('90 Min', timedelta(minutes=90)),
    ('120 Min', timedelta(minutes=120)),
    ('Session', 'session'),
    ('Day', 'day'),
]


# ==============================================================================
# INDICATOR CALCULATIONS
# ==============================================================================

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Calculate Volume Weighted Average Price."""
    if df.empty or 'volume' not in df.columns:
        return pd.Series()
    
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    cumulative_tp_vol = (typical_price * df['volume']).cumsum()
    cumulative_vol = df['volume'].cumsum()
    
    return cumulative_tp_vol / cumulative_vol


def calculate_ema(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """Calculate Exponential Moving Average."""
    if df.empty or column not in df.columns:
        return pd.Series()
    
    return df[column].ewm(span=period, adjust=False).mean()


def calculate_volume_average(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Calculate Volume Moving Average."""
    if df.empty or 'volume' not in df.columns:
        return pd.Series()
    
    return df['volume'].rolling(window=period, min_periods=1).mean()


def get_current_session(timestamp: datetime) -> str:
    """Get the current session name."""
    t = timestamp.time()
    for session_name, session in SESSIONS.items():
        if session['start'] <= t < session['end']:
            return session_name
    return 'closed'


def get_session_end(timestamp: datetime, session_name: str) -> datetime:
    """Get the end time of the current session."""
    session = SESSIONS.get(session_name)
    if session:
        return datetime.combine(timestamp.date(), session['end'])
    return timestamp


def get_next_session_start(timestamp: datetime) -> datetime:
    """Get the start of the next session."""
    t = timestamp.time()
    
    # Check sessions in order
    session_order = ['premarket', 'rth', 'afterhours']
    
    for session_name in session_order:
        session = SESSIONS[session_name]
        if t < session['start']:
            return datetime.combine(timestamp.date(), session['start'])
    
    # Next day's premarket
    return datetime.combine(timestamp.date() + timedelta(days=1), SESSIONS['premarket']['start'])


# ==============================================================================
# CHART BUILDING
# ==============================================================================

def build_candlestick_chart(
    candles: pd.DataFrame,
    current_tick: Optional[Dict],
    config: Dict,
    show_vwap: bool = True,
    show_ema9: bool = True,
    show_ema20: bool = True
) -> dict:
    """Build the PyEcharts candlestick chart configuration."""
    
    if candles.empty:
        return {}
    
    # Prepare data
    candles = candles.copy()
    if 'timestamp' in candles.columns:
        candles['timestamp'] = pd.to_datetime(candles['timestamp'])
        candles = candles.sort_values('timestamp')
    
    # Limit visible candles
    max_candles = config.get('max_visible_candles', 100)
    if len(candles) > max_candles:
        candles = candles.tail(max_candles)
    
    # Format x-axis labels
    x_data = candles['timestamp'].dt.strftime('%H:%M:%S').tolist()
    
    # Candlestick data: [open, close, low, high]
    candle_data = []
    for _, row in candles.iterrows():
        candle_data.append([
            round(row['open'], 2),
            round(row['close'], 2),
            round(row['low'], 2),
            round(row['high'], 2)
        ])
    
    # Calculate indicators
    vwap_data = calculate_vwap(candles).round(2).tolist() if show_vwap else []
    ema9_data = calculate_ema(candles, 9).round(2).tolist() if show_ema9 else []
    ema20_data = calculate_ema(candles, 20).round(2).tolist() if show_ema20 else []
    
    # Volume data
    volume_data = []
    for i, (_, row) in enumerate(candles.iterrows()):
        color = config['volume_up_color'] if row['close'] >= row['open'] else config['volume_down_color']
        volume_data.append({
            'value': int(row['volume']),
            'itemStyle': {'color': color}
        })
    
    volume_avg = calculate_volume_average(candles).round(0).tolist()
    
    # Build series
    series = [
        {
            'name': 'Candlestick',
            'type': 'candlestick',
            'data': candle_data,
            'xAxisIndex': 0,
            'yAxisIndex': 0,
            'itemStyle': {
                'color': config['up_candle_color'],
                'color0': config['down_candle_color'],
                'borderColor': config['up_candle_color'],
                'borderColor0': config['down_candle_color'],
            }
        }
    ]
    
    # Add indicator lines
    if show_vwap and vwap_data:
        series.append({
            'name': 'VWAP',
            'type': 'line',
            'data': vwap_data,
            'xAxisIndex': 0,
            'yAxisIndex': 0,
            'smooth': True,
            'lineStyle': {'color': config['vwap_color'], 'width': 2},
            'symbol': 'none',
        })
    
    if show_ema9 and ema9_data:
        series.append({
            'name': '9 EMA',
            'type': 'line',
            'data': ema9_data,
            'xAxisIndex': 0,
            'yAxisIndex': 0,
            'smooth': True,
            'lineStyle': {'color': config['ema9_color'], 'width': 1.5},
            'symbol': 'none',
        })
    
    if show_ema20 and ema20_data:
        series.append({
            'name': '20 EMA',
            'type': 'line',
            'data': ema20_data,
            'xAxisIndex': 0,
            'yAxisIndex': 0,
            'smooth': True,
            'lineStyle': {'color': config['ema20_color'], 'width': 1.5},
            'symbol': 'none',
        })
    
    # Volume series
    series.append({
        'name': 'Volume',
        'type': 'bar',
        'data': volume_data,
        'xAxisIndex': 1,
        'yAxisIndex': 1,
    })
    
    if volume_avg:
        series.append({
            'name': 'Vol Avg',
            'type': 'line',
            'data': volume_avg,
            'xAxisIndex': 1,
            'yAxisIndex': 1,
            'smooth': True,
            'lineStyle': {'color': config['volume_avg_color'], 'width': 1},
            'symbol': 'none',
        })
    
    # Calculate Y-axis range for price
    price_min = candles['low'].min()
    price_max = candles['high'].max()
    price_range = price_max - price_min
    price_padding = price_range * 0.1
    
    option = {
        'backgroundColor': config['background_color'],
        'animation': False,  # CRITICAL: Disable animation for smoother updates
        'legend': {
            'data': ['VWAP', '9 EMA', '20 EMA'],
            'top': 10,
            'textStyle': {'color': config['text_color']},
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'cross'},
            'backgroundColor': 'rgba(50, 50, 50, 0.9)',
            'textStyle': {'color': '#fff'},
        },
        'grid': [
            {'left': '10%', 'right': '10%', 'top': '10%', 'height': '55%'},
            {'left': '10%', 'right': '10%', 'top': '70%', 'height': '20%'},
        ],
        'xAxis': [
            {
                'type': 'category',
                'data': x_data,
                'gridIndex': 0,
                'axisLine': {'lineStyle': {'color': config['grid_color']}},
                'axisLabel': {'color': config['text_color']},
                'splitLine': {'show': True, 'lineStyle': {'color': config['grid_color'], 'opacity': 0.3}},
            },
            {
                'type': 'category',
                'data': x_data,
                'gridIndex': 1,
                'axisLine': {'lineStyle': {'color': config['grid_color']}},
                'axisLabel': {'show': False},
                'splitLine': {'show': False},
            },
        ],
        'yAxis': [
            {
                'type': 'value',
                'gridIndex': 0,
                'min': round(price_min - price_padding, 2),
                'max': round(price_max + price_padding, 2),
                'axisLine': {'lineStyle': {'color': config['grid_color']}},
                'axisLabel': {'color': config['text_color']},
                'splitLine': {'show': True, 'lineStyle': {'color': config['grid_color'], 'opacity': 0.3}},
            },
            {
                'type': 'value',
                'gridIndex': 1,
                'axisLine': {'lineStyle': {'color': config['grid_color']}},
                'axisLabel': {'color': config['text_color'], 'show': False},
                'splitLine': {'show': False},
            },
        ],
        'dataZoom': [
            {
                'type': 'inside',
                'xAxisIndex': [0, 1],
                'start': 0,
                'end': 100,
            },
        ],
        'series': series,
    }
    
    return option


# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================

def init_session_state():
    """Initialize Streamlit session state."""
    
    defaults = {
        'data_loader': None,
        'ohlc_builder': None,
        'current_timestamp': None,
        'is_playing': False,
        'playback_speed': 1.0,
        'timeframe': '1m',
        'last_tick': None,
        'candles': pd.DataFrame(),
        'config': DEFAULT_CONFIG.copy(),
        'show_vwap': True,
        'show_ema9': True,
        'show_ema20': True,
        'db_loaded': False,
        'selected_start_time': None,
        'selected_end_time': None,
        'update_counter': 0,  # For tracking updates
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==============================================================================
# FRAGMENT: CHART UPDATE (Partial Rerun)
# ==============================================================================

@st.fragment
def chart_fragment():
    """
    Fragment for chart display - only this section reruns on refresh.
    This reduces full page repaints and improves perceived performance.
    """
    # Update data if playing
    if st.session_state.is_playing and st.session_state.current_timestamp and st.session_state.data_loader:
        # Advance timestamp
        st.session_state.current_timestamp += timedelta(seconds=st.session_state.playback_speed)
        
        # Check bounds
        end_time = st.session_state.selected_end_time or st.session_state.data_loader.end_time
        if st.session_state.current_timestamp > end_time:
            st.session_state.current_timestamp = end_time
            st.session_state.is_playing = False
        
        # Load tick and update candles
        tick = st.session_state.data_loader.get_tick_at(st.session_state.current_timestamp)
        if tick:
            st.session_state.last_tick = tick
            if st.session_state.ohlc_builder:
                completed, current = st.session_state.ohlc_builder.add_tick(tick)
                st.session_state.candles = st.session_state.ohlc_builder.get_candles()
        
        st.session_state.update_counter += 1
    
    # Price Panel (inside fragment for updates)
    tick = st.session_state.last_tick
    
    price_cols = st.columns([2, 1, 1, 1, 1])
    
    with price_cols[0]:
        if st.session_state.current_timestamp:
            session = get_current_session(st.session_state.current_timestamp)
            session_info = SESSIONS.get(session, {'label': 'Closed', 'color': '#666'})
            st.markdown(
                f"""<div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='background-color: {session_info["color"]}; padding: 5px 10px; border-radius: 4px; font-weight: bold;'>
                        {session_info['label']}
                    </span>
                    <span style='color: white; font-size: 18px;'>
                        {st.session_state.current_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                    </span>
                    <span style='color: #666; font-size: 12px;'>
                        (Update #{st.session_state.update_counter})
                    </span>
                </div>""",
                unsafe_allow_html=True
            )
    
    with price_cols[1]:
        if tick:
            price = tick.get('price', 0)
            st.metric("Last", f"${price:.2f}")
    
    with price_cols[2]:
        if tick:
            st.metric("Bid", f"${tick.get('bid', 0):.2f}")
    
    with price_cols[3]:
        if tick:
            st.metric("Ask", f"${tick.get('ask', 0):.2f}")
    
    with price_cols[4]:
        if tick:
            st.metric("Spread", f"{tick.get('spread', 0):.2f}")
    
    # Chart display
    st.markdown("---")
    
    if not st.session_state.candles.empty:
        chart_option = build_candlestick_chart(
            st.session_state.candles,
            st.session_state.last_tick,
            st.session_state.config,
            st.session_state.show_vwap,
            st.session_state.show_ema9,
            st.session_state.show_ema20
        )
        
        if chart_option:
            # Use a container to help with updates
            st_echarts(
                chart_option, 
                height="600px",
                key=f"chart_{st.session_state.update_counter % 2}"  # Alternate keys to force update
            )
    else:
        st.info("📈 Chart will appear once data is loaded and playback begins.")
    
    # Stats Footer
    if st.session_state.candles is not None and not st.session_state.candles.empty:
        st.markdown("---")
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.metric("Candles", len(st.session_state.candles))
        
        with stat_cols[1]:
            if 'high' in st.session_state.candles.columns:
                day_high = st.session_state.candles['high'].max()
                st.metric("Day High", f"${day_high:.2f}")
        
        with stat_cols[2]:
            if 'low' in st.session_state.candles.columns:
                day_low = st.session_state.candles['low'].min()
                st.metric("Day Low", f"${day_low:.2f}")
        
        with stat_cols[3]:
            if 'volume' in st.session_state.candles.columns:
                total_vol = st.session_state.candles['volume'].sum()
                st.metric("Total Volume", f"{total_vol:,.0f}")
    
    # Auto-refresh trigger (inside fragment)
    if st.session_state.is_playing:
        # Minimum 200ms between updates for smoother experience
        refresh_interval = max(200, int(1000 / min(st.session_state.playback_speed, 5)))
        st_autorefresh(interval=refresh_interval, limit=None, key="chart_refresh")


# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    st.set_page_config(
        page_title="NQ Futures Real-Time Simulation (V2)",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
    }
    .price-panel {
        background-color: #2D2D2D;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .price-label {
        color: #9E9E9E;
        font-size: 12px;
    }
    .price-value {
        font-size: 20px;
        font-weight: bold;
    }
    .price-up {
        color: #26A69A;
    }
    .price-down {
        color: #EF5350;
    }
    .session-badge {
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: bold;
    }
    /* Reduce flicker */
    [data-testid="stMetric"] {
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("📊 NQ Futures Real-Time Simulation (V2 - Optimized)")
    
    # ==============================================================================
    # SIDEBAR - CONFIGURATION (Static - doesn't rerun with chart)
    # ==============================================================================
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Database selection
        st.subheader("📁 Data Source")
        
        # Default to the database in parent directory
        import os
        default_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nq_tick_simulation.db")
        if not os.path.exists(default_db):
            default_db = "nq_tick_simulation.db"
        
        db_path = st.text_input(
            "SQLite Database Path",
            value=default_db,
            help="Path to the tick data database"
        )
        
        if st.button("Load Data", type="primary"):
            try:
                st.session_state.data_loader = TickDataLoader(db_path=db_path)
                st.session_state.db_loaded = True
                st.session_state.current_timestamp = st.session_state.data_loader.start_time
                st.session_state.ohlc_builder = OHLCBuilder(st.session_state.timeframe)
                st.success(f"Loaded data from {st.session_state.data_loader.start_time} to {st.session_state.data_loader.end_time}")
            except Exception as e:
                st.error(f"Failed to load data: {e}")
        
        st.divider()
        
        # Time range selection
        if st.session_state.db_loaded and st.session_state.data_loader:
            st.subheader("📅 Time Range")
            
            available_dates = st.session_state.data_loader.get_available_dates()
            if available_dates:
                selected_date = st.selectbox(
                    "Select Date",
                    options=available_dates,
                    format_func=lambda x: x.strftime('%Y-%m-%d (%A)')
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    start_hour = st.number_input("Start Hour", min_value=4, max_value=20, value=9)
                    start_min = st.number_input("Start Min", min_value=0, max_value=59, value=30)
                
                with col2:
                    end_hour = st.number_input("End Hour", min_value=4, max_value=20, value=16)
                    end_min = st.number_input("End Min", min_value=0, max_value=59, value=0)
                
                if st.button("Set Time Range"):
                    st.session_state.selected_start_time = datetime.combine(
                        selected_date.date(), time(start_hour, start_min)
                    )
                    st.session_state.selected_end_time = datetime.combine(
                        selected_date.date(), time(end_hour, end_min)
                    )
                    st.session_state.current_timestamp = st.session_state.selected_start_time
                    st.session_state.ohlc_builder = OHLCBuilder(st.session_state.timeframe)
                    st.session_state.candles = pd.DataFrame()
                    st.session_state.update_counter = 0
                    st.success(f"Time range set: {start_hour}:{start_min:02d} - {end_hour}:{end_min:02d}")
        
        st.divider()
        
        # Timeframe selection
        st.subheader("⏱️ Timeframe")
        new_timeframe = st.selectbox(
            "Candle Timeframe",
            options=['1s', '1m', '5m'],
            index=['1s', '1m', '5m'].index(st.session_state.timeframe)
        )
        if new_timeframe != st.session_state.timeframe:
            st.session_state.timeframe = new_timeframe
            st.session_state.ohlc_builder = OHLCBuilder(new_timeframe)
            st.session_state.candles = pd.DataFrame()
        
        st.divider()
        
        # Playback speed
        st.subheader("⚡ Playback Speed")
        st.session_state.playback_speed = st.slider(
            "Speed Multiplier",
            min_value=1.0,
            max_value=100.0,
            value=st.session_state.playback_speed,
            step=1.0,
            help="1x = real-time, 100x = 100 times faster"
        )
        
        st.divider()
        
        # Indicators
        st.subheader("📈 Indicators")
        st.session_state.show_vwap = st.checkbox("VWAP", value=st.session_state.show_vwap)
        st.session_state.show_ema9 = st.checkbox("9 EMA", value=st.session_state.show_ema9)
        st.session_state.show_ema20 = st.checkbox("20 EMA", value=st.session_state.show_ema20)
        
        st.divider()
        
        # Candle colors
        st.subheader("🎨 Colors")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.config['up_candle_color'] = st.color_picker(
                "Up Candle", st.session_state.config['up_candle_color']
            )
        with col2:
            st.session_state.config['down_candle_color'] = st.color_picker(
                "Down Candle", st.session_state.config['down_candle_color']
            )
        
        st.divider()
        
        # Performance info
        st.subheader("ℹ️ V2 Improvements")
        st.caption("""
        - Uses `st.fragment` for partial reruns
        - Reduced full page repaints
        - Optimized refresh intervals
        - Animation disabled for smoother updates
        
        **Limitation**: Streamlit still recreates 
        the entire ECharts component each update.
        For true streaming, use Dash or WebSockets.
        """)
    
    # ==============================================================================
    # MAIN AREA - CONTROLS (Outside fragment - only updates on button clicks)
    # ==============================================================================
    
    if not st.session_state.db_loaded:
        st.info("👈 Please load a tick data database from the sidebar to begin.")
        st.markdown("""
        ### Quick Start
        1. Generate tick data: `python generate_tick_data.py --days 5`
        2. Enter the database path in the sidebar
        3. Click "Load Data"
        4. Select a time range
        5. Press Play to start the simulation!
        """)
        return
    
    # Playback Controls (Outside fragment - buttons cause full rerun anyway)
    control_cols = st.columns([1, 1, 1, 1, 1, 1, 2, 2])
    
    with control_cols[0]:
        if st.button("⏮️ Start", use_container_width=True):
            if st.session_state.selected_start_time:
                st.session_state.current_timestamp = st.session_state.selected_start_time
            elif st.session_state.data_loader:
                st.session_state.current_timestamp = st.session_state.data_loader.start_time
            st.session_state.ohlc_builder = OHLCBuilder(st.session_state.timeframe)
            st.session_state.candles = pd.DataFrame()
            st.session_state.update_counter = 0
    
    with control_cols[1]:
        if st.button("⏪ -1m", use_container_width=True):
            if st.session_state.current_timestamp:
                st.session_state.current_timestamp -= timedelta(minutes=1)
    
    with control_cols[2]:
        play_label = "⏸️ Pause" if st.session_state.is_playing else "▶️ Play"
        if st.button(play_label, use_container_width=True, type="primary"):
            st.session_state.is_playing = not st.session_state.is_playing
    
    with control_cols[3]:
        if st.button("⏩ +1m", use_container_width=True):
            if st.session_state.current_timestamp:
                st.session_state.current_timestamp += timedelta(minutes=1)
    
    with control_cols[4]:
        if st.button("⏭️ End", use_container_width=True):
            if st.session_state.selected_end_time:
                st.session_state.current_timestamp = st.session_state.selected_end_time
            elif st.session_state.data_loader:
                st.session_state.current_timestamp = st.session_state.data_loader.end_time
    
    with control_cols[5]:
        jump_amount = st.selectbox(
            "Jump",
            options=[opt[0] for opt in JUMP_OPTIONS],
            label_visibility="collapsed"
        )
    
    with control_cols[6]:
        if st.button("⏪ Jump Back", use_container_width=True):
            if st.session_state.current_timestamp:
                jump = next((opt[1] for opt in JUMP_OPTIONS if opt[0] == jump_amount), timedelta(minutes=1))
                if jump == 'session':
                    session = get_current_session(st.session_state.current_timestamp)
                    if session in SESSIONS:
                        st.session_state.current_timestamp = datetime.combine(
                            st.session_state.current_timestamp.date(),
                            SESSIONS[session]['start']
                        )
                elif jump == 'day':
                    st.session_state.current_timestamp = datetime.combine(
                        st.session_state.current_timestamp.date(),
                        time(4, 0)
                    )
                else:
                    st.session_state.current_timestamp -= jump
    
    with control_cols[7]:
        if st.button("⏩ Jump Forward", use_container_width=True):
            if st.session_state.current_timestamp:
                jump = next((opt[1] for opt in JUMP_OPTIONS if opt[0] == jump_amount), timedelta(minutes=1))
                if jump == 'session':
                    session = get_current_session(st.session_state.current_timestamp)
                    if session in SESSIONS:
                        st.session_state.current_timestamp = datetime.combine(
                            st.session_state.current_timestamp.date(),
                            SESSIONS[session]['end']
                        )
                elif jump == 'day':
                    next_day = st.session_state.current_timestamp.date() + timedelta(days=1)
                    st.session_state.current_timestamp = datetime.combine(next_day, time(4, 0))
                else:
                    st.session_state.current_timestamp += jump
    
    # ==============================================================================
    # CHART FRAGMENT (Partial rerun area)
    # ==============================================================================
    
    st.markdown("---")
    
    # Call the fragment - only this section reruns on auto-refresh
    chart_fragment()


if __name__ == "__main__":
    main()
