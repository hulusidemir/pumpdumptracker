# 🚀 Professional Crypto Pump Detector Bot

Bybit USDT Perpetual Futures için profesyonel pump tespit sistemi. Gün içerisinde %10-100 artış yapabilecek coinleri gerçek zamanlı olarak tespit eder ve Telegram'dan bildirim gönderir.

## 🎯 Özellikler

### 🆕 Performans Tracking Sistemi
- **Otomatik Sinyal Kaydı**: Her sinyal detaylarıyla kaydedilir
- **Background Price Tracking**: 5m, 15m, 30m, 1h, 4h, 24h fiyat takibi
- **Başarı Analizi**: Hangi sinyaller tuttu, hangileri tutmadı
- **Detaylı Raporlar**: Confidence, sinyal tipi, zaman bazlı analiz
- **Performans Metrikleri**: Success rate, average gain, best/worst signals
- **İnteraktif Viewer**: Raporları kolayca görüntüle

### Çok Katmanlı Sinyal Analizi
- **Volume Spike Detection**: Ani hacim artışlarını tespit eder (3x-5x normal hacim)
- **Price Momentum Analysis**: 5m, 15m, 1h timeframe'lerde fiyat momentumu
- **Order Book Imbalance**: Alım/satım emirlerindeki dengesizlik analizi
- **Large Order Detection**: Büyük alım emirlerini tespit eder ($100k+)
- **Funding Rate Analysis**: Funding rate değişimlerini izler
- **Open Interest Tracking**: Open Interest artışlarını takip eder
- **Breakout Pattern Detection**: Konsolidasyon sonrası patlama pattern'leri

### Akıllı Filtreleme
- 3 aşamalı filtreleme sistemi (hızlı ön eleme → derin analiz)
- Paralel işleme ile 200+ coin'i dakikalar içinde tarar
- Sadece likit piyasalara odaklanır ($500k+ günlük hacim)
- Adaptif watchlist ile önemli coinlere öncelik verir

### Profesyonel Skorlama
- 0-100 arası pump skoru
- Confidence seviyeleri: LOW, MEDIUM, HIGH, VERY_HIGH
- Signal confluence (birden fazla sinyalin birleşimi)
- Ağırlıklı skorlama sistemi

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- Telegram hesabı
- İnternet bağlantısı

## 🔧 Kurulum

### 1. Projeyi İndir

```bash
cd "New Folder"
```

### 2. Python Paketlerini Kur

```bash
pip install -r requirements.txt
```

### 3. Telegram Bot Kurulumu

#### a) Bot Oluştur
1. Telegram'da [@BotFather](https://t.me/BotFather) 'a git
2. `/newbot` komutunu kullan
3. Bot için isim ve kullanıcı adı belirle
4. Bot token'ı kopyala (örn: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

#### b) Chat ID Bul
1. Telegram'da [@userinfobot](https://t.me/userinfobot) 'a git
2. `/start` komutunu gönder
3. Chat ID'ni kopyala (örn: `123456789`)

### 4. Konfigürasyon

`.env.example` dosyasını `.env` olarak kopyala:

```bash
cp .env.example .env
```

`.env` dosyasını düzenle ve Telegram bilgilerini gir:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Opsiyonel**: Bybit API key'i eklersen rate limit'ler artar (ama gerekli değil):

```env
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
```

## 🚀 Kullanım

### Basit Başlatma (Tracking Otomatik)

```bash
python main.py
```

### Linux/Mac için Script

```bash
chmod +x start.sh
./start.sh
```

### Windows için Script

```
start.bat
```

### Durdurma

`Ctrl+C` ile durdur

### 📊 Performans Raporlarını Görüntüle

Bot çalışırken veya durduktan sonra:

```bash
# İnteraktif viewer
python view_report.py

# Veya komut satırından
python performance_analyzer.py        # Son 24 saat
python performance_analyzer.py 168    # Son 1 hafta
```

**Detaylı kullanım için**: [TRACKING_GUIDE.md](TRACKING_GUIDE.md)

