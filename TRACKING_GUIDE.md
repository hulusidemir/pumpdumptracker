# 📊 Signal Tracking & Performance Analysis

Bot artık tüm sinyalleri otomatik olarak kaydediyor ve performanslarını takip ediyor!

## 🎯 Nasıl Çalışır?

### 1. Otomatik Kayıt
Bot her sinyal gönderdiğinde:
```
✓ Coin adı
✓ Entry fiyatı
✓ Sinyal skoru
✓ Confidence seviyesi
✓ Tespit edilen sinyal tipleri
✓ Timestamp
```
Tüm bilgiler `signals_history.json` dosyasına kaydedilir.

### 2. Background Tracking
Arka planda çalışan bir thread sürekli olarak:
```
✓ 5 dakika sonra fiyatı kontrol eder
✓ 15 dakika sonra fiyatı kontrol eder
✓ 30 dakika sonra fiyatı kontrol eder
✓ 1 saat sonra fiyatı kontrol eder
✓ 4 saat sonra fiyatı kontrol eder
✓ 24 saat sonra fiyatı kontrol eder
```

### 3. Başarı Kriteri
Sinyal **başarılı** sayılır eğer:
- 1 saat içinde **%3 veya üzeri** artış yaparsa

### 4. Max Gain/Loss Tracking
Her coin için:
- En yüksek kazanç % kaydedilir
- En düşük kayıp % kaydedilir

---

## 📈 Raporları Görüntüleme

### Hızlı Yöntem - İnteraktif Viewer:
```bash
python view_report.py
```

Menüden seçim yapın:
```
1. Son 24 saat raporu
2. Son 1 hafta raporu
3. Tüm zamanlar raporu
4. Özet istatistikler
5. Raporu dosyaya kaydet
```

### Komut Satırı:
```bash
# Son 24 saat
python performance_analyzer.py

# Son 7 gün (168 saat)
python performance_analyzer.py 168

# Son 30 gün
python performance_analyzer.py 720
```

---

## 📊 Rapor İçeriği

### 1. Genel İstatistikler
```
Toplam Sinyal: 45
Tamamlanan Analiz: 38
Başarılı Sinyal: 27
Başarısız Sinyal: 11
Başarı Oranı: 71.1%

Ortalama Değişim (1h): +4.23%
Ortalama Değişim (4h): +6.78%

En Yüksek Kazanç: +23.45%
Ortalama Max Kazanç: +8.92%
En Düşük Kayıp: -5.67%
Ortalama Max Kayıp: -2.34%
```

### 2. Confidence Seviyelerine Göre
```
VERY_HIGH:
  • Toplam: 12 | Tamamlanan: 10
  • Başarılı: 9 | Accuracy: 90.0%
  • Ort. Değişim (1h): +6.45%

HIGH:
  • Toplam: 18 | Tamamlanan: 16
  • Başarılı: 12 | Accuracy: 75.0%
  • Ort. Değişim (1h): +4.23%

MEDIUM:
  • Toplam: 15 | Tamamlanan: 12
  • Başarılı: 6 | Accuracy: 50.0%
  • Ort. Değişim (1h): +2.11%
```

### 3. Sinyal Tiplerine Göre
```
En Başarılı Sinyal Tipleri:
  • EXTREME_VOLUME_SPIKE: 85.7% (12/14)
  • MOMENTUM_ACCELERATION: 80.0% (8/10)
  • BREAKOUT_PATTERN: 75.0% (9/12)
  • STRONG_BUY_PRESSURE: 71.4% (10/14)
  • STRONG_5M_MOMENTUM: 68.2% (15/22)
```

### 4. En İyi ve En Kötü Sinyaller
```
🥇 En Başarılı 5 Sinyal:
1. ARBUSDT - Score: 87.3 (VERY_HIGH)
   Entry: $1.2345 | Max Gain: +23.45%
   Time: 2026-01-16 14:32

2. OPUSDT - Score: 84.2 (VERY_HIGH)
   Entry: $2.3456 | Max Gain: +18.92%
   Time: 2026-01-16 15:15

...
```

