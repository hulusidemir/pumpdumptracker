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
        
        emoji = confidence_emoji.get(signal.confidence, '⚡')
        
        # Rank prefix
        rank_text = f"#{rank} " if rank else ""
        
        # Price change indicators
        change_5m_emoji = "🟢" if signal.price_change_5m > 0 else "🔴"
        change_1h_emoji = "🟢" if signal.price_change_1h > 0 else "🔴"
        
        # Build message
        message = f"""
{emoji} <b>PUMP ALERT {rank_text}</b> {emoji}

<b>Symbol:</b> {signal.coin}
<b>Score:</b> {signal.score:.1f}/100
<b>Confidence:</b> {signal.confidence}

<b>📊 Price Action:</b>
{change_5m_emoji} 5m: <b>{signal.price_change_5m:+.2f}%</b>
{change_1h_emoji} 1h: <b>{signal.price_change_1h:+.2f}%</b>
💰 Price: ${signal.price:,.4f}

<b>📈 Volume:</b>
24h Volume: ${signal.volume_24h:,.0f}

<b>🎯 Detected Signals:</b>
"""
        
        # Add top signals
        top_signals = sorted(signal.signals, key=lambda x: x.strength, reverse=True)[:5]
        for sig in top_signals:
            signal_emoji = "🚀" if sig.strength >= 80 else "⚡" if sig.strength >= 60 else "📊"
            signal_name = sig.signal_type.replace('_', ' ').title()
            message += f"{signal_emoji} {signal_name} ({sig.strength:.0f})\n"
        
        # Add Bybit link
        bybit_url = f"https://www.bybit.com/trade/usdt/{signal.coin}"
        message += f"\n<a href='{bybit_url}'>📱 Open on Bybit</a>"
        
        # Timestamp
        message += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    def _format_summary_message(self, signals: List[PumpSignal], scan_time: float) -> str:
        """
        Format market scan summary
        """
        if not signals:
            return "✅ <b>Market Scan Complete</b>\n\nNo pump signals detected this scan."
        
        message = f"""
🔍 <b>Market Scan Complete</b>

Found <b>{len(signals)}</b> pump signals in {scan_time:.1f}s

<b>Top Signals:</b>
"""
        
        for i, signal in enumerate(signals[:5], 1):
            emoji = "🔥" if signal.confidence == "VERY_HIGH" else "⚡"
            message += f"{i}. {emoji} <b>{signal.coin}</b> - {signal.score:.0f} pts - {signal.price_change_5m:+.2f}% (5m)\n"
        
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
🤖 <b>Pump Detector Bot Started</b>

Bot is now monitoring Bybit USDT perpetual futures for pump signals.

Will alert you when high-probability pump opportunities are detected.

Stay tuned! 🚀
"""
        await self.send_message(message)
    
    async def send_error_message(self, error: str):
        """Send error notification"""
        message = f"""
⚠️ <b>Error Alert</b>

{error}

Bot will attempt to continue...
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
