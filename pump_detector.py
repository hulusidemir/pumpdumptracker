"""
Professional Crypto Pump Detector - Core Engine
Detects coins that are about to pump using multiple signal confluence
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class MarketSignal:
    """Represents a single market signal"""
    coin: str
    signal_type: str
    strength: float  # 0-100
    timestamp: datetime
    details: Dict


@dataclass
class PumpSignal:
    """Complete pump signal with all analysis"""
    coin: str
    score: float  # 0-100
    confidence: str  # LOW, MEDIUM, HIGH, VERY_HIGH
    timeframe: str
    signals: List[MarketSignal]
    price: float
    volume_24h: float
    price_change_1h: float
    price_change_5m: float
    timestamp: datetime
    
    def to_dict(self):
        return {
            'coin': self.coin,
            'score': round(self.score, 2),
            'confidence': self.confidence,
            'timeframe': self.timeframe,
            'price': self.price,
            'volume_24h': self.volume_24h,
            'price_change_1h': round(self.price_change_1h, 2),
            'price_change_5m': round(self.price_change_5m, 2),
            'signals_count': len(self.signals),
            'timestamp': self.timestamp.isoformat()
        }


class PumpDetector:
    """
    Professional pump detection engine using multiple signal confluence
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_score = config.get('min_score', 65)
        self.signals_history = {}  # Track signals over time
        
        # Critical thresholds for pump detection
        self.thresholds = {
            'volume_spike_multiplier': 3.0,  # 3x normal volume
            'volume_extreme_multiplier': 5.0,  # 5x for extreme
            'price_momentum_5m': 2.0,  # 2% in 5 minutes
            'price_momentum_15m': 5.0,  # 5% in 15 minutes
            'order_book_imbalance': 2.0,  # 2:1 buy/sell ratio
            'order_book_extreme': 3.5,  # 3.5:1 for extreme
            'large_order_threshold': 100000,  # $100k orders
            'funding_rate_spike': 0.05,  # 0.05% sudden change
            'open_interest_change': 15.0,  # 15% OI increase
            'rsi_oversold': 30,
            'rsi_overbought': 70,
        }
    
    def analyze_volume_spike(self, current_volume: float, avg_volume: float, 
                            volume_1h_ago: float) -> Optional[MarketSignal]:
        """
        Detect volume spikes - one of the strongest pump indicators
        """
        if avg_volume == 0:
            return None
        
        volume_ratio = current_volume / avg_volume
        volume_acceleration = current_volume / max(volume_1h_ago, 1)
        
        strength = 0
        signal_type = ""
        
        if volume_ratio >= self.thresholds['volume_extreme_multiplier']:
            strength = 95
            signal_type = "EXTREME_VOLUME_SPIKE"
        elif volume_ratio >= self.thresholds['volume_spike_multiplier']:
            strength = 75
            signal_type = "VOLUME_SPIKE"
        elif volume_ratio >= 2.0:
            strength = 50
            signal_type = "ELEVATED_VOLUME"
        else:
            return None
        
        # Bonus for volume acceleration
        if volume_acceleration > 2.0:
            strength = min(100, strength + 10)
        
        return MarketSignal(
            coin="",
            signal_type=signal_type,
            strength=strength,
            timestamp=datetime.now(),
            details={
                'volume_ratio': round(volume_ratio, 2),
                'volume_acceleration': round(volume_acceleration, 2),
                'current_volume': current_volume,
                'avg_volume': avg_volume
            }
        )
    
    def analyze_price_momentum(self, price_changes: Dict[str, float]) -> List[MarketSignal]:
        """
        Analyze price momentum across multiple timeframes
        Strong momentum = early pump signal
        """
        signals = []
        
        # 5-minute momentum
        change_5m = price_changes.get('5m', 0)
        if abs(change_5m) >= self.thresholds['price_momentum_5m']:
            strength = min(100, abs(change_5m) * 15)  # Scale to 0-100
            signals.append(MarketSignal(
                coin="",
                signal_type="STRONG_5M_MOMENTUM",
                strength=strength,
                timestamp=datetime.now(),
                details={'change_5m': round(change_5m, 2)}
            ))
        
        # 15-minute momentum
        change_15m = price_changes.get('15m', 0)
        if abs(change_15m) >= self.thresholds['price_momentum_15m']:
            strength = min(100, abs(change_15m) * 8)
            signals.append(MarketSignal(
                coin="",
                signal_type="STRONG_15M_MOMENTUM",
                strength=strength,
                timestamp=datetime.now(),
                details={'change_15m': round(change_15m, 2)}
            ))
        
        # 1-hour momentum
        change_1h = price_changes.get('1h', 0)
        if abs(change_1h) >= 8.0:
            strength = min(100, abs(change_1h) * 5)
            signals.append(MarketSignal(
                coin="",
                signal_type="STRONG_1H_MOMENTUM",
                strength=strength,
                timestamp=datetime.now(),
                details={'change_1h': round(change_1h, 2)}
            ))
        
        # Momentum acceleration - very bullish
        if change_5m > 0 and change_15m > 0 and change_1h > 0:
            if change_5m / 5 > change_15m / 15:  # Accelerating
                signals.append(MarketSignal(
                    coin="",
                    signal_type="MOMENTUM_ACCELERATION",
                    strength=85,
                    timestamp=datetime.now(),
                    details={'acceleration': 'positive'}
                ))
        
        return signals
    
    def analyze_order_book(self, bid_volume: float, ask_volume: float,
                          large_bids: float, large_asks: float) -> List[MarketSignal]:
        """
        Order book imbalance is a leading indicator
        More bids than asks = buying pressure
        """
        signals = []
        
        if ask_volume == 0:
            return signals
        
        imbalance_ratio = bid_volume / ask_volume
        
        # Strong buy pressure
        if imbalance_ratio >= self.thresholds['order_book_extreme']:
            signals.append(MarketSignal(
                coin="",
                signal_type="EXTREME_BUY_PRESSURE",
                strength=90,
                timestamp=datetime.now(),
                details={
                    'bid_ask_ratio': round(imbalance_ratio, 2),
                    'bid_volume': bid_volume,
                    'ask_volume': ask_volume
                }
            ))
        elif imbalance_ratio >= self.thresholds['order_book_imbalance']:
            signals.append(MarketSignal(
                coin="",
                signal_type="STRONG_BUY_PRESSURE",
                strength=70,
                timestamp=datetime.now(),
                details={'bid_ask_ratio': round(imbalance_ratio, 2)}
            ))
        
        # Large order detection
        if large_bids > self.thresholds['large_order_threshold']:
            strength = min(100, (large_bids / self.thresholds['large_order_threshold']) * 30)
            signals.append(MarketSignal(
                coin="",
                signal_type="LARGE_BUY_ORDERS",
                strength=strength,
                timestamp=datetime.now(),
                details={'large_bids_usd': large_bids}
            ))
        
        return signals
    
    def analyze_funding_rate(self, current_rate: float, avg_rate: float,
                            rate_change: float) -> Optional[MarketSignal]:
        """
        Funding rate spikes indicate position changes
        """
        if abs(rate_change) >= self.thresholds['funding_rate_spike']:
            strength = min(100, abs(rate_change) * 500)
            return MarketSignal(
                coin="",
                signal_type="FUNDING_RATE_SPIKE",
                strength=strength,
                timestamp=datetime.now(),
                details={
                    'current_rate': round(current_rate, 4),
                    'rate_change': round(rate_change, 4),
                    'direction': 'long' if rate_change > 0 else 'short'
                }
            )
        return None
    
    def analyze_open_interest(self, oi_change_pct: float, oi_volume_ratio: float) -> Optional[MarketSignal]:
        """
        Open Interest increase with price increase = strong trend
        """
        if oi_change_pct >= self.thresholds['open_interest_change']:
            strength = min(100, oi_change_pct * 3)
            return MarketSignal(
                coin="",
                signal_type="OPEN_INTEREST_SURGE",
                strength=strength,
                timestamp=datetime.now(),
                details={
                    'oi_change_pct': round(oi_change_pct, 2),
                    'oi_volume_ratio': round(oi_volume_ratio, 2)
                }
            )
        return None
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Calculate RSI for momentum confirmation
        """
        if len(prices) < period + 1:
            return 50
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def detect_breakout_pattern(self, prices: List[float], volumes: List[float]) -> Optional[MarketSignal]:
        """
        Detect breakout patterns - consolidation then explosion
        """
        if len(prices) < 20:
            return None
        
        recent_prices = prices[-20:]
        recent_volumes = volumes[-20:]
        
        # Calculate price volatility in two halves
        first_half = recent_prices[:10]
        second_half = recent_prices[10:]
        
        first_std = np.std(first_half)
        second_std = np.std(second_half)
        
        # Low volatility then high volatility = breakout
        if first_std > 0 and second_std / first_std > 2.0:
            # Check if volume also increased
            first_vol = np.mean(recent_volumes[:10])
            second_vol = np.mean(recent_volumes[10:])
            
            if second_vol / max(first_vol, 1) > 1.5:
                return MarketSignal(
                    coin="",
                    signal_type="BREAKOUT_PATTERN",
                    strength=80,
                    timestamp=datetime.now(),
                    details={
                        'volatility_increase': round(second_std / first_std, 2),
                        'volume_increase': round(second_vol / max(first_vol, 1), 2)
                    }
                )
        
        return None
    
    def calculate_confluence_score(self, signals: List[MarketSignal]) -> Tuple[float, str]:
        """
        Calculate overall pump probability score based on signal confluence
        Multiple strong signals = higher confidence
        """
        if not signals:
            return 0, "NONE"
        
        # Weight different signal types
        signal_weights = {
            'EXTREME_VOLUME_SPIKE': 1.3,
            'VOLUME_SPIKE': 1.2,
            'EXTREME_BUY_PRESSURE': 1.2,
            'MOMENTUM_ACCELERATION': 1.15,
            'STRONG_5M_MOMENTUM': 1.1,
            'BREAKOUT_PATTERN': 1.15,
            'OPEN_INTEREST_SURGE': 1.1,
            'LARGE_BUY_ORDERS': 1.05,
        }
        
        total_score = 0
        for signal in signals:
            weight = signal_weights.get(signal.signal_type, 1.0)
            total_score += signal.strength * weight
        
        # Average but boost for signal confluence
        base_score = total_score / len(signals)
        confluence_bonus = min(20, len(signals) * 3)  # Bonus for multiple signals
        
        final_score = min(100, base_score + confluence_bonus)
        
        # Determine confidence level
        if final_score >= 85:
            confidence = "VERY_HIGH"
        elif final_score >= 75:
            confidence = "HIGH"
        elif final_score >= 65:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        return final_score, confidence
    
    def analyze_coin(self, coin_data: Dict) -> Optional[PumpSignal]:
        """
        Main analysis function - combines all signals
        """
        try:
            coin = coin_data['symbol']
            signals = []
            
            # 1. Volume Analysis
            volume_signal = self.analyze_volume_spike(
                coin_data.get('volume_current', 0),
                coin_data.get('volume_avg', 0),
                coin_data.get('volume_1h_ago', 0)
            )
            if volume_signal:
                volume_signal.coin = coin
                signals.append(volume_signal)
            
            # 2. Price Momentum
            price_changes = {
                '5m': coin_data.get('price_change_5m', 0),
                '15m': coin_data.get('price_change_15m', 0),
                '1h': coin_data.get('price_change_1h', 0)
            }
            momentum_signals = self.analyze_price_momentum(price_changes)
            for sig in momentum_signals:
                sig.coin = coin
                signals.append(sig)
            
            # 3. Order Book Analysis
            order_book_signals = self.analyze_order_book(
                coin_data.get('bid_volume', 0),
                coin_data.get('ask_volume', 0),
                coin_data.get('large_bids', 0),
                coin_data.get('large_asks', 0)
            )
            for sig in order_book_signals:
                sig.coin = coin
                signals.append(sig)
            
            # 4. Funding Rate
            funding_signal = self.analyze_funding_rate(
                coin_data.get('funding_rate', 0),
                coin_data.get('funding_rate_avg', 0),
                coin_data.get('funding_rate_change', 0)
            )
            if funding_signal:
                funding_signal.coin = coin
                signals.append(funding_signal)
            
            # 5. Open Interest
            oi_signal = self.analyze_open_interest(
                coin_data.get('oi_change_pct', 0),
                coin_data.get('oi_volume_ratio', 0)
            )
            if oi_signal:
                oi_signal.coin = coin
                signals.append(oi_signal)
            
            # 6. Breakout Pattern
            if 'prices_history' in coin_data and 'volumes_history' in coin_data:
                breakout_signal = self.detect_breakout_pattern(
                    coin_data['prices_history'],
                    coin_data['volumes_history']
                )
                if breakout_signal:
                    breakout_signal.coin = coin
                    signals.append(breakout_signal)
            
            # Calculate final score
            if not signals:
                return None
            
            score, confidence = self.calculate_confluence_score(signals)
            
            # Only return if score meets threshold
            if score < self.min_score:
                return None
            
            return PumpSignal(
                coin=coin,
                score=score,
                confidence=confidence,
                timeframe="INTRADAY",
                signals=signals,
                price=coin_data.get('price', 0),
                volume_24h=coin_data.get('volume_24h', 0),
                price_change_1h=coin_data.get('price_change_1h', 0),
                price_change_5m=coin_data.get('price_change_5m', 0),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {coin_data.get('symbol', 'UNKNOWN')}: {e}")
            return None
    
    def rank_signals(self, pump_signals: List[PumpSignal]) -> List[PumpSignal]:
        """
        Rank pump signals by score and confidence
        """
        return sorted(pump_signals, key=lambda x: x.score, reverse=True)
