"""
Extended Stock Trade Data Generator

Generates realistic simulated stock trades with:
- Mix of LONG and SHORT positions
- Various holding periods (day trades to swing trades)
- Multiple sectors and symbols
- Realistic win rates and P&L distributions

Output: CSV files compatible with TradingBook import

Usage:
    python generate_extended_stock_trades.py
    python generate_extended_stock_trades.py --trades 200 --win-rate 0.55
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import argparse
import os

# Popular trading symbols by sector
SYMBOLS = {
    'tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'AMD', 'TSLA', 'NFLX', 'CRM'],
    'finance': ['JPM', 'BAC', 'GS', 'MS', 'C', 'WFC', 'BLK', 'SCHW', 'AXP', 'V'],
    'healthcare': ['JNJ', 'UNH', 'PFE', 'MRK', 'ABBV', 'TMO', 'ABT', 'LLY', 'BMY', 'AMGN'],
    'consumer': ['WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST', 'LOW', 'DIS', 'CMCSA'],
    'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
    'etf': ['SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLK', 'XLE', 'XLV', 'GLD', 'TLT'],
}

# Approximate price ranges (as of late 2025)
PRICE_RANGES = {
    'AAPL': (180, 220), 'MSFT': (380, 440), 'GOOGL': (160, 190), 'AMZN': (180, 220),
    'META': (500, 600), 'NVDA': (450, 550), 'AMD': (140, 180), 'TSLA': (250, 350),
    'NFLX': (650, 750), 'CRM': (280, 340),
    'JPM': (180, 220), 'BAC': (35, 45), 'GS': (450, 550), 'MS': (95, 115),
    'C': (55, 70), 'WFC': (55, 70), 'BLK': (800, 950), 'SCHW': (70, 90),
    'AXP': (220, 280), 'V': (270, 320),
    'JNJ': (155, 175), 'UNH': (520, 600), 'PFE': (28, 38), 'MRK': (110, 135),
    'ABBV': (170, 200), 'TMO': (520, 600), 'ABT': (110, 130), 'LLY': (750, 900),
    'BMY': (50, 65), 'AMGN': (280, 340),
    'WMT': (160, 190), 'HD': (370, 430), 'MCD': (280, 320), 'NKE': (95, 120),
    'SBUX': (95, 115), 'TGT': (140, 170), 'COST': (850, 950), 'LOW': (250, 300),
    'DIS': (100, 130), 'CMCSA': (40, 50),
    'XOM': (105, 125), 'CVX': (145, 175), 'COP': (110, 135), 'SLB': (45, 60),
    'EOG': (120, 145), 'MPC': (160, 190), 'PSX': (130, 160), 'VLO': (140, 170),
    'OXY': (55, 75), 'HAL': (35, 45),
    'SPY': (550, 620), 'QQQ': (480, 540), 'IWM': (210, 240), 'DIA': (420, 470),
    'XLF': (42, 48), 'XLK': (200, 230), 'XLE': (85, 100), 'XLV': (140, 160),
    'GLD': (220, 260), 'TLT': (90, 110),
}

# Trade strategies
STRATEGIES = [
    'Momentum', 'Mean Reversion', 'Breakout', 'Gap Fill', 'VWAP',
    'Opening Range', 'Trend Following', 'Pullback', 'Reversal', 'Scalp'
]


def generate_random_price(symbol: str) -> float:
    """Generate a random price within the symbol's typical range."""
    if symbol in PRICE_RANGES:
        low, high = PRICE_RANGES[symbol]
    else:
        low, high = 50, 200  # Default range
    return round(np.random.uniform(low, high), 2)


