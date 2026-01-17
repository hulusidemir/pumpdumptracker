# 🚀 Hızlı Başlangıç Rehberi

## 1. Telegram Bot Kurulumu (2 dakika)

### Adım 1: Bot Oluştur

1. Telegram'da **@BotFather** ara ve başlat
2. `/newbot` komutunu gönder
3. Bot için bir isim seç (örn: "My Pump Detector")
4. Bot için kullanıcı adı seç (örn: "my_pump_bot")
5. BotFather sana bir **token** verecek. Kopyala!
   ```
   Örnek: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

### Adım 2: Chat ID Bul

1. Telegram'da **@userinfobot** ara ve başlat
2. `/start` gönder
3. Bot sana **ID**'ni gösterecek. Kopyala!
   ```
   Örnek: 123456789
   ```

### Adım 3: Bot'u Başlat

1. Oluşturduğun bot'u bul (örn: @my_pump_bot)
2. `/start` gönder
3. Bot artık sana mesaj gönderebilir

---

## 2. Kurulum (3 dakika)

### Linux/Mac:

```bash
# 1. Python paketlerini yükle
pip3 install -r requirements.txt

# 2. .env dosyasını oluştur
cp .env.example .env

# 3. .env dosyasını düzenle
nano .env

# Token ve Chat ID'yi yapıştır:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_CHAT_ID=123456789

# Kaydet ve çık (Ctrl+O, Enter, Ctrl+X)

# 4. Test et
python3 test_setup.py

# 5. Başlat!
./start.sh
```

### Windows:

```cmd
# 1. Python paketlerini yükle
pip install -r requirements.txt

# 2. .env dosyasını oluştur
copy .env.example .env

# 3. .env dosyasını Not Defteri ile aç ve düzenle
notepad .env

# Token ve Chat ID'yi yapıştır:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_CHAT_ID=123456789

# Kaydet ve kapat

# 4. Test et
python test_setup.py

# 5. Başlat!
start.bat
```

---

## 3. İlk Kullanım

### Bot Başlatma

```bash
# Terminal'de çalıştır
python main.py
```

Bot başladığında şunu göreceksin:

```
========================================
🤖 CRYPTO PUMP DETECTOR - CONFIGURATION
========================================
Bybit API Key: Not Set
Telegram Bot: ***ABCdefGhIJ
Telegram Chat: 123456789

Scan Interval: 90s
Min Score: 70
========================================

🚀 Starting pump detection...
```

Telegram'dan da bildirim alacaksın:

```
🤖 Pump Detector Bot Started

Bot is now monitoring Bybit USDT perpetual 
futures for pump signals.

Will alert you when high-probability pump 
opportunities are detected.

Stay tuned! 🚀
```

### İlk Tarama

Bot her 90 saniyede bir piyasayı tarar:

```
==========================================================
SCAN #1 - 2026-01-16 14:32:15
==========================================================
Stage 1: Fetching all tickers...
Stage 2: Quick filtering...
Quick filter: 23/187 symbols passed
Stage 3: Deep analysis of 23 symbols...

🚀 Found 3 pump signals:
1. ARBUSDT - Score: 84.2 - 5m: +3.42% - 1h: +8.76%
2. OPUSDT - Score: 78.5 - 5m: +2.87% - 1h: +6.23%
3. ETHUSDT - Score: 72.1 - 5m: +1.95% - 1h: +4.51%

Market scan completed in 45.3s - Found 3 signals
```

Telegram'da da bildirimler gelecek! 🎉

---

## 4. Ayarlar (Opsiyonel)

### Daha Fazla Sinyal İstiyorsan

`.env` dosyasını aç ve değiştir:

```env
MIN_SCORE=65                  # 70'ten 65'e indir
SCAN_INTERVAL=60              # 90'dan 60'a indir
MAX_NOTIFICATIONS=8           # 5'ten 8'e çıkar
```

### Daha Az Ama Güçlü Sinyaller İstiyorsan

```env
MIN_SCORE=80                  # 70'ten 80'e çıkar
MIN_VOLUME_24H=1000000        # 500k'dan 1M'a çıkar
MAX_NOTIFICATIONS=3           # 5'ten 3'e indir
```

### Scalping (Yüksek Frekanslı) İçin

```env
SCAN_INTERVAL=60              # Her dakika tara
MIN_SCORE=75                  # Orta-yüksek sinyaller
MIN_PRICE_CHANGE_5M=2.0       # En az %2 hareket
```

---

## 5. Telegram Bildirimi Nasıl Görünür?

```
🔥🔥🔥 PUMP ALERT #1 🔥🔥🔥