## ⚙️ Konfigürasyon Parametreleri

### Tarama Ayarları

```env
SCAN_INTERVAL=90              # Tarama aralığı (saniye)
                             # 60-120: Yüksek frekanslı tarama
                             # 120-300: Normal tarama
MAX_WORKERS=10                # Paralel thread sayısı
                             # 5-10: Orta güçlü PC
                             # 10-15: Güçlü PC
```

### Filtreleme Eşikleri

```env
MIN_VOLUME_24H=500000         # Minimum günlük hacim ($)
                             # 100k-500k: Küçük coinler dahil
                             # 500k-1M: Orta likit coinler
                             # 1M+: Sadece çok likit coinler

MIN_SCORE=70                  # Minimum pump skoru
                             # 60-65: Çok fazla sinyal (düşük kalite)
                             # 70-75: Dengeli (önerilen)
                             # 80+: Çok az ama çok güçlü sinyaller
```

### Bildirim Ayarları

```env
MAX_NOTIFICATIONS=5           # Tarama başına max bildirim
NOTIFICATION_COOLDOWN=900     # Aynı coin için bekleme süresi (sn)
```

## 📊 Sinyal Tipleri ve Anlamları

### Volume Sinyalleri
- **EXTREME_VOLUME_SPIKE** (95 pts): 5x+ normal hacim - Çok güçlü sinyal
- **VOLUME_SPIKE** (75 pts): 3x+ normal hacim - Güçlü sinyal
- **ELEVATED_VOLUME** (50 pts): 2x normal hacim - Orta sinyal

### Momentum Sinyalleri
- **MOMENTUM_ACCELERATION** (85 pts): Artan momentum - Çok güçlü
- **STRONG_5M_MOMENTUM** (70+ pts): 5 dakikada %2+ hareket
- **STRONG_15M_MOMENTUM** (60+ pts): 15 dakikada %5+ hareket
- **STRONG_1H_MOMENTUM** (50+ pts): 1 saatte %8+ hareket

### Order Book Sinyalleri
- **EXTREME_BUY_PRESSURE** (90 pts): 3.5:1 alım/satım oranı
- **STRONG_BUY_PRESSURE** (70 pts): 2:1 alım/satım oranı
- **LARGE_BUY_ORDERS** (60+ pts): $100k+ büyük alım emirleri

### Diğer Sinyaller
- **BREAKOUT_PATTERN** (80 pts): Konsolidasyon sonrası patlama
- **OPEN_INTEREST_SURGE** (60+ pts): %15+ OI artışı
- **FUNDING_RATE_SPIKE** (50+ pts): Ani funding rate değişimi

## 🎯 Confidence Seviyeleri

- **VERY_HIGH** (85+): En güçlü sinyaller, çoklu sinyal konfirmasyonu
- **HIGH** (75-84): Güçlü sinyaller, yüksek olasılık
- **MEDIUM** (65-74): Orta sinyaller, dikkatli takip
- **LOW** (<65): Zayıf sinyaller, filtrelenir

## 📱 Telegram Bildirimi Örneği

```
🔥🔥🔥 PUMP ALERT #1 🔥🔥🔥

Symbol: ETHUSDT
Score: 87.5/100
Confidence: VERY_HIGH

📊 Price Action:
🟢 5m: +3.42%
🟢 1h: +8.76%
💰 Price: $2,345.67

📈 Volume:
24h Volume: $1,234,567,890

🎯 Detected Signals:
🚀 Extreme Volume Spike (95)
🚀 Momentum Acceleration (85)
⚡ Strong Buy Pressure (75)
⚡ Breakout Pattern (80)
📊 Large Buy Orders (70)

📱 Open on Bybit

⏰ 14:32:15
```

## 🛠️ Troubleshooting

### Bot Başlamıyor
```bash
# Loglara bak
cat pump_detector.log

# Python versiyonunu kontrol et
python --version  # 3.8+ olmalı

# Paketleri tekrar yükle
pip install -r requirements.txt --upgrade
```