def generate_trade(
    trade_date: datetime,
    is_winner: bool,
    is_long: bool,
    trade_type: str  # 'scalp', 'day', 'swing'
) -> dict:
    """Generate a single trade with realistic parameters."""
    
    # Select random symbol
    sector = np.random.choice(list(SYMBOLS.keys()))
    symbol = np.random.choice(SYMBOLS[sector])
    
    # Entry price
    entry_price = generate_random_price(symbol)
    
    # Position size based on price (aim for ~$5000-$20000 position size)
    target_position = np.random.uniform(5000, 20000)
    quantity = max(1, int(target_position / entry_price))
    
    # Holding period
    if trade_type == 'scalp':
        hold_minutes = np.random.randint(5, 30)
        target_pct = np.random.uniform(0.003, 0.01)  # 0.3% - 1%
        stop_pct = np.random.uniform(0.002, 0.008)   # 0.2% - 0.8%
    elif trade_type == 'day':
        hold_minutes = np.random.randint(30, 360)
        target_pct = np.random.uniform(0.01, 0.03)   # 1% - 3%
        stop_pct = np.random.uniform(0.005, 0.02)    # 0.5% - 2%
    else:  # swing
        hold_minutes = np.random.randint(390, 390 * 5)  # 1-5 days
        target_pct = np.random.uniform(0.03, 0.08)   # 3% - 8%
        stop_pct = np.random.uniform(0.02, 0.05)     # 2% - 5%
    
    # Calculate exit price
    if is_winner:
        move_pct = target_pct * np.random.uniform(0.5, 1.5)  # Some variation
    else:
        move_pct = -stop_pct * np.random.uniform(0.5, 1.2)
    
    if is_long:
        exit_price = round(entry_price * (1 + move_pct), 2)
        side = 'LONG'
        pnl = (exit_price - entry_price) * quantity
    else:
        exit_price = round(entry_price * (1 - move_pct), 2)
        side = 'SHORT'
        pnl = (entry_price - exit_price) * quantity
    
    # Exit time
    entry_time = datetime.combine(trade_date, datetime.strptime('09:30', '%H:%M').time())
    entry_time += timedelta(minutes=np.random.randint(0, 360))  # Random entry in the day
    
    if trade_type == 'swing':
        exit_date = trade_date + timedelta(days=np.random.randint(1, 5))
        exit_time = datetime.combine(exit_date, datetime.strptime('15:30', '%H:%M').time())
    else:
        exit_time = entry_time + timedelta(minutes=hold_minutes)
        exit_date = trade_date
        if exit_time.hour >= 16:
            exit_time = datetime.combine(trade_date, datetime.strptime('15:59', '%H:%M').time())
    
    # Commission (~$0 for most brokers, but include small fees)
    commission = round(quantity * 0.005, 2)  # $0.005 per share
    
    # Strategy
    strategy = np.random.choice(STRATEGIES)
    
    return {
        'Date': entry_time.strftime('%m/%d/%Y'),
        'Time': entry_time.strftime('%H:%M:%S'),
        'Action': 'Buy' if is_long else 'Sell Short',
        'Symbol': symbol,
        'Description': f'{symbol} Common Stock',
        'Quantity': quantity,
        'Price': entry_price,
        'Entry Price': entry_price,
        'Exit Price': exit_price,
        'Exit Date': exit_date.strftime('%m/%d/%Y'),
        'Exit Time': exit_time.strftime('%H:%M:%S'),
        'Side': side,
        'Fees & Comm': commission,
        'P&L': round(pnl - commission, 2),
        'Amount': round(pnl - commission, 2),
        'Asset Type': 'STOCK',
        'Strategy': strategy,
        'Notes': f'{trade_type.capitalize()} trade - {strategy}'
    }


