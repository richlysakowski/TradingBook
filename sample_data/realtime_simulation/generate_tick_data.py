"""
NQ Futures 1-Second Tick Data Generator (Polars Version)

Generates realistic simulated tick data for NQ futures with:
- 1-second resolution for real-time candlestick simulation
- Pre-market (4:00 AM - 9:30 AM ET)
- Regular Trading Hours (9:30 AM - 4:00 PM ET)
- After-hours (4:00 PM - 8:00 PM ET)
- Realistic bid/ask spread dynamics
- Microstructure noise and price discovery
- Volume patterns matching session characteristics

Uses Polars for 5-10x faster data processing vs Pandas!

Output: SQLite database or chunked CSV/Parquet files (5-day blocks)

Usage:
    python generate_tick_data.py --days 5 --output-db nq_tick_data.db
    python generate_tick_data.py --days 5 --output-csv --chunk-days 5
    python generate_tick_data.py --days 252 --output-parquet --chunk-days 5  # 1 year
"""

import numpy as np
import polars as pl
from datetime import datetime, timedelta, time
import sqlite3
import argparse
import os
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass


@dataclass
class SessionConfig:
    """Trading session configuration."""
    name: str
    start_time: time
    end_time: time
    volatility_mult: float
    volume_mult: float
    spread_mult: float


# NQ Futures characteristics
NQ_CONFIG = {
    'symbol': 'NQH5',
    'base_price': 21500.0,
    'tick_size': 0.25,
    'tick_value': 5.00,
    'point_value': 20.00,
    
    # Annualized volatility (~22% for NQ)
    'annual_volatility': 0.22,
    
    # Base spread in ticks (usually 1-2 ticks for NQ)
    'base_spread_ticks': 1,
    
    # Sessions (Eastern Time)
    'sessions': [
        SessionConfig('premarket', time(4, 0), time(9, 30), 0.6, 0.3, 1.5),
        SessionConfig('rth_open', time(9, 30), time(10, 0), 2.0, 2.5, 1.0),
        SessionConfig('rth_morning', time(10, 0), time(11, 30), 1.2, 1.2, 1.0),
        SessionConfig('rth_lunch', time(11, 30), time(13, 30), 0.6, 0.6, 1.2),
        SessionConfig('rth_afternoon', time(13, 30), time(15, 30), 1.0, 1.0, 1.0),
        SessionConfig('rth_close', time(15, 30), time(16, 0), 1.8, 2.0, 1.0),
        SessionConfig('afterhours', time(16, 0), time(20, 0), 0.5, 0.2, 2.0),
    ],
    
    # Seconds per trading day (4 AM to 8 PM = 16 hours)
    'seconds_per_day': 16 * 60 * 60,  # 57,600 seconds
}


def get_session_config(current_time: time) -> SessionConfig:
    """Get the session configuration for a given time."""
    for session in NQ_CONFIG['sessions']:
        if session.start_time <= current_time < session.end_time:
            return session
    # Default to afterhours if outside all sessions
    return NQ_CONFIG['sessions'][-1]


def get_session_name(current_time: time) -> str:
    """Get just the session name for a given time."""
    return get_session_config(current_time).name


def calculate_second_volatility(annual_vol: float, session_mult: float) -> float:
    """Convert annual volatility to per-second volatility."""
    # Trading seconds per year: ~252 days * 57600 seconds
    seconds_per_year = 252 * NQ_CONFIG['seconds_per_day']
    return annual_vol / np.sqrt(seconds_per_year) * session_mult


def round_to_tick(price: float) -> float:
    """Round price to nearest tick size."""
    tick = NQ_CONFIG['tick_size']
    return round(price / tick) * tick


def round_to_tick_vectorized(prices: np.ndarray) -> np.ndarray:
    """Vectorized round to tick size."""
    tick = NQ_CONFIG['tick_size']
    return np.round(prices / tick) * tick


