"""
Configuration file for Crypto Pump Detector Bot
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load from environment variables or use defaults
CONFIG: Dict = {
    # Bybit API Configuration (Read-only, no trading)
    'bybit_api_key': os.getenv('BYBIT_API_KEY', ''),
    'bybit_api_secret': os.getenv('BYBIT_API_SECRET', ''),
    'testnet': os.getenv('BYBIT_TESTNET', 'false').lower() == 'true',
    
    # Telegram Configuration
    'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    
    # Scanner Settings
    'scan_interval': int(os.getenv('SCAN_INTERVAL', '90')),  # seconds between scans
    'max_workers': int(os.getenv('MAX_WORKERS', '10')),  # parallel processing
    
    # Filtering Thresholds
    'min_volume_24h': float(os.getenv('MIN_VOLUME_24H', '2000000')),  # $2M minimum - Filter out low liquidity coins
    'min_price_change_5m': float(os.getenv('MIN_PRICE_CHANGE_5M', '1.0')),  # 1%
    'max_price': float(os.getenv('MAX_PRICE', '100000')),  # Max coin price
    
    # Detection Thresholds (Fine-tuned for high accuracy)
    'min_score': float(os.getenv('MIN_SCORE', '80')),  # Minimum pump score to alert - Higher quality signals
    
    # Notification Settings
    'max_notifications_per_scan': int(os.getenv('MAX_NOTIFICATIONS', '5')),
    'notification_cooldown': int(os.getenv('NOTIFICATION_COOLDOWN', '900')),  # 15 min
    
    # Logging
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_file': os.getenv('LOG_FILE', 'pump_detector.log'),
}


def validate_config() -> bool:
    """
    Validate configuration
    Returns True if config is valid
    """
    errors = []
    
    # Check Telegram credentials
    if not CONFIG['telegram_bot_token']:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    
    if not CONFIG['telegram_chat_id']:
        errors.append("TELEGRAM_CHAT_ID is required")
    
    # Bybit API is optional (public endpoints work without auth)
    # But warn if not provided
    if not CONFIG['bybit_api_key']:
        print("⚠️  Warning: BYBIT_API_KEY not set. Using public endpoints only.")
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


def print_config():
    """Print current configuration (hide sensitive data)"""
    print("\n" + "="*60)
    print("🤖 CRYPTO PUMP DETECTOR - CONFIGURATION")
    print("="*60)
    print(f"Bybit API Key: {'***' + CONFIG['bybit_api_key'][-8:] if CONFIG['bybit_api_key'] else 'Not Set'}")
    print(f"Testnet Mode: {CONFIG['testnet']}")
    print(f"Telegram Bot: {'***' + CONFIG['telegram_bot_token'][-10:] if CONFIG['telegram_bot_token'] else 'Not Set'}")
    print(f"Telegram Chat: {CONFIG['telegram_chat_id']}")
    print(f"\nScan Interval: {CONFIG['scan_interval']}s")
    print(f"Max Workers: {CONFIG['max_workers']}")
    print(f"Min Score: {CONFIG['min_score']}")
    print(f"Min Volume 24h: ${CONFIG['min_volume_24h']:,.0f}")
    print(f"Max Notifications: {CONFIG['max_notifications_per_scan']}")
    print("="*60 + "\n")


# Export config
def get_config() -> Dict:
    """Get configuration dictionary"""
    return CONFIG.copy()
