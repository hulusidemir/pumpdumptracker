"""
Main entry point for Crypto Pump Detector Bot
Professional pump detection system for Bybit USDT perpetuals
"""

import logging
import sys
import time
from datetime import datetime

from config import CONFIG, validate_config, print_config
from market_scanner import MarketScanner
from telegram_notifier import TelegramNotifierSync
from signal_tracker import SignalTracker
from bybit_client import BybitClient

# Setup logging
def setup_logging():
    """Configure logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # File handler
    file_handler = logging.FileHandler(CONFIG['log_file'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class PumpDetectorBot:
    """
    Main bot orchestrator
    """
    
    def __init__(self):
        self.config = CONFIG
        self.scanner = None
        self.notifier = None
        self.tracker = None
        self.running = False
    
    def initialize(self):
        """Initialize bot components"""
        logger.info("Initializing Crypto Pump Detector Bot...")
        
        # Validate config
        if not validate_config():
            logger.error("Configuration validation failed")
            return False
        
        print_config()
        
        # Initialize scanner
        logger.info("Initializing market scanner...")
        self.scanner = MarketScanner(self.config)
        
        # Initialize Telegram notifier
        logger.info("Initializing Telegram notifier...")
        self.notifier = TelegramNotifierSync(
            bot_token=self.config['telegram_bot_token'],
            chat_id=self.config['telegram_chat_id']
        )
        
        # Initialize signal tracker
        logger.info("Initializing signal tracker...")
        bybit_client = BybitClient(
            api_key=self.config.get('bybit_api_key', ''),
            api_secret=self.config.get('bybit_api_secret', ''),
            testnet=self.config.get('testnet', False)
        )
        self.tracker = SignalTracker(self.config, bybit_client)
        
        # Send startup message
        try:
            self.notifier.send_startup_message()
            logger.info("Startup notification sent")
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")
        
        # Start signal tracker
        logger.info("Starting background signal tracker...")
        self.tracker.start_background_tracking()
        
        logger.info("✅ Bot initialization complete")
        return True
    
    def handle_pump_signals(self, signals):
        """
        Handle detected pump signals
        """
        if not signals:
            return
        
        try:
            # Record signals in tracker
            for signal in signals:
                self.tracker.record_signal(signal)
            
            # Send notifications
            self.notifier.notify_signals_batch(
                signals, 
                max_notify=self.config['max_notifications_per_scan']
            )
        except Exception as e:
            logger.error(f"Error handling pump signals: {e}")
    
    def run(self):
        """
        Run the bot
        """
        if not self.initialize():
            logger.error("Bot initialization failed. Exiting.")
            return
        
        logger.info("\n🚀 Starting pump detection...")
        logger.info(f"Monitoring Bybit USDT perpetual futures")
        logger.info(f"Scan interval: {self.config['scan_interval']}s\n")
        
        self.running = True
        
        try:
            # Run continuous scanner with callback
            self.scanner.run_continuous_scan(
                callback=self.handle_pump_signals
            )
        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Bot stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"\n\n❌ Fatal error: {e}")
            try:
                self.notifier.send_message(f"⚠️ Bot encountered fatal error: {e}")
            except:
                pass
        finally:
            self.running = False
            
            # Stop tracker
            if self.tracker:
                logger.info("Stopping signal tracker...")
                self.tracker.stop_background_tracking()
                
                # Show quick stats
                stats = self.tracker.get_statistics()
                if stats.get('completed_analysis', 0) > 0:
                    logger.info(f"\n📊 Final Statistics:")
                    logger.info(f"Total Signals: {stats['total_signals']}")
                    logger.info(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
                    logger.info(f"Avg 1h Change: {stats.get('avg_change_1h', 0):+.2f}%")
            
            logger.info("Bot shutdown complete")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 CRYPTO PUMP DETECTOR BOT")
    print("Bybit USDT Perpetual Futures Scanner")
    print("="*60 + "\n")
    
    # Setup logging
    setup_logging()
    
    # Create and run bot
    bot = PumpDetectorBot()
    bot.run()


if __name__ == "__main__":
    main()
