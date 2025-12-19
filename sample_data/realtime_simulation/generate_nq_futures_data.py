"""
NQ Futures 1-Minute Candlestick Data Generator

Generates realistic simulated Nasdaq-100 E-mini (NQ) futures data with:
- Proper volatility characteristics matching 2020-2025 market behavior
- Intraday patterns (higher volatility at open/close, lunch lull)
- Gap opens between sessions
- Trend days vs. range days
- Realistic bid-ask spread and volume patterns

Output: CSV files compatible with TradingBook import

Usage:
    python generate_nq_futures_data.py
    python generate_nq_futures_data.py --days 30 --start-date 2024-01-01
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse
import os

# NQ Futures characteristics (based on 2020-2025 data)
NQ_CONFIG = {
    'symbol': 'NQH5',  # March 2025 contract
    'base_price': 21500,  # Approximate NQ price level
    'tick_size': 0.25,  # Minimum price movement
    'tick_value': 5.00,  # Dollar value per tick
    'point_value': 20.00,  # Dollar value per point
    
    # Volatility parameters (annualized, then scaled to 1-min)
    'annual_volatility': 0.22,  # ~22% annual volatility
    'intraday_vol_multiplier': {
        'open': 2.5,      # First 30 min: high volatility
        'morning': 1.2,   # 9:30-11:30: moderate
        'lunch': 0.6,     # 11:30-13:30: low volatility
        'afternoon': 1.0, # 13:30-15:00: normal
        'close': 1.8,     # Last 30 min: high volatility
    },
    
    # Session times (Eastern Time)
    'rth_start': '09:30',  # Regular trading hours start
    'rth_end': '16:00',    # Regular trading hours end
    'minutes_per_day': 390,  # 6.5 hours * 60
    
    # Distribution of day types
    'trend_day_prob': 0.25,     # Strong directional days
    'range_day_prob': 0.55,     # Normal range-bound days
    'volatile_day_prob': 0.20,  # High volatility, mixed direction
}


def get_intraday_volatility_multiplier(minute_of_day: int) -> float:
    """
    Returns volatility multiplier based on time of day.
    minute_of_day: 0 = 9:30 AM, 390 = 4:00 PM
    """
    if minute_of_day < 30:  # First 30 min
        return NQ_CONFIG['intraday_vol_multiplier']['open']
    elif minute_of_day < 120:  # 9:30-11:30
        return NQ_CONFIG['intraday_vol_multiplier']['morning']
    elif minute_of_day < 240:  # 11:30-13:30
        return NQ_CONFIG['intraday_vol_multiplier']['lunch']
    elif minute_of_day < 330:  # 13:30-15:00
        return NQ_CONFIG['intraday_vol_multiplier']['afternoon']
    else:  # Last 30 min
        return NQ_CONFIG['intraday_vol_multiplier']['close']


def generate_day_type() -> str:
    """Randomly select the type of trading day."""
    rand = np.random.random()
    if rand < NQ_CONFIG['trend_day_prob']:
        return 'trend'
    elif rand < NQ_CONFIG['trend_day_prob'] + NQ_CONFIG['range_day_prob']:
        return 'range'
    else:
        return 'volatile'


def round_to_tick(price: float) -> float:
    """Round price to nearest tick size (0.25 for NQ)."""
    tick = NQ_CONFIG['tick_size']
    return round(price / tick) * tick


def generate_single_day_candles(
    date: datetime,
    open_price: float,
    day_type: str
) -> pd.DataFrame:
    """
    Generate 1-minute candles for a single trading day.
    
    Returns DataFrame with columns: datetime, open, high, low, close, volume
    """
    minutes = NQ_CONFIG['minutes_per_day']
    
    # Day-specific parameters
    if day_type == 'trend':
        # Trend day: strong directional move
        daily_drift = np.random.choice([-1, 1]) * np.random.uniform(0.008, 0.02)
        vol_scale = 1.3
    elif day_type == 'volatile':
        # Volatile day: large swings both directions
        daily_drift = np.random.uniform(-0.005, 0.005)
        vol_scale = 1.8
    else:  # range day
        # Range day: mean-reverting, smaller moves
        daily_drift = np.random.uniform(-0.003, 0.003)
        vol_scale = 0.8
    
    # Base per-minute volatility (from annual)
    annual_vol = NQ_CONFIG['annual_volatility']
    minutes_per_year = 252 * 390  # Trading days * minutes per day
    base_minute_vol = annual_vol / np.sqrt(minutes_per_year) * vol_scale
    
    # Generate price path
    prices = [open_price]
    current_price = open_price
    
    for minute in range(minutes):
        # Time-of-day volatility adjustment
        tod_mult = get_intraday_volatility_multiplier(minute)
        minute_vol = base_minute_vol * tod_mult
        
        # Drift component (slightly stronger at open for trend days)
        drift_mult = 1.5 if minute < 60 and day_type == 'trend' else 1.0
        drift = (daily_drift / minutes) * drift_mult
        
        # Random return
        random_return = np.random.normal(drift, minute_vol)
        
        # Mean reversion for range days
        if day_type == 'range':
            deviation = (current_price - open_price) / open_price
            mean_reversion = -0.1 * deviation  # Pull back toward open
            random_return += mean_reversion / minutes
        
        # Update price
        current_price = current_price * (1 + random_return)
        prices.append(current_price)
    
    # Generate OHLC from price path
    candles = []
    start_time = datetime.combine(date, datetime.strptime(NQ_CONFIG['rth_start'], '%H:%M').time())
    
    for minute in range(minutes):
        candle_time = start_time + timedelta(minutes=minute)
        
        # Get prices for this minute (use surrounding prices for OHLC)
        base_price = prices[minute]
        next_price = prices[minute + 1]
        
        # Generate intracandle movement
        tod_mult = get_intraday_volatility_multiplier(minute)
        intracandle_vol = base_minute_vol * tod_mult * 0.5
        
        candle_open = round_to_tick(base_price)
        candle_close = round_to_tick(next_price)
        
        # High and Low
        high_extension = abs(np.random.normal(0, intracandle_vol * base_price))
        low_extension = abs(np.random.normal(0, intracandle_vol * base_price))
        
        candle_high = round_to_tick(max(candle_open, candle_close) + high_extension)
        candle_low = round_to_tick(min(candle_open, candle_close) - low_extension)
        
        # Volume (higher at open/close, correlated with volatility)
        base_volume = np.random.randint(500, 2000)
        volume = int(base_volume * tod_mult * (1 + abs(candle_close - candle_open) / candle_open * 100))
        
        candles.append({
            'datetime': candle_time,
            'open': candle_open,
            'high': candle_high,
            'low': candle_low,
            'close': candle_close,
            'volume': volume
        })
    
    return pd.DataFrame(candles)


def generate_nq_dataset(
    num_days: int = 20,
    start_date: datetime = None,
    start_price: float = None
) -> pd.DataFrame:
    """
    Generate multi-day NQ futures 1-minute data.
    
    Args:
        num_days: Number of trading days to generate
        start_date: Starting date (default: 20 days ago)
        start_price: Starting price (default: NQ_CONFIG base_price)
    
    Returns:
        DataFrame with all candle data
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days + 10)
    if start_price is None:
        start_price = NQ_CONFIG['base_price']
    
    all_candles = []
    current_price = start_price
    current_date = start_date
    days_generated = 0
    
    print(f"Generating {num_days} days of NQ futures data...")
    print(f"Starting price: {start_price}")
    print(f"Starting date: {start_date.strftime('%Y-%m-%d')}")
    print()
    
    while days_generated < num_days:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Determine day type
        day_type = generate_day_type()
        
        # Gap open (overnight move)
        gap_percent = np.random.normal(0, 0.003)  # ~0.3% avg gap
        gap_open = round_to_tick(current_price * (1 + gap_percent))
        
        # Generate day's candles
        day_candles = generate_single_day_candles(current_date, gap_open, day_type)
        all_candles.append(day_candles)
        
        # Update for next day
        current_price = day_candles.iloc[-1]['close']
        
        # Print progress
        day_return = (current_price - gap_open) / gap_open * 100
        print(f"  {current_date.strftime('%Y-%m-%d')} ({day_type:8s}): "
              f"Open={gap_open:.2f}, Close={current_price:.2f}, "
              f"Return={day_return:+.2f}%")
        
        current_date += timedelta(days=1)
        days_generated += 1
    
    result = pd.concat(all_candles, ignore_index=True)
    print(f"\nGenerated {len(result)} candles across {num_days} trading days")
    print(f"Final price: {current_price:.2f}")
    print(f"Total return: {(current_price - start_price) / start_price * 100:+.2f}%")
    
    return result


