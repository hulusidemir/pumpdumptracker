#!/usr/bin/env python3
"""
View Performance Report - Quick tool to view signal tracking results
"""

import sys
import os
from performance_analyzer import PerformanceAnalyzer


def print_menu():
    """Print menu options"""
    print("\n" + "="*70)
    print("📊 SIGNAL PERFORMANCE VIEWER")
    print("="*70)
    print("\nSeçenekler:")
    print("  1. Son 24 saat raporu")
    print("  2. Son 1 hafta raporu")
    print("  3. Tüm zamanlar raporu")
    print("  4. Özet istatistikler")
    print("  5. Raporu dosyaya kaydet")
    print("  0. Çıkış")
    print()


def main():
    """Main function"""
    
    # Check if signals file exists
    if not os.path.exists("signals_history.json"):
        print("\n❌ Henüz kayıtlı sinyal yok!")
        print("Bot'u çalıştırın ve sinyallerin kaydedilmesini bekleyin.\n")
        return
    
    analyzer = PerformanceAnalyzer()
    
    while True:
        print_menu()
        choice = input("Seçiminiz (0-5): ").strip()
        
        if choice == '0':
            print("\n👋 Görüşmek üzere!\n")
            break
        
        elif choice == '1':
            print("\n" + analyzer.generate_report(hours=24))
            input("\nDevam etmek için Enter'a basın...")
        
        elif choice == '2':
            print("\n" + analyzer.generate_report(hours=168))  # 7 days
            input("\nDevam etmek için Enter'a basın...")
        
        elif choice == '3':
            print("\n" + analyzer.generate_report(hours=8760))  # 1 year
            input("\nDevam etmek için Enter'a basın...")
        
        elif choice == '4':
            summary = analyzer.get_summary()
            print("\n" + "="*70)
            print("📊 ÖZET İSTATİSTİKLER")
            print("="*70)
            
            if summary.get('completed', 0) == 0:
                print("\n⏳ Henüz tamamlanan analiz yok")
                print("En az 1 saat bekleyin...")
            else:
                print(f"\nToplam Sinyal: {summary['total_signals']}")
                print(f"Tamamlanan Analiz: {summary['completed']}")
                print(f"Başarılı Sinyal: {summary['successful']}")
                print(f"Başarı Oranı: {summary['success_rate']:.1f}%")
                print(f"\nOrtalama Değişim (1h): {summary['avg_change_1h']:+.2f}%")
                print(f"En İyi Kazanç: +{summary['best_gain']:.2f}%")
                print(f"En Kötü Kayıp: {summary['worst_loss']:.2f}%")
            
            print("="*70)
            input("\nDevam etmek için Enter'a basın...")
        
        elif choice == '5':
            hours = input("\nKaç saatlik rapor? (varsayılan: 24): ").strip()
            try:
                hours = int(hours) if hours else 24
            except:
                hours = 24
            
            filename = analyzer.save_report(hours=hours)
            if filename:
                print(f"\n✅ Rapor kaydedildi: {filename}")
            else:
                print("\n❌ Rapor kaydedilemedi!")
            
            input("\nDevam etmek için Enter'a basın...")
        
        else:
            print("\n❌ Geçersiz seçim!")
            input("\nDevam etmek için Enter'a basın...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Görüşmek üzere!\n")
    except Exception as e:
        print(f"\n❌ Hata: {e}\n")
