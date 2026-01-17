"""
Telegram Notifier - Sends professional pump alerts to Telegram
"""

import logging
import asyncio
from typing import List, Optional
from datetime import datetime
from telegram import Bot, Update
from telegram.error import TelegramError
from telegram.constants import ParseMode

from pump_detector import PumpSignal

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Professional Telegram notification system for pump alerts
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        
        # Track sent signals to avoid spam
        self.sent_signals = {}  # {symbol: timestamp}
        self.notification_cooldown = 900  # 15 minutes between same coin alerts
        
        # Initialize bot
        self._init_bot()
    
    def _init_bot(self):
        """Initialize Telegram bot"""
        try:
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            self.bot = None
    
    def _should_notify(self, symbol: str) -> bool:
        """Check if we should send notification for this symbol"""
        if symbol not in self.sent_signals:
            return True
        
        last_sent = self.sent_signals[symbol]
        elapsed = (datetime.now() - last_sent).total_seconds()
        
        return elapsed > self.notification_cooldown
    
    def _format_signal_message(self, signal: PumpSignal, rank: int = None) -> str:
        """
        Format pump signal as professional Telegram message
        """
        # Confidence emoji
        confidence_emoji = {
            'VERY_HIGH': '🔥🔥🔥',
            'HIGH': '🔥🔥',
            'MEDIUM': '🔥',
            'LOW': '⚡'
        }
        
        confidence_text = {
            'VERY_HIGH': 'ÇOK YÜKSEK',
            'HIGH': 'YÜKSEK',
            'MEDIUM': 'ORTA',
            'LOW': 'DÜŞÜK'
        }
        
        emoji = confidence_emoji.get(signal.confidence, '⚡')
        guven = confidence_text.get(signal.confidence, signal.confidence)
        
        # Rank prefix
        rank_text = f"#{rank} " if rank else ""
        
        # Price change indicators
        change_5m_emoji = "🟢" if signal.price_change_5m > 0 else "🔴"
        change_1h_emoji = "🟢" if signal.price_change_1h > 0 else "🔴"
        
        # Signal translations
        signal_names_tr = {
            'EXTREME_VOLUME_SPIKE': '💥 Aşırı Hacim Patlaması',
            'VOLUME_SPIKE': '📈 Hacim Artışı',
            'ELEVATED_VOLUME': '📊 Yükselen Hacim',
            'EXTREME_BUY_PRESSURE': '🐋 Aşırı Alım Baskısı',
            'STRONG_BUY_PRESSURE': '💪 Güçlü Alım Baskısı',
            'LARGE_BUY_ORDERS': '🎯 Büyük Alış Emirleri',
            'STRONG_5M_MOMENTUM': '⚡ 5 Dakika Momentum',
            'STRONG_15M_MOMENTUM': '⚡ 15 Dakika Momentum',
            'STRONG_1H_MOMENTUM': '⚡ 1 Saat Momentum',
            'MOMENTUM_ACCELERATION': '🚀 Hızlanan Momentum',
            'BREAKOUT_PATTERN': '📊 Breakout Paterni',
            'FUNDING_RATE_SPIKE': '💰 Funding Rate Atışı',
            'OPEN_INTEREST_SURGE': '📊 Open Interest Artışı',
            'LONG_BUILDUP': '🟢 Long Buildup (Yeni Longlar)',
            'SHORT_COVERING': '💥 SHORT SQUEEZE!',
            'SHORT_BUILDUP': '🔴 Short Buildup (Dikkat)',
            'LONG_UNWINDING': '⚠️ Long Unwinding',
            'EXTREME_TAKER_BUYING': '🔥 AŞIRI TAKERbuying',
            'AGGRESSIVE_TAKER_BUYING': '💪 Agresif Taker Alımı',
            'EXTREME_TAKER_SELLING': '🔻 Aşırı Taker Satışı',
            'SHORT_SQUEEZE_SETUP': '💣 SHORT SQUEEZE HAZIRLIĞI!',
            'HIGH_SHORT_INTEREST': '🎯 Yüksek Short Pozisyonu',
            'OVERCROWDED_LONGS': '⚠️ Aşırı Long Kalabalığı',
            'SHORT_LIQUIDATION_CASCADE': '🌊 SHORT TAHLİYE KASKADI!',
            'LARGE_LIQUIDATION_ZONE': '⚡ Büyük Tasfiye Bölgesi'
        }
        
        # Build message
        message = f"""
{emoji} <b>PUMP SINYALI {rank_text}</b> {emoji}

<b>🪙 Coin:</b> {signal.coin}
<b>⭐ Skor:</b> {signal.score:.1f}/100
<b>🎯 Güven:</b> {guven}

<b>💹 FİYAT HAREKETİ:</b>
{change_5m_emoji} 5 dakika: <b>{signal.price_change_5m:+.2f}%</b>
{change_1h_emoji} 1 saat: <b>{signal.price_change_1h:+.2f}%</b>
💰 Fiyat: ${signal.price:,.4f}

<b>📊 HACİM:</b>
24 saat: ${signal.volume_24h:,.0f}

<b>🔍 TESPİT EDİLEN SİNYALLER:</b>
"""
        
        # Add top signals
        top_signals = sorted(signal.signals, key=lambda x: x.strength, reverse=True)[:5]
        for sig in top_signals:
            signal_name = signal_names_tr.get(sig.signal_type, sig.signal_type.replace('_', ' ').title())
            
            # Add scenario details for OI signals
            scenario = sig.details.get('scenario', '') if hasattr(sig, 'details') and sig.details else ''
            if scenario:
                message += f"• {signal_name}\n  └ {scenario} ({sig.strength:.0f} puan)\n"
            else:
                message += f"• {signal_name} ({sig.strength:.0f} puan)\n"
        
        # Add trading advice
        message += f"\n<b>💡 CONFLUENCES:</b> {len(signal.signals)} adet sinyal bir arada!\n"
        
        # Add Bybit link
        bybit_url = f"https://www.bybit.com/trade/usdt/{signal.coin}"
        message += f"\n<a href='{bybit_url}'>📱 Bybit'te Aç</a>"
        
        # Timestamp
        message += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    def _format_summary_message(self, signals: List[PumpSignal], scan_time: float) -> str:
        """
        Format market scan summary
        """
        if not signals:
            return "✅ <b>Tarama Tamamlandı</b>\n\nBu taramada pump sinyali tespit edilmedi."
        
        message = f"""
🔍 <b>Piyasa Taraması Tamamlandı</b>

<b>{len(signals)}</b> adet pump sinyali bulundu ({scan_time:.1f} saniye)

<b>🏆 En Güçlü Sinyaller:</b>
"""
        
        for i, signal in enumerate(signals[:5], 1):
            emoji = "🔥" if signal.confidence == "VERY_HIGH" else "⚡"
            message += f"{i}. {emoji} <b>{signal.coin}</b> - {signal.score:.0f} puan - {signal.price_change_5m:+.2f}% (5dk)\n"
        
        return message
    
    async def send_message(self, message: str, disable_preview: bool = True):
        """Send message to Telegram"""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=disable_preview
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def notify_signal(self, signal: PumpSignal, rank: int = None):
        """
        Send notification for a single pump signal
        """
        # Check cooldown
        if not self._should_notify(signal.coin):
            logger.info(f"Skipping notification for {signal.coin} (cooldown)")
            return False
        
        # Format and send message
        message = self._format_signal_message(signal, rank)
        success = await self.send_message(message)
        
        if success:
            self.sent_signals[signal.coin] = datetime.now()
            logger.info(f"Sent notification for {signal.coin}")
        
        return success
    
    async def notify_signals_batch(self, signals: List[PumpSignal], max_notify: int = 5):
        """
        Send notifications for multiple signals
        Only sends top N to avoid spam
        """
        if not signals:
            return
        
        # Filter by cooldown
        signals_to_send = [s for s in signals if self._should_notify(s.coin)]
        
        if not signals_to_send:
            logger.info("No new signals to notify (all in cooldown)")
            return
        
        # Send top signals
        for i, signal in enumerate(signals_to_send[:max_notify], 1):
            await self.notify_signal(signal, rank=i)
            await asyncio.sleep(1)  # Rate limiting
    
    async def notify_scan_summary(self, signals: List[PumpSignal], scan_time: float):
        """
        Send market scan summary
        """
        message = self._format_summary_message(signals, scan_time)
        await self.send_message(message)
    
    async def send_startup_message(self):
        """Send bot startup notification"""
        message = """
🤖 <b>Pump Detector Bot Başlatıldı</b>

Bot şimdi Bybit USDT perpetual futures piyasasını taramaya başladı.

Yüksek olasılıklı pump fırsatları tespit edildiğinde sizi bilgilendireceğim.

Hazır olun! 🚀
"""
        await self.send_message(message)
    
    async def send_error_message(self, error: str):
        """Send error notification"""
        message = f"""
⚠️ <b>Hata Bildirimi</b>

{error}

Bot çalışmaya devam etmeye çalışıyor...
"""
        await self.send_message(message)


# Synchronous wrapper for easier use
class TelegramNotifierSync:
    """
    Synchronous wrapper for TelegramNotifier
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        self.notifier = TelegramNotifier(bot_token, chat_id)
        self.loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        if self.loop is None:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        return self.loop
    
    def notify_signal(self, signal: PumpSignal, rank: int = None):
        """Send notification for a single pump signal"""
        loop = self._get_loop()
        return loop.run_until_complete(self.notifier.notify_signal(signal, rank))
    
    def notify_signals_batch(self, signals: List[PumpSignal], max_notify: int = 5):
        """Send notifications for multiple signals"""
        loop = self._get_loop()
        return loop.run_until_complete(self.notifier.notify_signals_batch(signals, max_notify))
    
    def send_startup_message(self):
        """Send bot startup notification"""
        loop = self._get_loop()
        return loop.run_until_complete(self.notifier.send_startup_message())
    
    def send_message(self, message: str):
        """Send custom message"""
        loop = self._get_loop()
        return loop.run_until_complete(self.notifier.send_message(message))