def generate_trades(
    num_trades: int = 150,
    win_rate: float = 0.53,
    long_ratio: float = 0.65,  # 65% long, 35% short
    start_date: datetime = None,
    num_days: int = 30
) -> pd.DataFrame:
    """Generate a dataset of realistic stock trades."""
    
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days + 10)
    
    trades = []
    trade_types = ['scalp', 'day', 'swing']
    trade_type_probs = [0.3, 0.5, 0.2]  # 30% scalp, 50% day, 20% swing
    
    # Generate trading days
    trading_days = []
    current_date = start_date
    while len(trading_days) < num_days:
        if current_date.weekday() < 5:  # Skip weekends
            trading_days.append(current_date)
        current_date += timedelta(days=1)
    
    print(f"Generating {num_trades} stock trades across {num_days} trading days...")
    print(f"Date range: {trading_days[0].strftime('%Y-%m-%d')} to {trading_days[-1].strftime('%Y-%m-%d')}")
    print(f"Target win rate: {win_rate*100:.0f}%")
    print(f"Long/Short ratio: {long_ratio*100:.0f}% / {(1-long_ratio)*100:.0f}%")
    print()
    
    for i in range(num_trades):
        # Random trading day
        trade_date = np.random.choice(trading_days)
        
        # Determine win/loss and long/short
        is_winner = np.random.random() < win_rate
        is_long = np.random.random() < long_ratio
        
        # Trade type
        trade_type = np.random.choice(trade_types, p=trade_type_probs)
        
        trade = generate_trade(trade_date, is_winner, is_long, trade_type)
        trades.append(trade)
    
    # Sort by date
    df = pd.DataFrame(trades)
    df['_sort_date'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.sort_values('_sort_date').drop('_sort_date', axis=1).reset_index(drop=True)
    
    return df


def save_outputs(trades: pd.DataFrame, output_dir: str):
    """Save generated data to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save full trade data
    full_file = os.path.join(output_dir, 'extended_stock_trades_full.csv')
    trades.to_csv(full_file, index=False)
    print(f"Saved full trade data to: {full_file}")
    
    # Save Schwab-format (for import)
    schwab_cols = ['Date', 'Action', 'Symbol', 'Description', 'Quantity', 'Price', 'Fees & Comm', 'Amount']
    schwab_file = os.path.join(output_dir, 'extended_stock_trades_schwab.csv')
    trades[schwab_cols].to_csv(schwab_file, index=False)
    print(f"Saved Schwab-format trades to: {schwab_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("TRADE SUMMARY")
    print("="*60)
    
    total_pnl = trades['P&L'].sum()
    winners = trades[trades['P&L'] > 0]
    losers = trades[trades['P&L'] <= 0]
    longs = trades[trades['Side'] == 'LONG']
    shorts = trades[trades['Side'] == 'SHORT']
    
    print(f"Total Trades: {len(trades)}")
    print(f"  Long: {len(longs)} ({len(longs)/len(trades)*100:.1f}%)")
    print(f"  Short: {len(shorts)} ({len(shorts)/len(trades)*100:.1f}%)")
    print()
    print(f"Winners: {len(winners)} ({len(winners)/len(trades)*100:.1f}%)")
    print(f"Losers: {len(losers)} ({len(losers)/len(trades)*100:.1f}%)")
    print()
    print(f"Total P&L: ${total_pnl:,.2f}")
    print(f"Average Win: ${winners['P&L'].mean():,.2f}" if len(winners) > 0 else "No winners")
    print(f"Average Loss: ${losers['P&L'].mean():,.2f}" if len(losers) > 0 else "No losers")
    print(f"Largest Win: ${winners['P&L'].max():,.2f}" if len(winners) > 0 else "N/A")
    print(f"Largest Loss: ${losers['P&L'].min():,.2f}" if len(losers) > 0 else "N/A")
    
    # Breakdown by side
    print("\n" + "-"*40)
    print("LONG TRADES:")
    long_winners = longs[longs['P&L'] > 0]
    print(f"  Win Rate: {len(long_winners)/len(longs)*100:.1f}%")
    print(f"  Total P&L: ${longs['P&L'].sum():,.2f}")
    
    print("\nSHORT TRADES:")
    short_winners = shorts[shorts['P&L'] > 0]
    print(f"  Win Rate: {len(short_winners)/len(shorts)*100:.1f}%")
    print(f"  Total P&L: ${shorts['P&L'].sum():,.2f}")
    
    # Top symbols
    print("\n" + "-"*40)
    print("TOP TRADED SYMBOLS:")
    symbol_stats = trades.groupby('Symbol').agg({
        'P&L': ['count', 'sum']
    }).round(2)
    symbol_stats.columns = ['Trades', 'P&L']
    symbol_stats = symbol_stats.sort_values('Trades', ascending=False).head(10)
    print(symbol_stats.to_string())


def main():
    parser = argparse.ArgumentParser(
        description='Generate realistic stock trade data with long and short positions'
    )
    parser.add_argument('--trades', type=int, default=150,
                        help='Number of trades to generate (default: 150)')
    parser.add_argument('--win-rate', type=float, default=0.53,
                        help='Win rate (default: 0.53)')
    parser.add_argument('--long-ratio', type=float, default=0.65,
                        help='Ratio of long trades (default: 0.65)')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of trading days (default: 30)')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory (default: current directory)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    if args.seed is not None:
        np.random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    
    print("="*60)
    print("EXTENDED STOCK TRADE GENERATOR")
    print("="*60)
    print()
    
    trades = generate_trades(
        num_trades=args.trades,
        win_rate=args.win_rate,
        long_ratio=args.long_ratio,
        num_days=args.days
    )
    
    save_outputs(trades, args.output_dir)
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