def generate_trades_from_candles(
    candles: pd.DataFrame,
    num_trades: int = 50,
    win_rate: float = 0.55
) -> pd.DataFrame:
    """
    Generate realistic trade entries/exits from candle data.
    
    Creates a mix of:
    - Scalp trades (5-15 min hold, 5-20 tick targets)
    - Day trades (30-120 min hold, 30-100 tick targets)
    - Swing trades (multiple hours, 100+ tick targets)
    
    Returns DataFrame in TradingBook CSV format.
    """
    trades = []
    
    # Trade type distribution
    trade_types = {
        'scalp': {'prob': 0.5, 'hold_min': (5, 15), 'target_ticks': (5, 20), 'stop_ticks': (8, 15)},
        'day': {'prob': 0.35, 'hold_min': (30, 120), 'target_ticks': (30, 80), 'stop_ticks': (20, 40)},
        'swing': {'prob': 0.15, 'hold_min': (120, 300), 'target_ticks': (80, 200), 'stop_ticks': (40, 80)},
    }
    
    tick_value = NQ_CONFIG['tick_value']
    
    for i in range(num_trades):
        # Select trade type
        rand = np.random.random()
        if rand < trade_types['scalp']['prob']:
            trade_type = 'scalp'
        elif rand < trade_types['scalp']['prob'] + trade_types['day']['prob']:
            trade_type = 'day'
        else:
            trade_type = 'swing'
        
        config = trade_types[trade_type]
        
        # Random entry point (not in last 2 hours of data for swing trades)
        max_entry_idx = len(candles) - config['hold_min'][1] - 60
        if max_entry_idx < 100:
            max_entry_idx = len(candles) - 100
        
        entry_idx = np.random.randint(60, max(61, max_entry_idx))
        entry_candle = candles.iloc[entry_idx]
        
        # Entry details
        side = np.random.choice(['LONG', 'SHORT'])
        entry_price = entry_candle['close']
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.4, 0.3, 0.15, 0.1, 0.05])
        
        # Determine win/loss
        is_winner = np.random.random() < win_rate
        
        # Calculate exit
        hold_minutes = np.random.randint(*config['hold_min'])
        exit_idx = min(entry_idx + hold_minutes, len(candles) - 1)
        exit_candle = candles.iloc[exit_idx]
        
        if is_winner:
            target_ticks = np.random.randint(*config['target_ticks'])
            if side == 'LONG':
                exit_price = entry_price + (target_ticks * NQ_CONFIG['tick_size'])
            else:
                exit_price = entry_price - (target_ticks * NQ_CONFIG['tick_size'])
        else:
            stop_ticks = np.random.randint(*config['stop_ticks'])
            if side == 'LONG':
                exit_price = entry_price - (stop_ticks * NQ_CONFIG['tick_size'])
            else:
                exit_price = entry_price + (stop_ticks * NQ_CONFIG['tick_size'])
        
        exit_price = round_to_tick(exit_price)
        
        # Calculate P&L
        if side == 'LONG':
            pnl = (exit_price - entry_price) * NQ_CONFIG['point_value'] * quantity
        else:
            pnl = (entry_price - exit_price) * NQ_CONFIG['point_value'] * quantity
        
        # Commission (~$4.50 per contract round trip)
        commission = quantity * 4.50
        
        trades.append({
            'Date': entry_candle['datetime'].strftime('%m/%d/%Y'),
            'Time': entry_candle['datetime'].strftime('%H:%M:%S'),
            'Symbol': NQ_CONFIG['symbol'],
            'Side': side,
            'Quantity': quantity,
            'Entry Price': entry_price,
            'Exit Price': exit_price,
            'Exit Date': exit_candle['datetime'].strftime('%m/%d/%Y'),
            'Exit Time': exit_candle['datetime'].strftime('%H:%M:%S'),
            'P&L': round(pnl - commission, 2),
            'Commission': commission,
            'Asset Type': 'FUTURES',
            'Strategy': f'{trade_type.upper()}_{side}',
            'Notes': f'{trade_type} trade, {hold_minutes} min hold'
        })
    
    return pd.DataFrame(trades)


