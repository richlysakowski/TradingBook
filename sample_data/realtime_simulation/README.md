# NQ Futures Real-Time Candlestick Simulation

A Streamlit application for simulating real-time NQ futures candlestick chart evolution with 1-second tick resolution. Watch candles grow tick by tick as if you were trading live!

**Now powered by Polars for 5-10x faster data generation!**

![Demo Screenshot](docs/demo.png)

## Features

### 📊 Real-Time Candlestick Visualization
- **Growing Candles**: Watch 1-minute candles build tick by tick from 1-second data
- **Multiple Timeframes**: Switch between 1-second, 1-minute, and 5-minute candles
- **Session Awareness**: Pre-market (4:00 AM), Regular Hours (9:30 AM - 4:00 PM), After-hours (4:00 PM - 8:00 PM)

### 📈 Technical Indicators
- **VWAP** (Volume Weighted Average Price) - with daily reset
- **9 EMA** (Exponential Moving Average)
- **20 EMA** (Exponential Moving Average)
- **Volume Bars** with color coding (green for up candles, red for down)
- **Volume Average** (20-period moving average)

### 🎮 Playback Controls
- **Play/Pause**: Start and stop simulation
- **Speed Control**: 1x (real-time) to 100x speed
- **Jump Controls**: Jump by 1m, 5m, 30m, 60m, 90m, 120m, Session, or Day
- **Time Range Selection**: Choose specific start/end times

### 💰 Price Panel
- **Last Price**: Current market price
- **Bid/Ask**: Current bid and ask prices
- **Spread**: Current bid-ask spread
- **Session Indicator**: Shows current market session

### 🎨 Customization
- **Candle Colors**: Choose your own up/down candle colors
- **Indicator Toggles**: Show/hide individual indicators
- **Max Visible Candles**: Configure chart history

## Quick Start

### 1. Setup Conda Environment (Recommended)

```bash
cd sample_data/realtime_simulation

# Run setup script (creates nq_sims_city environment)
setup_conda_env.bat

# Activate the environment
conda activate nq_sims_city
```

Or manually:
```bash
conda env create -f environment.yml
conda activate nq_sims_city
```

### 2. Alternative: pip install

```bash
pip install -r requirements.txt
```

### 3. Generate Sample Data

Generate 5 days of tick data (default):
```bash
python generate_tick_data.py --days 5 --seed 42
```

Generate more data for longer simulations:
```bash
# 1 week
python generate_tick_data.py --days 5 --seed 42

# 1 month
python generate_tick_data.py --days 22 --seed 42

# 1 year (large dataset!) - outputs to Parquet for efficiency
python generate_tick_data.py --days 252 --seed 42 --output-parquet
```

### 4. Run the Application

```bash
streamlit run realtime_candlestick_app.py
```

The app will open in your browser at `http://localhost:8501`

### 5. Load Data and Start Simulation

1. Enter the database path in the sidebar (default: `nq_tick_simulation.db`)
2. Click "Load Data"
3. Select a date and time range
4. Click "Set Time Range"
5. Press ▶️ Play to start the simulation!

## Data Generation Details

### Tick Data Structure
Each tick contains:
- `timestamp`: 1-second resolution timestamp
- `price`: Last trade price
- `bid`: Current bid price
- `ask`: Current ask price
- `spread`: Bid-ask spread
- `volume`: Trade volume for that second
- `session`: Market session (premarket, rth_open, rth_morning, etc.)

### Market Simulation Characteristics
- **Volatility**: ~22% annualized (realistic for NQ)
- **Sessions**: Different volatility and volume patterns by session
- **Day Types**: Trending, range-bound, volatile days
- **Spread Dynamics**: Wider spreads in pre/after-market
- **Volume Patterns**: Higher at open/close, lower at lunch

### Database Schema

```sql
-- Tick data (1-second resolution)
tick_data (
    id, timestamp, price, bid, ask, spread, volume, session
)

-- Pre-aggregated OHLC for performance
ohlc_1s, ohlc_1m, ohlc_5m (
    timestamp, open, high, low, close, volume, vwap, trade_count
)

-- Simulation state
simulation_state (
    id, current_timestamp, playback_speed, is_playing, timeframe
)
```

## Command Line Options

```bash
python generate_tick_data.py [OPTIONS]

Options:
  --days N           Number of trading days to generate (default: 5)
  --start-date DATE  Start date in YYYY-MM-DD format
  --start-price P    Starting price (default: 21500.0)
  --output-db PATH   Output SQLite database path
  --output-csv       Output to chunked CSV files instead
  --csv-dir DIR      Directory for CSV chunks (default: tick_data_chunks)
  --chunk-days N     Days per CSV chunk (default: 5)
  --seed N           Random seed for reproducibility
  --aggregate        Pre-aggregate OHLC data (recommended)
```

## File Structure

```
realtime_simulation/
├── generate_tick_data.py      # Tick data generator
├── data_loader.py             # Data loading and OHLC building
├── realtime_candlestick_app.py # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── nq_tick_simulation.db      # Generated database (after running generator)
```

## Usage Tips

### Performance
- For best performance, use the SQLite database with pre-aggregated OHLC tables
- Limit visible candles to 100-200 for smooth playback
- At high playback speeds (50-100x), the app updates ~10 times per second

### Realistic Trading Practice
1. Start at market open (9:30 AM)
2. Set playback speed to 10-20x for faster but still readable charts
3. Practice identifying patterns and making decisions
4. Use the pause button to analyze setups

### Analyzing Specific Events
1. Jump to a specific time using the time range selector
2. Set playback speed to 1-5x for detailed analysis
3. Step through tick by tick using the +1m / -1m buttons

## Troubleshooting

### "Database not found"
Run the data generator first:
```bash
python generate_tick_data.py --days 5
```

### Chart not updating
1. Make sure the database is loaded (green success message)
2. Check that the time range is set
3. Ensure playback is not paused

### Slow performance
1. Reduce max visible candles in sidebar
2. Use pre-aggregated OHLC tables
3. Close other browser tabs

## Future Enhancements

- [ ] Multiple chart layouts (2x2 timeframes)
- [ ] Drawing tools (trend lines, Fibonacci)
- [ ] Trade entry/exit markers
- [ ] P&L tracking for simulated trades
- [ ] Order flow / Level 2 simulation
- [ ] Save/load simulation states
- [ ] Export chart as image

## License

This project is part of the TradingBook application. See the main project license for details.
