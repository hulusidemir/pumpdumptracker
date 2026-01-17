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
        
        # Critical thresholds for pump detection (STRICTER)
        self.thresholds = {
            'volume_spike_multiplier': 5.0,  # 5x normal volume (was 3x)
            'volume_extreme_multiplier': 8.0,  # 8x for extreme (was 5x)
            'price_momentum_5m': 3.0,  # 3% in 5 minutes (was 2%)
            'price_momentum_15m': 7.0,  # 7% in 15 minutes (was 5%)
            'order_book_imbalance': 3.0,  # 3:1 buy/sell ratio (was 2:1)
            'order_book_extreme': 5.0,  # 5:1 for extreme (was 3.5:1)
            'large_order_threshold': 200000,  # $200k orders (was $100k)
            'funding_rate_spike': 0.08,  # 0.08% sudden change (was 0.05%)
            'open_interest_change': 20.0,  # 20% OI increase (was 15%)
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            # New thresholds for advanced metrics
            'taker_buy_aggressive': 60,  # 60%+ taker buy = aggressive buying
            'taker_buy_extreme': 70,  # 70%+ = extreme buying
            'long_short_extreme': 70,  # 70%+ on one side = extreme positioning
            'liquidation_cascade_threshold': 1000000,  # $1M+ liquidation zone
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
    
    def analyze_open_interest(self, oi_change_pct: float, oi_volume_ratio: float, 
                             price_change: float = 0) -> Optional[MarketSignal]:
        """
        Advanced OI Analysis with price correlation
        
        Scenarios:
        1. Long Buildup: Price UP + OI UP → Bullish (yeni longlar açılıyor)
        2. Short Buildup: Price DOWN + OI UP → Bearish (yeni shortlar açılıyor)
        3. Long Unwinding: Price DOWN + OI DOWN → Bearish (longlar kapanıyor)
        4. Short Covering: Price UP + OI DOWN → Bullish Short Squeeze! (shortlar kapanıyor)
        """
        # Basic OI surge
        if abs(oi_change_pct) < 10:  # Too small to be meaningful
            return None
        
        signal_type = ""
        strength = 0
        scenario = ""
        
        # Scenario 1: LONG BUILDUP (En güçlü bullish sinyal)
        if price_change > 1.0 and oi_change_pct >= self.thresholds['open_interest_change']:
            signal_type = "LONG_BUILDUP"
            strength = min(95, oi_change_pct * 3 + abs(price_change) * 2)
            scenario = "Yeni long pozisyonlar açılıyor! 🚀"
        
        # Scenario 2: SHORT COVERING (Short Squeeze - Pump için ideal!)
        elif price_change > 2.0 and oi_change_pct < -10:
            signal_type = "SHORT_COVERING"
            strength = min(90, abs(oi_change_pct) * 4 + abs(price_change) * 3)
            scenario = "SHORT SQUEEZE! Shortlar kapanıyor! 💥"
        
        # Scenario 3: SHORT BUILDUP (Bearish - kaçın!)
        elif price_change < -1.0 and oi_change_pct >= 15:
            signal_type = "SHORT_BUILDUP"
            strength = 30  # Low strength - not a pump signal
            scenario = "Short pozisyonlar artıyor (Bearish)"
        
        # Scenario 4: LONG UNWINDING (Bearish - kaçın!)
        elif price_change < -2.0 and oi_change_pct < -10:
            signal_type = "LONG_UNWINDING"
            strength = 25  # Very low - not a pump signal
            scenario = "Long pozisyonlar kapanıyor (Bearish)"
        
        # Simple OI surge without clear direction
        elif oi_change_pct >= self.thresholds['open_interest_change']:
            signal_type = "OPEN_INTEREST_SURGE"
            strength = min(70, oi_change_pct * 2.5)
            scenario = "Open Interest artıyor"
        
        if not signal_type:
            return None
        
        return MarketSignal(
            coin="",
            signal_type=signal_type,
            strength=strength,
            timestamp=datetime.now(),
            details={
                'oi_change_pct': round(oi_change_pct, 2),
                'price_change': round(price_change, 2),
                'scenario': scenario,
                'oi_volume_ratio': round(oi_volume_ratio, 2)
            }
        )
    
    def analyze_taker_buy_sell(self, taker_buy_ratio: float, taker_pressure: str) -> Optional[MarketSignal]:
        """
        Analyze taker buy/sell ratio - aggressive buying/selling
        Similar to CVD (Cumulative Volume Delta)
        """
        if taker_buy_ratio >= self.thresholds['taker_buy_extreme']:
            return MarketSignal(
                coin="",
                signal_type="EXTREME_TAKER_BUYING",
                strength=95,
                timestamp=datetime.now(),
                details={
                    'taker_buy_ratio': round(taker_buy_ratio, 2),
                    'scenario': f'Agresif alım baskısı! Market order ile alınıyor'
                }
            )
        elif taker_buy_ratio >= self.thresholds['taker_buy_aggressive']:
            return MarketSignal(
                coin="",
                signal_type="AGGRESSIVE_TAKER_BUYING",
                strength=75,
                timestamp=datetime.now(),
                details={
                    'taker_buy_ratio': round(taker_buy_ratio, 2),
                    'scenario': f'Güçlü taker buy pressure'
                }
            )
        elif taker_buy_ratio <= (100 - self.thresholds['taker_buy_extreme']):
            return MarketSignal(
                coin="",
                signal_type="EXTREME_TAKER_SELLING",
                strength=20,  # Bearish - low score
                timestamp=datetime.now(),
                details={
                    'taker_buy_ratio': round(taker_buy_ratio, 2),
                    'scenario': f'Agresif satış baskısı (Bearish)'
                }
            )
        
        return None
    
    def analyze_long_short_ratio(self, long_ratio: float, short_ratio: float, 
                                 price_change: float) -> Optional[MarketSignal]:
        """
        Analyze long/short positioning - contrarian indicator
        When too many shorts → short squeeze potential
        When too many longs → long squeeze risk
        """
        # Extreme short positioning + price rising = SHORT SQUEEZE SETUP
        if short_ratio >= self.thresholds['long_short_extreme'] and price_change > 1.0:
            return MarketSignal(
                coin="",
                signal_type="SHORT_SQUEEZE_SETUP",
                strength=90,
                timestamp=datetime.now(),
                details={
                    'short_ratio': round(short_ratio, 2),
                    'long_ratio': round(long_ratio, 2),
                    'scenario': f'Pozisyonların %{short_ratio:.0f}\'si short! Squeeze riski yüksek! 💥'
                }
            )
        
        # Many shorts (contrarian bullish)
        elif short_ratio > 60:
            return MarketSignal(
                coin="",
                signal_type="HIGH_SHORT_INTEREST",
                strength=70,
                timestamp=datetime.now(),
                details={
                    'short_ratio': round(short_ratio, 2),
                    'scenario': f'Yüksek short ratio (%{short_ratio:.0f}) - Kontra sinyal'
                }
            )
        
        # Too many longs (risk of long squeeze)
        elif long_ratio >= self.thresholds['long_short_extreme']:
            return MarketSignal(
                coin="",
                signal_type="OVERCROWDED_LONGS",
                strength=30,  # Warning signal
                timestamp=datetime.now(),
                details={
                    'long_ratio': round(long_ratio, 2),
                    'scenario': f'Çok fazla long (%{long_ratio:.0f}) - Dikkatli ol!'
                }
            )
        
        return None
    
    def analyze_liquidation_zones(self, current_price: float, long_liq_price: float, 
                                  short_liq_price: float, est_long_liq: float, 
                                  est_short_liq: float, price_change: float) -> Optional[MarketSignal]:
        """
        Analyze liquidation zones - cascade liquidation potential
        """
        # Distance to liquidation zones
        dist_to_short_liq = ((short_liq_price - current_price) / current_price * 100)
        dist_to_long_liq = ((current_price - long_liq_price) / current_price * 100)
        
        # Short liquidation cascade approaching (price rising towards short liq zone)
        if dist_to_short_liq < 2.0 and price_change > 1.5 and est_short_liq >= self.thresholds['liquidation_cascade_threshold']:
            return MarketSignal(
                coin="",
                signal_type="SHORT_LIQUIDATION_CASCADE",
                strength=85,
                timestamp=datetime.now(),
                details={
                    'distance_to_zone': round(dist_to_short_liq, 2),
                    'liquidation_volume': est_short_liq,
                    'scenario': f'${short_liq_price:.4f}\'da ${est_short_liq/1e6:.1f}M short tasfiye! Cascade riski!'
                }
            )
        
        # Large liquidation zone nearby
        elif est_short_liq >= self.thresholds['liquidation_cascade_threshold']:
            return MarketSignal(
                coin="",
                signal_type="LARGE_LIQUIDATION_ZONE",
                strength=60,
                timestamp=datetime.now(),
                details={
                    'short_liq_zone': round(short_liq_price, 4),
                    'liquidation_volume': est_short_liq,
                    'scenario': f'Yakında ${est_short_liq/1e6:.1f}M short tasfiye bölgesi'
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
            'SHORT_COVERING': 1.25,  # Short squeeze is very bullish!
            'LONG_BUILDUP': 1.2,  # Fresh longs entering
            'EXTREME_TAKER_BUYING': 1.25,  # Aggressive market buying!
            'AGGRESSIVE_TAKER_BUYING': 1.15,
            'SHORT_SQUEEZE_SETUP': 1.3,  # High short interest + price rising
            'SHORT_LIQUIDATION_CASCADE': 1.35,  # Liquidation cascade incoming!
            'HIGH_SHORT_INTEREST': 1.1,  # Contrarian bullish
            'LARGE_LIQUIDATION_ZONE': 1.1,
            'MOMENTUM_ACCELERATION': 1.15,
            'STRONG_5M_MOMENTUM': 1.1,
            'BREAKOUT_PATTERN': 1.15,
            'OPEN_INTEREST_SURGE': 1.05,
            'LARGE_BUY_ORDERS': 1.05,
            'SHORT_BUILDUP': 0.5,  # Bearish signal - reduce weight
            'LONG_UNWINDING': 0.5,  # Bearish signal - reduce weight
            'EXTREME_TAKER_SELLING': 0.4,  # Very bearish
            'OVERCROWDED_LONGS': 0.6,  # Warning signal
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
            
            # 5. Open Interest (with price correlation)
            oi_signal = self.analyze_open_interest(
                coin_data.get('oi_change_pct', 0),
                coin_data.get('oi_volume_ratio', 0),
                coin_data.get('price_change_1h', 0)  # Use 1h price change for OI correlation
            )
            if oi_signal:
                oi_signal.coin = coin
                signals.append(oi_signal)
            
            # 6. Taker Buy/Sell Ratio (CVD alternative)
            taker_signal = self.analyze_taker_buy_sell(
                coin_data.get('taker_buy_ratio', 50),
                coin_data.get('taker_pressure', 'NEUTRAL')
            )
            if taker_signal:
                taker_signal.coin = coin
                signals.append(taker_signal)
            
            # 7. Long/Short Ratio (contrarian indicator)
            ls_signal = self.analyze_long_short_ratio(
                coin_data.get('long_ratio', 50),
                coin_data.get('short_ratio', 50),
                coin_data.get('price_change_1h', 0)
            )
            if ls_signal:
                ls_signal.coin = coin
                signals.append(ls_signal)
            
            # 8. Liquidation Zones
            liq_signal = self.analyze_liquidation_zones(
                coin_data.get('price', 0),
                coin_data.get('long_liq_price', 0),
                coin_data.get('short_liq_price', 0),
                coin_data.get('est_long_liq_volume', 0),
                coin_data.get('est_short_liq_volume', 0),
                coin_data.get('price_change_1h', 0)
            )
            if liq_signal:
                liq_signal.coin = coin
                signals.append(liq_signal)
            
            # 9. Breakout Pattern
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
