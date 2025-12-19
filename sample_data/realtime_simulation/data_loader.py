"""
Chunked Data Loader for Real-Time Candlestick Simulation

Handles seamless loading and transition between chunked tick data files.
Supports both SQLite database and CSV file sources.

Features:
- Seamless file transitions during playback
- Prefetching for smooth performance
- Memory-efficient streaming
- Session-aware data loading
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Generator, List, Dict, Tuple
from pathlib import Path
import os
from dataclasses import dataclass


@dataclass 
class ChunkInfo:
    """Information about a data chunk."""
    filename: str
    start_timestamp: datetime
    end_timestamp: datetime
    records: int


class TickDataLoader:
    """
    Unified loader for tick data from SQLite or chunked CSV files.
    """
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        csv_dir: Optional[str] = None,
        cache_size: int = 300000  # ~5 minutes of 1-second data
    ):
        """
        Initialize the data loader.
        
        Args:
            db_path: Path to SQLite database
            csv_dir: Path to directory with chunked CSV files
            cache_size: Number of records to keep in memory cache
        """
        self.db_path = db_path
        self.csv_dir = csv_dir
        self.cache_size = cache_size
        
        # Data cache
        self._cache: pd.DataFrame = pd.DataFrame()
        self._cache_start: Optional[datetime] = None
        self._cache_end: Optional[datetime] = None
        
        # Chunk management (for CSV mode)
        self._chunks: List[ChunkInfo] = []
        self._current_chunk_idx: int = 0
        
        # Metadata
        self._data_start: Optional[datetime] = None
        self._data_end: Optional[datetime] = None
        self._total_records: int = 0
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the loader and load metadata."""
        if self.db_path and os.path.exists(self.db_path):
            self._init_sqlite()
        elif self.csv_dir and os.path.exists(self.csv_dir):
            self._init_csv()
        else:
            raise ValueError("Must provide valid db_path or csv_dir")
    
    def _init_sqlite(self):
        """Initialize from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        
        # Get metadata
        try:
            cursor = conn.execute("SELECT value FROM metadata WHERE key='start_timestamp'")
            row = cursor.fetchone()
            if row:
                self._data_start = pd.to_datetime(row[0])
            
            cursor = conn.execute("SELECT value FROM metadata WHERE key='end_timestamp'")
            row = cursor.fetchone()
            if row:
                self._data_end = pd.to_datetime(row[0])
            
            cursor = conn.execute("SELECT value FROM metadata WHERE key='total_records'")
            row = cursor.fetchone()
            if row:
                self._total_records = int(row[0])
        except:
            # Fallback: query the data directly
            cursor = conn.execute("SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM tick_data")
            row = cursor.fetchone()
            if row:
                self._data_start = pd.to_datetime(row[0])
                self._data_end = pd.to_datetime(row[1])
                self._total_records = row[2]
        
        conn.close()
        print(f"SQLite loaded: {self._data_start} to {self._data_end} ({self._total_records:,} records)")
    
    def _init_csv(self):
        """Initialize from chunked CSV directory."""
        manifest_path = os.path.join(self.csv_dir, 'manifest.csv')
        
        if os.path.exists(manifest_path):
            # Load from manifest
            manifest = pd.read_csv(manifest_path)
            for _, row in manifest.iterrows():
                self._chunks.append(ChunkInfo(
                    filename=row['filename'],
                    start_timestamp=pd.to_datetime(row['start_timestamp']),
                    end_timestamp=pd.to_datetime(row['end_timestamp']),
                    records=row['records']
                ))
        else:
            # Scan directory for CSV files
            csv_files = sorted([f for f in os.listdir(self.csv_dir) 
                               if f.startswith('nq_ticks_') and f.endswith('.csv')])
            
            for filename in csv_files:
                filepath = os.path.join(self.csv_dir, filename)
                df = pd.read_csv(filepath, nrows=1)
                df_last = pd.read_csv(filepath).tail(1)
                total_rows = len(pd.read_csv(filepath))
                
                self._chunks.append(ChunkInfo(
                    filename=filename,
                    start_timestamp=pd.to_datetime(df['timestamp'].iloc[0]),
                    end_timestamp=pd.to_datetime(df_last['timestamp'].iloc[0]),
                    records=total_rows
                ))
        
        if self._chunks:
            self._chunks.sort(key=lambda x: x.start_timestamp)
            self._data_start = self._chunks[0].start_timestamp
            self._data_end = self._chunks[-1].end_timestamp
            self._total_records = sum(c.records for c in self._chunks)
        
        print(f"CSV loaded: {len(self._chunks)} chunks, {self._data_start} to {self._data_end}")
    
    @property
    def start_time(self) -> datetime:
        """Get the start timestamp of available data."""
        return self._data_start
    
    @property
    def end_time(self) -> datetime:
        """Get the end timestamp of available data."""
        return self._data_end
    
    @property
    def total_records(self) -> int:
        """Get total number of records."""
        return self._total_records
    
    def get_available_dates(self) -> List[datetime]:
        """Get list of available trading dates."""
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT DISTINCT DATE(timestamp) as date 
                FROM tick_data 
                ORDER BY date
            """)
            dates = [pd.to_datetime(row[0]) for row in cursor.fetchall()]
            conn.close()
            return dates
        else:
            dates = set()
            for chunk in self._chunks:
                dates.add(chunk.start_timestamp.date())
            return sorted([datetime.combine(d, datetime.min.time()) for d in dates])
    
    def _load_cache(self, start: datetime, end: datetime):
        """Load data into cache for the specified time range."""
        if self.db_path:
            self._load_cache_sqlite(start, end)
        else:
            self._load_cache_csv(start, end)
    
    def _load_cache_sqlite(self, start: datetime, end: datetime):
        """Load cache from SQLite database."""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT timestamp, price, bid, ask, spread, volume, session
            FROM tick_data
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
            LIMIT ?
        """
        
        self._cache = pd.read_sql(
            query, conn,
            params=(str(start), str(end), self.cache_size)
        )
        
        conn.close()
        
        if not self._cache.empty:
            self._cache['timestamp'] = pd.to_datetime(self._cache['timestamp'])
            self._cache_start = self._cache['timestamp'].min()
            self._cache_end = self._cache['timestamp'].max()
    
    def _load_cache_csv(self, start: datetime, end: datetime):
        """Load cache from chunked CSV files."""
        # Find chunks that overlap with the time range
        relevant_chunks = []
        for chunk in self._chunks:
            if chunk.start_timestamp <= end and chunk.end_timestamp >= start:
                relevant_chunks.append(chunk)
        
        if not relevant_chunks:
            self._cache = pd.DataFrame()
            return
        
        # Load and concatenate relevant chunks
        dfs = []
        for chunk in relevant_chunks:
            filepath = os.path.join(self.csv_dir, chunk.filename)
            df = pd.read_csv(filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter to time range
            df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
            dfs.append(df)
        
        if dfs:
            self._cache = pd.concat(dfs, ignore_index=True)
            self._cache = self._cache.sort_values('timestamp').head(self.cache_size)
            self._cache_start = self._cache['timestamp'].min()
            self._cache_end = self._cache['timestamp'].max()
        else:
            self._cache = pd.DataFrame()
    
    def get_tick_at(self, timestamp: datetime) -> Optional[Dict]:
        """Get the tick data at a specific timestamp."""
        # Check if we need to reload cache
        if self._cache.empty or timestamp < self._cache_start or timestamp > self._cache_end:
            # Load cache centered around the requested timestamp
            buffer = timedelta(minutes=30)
            self._load_cache(timestamp - buffer, timestamp + timedelta(hours=2))
        
        if self._cache.empty:
            return None
        
        # Find the tick at or before the timestamp
        mask = self._cache['timestamp'] <= timestamp
        if not mask.any():
            return None
        
        row = self._cache[mask].iloc[-1]
        return row.to_dict()
    
    def get_ticks_range(
        self, 
        start: datetime, 
        end: datetime,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Get tick data for a time range."""
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT timestamp, price, bid, ask, spread, volume, session
                FROM tick_data
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp
            """
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql(query, conn, params=(str(start), str(end)))
            conn.close()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            # Use CSV loading
            self._load_cache(start, end)
            df = self._cache[
                (self._cache['timestamp'] >= start) & 
                (self._cache['timestamp'] <= end)
            ].copy()
            if limit:
                df = df.head(limit)
            return df
    
    def get_ohlc(
        self, 
        start: datetime, 
        end: datetime, 
        timeframe: str = '1m'
    ) -> pd.DataFrame:
        """
        Get OHLC data for a time range and timeframe.
        
        Args:
            start: Start timestamp
            end: End timestamp
            timeframe: '1s', '1m', or '5m'
        
        Returns:
            DataFrame with OHLC data
        """
        if self.db_path:
            # Try to use pre-aggregated tables
            table_map = {'1s': 'ohlc_1s', '1m': 'ohlc_1m', '5m': 'ohlc_5m'}
            table = table_map.get(timeframe)
            
            if table:
                conn = sqlite3.connect(self.db_path)
                try:
                    df = pd.read_sql(f"""
                        SELECT * FROM {table}
                        WHERE timestamp >= ? AND timestamp <= ?
                        ORDER BY timestamp
                    """, conn, params=(str(start), str(end)))
                    conn.close()
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    return df
                except:
                    conn.close()
        
        # Fallback: aggregate from tick data
        ticks = self.get_ticks_range(start, end)
        if ticks.empty:
            return pd.DataFrame()
        
        ticks.set_index('timestamp', inplace=True)
        
        freq_map = {'1s': '1s', '1m': '1min', '5m': '5min'}
        freq = freq_map.get(timeframe, '1min')
        
        ohlc = ticks.resample(freq).agg({
            'price': ['first', 'max', 'min', 'last'],
            'volume': 'sum'
        }).dropna()
        
        ohlc.columns = ['open', 'high', 'low', 'close', 'volume']
        ohlc = ohlc.reset_index()
        
        return ohlc
    
    def stream_ticks(
        self, 
        start: datetime,
        end: Optional[datetime] = None,
        batch_size: int = 1
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Stream tick data from start to end.
        
        Args:
            start: Start timestamp
            end: End timestamp (defaults to data end)
            batch_size: Number of ticks per batch
        
        Yields:
            DataFrame with batch_size rows
        """
        if end is None:
            end = self._data_end
        
        current = start
        buffer_duration = timedelta(minutes=60)
        
        while current < end:
            # Load a buffer
            buffer_end = min(current + buffer_duration, end)
            self._load_cache(current, buffer_end)
            
            if self._cache.empty:
                break
            
            # Yield batches
            for i in range(0, len(self._cache), batch_size):
                batch = self._cache.iloc[i:i + batch_size]
                if batch['timestamp'].max() > end:
                    batch = batch[batch['timestamp'] <= end]
                    if not batch.empty:
                        yield batch
                    return
                yield batch
                current = batch['timestamp'].max() + timedelta(seconds=1)
            
            # Move to next buffer
            current = self._cache_end + timedelta(seconds=1)
    
    def get_session_boundaries(self, date: datetime) -> Dict[str, Tuple[datetime, datetime]]:
        """Get session start/end times for a given date."""
        from datetime import time
        
        sessions = {
            'premarket': (time(4, 0), time(9, 30)),
            'rth': (time(9, 30), time(16, 0)),
            'afterhours': (time(16, 0), time(20, 0))
        }
        
        result = {}
        for name, (start_time, end_time) in sessions.items():
            result[name] = (
                datetime.combine(date.date(), start_time),
                datetime.combine(date.date(), end_time)
            )
        
        return result