def generate_single_day_ticks_vectorized(
    date: datetime,
    open_price: float,
    day_type: str = 'normal'
) -> pl.DataFrame:
    """
    Generate 1-second tick data for a single trading day using vectorized operations.
    Much faster than the iterative approach!
    
    Args:
        date: The trading date
        open_price: Opening price for the day
        day_type: 'trend_up', 'trend_down', 'range', 'volatile', 'normal'
    
    Returns:
        Polars DataFrame with columns: timestamp, price, bid, ask, spread, volume, session
    """
    total_seconds = NQ_CONFIG['seconds_per_day']
    
    # Day parameters based on type
    if day_type == 'trend_up':
        daily_drift = np.random.uniform(0.005, 0.015)
        vol_scale = 1.2
    elif day_type == 'trend_down':
        daily_drift = np.random.uniform(-0.015, -0.005)
        vol_scale = 1.2
    elif day_type == 'volatile':
        daily_drift = np.random.uniform(-0.003, 0.003)
        vol_scale = 1.8
    elif day_type == 'range':
        daily_drift = 0
        vol_scale = 0.7
    else:  # normal
        daily_drift = np.random.uniform(-0.005, 0.005)
        vol_scale = 1.0
    
    # Generate all timestamps at once
    start_time = datetime.combine(date, time(4, 0, 0))
    timestamps = [start_time + timedelta(seconds=i) for i in range(total_seconds)]
    
    # Get session info for each timestamp
    session_names = [get_session_name(ts.time()) for ts in timestamps]
    
    # Create session multiplier arrays
    session_vol_mults = np.array([get_session_config(ts.time()).volatility_mult for ts in timestamps])
    session_spread_mults = np.array([get_session_config(ts.time()).spread_mult for ts in timestamps])
    session_volume_mults = np.array([get_session_config(ts.time()).volume_mult for ts in timestamps])
    
    # Calculate per-second volatilities
    base_second_vol = NQ_CONFIG['annual_volatility'] / np.sqrt(252 * total_seconds)
    second_vols = base_second_vol * session_vol_mults * vol_scale
    
    # Generate random returns with drift
    drift_per_second = daily_drift / total_seconds
    
    # For range days, we need to add mean reversion, so generate iteratively for that case
    if day_type == 'range':
        # Use semi-vectorized approach for range days
        prices = np.zeros(total_seconds)
        prices[0] = open_price
        
        for i in range(1, total_seconds):
            deviation = (prices[i-1] - open_price) / open_price
            mean_reversion = -0.0001 * deviation
            adjusted_drift = drift_per_second + mean_reversion
            ret = np.random.normal(adjusted_drift, second_vols[i])
            prices[i] = prices[i-1] * (1 + ret)
    else:
        # Fully vectorized for non-range days
        returns = np.random.normal(drift_per_second, second_vols)
        cumulative_returns = np.cumprod(1 + returns)
        prices = open_price * cumulative_returns
    
    # Round prices to tick size
    prices = round_to_tick_vectorized(prices)
    
    # Generate spreads
    spread_noise = np.random.uniform(0.8, 1.5, total_seconds)
    spread_ticks = np.maximum(1, np.round(NQ_CONFIG['base_spread_ticks'] * session_spread_mults * spread_noise))
    spreads = spread_ticks * NQ_CONFIG['tick_size']
    
    # Calculate bid/ask
    half_spreads = spreads / 2
    bids = round_to_tick_vectorized(prices - half_spreads)
    asks = round_to_tick_vectorized(prices + half_spreads)
    
    # Ensure ask > bid
    asks = np.where(asks <= bids, bids + NQ_CONFIG['tick_size'], asks)
    spreads = np.round(asks - bids, 2)
    
    # Generate volumes (Poisson with session scaling)
    base_volumes = np.random.poisson(50, total_seconds)
    # Price change effect on volume
    price_changes = np.abs(np.diff(prices, prepend=prices[0]) / prices)
    volume_multiplier = 1 + price_changes * 1000
    volumes = np.maximum(1, (base_volumes * session_volume_mults * volume_multiplier * 
                            np.random.uniform(0.5, 2.0, total_seconds)).astype(int))
    
    # Create Polars DataFrame (much faster than pandas for large data)
    df = pl.DataFrame({
        'timestamp': timestamps,
        'price': prices,
        'bid': bids,
        'ask': asks,
        'spread': spreads,
        'volume': volumes,
        'session': session_names
    })
    
    return df