Symbol: ARBUSDT
Score: 84.2/100
Confidence: VERY_HIGH

📊 Price Action:
🟢 5m: +3.42%
🟢 1h: +8.76%
💰 Price: $1.2345

📈 Volume:
24h Volume: $123,456,789

🎯 Detected Signals:
🚀 Extreme Volume Spike (95)
🚀 Momentum Acceleration (85)
⚡ Strong Buy Pressure (75)
⚡ Breakout Pattern (80)

📱 Open on Bybit

⏰ 14:32:15
```

---

## 6. Sorun Giderme

### "Telegram bildirim gelmiyor"

```bash
# Test script'ini çalıştır
python test_setup.py

# Şunları kontrol et:
# ✓ Bot token doğru mu?
# ✓ Chat ID doğru mu?
# ✓ Bot'a /start gönderdin mi?
```

### "Çok az sinyal geliyor"

Piyasa sakin olabilir veya skorlar düşük olabilir:

```env
# MIN_SCORE'u azalt
MIN_SCORE=65
```

### "Bot çalışmıyor"

```bash
# Loglara bak
cat pump_detector.log

# veya Windows'ta
type pump_detector.log

# En son 50 satırı göster
tail -50 pump_detector.log
```

---

## 7. İpuçları

### ✅ Yapılması Gerekenler

1. **Her zaman risk yönetimi uygula**: Bot %100 doğru değildir
2. **Stop-loss kullan**: Kayıpları sınırla
3. **Pozisyon boyutuna dikkat et**: Sermayenin %1-2'si ile trade yap
4. **Birden fazla sinyal bekle**: Tek sinyal yeterli değil
5. **Bybit'te manuel kontrol et**: Bot'un tespitini doğrula

### ❌ Yapılmaması Gerekenler

1. **Blind entry yapma**: Mutlaka grafiği kontrol et
2. **Tüm sinyallere girme**: Sadece en güçlülerine odaklan
3. **Over-leverage kullanma**: Düşük kaldıraç ile başla (2x-5x)
4. **Bot'u tek kaynak olarak görme**: Diğer analizlerle birleştir
5. **Panik yapma**: Soğukkanlı ol

---

## 8. En İyi Kullanım Stratejisi

### Sabah Rutini (09:00)
```bash
# Bot'u başlat
./start.sh

# İlk taramayı izle
# Piyasa durumunu gözlemle
```

### Gün İçi (09:00-22:00)
```
# Telegram bildirimlerini takip et
# Yüksek skorlu sinyalleri değerlendir (80+)
# Bybit'te grafiği kontrol et
# Entry/exit stratejin uygula
```

### Gece/İstirahat (22:00+)
```bash
# Bot'u durdur (isteğe bağlı)
# Ctrl+C ile durdur

# veya çalışır bırak (önerilen)
# Kritik sinyallerde uyarsın
```

---

## 9. Örnek Günlük Senaryo

**14:30** - Bot çalışıyor, piyasayı tarıyor

**14:32** - 🔥 Bildirim geldi!
```
ARBUSDT - Score: 87.3
5m: +4.2% | 1h: +9.8%
Extreme Volume Spike + Breakout
```

**14:33** - Bybit'i aç, grafiği kontrol et
- Volume spike ✓
- Güçlü yeşil mumlar ✓
- Direnç kırıldı ✓

**14:34** - Entry yap
- Entry: $1.245
- Stop-loss: $1.220 (-2%)
- Take-profit: $1.295 (+4%)

**14:42** - Take-profit! +4% kazanç 🎉

---

## 10. Ek Kaynaklar

### Log Dosyası
```bash
# Canlı log izle
tail -f pump_detector.log
```

### Konfigürasyon Dosyası
```bash
# .env dosyasını düzenle
nano .env    # Linux/Mac
notepad .env # Windows
```

### Yardım ve Destek
- README.md - Detaylı dokümantasyon
- test_setup.py - Konfigürasyon testi
- pump_detector.log - Hata logları

---

## 🎯 Başarılar!

Artık profesyonel bir pump detector bot'un var! 

**Unutma**: 
- Sabırlı ol
- Risk yönetimi uygula
- Sürekli öğren ve geliştir

**İyi trade'ler! 🚀**

---

## Hızlı Komutlar Özeti

```bash
# Kurulum
pip install -r requirements.txt

# Test
python test_setup.py

# Başlat
python main.py
# veya
./start.sh    # Linux/Mac
start.bat     # Windows

# Durdur
Ctrl+C

# Logları izle
tail -f pump_detector.log
```

**5 dakikada çalışır hale gelir! Let's pump! 🔥**
