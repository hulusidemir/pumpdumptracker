"""
Bybit API Client for Perpetual Futures Data
Fetches real-time market data, order book, funding rates, and open interest
"""

import requests
import time
import hmac
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BybitClient:
    """
    Professional Bybit API client for fetching perpetual futures data
    """
    
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PumpDetectorBot/1.0'
        })
        
        # Cache for rate limiting
        self.last_request_time = {}
        self.min_request_interval = 0.1  # 100ms between requests
    
    def _rate_limit(self, endpoint: str):
        """Simple rate limiting"""
        now = time.time()
        if endpoint in self.last_request_time:
            elapsed = now - self.last_request_time[endpoint]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time[endpoint] = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            self._rate_limit(endpoint)
            url = f"{self.base_url}{endpoint}"
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('retCode') == 0:
                return data.get('result', {})
            else:
                logger.error(f"Bybit API error: {data.get('retMsg')}")
                return None
                
        except Exception as e:
            logger.error(f"Request error for {endpoint}: {e}")
            return None
    
    def get_all_usdt_perpetuals(self) -> List[str]:
        """
        Get all USDT perpetual futures symbols
        Focus on liquid pairs only
        """
        try:
            endpoint = "/v5/market/tickers"
            params = {
                'category': 'linear'  # USDT perpetuals
            }
            
            result = self._make_request(endpoint, params)
            if not result:
                return []
            
            symbols = []
            for ticker in result.get('list', []):
                symbol = ticker.get('symbol', '')
                # Only USDT pairs
                if symbol.endswith('USDT'):
                    # Filter out low volume pairs
                    volume_24h = float(ticker.get('turnover24h', 0))
                    if volume_24h > 100000:  # Min $100k daily volume
                        symbols.append(symbol)
            
            logger.info(f"Found {len(symbols)} liquid USDT perpetual pairs")
            return symbols
            
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []
    
    def get_ticker_data(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time ticker data for a symbol
        """
        endpoint = "/v5/market/tickers"
        params = {
            'category': 'linear',
            'symbol': symbol
        }
        
        result = self._make_request(endpoint, params)
        if not result or not result.get('list'):
            return None
        
        ticker = result['list'][0]
        
        return {
            'symbol': symbol,
            'price': float(ticker.get('lastPrice', 0)),
            'volume_24h': float(ticker.get('turnover24h', 0)),
            'price_change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
            'high_24h': float(ticker.get('highPrice24h', 0)),
            'low_24h': float(ticker.get('lowPrice24h', 0)),
            'bid': float(ticker.get('bid1Price', 0)),
            'ask': float(ticker.get('ask1Price', 0)),
            'funding_rate': float(ticker.get('fundingRate', 0)),
            'open_interest': float(ticker.get('openInterest', 0)),
            'open_interest_value': float(ticker.get('openInterestValue', 0)),
        }
    
    def get_klines(self, symbol: str, interval: str, limit: int = 200) -> List[Dict]:
        """
        Get historical klines for technical analysis
        interval: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M
        """
        endpoint = "/v5/market/kline"
        params = {
            'category': 'linear',
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        result = self._make_request(endpoint, params)
        if not result or not result.get('list'):
            return []
        
        klines = []
        for k in result['list']:
            klines.append({
                'timestamp': int(k[0]),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5]),
                'turnover': float(k[6])
            })
        
        # Sort by timestamp ascending
        klines.sort(key=lambda x: x['timestamp'])
        return klines
    
    def get_orderbook(self, symbol: str, limit: int = 50) -> Optional[Dict]:
        """
        Get order book data for buy/sell pressure analysis
        """
        endpoint = "/v5/market/orderbook"
        params = {
            'category': 'linear',
            'symbol': symbol,
            'limit': limit
        }
        
        result = self._make_request(endpoint, params)
        if not result:
            return None
        
        bids = result.get('b', [])
        asks = result.get('a', [])
        
        # Calculate volumes
        bid_volume = sum(float(price) * float(qty) for price, qty in bids)
        ask_volume = sum(float(price) * float(qty) for price, qty in asks)
        
        # Find large orders (top 20%)
        all_orders = [(float(p), float(q)) for p, q in bids + asks]
        if all_orders:
            order_sizes = [p * q for p, q in all_orders]
            threshold = sorted(order_sizes, reverse=True)[min(10, len(order_sizes)-1)]
            
            large_bids = sum(float(p) * float(q) for p, q in bids if float(p) * float(q) >= threshold)
            large_asks = sum(float(p) * float(q) for p, q in asks if float(p) * float(q) >= threshold)
        else:
            large_bids = large_asks = 0
        
        return {
            'symbol': symbol,
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'large_bids': large_bids,
            'large_asks': large_asks,
            'bid_levels': len(bids),
            'ask_levels': len(asks),
            'spread': (float(asks[0][0]) - float(bids[0][0])) / float(bids[0][0]) * 100 if bids and asks else 0
        }
    
    def get_funding_rate_history(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get funding rate history
        """
        endpoint = "/v5/market/funding/history"
        params = {
            'category': 'linear',
            'symbol': symbol,
            'limit': limit
        }
        
        result = self._make_request(endpoint, params)
        if not result or not result.get('list'):
            return []
        
        history = []
        for item in result['list']:
            history.append({
                'timestamp': int(item.get('fundingRateTimestamp', 0)),
                'rate': float(item.get('fundingRate', 0))
            })
        
        return history
    
    def get_open_interest_history(self, symbol: str, interval: str = "5min", limit: int = 50) -> List[Dict]:
        """
        Get open interest history for trend analysis
        interval: 5min, 15min, 30min, 1h, 4h, 1d
        """
        endpoint = "/v5/market/open-interest"
        params = {
            'category': 'linear',
            'symbol': symbol,
            'intervalTime': interval,
            'limit': limit
        }
        
        result = self._make_request(endpoint, params)
        if not result or not result.get('list'):
            return []
        
        history = []
        for item in result['list']:
            history.append({
                'timestamp': int(item.get('timestamp', 0)),
                'open_interest': float(item.get('openInterest', 0)),
                'open_interest_value': float(item.get('openInterestValue', 0))
            })
        
        return history
    
    def get_long_short_ratio(self, symbol: str, period: str = "5min", limit: int = 20) -> Optional[Dict]:
        """
        Get long/short account ratio - retail sentiment
        period: 5min, 15min, 30min, 1h, 4h, 1d
        """
        endpoint = "/v5/market/account-ratio"
        params = {
            'category': 'linear',
            'symbol': symbol,
            'period': period,
            'limit': limit
        }
        
        result = self._make_request(endpoint, params)
        if not result or not result.get('list'):
            return None
        
        # Get latest data
        latest = result['list'][0] if result['list'] else None
        if not latest:
            return None
        
        buy_ratio = float(latest.get('buyRatio', 0))
        sell_ratio = float(latest.get('sellRatio', 0))
        
        return {
            'symbol': symbol,
            'long_ratio': buy_ratio,
            'short_ratio': sell_ratio,
            'timestamp': int(latest.get('timestamp', 0)),
            'sentiment': 'BULLISH' if buy_ratio > sell_ratio else 'BEARISH'
        }
    
    def get_taker_buy_sell_ratio(self, symbol: str, period: str = "5min", limit: int = 20) -> Optional[Dict]:
        """
        Get taker buy/sell volume ratio - shows aggressive buying/selling
        This is similar to CVD (Cumulative Volume Delta)
        """
        # Use recent klines to calculate taker buy/sell
        klines = self.get_klines(symbol, '1', limit=60)
        if not klines:
            return None
        
        # Calculate taker buy volume from recent trades
        # Approximation: if close > open, it's mostly buy pressure
        total_volume = sum(k['volume'] for k in klines)
        buy_volume = sum(k['volume'] for k in klines if k['close'] > k['open'])
        sell_volume = total_volume - buy_volume
        
        buy_ratio = (buy_volume / total_volume * 100) if total_volume > 0 else 50
        sell_ratio = 100 - buy_ratio
        
        return {
            'symbol': symbol,
            'taker_buy_ratio': buy_ratio,
            'taker_sell_ratio': sell_ratio,
            'taker_buy_volume': buy_volume,
            'taker_sell_volume': sell_volume,
            'pressure': 'BUY' if buy_ratio > 55 else 'SELL' if buy_ratio < 45 else 'NEUTRAL'
        }
    
    def get_liquidations_estimate(self, symbol: str) -> Optional[Dict]:
        """
        Estimate liquidation zones using order book and OI data
        Note: Bybit doesn't provide direct liquidation data via public API
        We estimate based on open interest and price levels
        """
        try:
            ticker = self.get_ticker_data(symbol)
            orderbook = self.get_orderbook(symbol, limit=100)
            
            if not ticker or not orderbook:
                return None
            
            current_price = ticker['price']
            oi_value = ticker['open_interest_value']
            
            # Estimate liquidation zones (simplified)
            # Long liquidations typically 2-5% below current price
            # Short liquidations typically 2-5% above current price
            
            long_liq_price = current_price * 0.97  # -3% for leveraged longs
            short_liq_price = current_price * 1.03  # +3% for leveraged shorts
            
            # Estimate liquidation amounts (rough approximation)
            estimated_long_liq = oi_value * 0.3  # Assume 30% are longs near liquidation
            estimated_short_liq = oi_value * 0.3  # Assume 30% are shorts near liquidation
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'long_liquidation_price': long_liq_price,
                'short_liquidation_price': short_liq_price,
                'estimated_long_liq_volume': estimated_long_liq,
                'estimated_short_liq_volume': estimated_short_liq,
                'warning': 'Estimated values - not exact liquidation data'
            }
            
        except Exception as e:
            logger.error(f"Error estimating liquidations for {symbol}: {e}")
            return None
    
    def get_comprehensive_data(self, symbol: str) -> Optional[Dict]:
        """
        Get all data needed for pump detection in one call
        This is the main function used by the detector
        """
        try:
            # 1. Current ticker
            ticker = self.get_ticker_data(symbol)
            if not ticker:
                return None
            
            # 2. Multi-timeframe klines
            klines_1m = self.get_klines(symbol, '1', limit=60)
            klines_5m = self.get_klines(symbol, '5', limit=50)
            klines_15m = self.get_klines(symbol, '15', limit=30)
            
            if not klines_1m:
                return None
            
            # Calculate price changes
            current_price = ticker['price']
            
            price_5m_ago = klines_1m[-5]['close'] if len(klines_1m) >= 5 else current_price
            price_15m_ago = klines_5m[-3]['close'] if len(klines_5m) >= 3 else current_price
            price_1h_ago = klines_5m[-12]['close'] if len(klines_5m) >= 12 else current_price
            
            price_change_5m = ((current_price - price_5m_ago) / price_5m_ago * 100) if price_5m_ago > 0 else 0
            price_change_15m = ((current_price - price_15m_ago) / price_15m_ago * 100) if price_15m_ago > 0 else 0
            price_change_1h = ((current_price - price_1h_ago) / price_1h_ago * 100) if price_1h_ago > 0 else 0
            
            # 3. Volume analysis
            recent_volumes = [k['volume'] for k in klines_5m[-12:]]
            avg_volume = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0
            current_volume = klines_5m[-1]['volume'] if klines_5m else 0
            volume_1h_ago = klines_5m[-12]['volume'] if len(klines_5m) >= 12 else current_volume
            
            # 4. Order book
            orderbook = self.get_orderbook(symbol)
            
            # 5. Funding rate
            funding_history = self.get_funding_rate_history(symbol, limit=5)
            funding_rate_current = ticker['funding_rate']
            funding_rate_avg = sum(f['rate'] for f in funding_history) / len(funding_history) if funding_history else funding_rate_current
            funding_rate_change = funding_rate_current - funding_history[-2]['rate'] if len(funding_history) >= 2 else 0
            
            # 6. Open interest
            oi_history = self.get_open_interest_history(symbol, interval='5min', limit=20)
            oi_current = ticker['open_interest_value']
            oi_1h_ago = oi_history[-12]['open_interest_value'] if len(oi_history) >= 12 else oi_current
            oi_change_pct = ((oi_current - oi_1h_ago) / oi_1h_ago * 100) if oi_1h_ago > 0 else 0
            oi_volume_ratio = oi_current / ticker['volume_24h'] if ticker['volume_24h'] > 0 else 0
            
            # 7. Long/Short Ratio
            long_short_data = self.get_long_short_ratio(symbol)
            
            # 8. Taker Buy/Sell Ratio
            taker_data = self.get_taker_buy_sell_ratio(symbol)
            
            # 9. Liquidation Estimates
            liquidation_data = self.get_liquidations_estimate(symbol)
            
            # Prepare comprehensive data structure
            data = {
                'symbol': symbol,
                'price': current_price,
                'volume_24h': ticker['volume_24h'],
                'price_change_5m': price_change_5m,
                'price_change_15m': price_change_15m,
                'price_change_1h': price_change_1h,
                'price_change_24h': ticker['price_change_24h'],
                'volume_current': current_volume,
                'volume_avg': avg_volume,
                'volume_1h_ago': volume_1h_ago,
                'bid_volume': orderbook['bid_volume'] if orderbook else 0,
                'ask_volume': orderbook['ask_volume'] if orderbook else 0,
                'large_bids': orderbook['large_bids'] if orderbook else 0,
                'large_asks': orderbook['large_asks'] if orderbook else 0,
                'funding_rate': funding_rate_current,
                'funding_rate_avg': funding_rate_avg,
                'funding_rate_change': funding_rate_change,
                'open_interest': ticker['open_interest'],
                'open_interest_value': oi_current,
                'oi_change_pct': oi_change_pct,
                'oi_volume_ratio': oi_volume_ratio,
                'prices_history': [k['close'] for k in klines_5m],
                'volumes_history': [k['volume'] for k in klines_5m],
                # New advanced metrics
                'long_ratio': long_short_data['long_ratio'] if long_short_data else 50,
                'short_ratio': long_short_data['short_ratio'] if long_short_data else 50,
                'sentiment': long_short_data['sentiment'] if long_short_data else 'NEUTRAL',
                'taker_buy_ratio': taker_data['taker_buy_ratio'] if taker_data else 50,
                'taker_sell_ratio': taker_data['taker_sell_ratio'] if taker_data else 50,
                'taker_pressure': taker_data['pressure'] if taker_data else 'NEUTRAL',
                'long_liq_price': liquidation_data['long_liquidation_price'] if liquidation_data else 0,
                'short_liq_price': liquidation_data['short_liquidation_price'] if liquidation_data else 0,
                'est_long_liq_volume': liquidation_data['estimated_long_liq_volume'] if liquidation_data else 0,
                'est_short_liq_volume': liquidation_data['estimated_short_liq_volume'] if liquidation_data else 0,
                'timestamp': datetime.now()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive data for {symbol}: {e}")
            return None
    
    def batch_get_tickers(self, symbols: List[str], max_workers: int = 5) -> List[Dict]:
        """
        Get ticker data for multiple symbols
        Returns basic screening data for initial filter
        """
        results = []
        
        for symbol in symbols:
            ticker = self.get_ticker_data(symbol)
            if ticker:
                results.append(ticker)
            time.sleep(0.05)  # Small delay to avoid rate limits
        
        return results