def generate_multi_day_ticks(
    num_days: int,
    start_date: Optional[datetime] = None,
    start_price: Optional[float] = None
) -> Tuple[pl.DataFrame, float]:
    """
    Generate multi-day tick data using Polars.
    
    Returns:
        Tuple of (Polars DataFrame with all ticks, final closing price)
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days + 5)
    if start_price is None:
        start_price = NQ_CONFIG['base_price']
    
    all_dfs: List[pl.DataFrame] = []
    current_price = start_price
    current_date = start_date
    days_generated = 0
    
    # Day types distribution
    day_types = ['normal', 'normal', 'normal', 'range', 'range', 
                 'trend_up', 'trend_down', 'volatile']
    
    print(f"Generating {num_days} days of 1-second tick data (Polars vectorized)...")
    print(f"Starting price: {start_price}")
    print(f"Starting date: {start_date.strftime('%Y-%m-%d')}")
    print(f"Estimated rows: {num_days * NQ_CONFIG['seconds_per_day']:,}")
    print()
    
    while days_generated < num_days:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Determine day type
        day_type = np.random.choice(day_types)
        
        # Gap open (overnight move)
        gap_percent = np.random.normal(0, 0.002)
        gap_open = round_to_tick(current_price * (1 + gap_percent))
        
        print(f"  Day {days_generated + 1}/{num_days}: {current_date.strftime('%Y-%m-%d')} ({day_type})")
        
        # Generate day's ticks (vectorized - much faster!)
        day_df = generate_single_day_ticks_vectorized(current_date, gap_open, day_type)
        all_dfs.append(day_df)
        
        # Update for next day
        current_price = day_df['price'][-1]
        day_return = (current_price - gap_open) / gap_open * 100
        print(f"    Open: {gap_open:.2f}, Close: {current_price:.2f}, Return: {day_return:+.2f}%")
        
        current_date += timedelta(days=1)
        days_generated += 1
    
    # Concatenate all days (Polars is very fast at this)
    result = pl.concat(all_dfs)
    print(f"\nGenerated {len(result):,} tick records")
    
    return result, current_price


def save_to_sqlite(df: pl.DataFrame, db_path: str):
    """Save tick data to SQLite database."""
    print(f"\nSaving to SQLite: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    # Create tick_data table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tick_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            price REAL NOT NULL,
            bid REAL NOT NULL,
            ask REAL NOT NULL,
            spread REAL NOT NULL,
            volume INTEGER NOT NULL,
            session TEXT NOT NULL
        )
    ''')
    
    # Create index on timestamp
    conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON tick_data(timestamp)')
    
    # Convert to pandas for SQLite insertion (polars write_database requires connectorx)
    # This is a one-time operation so pandas overhead is acceptable
    pdf = df.to_pandas()
    pdf['timestamp'] = pdf['timestamp'].astype(str)
    pdf.to_sql('tick_data', conn, if_exists='append', index=False)
    
    # Create metadata table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Store metadata
    min_ts = df['timestamp'].min()
    max_ts = df['timestamp'].max()
    
    conn.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                 ('start_timestamp', str(min_ts)))
    conn.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                 ('end_timestamp', str(max_ts)))
    conn.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                 ('total_records', str(len(df))))
    conn.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                 ('symbol', NQ_CONFIG['symbol']))
    
    conn.commit()
    conn.close()
    
    print(f"Saved {len(df):,} records to {db_path}")


def save_to_chunked_files(
    df: pl.DataFrame, 
    output_dir: str, 
    chunk_days: int = 5,
    format: str = 'parquet'  # 'parquet' or 'csv'
):
    """Save tick data to chunked files (5 days per file). Parquet is ~5x smaller and faster."""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving to chunked {format.upper()} files in: {output_dir}")
    
    # Add date column for grouping
    df = df.with_columns(
        pl.col('timestamp').dt.date().alias('date')
    )
    
    dates = sorted(df['date'].unique().to_list())
    
    chunk_num = 0
    manifest_data = []
    
    for i in range(0, len(dates), chunk_days):
        chunk_dates = dates[i:i + chunk_days]
        chunk_df = df.filter(pl.col('date').is_in(chunk_dates)).drop('date')
        
        if len(chunk_df) == 0:
            continue
        
        start_dt = chunk_dates[0]
        end_dt = chunk_dates[-1]
        
        if format == 'parquet':
            filename = f"nq_ticks_{start_dt}_{end_dt}.parquet"
            filepath = os.path.join(output_dir, filename)
            chunk_df.write_parquet(filepath, compression='zstd')
        else:
            filename = f"nq_ticks_{start_dt}_{end_dt}.csv"
            filepath = os.path.join(output_dir, filename)
            chunk_df.write_csv(filepath)
        
        print(f"  Saved {filename} ({len(chunk_df):,} records)")
        
        manifest_data.append({
            'filename': filename,
            'start_timestamp': str(chunk_df['timestamp'].min()),
            'end_timestamp': str(chunk_df['timestamp'].max()),
            'records': len(chunk_df)
        })
        
        chunk_num += 1
    
    # Create manifest file
    manifest_path = os.path.join(output_dir, 'manifest.csv')
    manifest_df = pl.DataFrame(manifest_data)
    manifest_df.write_csv(manifest_path)
    
    print(f"\nCreated manifest: {manifest_path}")
    print(f"Total chunks: {chunk_num}")


def create_database_schema(db_path: str):
    """Create the full database schema for the simulation app."""
    conn = sqlite3.connect(db_path)
    
    # Tick data table (1-second resolution)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tick_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            price REAL NOT NULL,
            bid REAL NOT NULL,
            ask REAL NOT NULL,
            spread REAL NOT NULL,
            volume INTEGER NOT NULL,
            session TEXT NOT NULL
        )
    ''')
    
    # Pre-aggregated OHLC tables for performance
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ohlc_1s (
            timestamp TEXT PRIMARY KEY,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            vwap REAL,
            trade_count INTEGER
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ohlc_1m (
            timestamp TEXT PRIMARY KEY,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            vwap REAL,
            trade_count INTEGER
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ohlc_5m (
            timestamp TEXT PRIMARY KEY,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            vwap REAL,
            trade_count INTEGER
        )
    ''')
    
    # Simulation state
    conn.execute('''
        CREATE TABLE IF NOT EXISTS simulation_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_timestamp TEXT,
            playback_speed REAL DEFAULT 1.0,
            is_playing INTEGER DEFAULT 0,
            timeframe TEXT DEFAULT '1m'
        )
    ''')
    
    # Initialize simulation state
    conn.execute('''
        INSERT OR IGNORE INTO simulation_state (id, playback_speed, is_playing, timeframe)
        VALUES (1, 1.0, 0, '1m')
    ''')
    
    # Metadata
    conn.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Create indexes
    conn.execute('CREATE INDEX IF NOT EXISTS idx_tick_timestamp ON tick_data(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ohlc_1s_timestamp ON ohlc_1s(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ohlc_1m_timestamp ON ohlc_1m(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ohlc_5m_timestamp ON ohlc_5m(timestamp)')
    
    conn.commit()
    conn.close()
    
    print(f"Created database schema: {db_path}")


def aggregate_to_ohlc(db_path: str):
    """Pre-aggregate tick data to OHLC tables for performance using Polars."""
    print("\nPre-aggregating OHLC data with Polars...")
    
    conn = sqlite3.connect(db_path)
    
    # Read tick data into Polars (via pandas bridge for SQLite)
    import pandas as pd
    pdf = pd.read_sql('SELECT timestamp, price, volume FROM tick_data', conn)
    df = pl.from_pandas(pdf)
    df = df.with_columns(pl.col('timestamp').str.to_datetime())
    
    def aggregate_ohlc(df: pl.DataFrame, interval: str) -> pl.DataFrame:
        """Aggregate to OHLC at specified interval."""
        return df.group_by_dynamic(
            'timestamp',
            every=interval,
            closed='left'
        ).agg([
            pl.col('price').first().alias('open'),
            pl.col('price').max().alias('high'),
            pl.col('price').min().alias('low'),
            pl.col('price').last().alias('close'),
            pl.col('volume').sum().alias('volume'),
            ((pl.col('price') * pl.col('volume')).sum() / pl.col('volume').sum()).alias('vwap'),
            pl.len().alias('trade_count')
        ])
    
    # 1-second OHLC
    print("  Aggregating 1-second OHLC...")
    ohlc_1s = aggregate_ohlc(df, '1s')
    ohlc_1s_pdf = ohlc_1s.to_pandas()
    ohlc_1s_pdf['timestamp'] = ohlc_1s_pdf['timestamp'].astype(str)
    ohlc_1s_pdf.to_sql('ohlc_1s', conn, if_exists='replace', index=False)
    
    # 1-minute OHLC
    print("  Aggregating 1-minute OHLC...")
    ohlc_1m = aggregate_ohlc(df, '1m')
    ohlc_1m_pdf = ohlc_1m.to_pandas()
    ohlc_1m_pdf['timestamp'] = ohlc_1m_pdf['timestamp'].astype(str)
    ohlc_1m_pdf.to_sql('ohlc_1m', conn, if_exists='replace', index=False)
    
    # 5-minute OHLC
    print("  Aggregating 5-minute OHLC...")
    ohlc_5m = aggregate_ohlc(df, '5m')
    ohlc_5m_pdf = ohlc_5m.to_pandas()
    ohlc_5m_pdf['timestamp'] = ohlc_5m_pdf['timestamp'].astype(str)
    ohlc_5m_pdf.to_sql('ohlc_5m', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    
    print(f"  Created {len(ohlc_1s):,} 1-second bars")
    print(f"  Created {len(ohlc_1m):,} 1-minute bars")
    print(f"  Created {len(ohlc_5m):,} 5-minute bars")


def main():
    parser = argparse.ArgumentParser(
        description='Generate realistic NQ futures 1-second tick data (Polars-optimized)'
    )
    parser.add_argument('--days', type=int, default=5,
                        help='Number of trading days to generate (default: 5)')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Start date in YYYY-MM-DD format')
    parser.add_argument('--start-price', type=float, default=None,
                        help=f'Starting price (default: {NQ_CONFIG["base_price"]})')
    parser.add_argument('--output-db', type=str, default=None,
                        help='Output SQLite database path')
    parser.add_argument('--output-csv', action='store_true',
                        help='Output to chunked CSV files')
    parser.add_argument('--output-parquet', action='store_true',
                        help='Output to chunked Parquet files (recommended, ~5x smaller)')
    parser.add_argument('--output-dir', type=str, default='tick_data_chunks',
                        help='Directory for chunked files')
    parser.add_argument('--chunk-days', type=int, default=5,
                        help='Days per file chunk (default: 5)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--aggregate', action='store_true',
                        help='Pre-aggregate OHLC data (requires --output-db)')
    
    args = parser.parse_args()
    
    # Set random seed
    if args.seed is not None:
        np.random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Parse start date
    start_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    
    print("=" * 60)
    print("NQ FUTURES TICK DATA GENERATOR (Polars Optimized)")
    print("=" * 60)
    print()
    
    # Generate data
    df, final_price = generate_multi_day_ticks(
        num_days=args.days,
        start_date=start_date,
        start_price=args.start_price
    )
    
    # Save outputs
    if args.output_db:
        create_database_schema(args.output_db)
        save_to_sqlite(df, args.output_db)
        
        if args.aggregate:
            aggregate_to_ohlc(args.output_db)
    
    if args.output_parquet:
        save_to_chunked_files(df, args.output_dir, args.chunk_days, format='parquet')
    
    if args.output_csv:
        save_to_chunked_files(df, args.output_dir, args.chunk_days, format='csv')
    
    # Default: save to SQLite if no output specified
    if not args.output_db and not args.output_csv and not args.output_parquet:
        default_db = 'nq_tick_simulation.db'
        create_database_schema(default_db)
        save_to_sqlite(df, default_db)
        aggregate_to_ohlc(default_db)
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Final price: {final_price:.2f}")


if __name__ == '__main__':
    main()
