"""
Market Scanner - Continuously scans all USDT perpetuals for pump signals
Uses multi-stage filtering to efficiently process hundreds of coins
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

from bybit_client import BybitClient
from pump_detector import PumpDetector, PumpSignal

logger = logging.getLogger(__name__)


class MarketScanner:
    """
    Professional market scanner that monitors all USDT perpetuals
    Uses intelligent filtering to focus on most promising coins
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.bybit = BybitClient(
            api_key=config.get('bybit_api_key', ''),
            api_secret=config.get('bybit_api_secret', ''),
            testnet=config.get('testnet', False)
        )
        self.detector = PumpDetector(config)
        
        # Scanning parameters
        self.scan_interval = config.get('scan_interval', 60)  # seconds
        self.max_workers = config.get('max_workers', 10)
        
        # Filtering thresholds for quick pre-screening
        self.filter_thresholds = {
            'min_volume_24h': config.get('min_volume_24h', 500000),  # $500k
            'min_price_change_5m': config.get('min_price_change_5m', 1.0),  # 1%
            'max_price': config.get('max_price', 100000),  # Filter out extremely high price coins
        }
        
        # Track symbols and their last scan
        self.all_symbols = []
        self.last_symbol_refresh = None
        self.symbol_refresh_interval = 3600  # Refresh symbol list every hour
        
        # Watchlist for hot coins
        self.watchlist = {}  # {symbol: last_signal_time}
        self.watchlist_timeout = 1800  # Keep in watchlist for 30 minutes
        
        # Results queue
        self.signal_queue = queue.Queue()
    
    def refresh_symbols(self):
        """Refresh the list of tradeable symbols"""
        logger.info("Refreshing symbol list from Bybit...")
        symbols = self.bybit.get_all_usdt_perpetuals()
        
        if symbols:
            self.all_symbols = symbols
            self.last_symbol_refresh = datetime.now()
            logger.info(f"Symbol list refreshed: {len(symbols)} symbols")
        else:
            logger.warning("Failed to refresh symbol list, using cached list")
    
    def quick_filter(self, tickers: List[Dict]) -> List[str]:
        """
        Quick filter to reduce symbols to scan in depth
        Only process coins showing early signs of movement
        STRICTER: Higher thresholds for elite signals only
        """
        filtered = []
        
        for ticker in tickers:
            try:
                symbol = ticker['symbol']
                volume_24h = ticker.get('volume_24h', 0)
                price = ticker.get('price', 0)
                price_change_24h = ticker.get('price_change_24h', 0)
                
                # Basic filters (STRICTER)
                if volume_24h < self.filter_thresholds['min_volume_24h']:
                    continue
                
                if price > self.filter_thresholds['max_price']:
                    continue
                
                # Look for stronger signs of movement (STRICTER)
                if abs(price_change_24h) > 8.0:  # 8% move in 24h (was 5%)
                    filtered.append(symbol)
                    continue
                
                # High volume with moderate movement
                if volume_24h > self.filter_thresholds['min_volume_24h'] * 2 and abs(price_change_24h) > 3.0:
                    filtered.append(symbol)
                    continue
                
                # Check if in watchlist
                if symbol in self.watchlist:
                    filtered.append(symbol)
                    continue
                
            except Exception as e:
                logger.error(f"Error filtering {ticker.get('symbol')}: {e}")
                continue
        
        logger.info(f"Quick filter: {len(filtered)}/{len(tickers)} symbols passed")
        return filtered
    
    def scan_symbol(self, symbol: str) -> Optional[PumpSignal]:
        """
        Deep scan a single symbol for pump signals
        """
        try:
            # Get comprehensive data
            coin_data = self.bybit.get_comprehensive_data(symbol)
            if not coin_data:
                return None
            
            # Analyze for pump signals
            pump_signal = self.detector.analyze_coin(coin_data)
            
            if pump_signal:
                logger.info(f"🎯 PUMP SIGNAL: {symbol} - Score: {pump_signal.score:.1f} ({pump_signal.confidence})")
                
                # Add to watchlist
                self.watchlist[symbol] = datetime.now()
            
            return pump_signal
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return None
    
    def scan_symbols_batch(self, symbols: List[str]) -> List[PumpSignal]:
        """
        Scan multiple symbols in parallel
        """
        signals = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.scan_symbol, symbol): symbol 
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                try:
                    signal = future.result(timeout=30)
                    if signal:
                        signals.append(signal)
                except Exception as e:
                    symbol = future_to_symbol[future]
                    logger.error(f"Error processing {symbol}: {e}")
        
        return signals
    
    def clean_watchlist(self):
        """Remove old entries from watchlist"""
        now = datetime.now()
        to_remove = []
        
        for symbol, last_time in self.watchlist.items():
            if (now - last_time).total_seconds() > self.watchlist_timeout:
                to_remove.append(symbol)
        
        for symbol in to_remove:
            del self.watchlist[symbol]
        
        if to_remove:
            logger.info(f"Cleaned {len(to_remove)} symbols from watchlist")
    
    def scan_market(self) -> List[PumpSignal]:
        """
        Full market scan - main scanning function
        """
        try:
            # Refresh symbol list if needed
            if (not self.last_symbol_refresh or 
                (datetime.now() - self.last_symbol_refresh).total_seconds() > self.symbol_refresh_interval):
                self.refresh_symbols()
            
            if not self.all_symbols:
                logger.error("No symbols available to scan")
                return []
            
            logger.info(f"Starting market scan of {len(self.all_symbols)} symbols...")
            scan_start = time.time()
            
            # Stage 1: Get all tickers for quick filtering
            logger.info("Stage 1: Fetching all tickers...")
            all_tickers = self.bybit.batch_get_tickers(self.all_symbols)
            
            # Stage 2: Quick filter
            logger.info("Stage 2: Quick filtering...")
            filtered_symbols = self.quick_filter(all_tickers)
            
            if not filtered_symbols:
                logger.info("No symbols passed quick filter")
                return []
            
            # Stage 3: Deep analysis
            logger.info(f"Stage 3: Deep analysis of {len(filtered_symbols)} symbols...")
            pump_signals = self.scan_symbols_batch(filtered_symbols)
            
            # Rank signals
            if pump_signals:
                pump_signals = self.detector.rank_signals(pump_signals)
            
            # Clean watchlist
            self.clean_watchlist()
            
            scan_duration = time.time() - scan_start
            logger.info(f"Market scan completed in {scan_duration:.1f}s - Found {len(pump_signals)} signals")
            
            return pump_signals
            
        except Exception as e:
            logger.error(f"Error in market scan: {e}")
            return []
    
    def run_continuous_scan(self, callback=None):
        """
        Run continuous market scanning
        callback: function to call with pump signals
        """
        logger.info(f"Starting continuous market scanner (interval: {self.scan_interval}s)")
        
        scan_count = 0
        
        while True:
            try:
                scan_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"SCAN #{scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*60}")
                
                # Run scan
                pump_signals = self.scan_market()
                
                # Process signals
                if pump_signals:
                    logger.info(f"\n🚀 Found {len(pump_signals)} pump signals:")
                    for i, signal in enumerate(pump_signals[:10], 1):  # Top 10
                        logger.info(f"{i}. {signal.coin} - Score: {signal.score:.1f} - "
                                  f"5m: {signal.price_change_5m:+.2f}% - "
                                  f"1h: {signal.price_change_1h:+.2f}%")
                    
                    # Call callback if provided
                    if callback:
                        try:
                            callback(pump_signals)
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
                else:
                    logger.info("No pump signals detected this scan")
                
                # Wait for next scan
                logger.info(f"\nWaiting {self.scan_interval}s until next scan...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("\nScanner stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous scan: {e}")
                logger.info(f"Retrying in {self.scan_interval}s...")
                time.sleep(self.scan_interval)
    
    def get_top_movers(self, limit: int = 20) -> List[Dict]:
        """
        Quick scan to get top moving coins
        Useful for quick overview
        """
        try:
            all_tickers = self.bybit.batch_get_tickers(self.all_symbols[:100])  # Scan top 100
            
            # Sort by 24h change
            all_tickers.sort(key=lambda x: abs(x.get('price_change_24h', 0)), reverse=True)
            
            return all_tickers[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top movers: {e}")
            return []