def save_outputs(candles: pd.DataFrame, trades: pd.DataFrame, output_dir: str):
    """Save generated data to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save candle data
    candle_file = os.path.join(output_dir, 'nq_futures_1min_candles.csv')
    candles.to_csv(candle_file, index=False)
    print(f"\nSaved candle data to: {candle_file}")
    
    # Save trade data (TradingBook format)
    trade_file = os.path.join(output_dir, 'nq_futures_sample_trades.csv')
    trades.to_csv(trade_file, index=False)
    print(f"Saved trade data to: {trade_file}")
    
    # Also save in Schwab-like format for direct import
    schwab_trades = trades.copy()
    schwab_trades['Action'] = schwab_trades['Side'].map({'LONG': 'Buy to Open', 'SHORT': 'Sell to Open'})
    schwab_trades['Description'] = 'E-MINI NASDAQ-100 INDEX FUTURES'
    schwab_trades['Fees & Comm'] = schwab_trades['Commission']
    schwab_trades['Amount'] = schwab_trades['P&L']
    schwab_trades['Price'] = schwab_trades['Entry Price']
    
    schwab_file = os.path.join(output_dir, 'nq_futures_schwab_format.csv')
    schwab_cols = ['Date', 'Action', 'Symbol', 'Description', 'Quantity', 'Price', 'Fees & Comm', 'Amount']
    schwab_trades[schwab_cols].to_csv(schwab_file, index=False)
    print(f"Saved Schwab-format trades to: {schwab_file}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("TRADE SUMMARY")
    print("="*60)
    total_pnl = trades['P&L'].sum()
    winners = trades[trades['P&L'] > 0]
    losers = trades[trades['P&L'] <= 0]
    
    print(f"Total Trades: {len(trades)}")
    print(f"Winners: {len(winners)} ({len(winners)/len(trades)*100:.1f}%)")
    print(f"Losers: {len(losers)} ({len(losers)/len(trades)*100:.1f}%)")
    print(f"Total P&L: ${total_pnl:,.2f}")
    print(f"Average Win: ${winners['P&L'].mean():,.2f}" if len(winners) > 0 else "No winners")
    print(f"Average Loss: ${losers['P&L'].mean():,.2f}" if len(losers) > 0 else "No losers")
    print(f"Largest Win: ${winners['P&L'].max():,.2f}" if len(winners) > 0 else "N/A")
    print(f"Largest Loss: ${losers['P&L'].min():,.2f}" if len(losers) > 0 else "N/A")


def main():
    parser = argparse.ArgumentParser(
        description='Generate realistic NQ futures 1-minute candlestick data'
    )
    parser.add_argument('--days', type=int, default=20,
                        help='Number of trading days to generate (default: 20)')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Start date in YYYY-MM-DD format (default: 30 days ago)')
    parser.add_argument('--start-price', type=float, default=None,
                        help=f'Starting price (default: {NQ_CONFIG["base_price"]})')
    parser.add_argument('--trades', type=int, default=75,
                        help='Number of sample trades to generate (default: 75)')
    parser.add_argument('--win-rate', type=float, default=0.52,
                        help='Win rate for generated trades (default: 0.52)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory (default: current directory)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        np.random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    # Parse start date
    start_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    
    print("="*60)
    print("NQ FUTURES DATA GENERATOR")
    print("="*60)
    print()
    
    # Generate candle data
    candles = generate_nq_dataset(
        num_days=args.days,
        start_date=start_date,
        start_price=args.start_price
    )
    
    print()
    
    # Generate trades from candles
    print("="*60)
    print("GENERATING SAMPLE TRADES")
    print("="*60)
    trades = generate_trades_from_candles(
        candles,
        num_trades=args.trades,
        win_rate=args.win_rate
    )
    
    # Save outputs
    save_outputs(candles, trades, args.output_dir)
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