### 5. Zaman Bazlı Analiz
```
Saate Göre Başarı Oranı:
  • 09:00 - 82.3% (14/17)
  • 10:00 - 75.0% (9/12)
  • 14:00 - 71.4% (10/14)
  • 15:00 - 68.0% (17/25)
```

---

## 💡 Raporları Anlama

### Başarı Oranı Nedir?
- **%70+**: Mükemmel! Bot çok iyi çalışıyor
- **%60-70**: İyi! Güvenilir sonuçlar
- **%50-60**: Orta! Ayarlar iyileştirilebilir
- **<%50**: Zayıf! Threshold'ları artır

### Hangi Confidence'a Güvenelim?
```
VERY_HIGH (85+): 
  - En güvenilir
  - %70-90 accuracy beklenir
  - Mutlaka incele

HIGH (75-84):
  - Güvenilir
  - %60-75 accuracy beklenir
  - Detaylı bak

MEDIUM (65-74):
  - Orta güvenilir
  - %40-60 accuracy beklenir
  - Dikkatli ol
```

### Hangi Sinyal Tipleri Daha İyi?
Raporda göreceksin! Genelde:
```
✅ En Güvenilir:
  - EXTREME_VOLUME_SPIKE
  - MOMENTUM_ACCELERATION
  - BREAKOUT_PATTERN

⚠️  Dikkatli Olunması Gereken:
  - Tek başına RSI sinyalleri
  - Funding rate değişimleri
  - Zayıf volume spike'lar
```

---

## 🔧 Ayarları Optimize Etme

### Bot Çok Az Başarılıysa (%50 altı):

**1. MIN_SCORE'u artır:**
```env
MIN_SCORE=80  # 70'ten 80'e çıkar
```
Sadece çok güçlü sinyalleri alırsın.

**2. Daha likit piyasalara odaklan:**
```env
MIN_VOLUME_24H=1000000  # 500k'dan 1M'a çıkar
```

**3. Confidence filtrele:**
Sadece VERY_HIGH ve HIGH sinyalleri değerlendir.

### Bot Az Sinyal Veriyorsa:

**1. MIN_SCORE'u azalt:**
```env
MIN_SCORE=65  # 70'ten 65'e indir
```

**2. Tarama sıklığını artır:**
```env
SCAN_INTERVAL=60  # 90'dan 60'a indir
```

---

## 📁 Dosyalar

### `signals_history.json`
Tüm sinyallerin ham verileri:
```json
{
  "ARBUSDT_20260116_143215": {
    "id": "ARBUSDT_20260116_143215",
    "coin": "ARBUSDT",
    "timestamp": "2026-01-16T14:32:15",
    "entry_price": 1.2345,
    "score": 87.3,
    "confidence": "VERY_HIGH",
    "signals": ["EXTREME_VOLUME_SPIKE", "MOMENTUM_ACCELERATION"],
    "price_5m": 1.2456,
    "price_15m": 1.2567,
    "price_1h": 1.2734,
    "change_5m": 0.90,
    "change_15m": 1.80,
    "change_1h": 3.15,
    "max_gain": 4.23,
    "max_loss": -0.45,
    "success": true
  }
}
```

### `performance_report_*.txt`
Oluşturulan raporlar kaydedilir:
```
performance_report_20260116_153045.txt
performance_report_20260117_090012.txt
```

---

## 🎯 Kullanım Örnekleri

### Senaryo 1: Günlük Kontrol
```bash
# Sabah bot'u başlat
python main.py

# Akşam performansa bak
python view_report.py
# Seçenek 1 (son 24 saat)

# Hangi confidence daha başarılı?
# Hangi saat dilimleri daha iyi?
# Ayarları ona göre optimize et
```