class OHLCBuilder:
    """
    Builds OHLC candles in real-time from streaming tick data.
    Handles the "growing candle" visualization requirement.
    """
    
    def __init__(self, timeframe: str = '1m'):
        """
        Initialize the OHLC builder.
        
        Args:
            timeframe: Candle timeframe ('1s', '1m', '5m')
        """
        self.timeframe = timeframe
        self._timeframe_seconds = self._parse_timeframe(timeframe)
        
        # Current candle being built
        self._current_candle: Optional[Dict] = None
        self._current_candle_start: Optional[datetime] = None
        
        # Completed candles
        self._completed_candles: List[Dict] = []
        self._max_candles = 500  # Keep last 500 candles in memory
    
    def _parse_timeframe(self, tf: str) -> int:
        """Convert timeframe string to seconds."""
        if tf.endswith('s'):
            return int(tf[:-1])
        elif tf.endswith('m'):
            return int(tf[:-1]) * 60
        elif tf.endswith('h'):
            return int(tf[:-1]) * 3600
        return 60  # Default 1 minute
    
    def _get_candle_start(self, timestamp: datetime) -> datetime:
        """Get the candle start time for a given timestamp."""
        seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
        candle_seconds = (seconds // self._timeframe_seconds) * self._timeframe_seconds
        
        hours = candle_seconds // 3600
        minutes = (candle_seconds % 3600) // 60
        secs = candle_seconds % 60
        
        return timestamp.replace(hour=hours, minute=minutes, second=secs, microsecond=0)
    
    def add_tick(self, tick: Dict) -> Tuple[Optional[Dict], Dict]:
        """
        Add a tick and update the current candle.
        
        Args:
            tick: Dict with timestamp, price, volume
        
        Returns:
            Tuple of (completed_candle or None, current_candle)
        """
        timestamp = tick['timestamp']
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        price = tick['price']
        volume = tick.get('volume', 0)
        
        candle_start = self._get_candle_start(timestamp)
        completed_candle = None
        
        # Check if we need to start a new candle
        if self._current_candle is None or candle_start > self._current_candle_start:
            # Complete the current candle if it exists
            if self._current_candle is not None:
                completed_candle = self._current_candle.copy()
                self._completed_candles.append(completed_candle)
                
                # Trim old candles
                if len(self._completed_candles) > self._max_candles:
                    self._completed_candles = self._completed_candles[-self._max_candles:]
            
            # Start new candle
            self._current_candle_start = candle_start
            self._current_candle = {
                'timestamp': candle_start,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': volume,
                'tick_count': 1
            }
        else:
            # Update current candle
            self._current_candle['high'] = max(self._current_candle['high'], price)
            self._current_candle['low'] = min(self._current_candle['low'], price)
            self._current_candle['close'] = price
            self._current_candle['volume'] += volume
            self._current_candle['tick_count'] += 1
        
        return completed_candle, self._current_candle
    
    def get_candles(self, include_current: bool = True) -> pd.DataFrame:
        """Get all candles as a DataFrame."""
        candles = self._completed_candles.copy()
        if include_current and self._current_candle:
            candles.append(self._current_candle)
        
        if not candles:
            return pd.DataFrame()
        
        return pd.DataFrame(candles)
    
    def reset(self):
        """Reset the builder."""
        self._current_candle = None
        self._current_candle_start = None
        self._completed_candles = []


if __name__ == '__main__':
    # Test the loader
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = 'nq_tick_simulation.db'
    
    if os.path.exists(db_path):
        loader = TickDataLoader(db_path=db_path)
        
        print(f"\nData range: {loader.start_time} to {loader.end_time}")
        print(f"Total records: {loader.total_records:,}")
        
        # Get available dates
        dates = loader.get_available_dates()
        print(f"Available dates: {len(dates)}")
        
        if dates:
            # Test getting ticks
            start = dates[0]
            end = start + timedelta(minutes=5)
            ticks = loader.get_ticks_range(start, end)
            print(f"\nSample ticks ({start} to {end}):")
            print(ticks.head(10))
            
            # Test OHLC builder
            print("\nTesting OHLC Builder:")
            builder = OHLCBuilder(timeframe='1m')
            
            for _, tick in ticks.iterrows():
                completed, current = builder.add_tick(tick.to_dict())
                if completed:
                    print(f"  Completed candle: {completed}")
            
            candles = builder.get_candles()
            print(f"\nBuilt {len(candles)} candles:")
            print(candles)
    else:
        print(f"Database not found: {db_path}")
        print("Run generate_tick_data.py first to create test data")
