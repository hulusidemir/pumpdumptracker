"""
Quick test script to verify bot configuration and connectivity
"""

import os
import sys
from datetime import datetime

def test_python_version():
    """Check Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def test_dependencies():
    """Check if all required packages are installed"""
    print("\n📦 Testing dependencies...")
    
    required = {
        'requests': 'requests',
        'numpy': 'numpy',
        'telegram': 'python-telegram-bot'
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (Run: pip install {package})")
            all_ok = False
    
    return all_ok

def test_config():
    """Check configuration"""
    print("\n⚙️  Testing configuration...")
    
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("   ✅ .env file loaded")
    except ImportError:
        print("   ⚠️  python-dotenv not installed (optional)")
        print("      You can set env vars manually or: pip install python-dotenv")
    
    # Check critical config
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID', '')
    
    all_ok = True
    
    if telegram_token and len(telegram_token) > 20:
        print(f"   ✅ TELEGRAM_BOT_TOKEN (***{telegram_token[-8:]})")
    else:
        print(f"   ❌ TELEGRAM_BOT_TOKEN not set or invalid")
        all_ok = False
    
    if telegram_chat and telegram_chat.isdigit():
        print(f"   ✅ TELEGRAM_CHAT_ID ({telegram_chat})")
    else:
        print(f"   ❌ TELEGRAM_CHAT_ID not set or invalid")
        all_ok = False
    
    return all_ok

def test_bybit_connection():
    """Test Bybit API connection"""
    print("\n🔌 Testing Bybit connection...")
    
    try:
        import requests
        
        response = requests.get(
            "https://api.bybit.com/v5/market/tickers",
            params={'category': 'linear', 'symbol': 'BTCUSDT'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                ticker = data['result']['list'][0]
                price = float(ticker['lastPrice'])
                print(f"   ✅ Bybit API responding")
                print(f"   📊 BTCUSDT: ${price:,.2f}")
                return True
        
        print(f"   ❌ API returned error: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def test_telegram():
    """Test Telegram bot connection"""
    print("\n📱 Testing Telegram bot...")
    
    try:
        from telegram import Bot
        import asyncio
        
        token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        if not token or not chat_id:
            print("   ⚠️  Telegram credentials not set, skipping test")
            return None
        
        async def test_bot():
            bot = Bot(token=token)
            
            # Get bot info
            me = await bot.get_me()
            print(f"   ✅ Bot connected: @{me.username}")
            
            # Try to send test message
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text="🧪 Test message from Pump Detector Bot\n\nConfiguration test successful! ✅"
                )
                print(f"   ✅ Test message sent to chat {chat_id}")
                return True
            except Exception as e:
                print(f"   ❌ Failed to send message: {e}")
                print(f"      Make sure chat_id is correct and you've started the bot")
                return False
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_bot())
        return result
        
    except ImportError:
        print("   ❌ python-telegram-bot not installed")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 PUMP DETECTOR BOT - CONFIGURATION TEST")
    print("="*60)
    
    results = {}
    
    # Run tests
    results['python'] = test_python_version()
    results['dependencies'] = test_dependencies()
    results['config'] = test_config()
    results['bybit'] = test_bybit_connection()
    results['telegram'] = test_telegram()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    if skipped:
        print(f"⚠️  Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Bot is ready to run.")
        print("\n▶️  Start the bot with: python main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n📝 Common fixes:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Configure .env file with your Telegram credentials")
        print("   3. Check your internet connection")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
