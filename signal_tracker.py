"""
Signal Tracker - Records and tracks pump signals for performance analysis
Saves signal details and monitors price changes over time
"""

import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading
import time

from pump_detector import PumpSignal
from bybit_client import BybitClient

logger = logging.getLogger(__name__)


@dataclass
class SignalRecord:
    """Complete record of a pump signal and its outcome"""
    # Signal info
    id: str
    coin: str
    timestamp: str
    entry_price: float
    score: float
    confidence: str
    signals: List[str]  # Signal types
    
    # Price tracking (will be updated)
    price_5m: Optional[float] = None
    price_15m: Optional[float] = None
    price_30m: Optional[float] = None
    price_1h: Optional[float] = None
    price_4h: Optional[float] = None
    price_24h: Optional[float] = None
    
    # Performance metrics (will be calculated)
    change_5m: Optional[float] = None
    change_15m: Optional[float] = None
    change_30m: Optional[float] = None
    change_1h: Optional[float] = None
    change_4h: Optional[float] = None
    change_24h: Optional[float] = None
    
    # Analysis
    max_gain: Optional[float] = None  # En yüksek kazanç %
    max_loss: Optional[float] = None  # En düşük kayıp %
    success: Optional[bool] = None  # Did it pump?
    
    def to_dict(self):
        return asdict(self)