### Telegram Bildirimleri Gelmiyor
- Bot token'ı doğru mu?
- Chat ID doğru mu?
- Bot'u Telegram'da başlattın mı? (Bot'a `/start` gönder)
- Firewall/antivirus engelliyor olabilir

### Çok Az Sinyal Geliyor
```env
# MIN_SCORE'u düşür
MIN_SCORE=65

# SCAN_INTERVAL'i kısalt
SCAN_INTERVAL=60
```

### Çok Fazla Sinyal Geliyor
```env
# MIN_SCORE'u yükselt
MIN_SCORE=80

# MAX_NOTIFICATIONS'ı azalt
MAX_NOTIFICATIONS=3
```

## 🔒 Güvenlik Notları

- **Bot İŞLEM YAPMAZ**: Sadece okuma yapan bir analiz botu
- API key'leri `.env` dosyasında saklan
- `.env` dosyasını asla paylaşma
- Public endpoint'ler kullanıldığı için API key opsiyonel

## 📈 Performans İpuçları

### Yüksek Doğruluk için:
```env
MIN_SCORE=80                  # Sadece çok güçlü sinyaller
MAX_NOTIFICATIONS=3           # Az ama öz
MIN_VOLUME_24H=1000000        # Sadece likit coinler
```

### Daha Fazla Sinyal için:
```env
MIN_SCORE=65                  # Daha fazla sinyal
MAX_NOTIFICATIONS=8           # Daha fazla bildirim
MIN_VOLUME_24H=250000         # Küçük coinler dahil
```

### Scalping için (Yüksek Frekanslı):
```env
SCAN_INTERVAL=60              # 1 dakikada bir tara
MIN_SCORE=75
MIN_PRICE_CHANGE_5M=2.0       # En az %2 hareket
```

## 📊 Önerilen Kullanım Stratejisi

1. **İlk Kurulum**: `MIN_SCORE=75` ile başla, sistemi tanı
2. **İzleme**: 1-2 gün sinyalleri takip et, doğruluğu gözlemle
3. **Optimizasyon**: Sonuçlara göre MIN_SCORE'u ayarla
4. **Scalping**: 60-90 saniyelik tarama ile kullan
5. **Swing Trading**: 300 saniyelik tarama ile daha büyük hareketleri yakala

## 🎓 Sinyal Yorumlama

### Çok Güçlü Sinyal (87+)
- Birden fazla güçlü sinyal konfirmasyonu
- Yüksek volume spike + momentum + order book
- Hızlı inceleme gerektirir

### Güçlü Sinyal (75-86)
- 2-3 güçlü sinyal konfirmasyonu
- İyi takip sinyali
- Detaylı analiz yap

### Orta Sinyal (65-74)
- Tek güçlü sinyal veya birden fazla zayıf sinyal
- Dikkatli takip
- Diğer sinyallerle beraber değerlendir

## 💡 Pro Tips

1. **Birden Fazla Timeframe Kullan**: 5m, 15m, 1h sinyallerini birlikte değerlendir
2. **Volume Spike En Güçlü Sinyal**: Volume spike + price momentum = altın kombinasyon
3. **Order Book İzle**: Büyük alım emirleri güçlü sinyal
4. **Watchlist Özelliği**: Bot önemli coinleri otomatik takip eder
5. **Cooldown Sistemi**: Aynı coin için spam önleme

## 📞 Destek

Sorularınız için:
- Log dosyasını inceleyin: `pump_detector.log`
- Hata mesajlarını kontrol edin
- Konfigürasyonu gözden geçirin

## ⚠️ Sorumluluk Reddi

Bu bot sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir. Kripto para yatırımları risklidir. Kendi araştırmanızı yapın ve risk yönetimi uygulayın.

## 🚀 İyi Trade'ler!

**Unutma**: En iyi bot bile %100 doğruluk sağlayamaz. Her zaman risk yönetimi uygula, stop-loss kullan ve pozisyon boyutlarına dikkat et.

---

Made with 🔥 for professional crypto traders