### Senaryo 2: Haftalık Analiz
```bash
# Hafta sonu detaylı analiz
python view_report.py
# Seçenek 2 (son 1 hafta)

# Hangi sinyal tipleri en başarılı?
# Hangi coinler tekrar ediyor?
# Pattern'leri öğren
```

### Senaryo 3: A/B Testing
```bash
# 1. Hafta:
MIN_SCORE=70
# Sonuçlara bak

# 2. Hafta:
MIN_SCORE=80
# Sonuçlara bak

# Hangisi daha iyi? Onu kullan!
```

---

## ⚠️  Önemli Notlar

### 1. İlk Sonuçlar İçin Bekle
- En az **1 saat** beklemen gerek
- Bot sinyalleri kaydeder ama hemen sonuç göremezsin
- 1 saat sonra ilk success/fail bilgileri gelir

### 2. 24 Saat İzleniyor
- Her sinyal 24 saat boyunca takip edilir
- Max gain/loss sürekli güncellenir
- 24 saat sonra tracking durur

### 3. Background Thread
- Tracker arka planda çalışır
- Bot'u kapatsan bile veriler kayıtlıdır
- Tekrar başlatınca kaldığı yerden devam eder

### 4. Dosya Boyutu
- `signals_history.json` büyüyebilir
- 1000 sinyal ~1-2 MB
- Eski verileri manuel silebilirsin

---

## 📊 Örnek Çıktı

```
══════════════════════════════════════════════════════════════════
📊 PUMP DETECTOR BOT - PERFORMANS RAPORU
⏰ Zaman Aralığı: Son 24 saat
📅 Rapor Tarihi: 2026-01-16 20:30:45
══════════════════════════════════════════════════════════════════

📈 GENEL İSTATİSTİKLER
──────────────────────────────────────────────────────────────────
Toplam Sinyal: 23
Tamamlanan Analiz: 18
Başarılı Sinyal: 13
Başarısız Sinyal: 5
Başarı Oranı: 72.2%

Ortalama Değişim (1h): +4.56%
Ortalama Değişim (4h): +6.89%

En Yüksek Kazanç: +18.92%
Ortalama Max Kazanç: +7.34%
En Düşük Kayıp: -3.45%
Ortalama Max Kayıp: -1.67%

🎯 CONFIDENCE SEVİYELERİNE GÖRE ANALİZ
──────────────────────────────────────────────────────────────────
VERY_HIGH:
  • Toplam: 6 | Tamamlanan: 5
  • Başarılı: 5 | Accuracy: 100.0%
  • Ort. Değişim (1h): +7.89%

HIGH:
  • Toplam: 10 | Tamamlanan: 8
  • Başarılı: 6 | Accuracy: 75.0%
  • Ort. Değişim (1h): +4.12%

MEDIUM:
  • Toplam: 7 | Tamamlanan: 5
  • Başarılı: 2 | Accuracy: 40.0%
  • Ort. Değişim (1h): +1.23%

══════════════════════════════════════════════════════════════════
```

---

## 🚀 Sonraki Adımlar

1. **Bot'u çalıştır**: `python main.py`
2. **Birkaç saat bekle**: En az 1 saat
3. **Raporu kontrol et**: `python view_report.py`
4. **Optimize et**: Ayarları iyileştir
5. **Tekrar et**: Sürekli öğren ve geliştir

---

## 💡 Pro Tips

1. **VERY_HIGH sinyallere odaklan**: %90+ accuracy
2. **Sabah saatleri genelde iyi**: Volume yüksek
3. **Confluence sinyaller daha başarılı**: 3+ sinyal tipi
4. **Her hafta raporları incele**: Pattern'leri öğren
5. **A/B testing yap**: Farklı ayarları dene

---

**Artık bot'un ne kadar başarılı olduğunu görebilirsin! 📊📈**

Good luck with your analysis! 🚀