class SignalTracker:
    """
    Tracks pump signals and monitors their performance
    """
    
    def __init__(self, config: Dict, bybit_client: BybitClient):
        self.config = config
        self.bybit = bybit_client
        
        # Storage
        self.storage_file = "signals_history.json"
        self.signals_db = self._load_signals()
        
        # Active tracking
        self.active_signals = {}  # {signal_id: SignalRecord}
        
        # Tracking intervals (minutes)
        self.track_intervals = [5, 15, 30, 60, 240, 1440]  # 5m, 15m, 30m, 1h, 4h, 24h
        
        # Success criteria
        self.success_threshold = 3.0  # %3 veya üzeri = başarılı
        
        # Background tracker thread
        self.tracking_enabled = True
        self.tracker_thread = None
        
    def _load_signals(self) -> Dict:
        """Load signal history from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} signals from history")
                    return data
            except Exception as e:
                logger.error(f"Error loading signals: {e}")
                return {}
        return {}
    
    def _save_signals(self):
        """Save signal history to file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.signals_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving signals: {e}")
    
    def record_signal(self, pump_signal: PumpSignal) -> str:
        """
        Record a new pump signal
        Returns signal_id
        """
        # Generate unique ID
        signal_id = f"{pump_signal.coin}_{pump_signal.timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Extract signal types
        signal_types = [s.signal_type for s in pump_signal.signals]
        
        # Create record
        record = SignalRecord(
            id=signal_id,
            coin=pump_signal.coin,
            timestamp=pump_signal.timestamp.isoformat(),
            entry_price=pump_signal.price,
            score=pump_signal.score,
            confidence=pump_signal.confidence,
            signals=signal_types
        )
        
        # Add to database
        self.signals_db[signal_id] = record.to_dict()
        self._save_signals()
        
        # Add to active tracking
        self.active_signals[signal_id] = record
        
        logger.info(f"📝 Recorded signal: {pump_signal.coin} @ ${pump_signal.price:.4f} (Score: {pump_signal.score:.1f})")
        
        return signal_id
    
    def _calculate_change(self, entry_price: float, current_price: float) -> float:
        """Calculate percentage change"""
        if entry_price == 0:
            return 0
        return ((current_price - entry_price) / entry_price) * 100
    
    def update_signal_price(self, signal_id: str, interval_minutes: int):
        """
        Update price for a specific interval
        """
        if signal_id not in self.signals_db:
            return
        
        record_dict = self.signals_db[signal_id]
        coin = record_dict['coin']
        entry_price = record_dict['entry_price']
        
        # Get current price
        try:
            ticker = self.bybit.get_ticker_data(coin)
            if not ticker:
                return
            
            current_price = ticker['price']
            change = self._calculate_change(entry_price, current_price)
            
            # Update record based on interval
            if interval_minutes == 5:
                record_dict['price_5m'] = current_price
                record_dict['change_5m'] = change
            elif interval_minutes == 15:
                record_dict['price_15m'] = current_price
                record_dict['change_15m'] = change
            elif interval_minutes == 30:
                record_dict['price_30m'] = current_price
                record_dict['change_30m'] = change
            elif interval_minutes == 60:
                record_dict['price_1h'] = current_price
                record_dict['change_1h'] = change
            elif interval_minutes == 240:
                record_dict['price_4h'] = current_price
                record_dict['change_4h'] = change
            elif interval_minutes == 1440:
                record_dict['price_24h'] = current_price
                record_dict['change_24h'] = change
            
            # Update max gain/loss
            if record_dict['max_gain'] is None or change > record_dict['max_gain']:
                record_dict['max_gain'] = change
            
            if record_dict['max_loss'] is None or change < record_dict['max_loss']:
                record_dict['max_loss'] = change
            
            # Update success flag (after 1h)
            if interval_minutes == 60:
                record_dict['success'] = change >= self.success_threshold
            
            # Save
            self.signals_db[signal_id] = record_dict
            self._save_signals()
            
            logger.debug(f"Updated {coin} {interval_minutes}m: {change:+.2f}%")
            
        except Exception as e:
            logger.error(f"Error updating signal {signal_id}: {e}")
    
    def start_background_tracking(self):
        """
        Start background thread to track active signals
        """
        if self.tracker_thread and self.tracker_thread.is_alive():
            logger.warning("Tracker thread already running")
            return
        
        self.tracking_enabled = True
        self.tracker_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracker_thread.start()
        logger.info("✅ Background signal tracker started")
    
    def stop_background_tracking(self):
        """Stop background tracking"""
        self.tracking_enabled = False
        if self.tracker_thread:
            self.tracker_thread.join(timeout=5)
        logger.info("Background signal tracker stopped")
    
    def _tracking_loop(self):
        """
        Background loop that tracks active signals
        """
        logger.info("Signal tracking loop started")
        
        while self.tracking_enabled:
            try:
                now = datetime.now()
                signals_to_remove = []
                
                for signal_id, record_dict in list(self.signals_db.items()):
                    # Parse timestamp
                    signal_time = datetime.fromisoformat(record_dict['timestamp'])
                    elapsed_minutes = (now - signal_time).total_seconds() / 60
                    
                    # Check if we need to update any interval
                    for interval in self.track_intervals:
                        interval_key = f"price_{interval}m" if interval < 60 else (
                            f"price_{interval//60}h" if interval < 1440 else "price_24h"
                        )
                        
                        # Update if interval passed and not yet recorded
                        if elapsed_minutes >= interval and record_dict.get(interval_key) is None:
                            self.update_signal_price(signal_id, interval)
                    
                    # Remove from active tracking after 24h
                    if elapsed_minutes > 1440:
                        signals_to_remove.append(signal_id)
                
                # Clean up old signals from active tracking
                for signal_id in signals_to_remove:
                    if signal_id in self.active_signals:
                        del self.active_signals[signal_id]
                        logger.info(f"Completed tracking: {signal_id}")
                
                # Sleep 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(60)
        
        logger.info("Signal tracking loop ended")
    
    def get_active_signals(self) -> List[Dict]:
        """Get currently tracked signals"""
        return list(self.signals_db.values())
    
    def get_signal_by_id(self, signal_id: str) -> Optional[Dict]:
        """Get specific signal record"""
        return self.signals_db.get(signal_id)
    
    def get_recent_signals(self, hours: int = 24) -> List[Dict]:
        """Get signals from last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = []
        for signal_id, record in self.signals_db.items():
            signal_time = datetime.fromisoformat(record['timestamp'])
            if signal_time >= cutoff:
                recent.append(record)
        
        # Sort by timestamp descending
        recent.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent
    
    def get_statistics(self) -> Dict:
        """
        Get overall performance statistics
        """
        if not self.signals_db:
            return {
                'total_signals': 0,
                'message': 'No signals recorded yet'
            }
        
        total = len(self.signals_db)
        completed = sum(1 for r in self.signals_db.values() if r.get('success') is not None)
        
        if completed == 0:
            return {
                'total_signals': total,
                'completed_analysis': 0,
                'message': 'Waiting for signals to mature (1h minimum)'
            }
        
        # Calculate success metrics
        successful = sum(1 for r in self.signals_db.values() if r.get('success') is True)
        
        # Average changes
        changes_1h = [r['change_1h'] for r in self.signals_db.values() if r.get('change_1h') is not None]
        changes_4h = [r['change_4h'] for r in self.signals_db.values() if r.get('change_4h') is not None]
        
        # Max gains/losses
        max_gains = [r['max_gain'] for r in self.signals_db.values() if r.get('max_gain') is not None]
        max_losses = [r['max_loss'] for r in self.signals_db.values() if r.get('max_loss') is not None]
        
        # By confidence
        confidence_stats = {}
        for confidence in ['VERY_HIGH', 'HIGH', 'MEDIUM']:
            conf_signals = [r for r in self.signals_db.values() if r['confidence'] == confidence and r.get('success') is not None]
            if conf_signals:
                conf_success = sum(1 for r in conf_signals if r['success'])
                confidence_stats[confidence] = {
                    'total': len(conf_signals),
                    'successful': conf_success,
                    'accuracy': (conf_success / len(conf_signals) * 100) if conf_signals else 0
                }
        
        return {
            'total_signals': total,
            'completed_analysis': completed,
            'successful_signals': successful,
            'success_rate': (successful / completed * 100) if completed else 0,
            'avg_change_1h': sum(changes_1h) / len(changes_1h) if changes_1h else 0,
            'avg_change_4h': sum(changes_4h) / len(changes_4h) if changes_4h else 0,
            'avg_max_gain': sum(max_gains) / len(max_gains) if max_gains else 0,
            'avg_max_loss': sum(max_losses) / len(max_losses) if max_losses else 0,
            'best_signal': max(max_gains) if max_gains else 0,
            'worst_signal': min(max_losses) if max_losses else 0,
            'confidence_breakdown': confidence_stats
        }
