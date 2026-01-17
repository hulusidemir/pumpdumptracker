"""
Performance Analyzer - Analyzes signal performance and generates reports
"""

import json
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    Analyzes signal tracker data and generates performance reports
    """
    
    def __init__(self, signals_file: str = "signals_history.json"):
        self.signals_file = signals_file
        self.signals = self._load_signals()
    
    def _load_signals(self) -> List[Dict]:
        """Load signals from file"""
        try:
            with open(self.signals_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return list(data.values())
        except Exception as e:
            logger.error(f"Error loading signals: {e}")
            return []
    
    def refresh_data(self):
        """Reload signals from file"""
        self.signals = self._load_signals()
    
    def generate_report(self, hours: int = 24) -> str:
        """
        Generate comprehensive performance report
        """
        self.refresh_data()
        
        if not self.signals:
            return "📊 PERFORMANS RAPORU\n\n❌ Henüz kayıtlı sinyal yok."
        
        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_signals = [
            s for s in self.signals 
            if datetime.fromisoformat(s['timestamp']) >= cutoff
        ]
        
        if not recent_signals:
            return f"📊 PERFORMANS RAPORU (Son {hours}h)\n\n❌ Bu zaman aralığında sinyal yok."
        
        # Build report
        report = []
        report.append("=" * 70)
        report.append(f"📊 PUMP DETECTOR BOT - PERFORMANS RAPORU")
        report.append(f"⏰ Zaman Aralığı: Son {hours} saat")
        report.append(f"📅 Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")
        
        # Overall statistics
        report.extend(self._overall_stats(recent_signals))
        report.append("")
        
        # Confidence breakdown
        report.extend(self._confidence_analysis(recent_signals))
        report.append("")
        
        # Signal type analysis
        report.extend(self._signal_type_analysis(recent_signals))
        report.append("")
        
        # Best and worst signals
        report.extend(self._best_worst_signals(recent_signals))
        report.append("")
        
        # Time-based analysis
        report.extend(self._time_analysis(recent_signals))
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def _overall_stats(self, signals: List[Dict]) -> List[str]:
        """Overall statistics"""
        lines = []
        lines.append("📈 GENEL İSTATİSTİKLER")
        lines.append("-" * 70)
        
        total = len(signals)
        completed = [s for s in signals if s.get('success') is not None]
        
        lines.append(f"Toplam Sinyal: {total}")
        lines.append(f"Tamamlanan Analiz: {len(completed)}")
        
        if not completed:
            lines.append("\n⏳ Henüz tamamlanan analiz yok (1 saat beklenmeli)")
            return lines
        
        successful = sum(1 for s in completed if s.get('success'))
        success_rate = (successful / len(completed) * 100) if completed else 0
        
        lines.append(f"Başarılı Sinyal: {successful}")
        lines.append(f"Başarısız Sinyal: {len(completed) - successful}")
        lines.append(f"Başarı Oranı: {success_rate:.1f}%")
        
        # Average changes
        changes_1h = [s['change_1h'] for s in completed if s.get('change_1h') is not None]
        changes_4h = [s['change_4h'] for s in completed if s.get('change_4h') is not None]
        
        if changes_1h:
            lines.append(f"\nOrtalama Değişim (1h): {sum(changes_1h)/len(changes_1h):+.2f}%")
        if changes_4h:
            lines.append(f"Ortalama Değişim (4h): {sum(changes_4h)/len(changes_4h):+.2f}%")
        
        # Max gains/losses
        max_gains = [s['max_gain'] for s in completed if s.get('max_gain') is not None]
        max_losses = [s['max_loss'] for s in completed if s.get('max_loss') is not None]
        
        if max_gains:
            lines.append(f"\nEn Yüksek Kazanç: +{max(max_gains):.2f}%")
            lines.append(f"Ortalama Max Kazanç: +{sum(max_gains)/len(max_gains):.2f}%")
        
        if max_losses:
            lines.append(f"En Düşük Kayıp: {min(max_losses):.2f}%")
            lines.append(f"Ortalama Max Kayıp: {sum(max_losses)/len(max_losses):.2f}%")
        
        return lines
    
    def _confidence_analysis(self, signals: List[Dict]) -> List[str]:
        """Confidence level breakdown"""
        lines = []
        lines.append("🎯 CONFIDENCE SEVİYELERİNE GÖRE ANALİZ")
        lines.append("-" * 70)
        
        for confidence in ['VERY_HIGH', 'HIGH', 'MEDIUM', 'LOW']:
            conf_signals = [s for s in signals if s['confidence'] == confidence]
            if not conf_signals:
                continue
            
            completed = [s for s in conf_signals if s.get('success') is not None]
            if not completed:
                lines.append(f"{confidence}: {len(conf_signals)} sinyal (henüz tamamlanmadı)")
                continue
            
            successful = sum(1 for s in completed if s.get('success'))
            accuracy = (successful / len(completed) * 100) if completed else 0
            
            avg_change_1h = sum(s['change_1h'] for s in completed if s.get('change_1h')) / len(completed)
            
            lines.append(f"{confidence}:")
            lines.append(f"  • Toplam: {len(conf_signals)} | Tamamlanan: {len(completed)}")
            lines.append(f"  • Başarılı: {successful} | Accuracy: {accuracy:.1f}%")
            lines.append(f"  • Ort. Değişim (1h): {avg_change_1h:+.2f}%")
        
        return lines
    
    def _signal_type_analysis(self, signals: List[Dict]) -> List[str]:
        """Signal type effectiveness"""
        lines = []
        lines.append("🔍 SİNYAL TİPLERİNE GÖRE ANALİZ")
        lines.append("-" * 70)
        
        # Count signal types in successful vs failed
        signal_success = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        for s in signals:
            if s.get('success') is None:
                continue
            
            for signal_type in s.get('signals', []):
                signal_success[signal_type]['total'] += 1
                if s['success']:
                    signal_success[signal_type]['successful'] += 1
        
        if not signal_success:
            lines.append("Henüz tamamlanan sinyal yok")
            return lines
        
        # Sort by accuracy
        sorted_signals = sorted(
            signal_success.items(),
            key=lambda x: x[1]['successful'] / x[1]['total'] if x[1]['total'] > 0 else 0,
            reverse=True
        )
        
        lines.append("En Başarılı Sinyal Tipleri:")
        for signal_type, stats in sorted_signals[:10]:
            if stats['total'] < 3:  # Skip rare signals
                continue
            accuracy = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            lines.append(f"  • {signal_type}: {accuracy:.1f}% ({stats['successful']}/{stats['total']})")
        
        return lines
    
    def _best_worst_signals(self, signals: List[Dict]) -> List[str]:
        """Best and worst performing signals"""
        lines = []
        lines.append("🏆 EN İYİ VE EN KÖTÜ SİNYALLER")
        lines.append("-" * 70)
        
        completed = [s for s in signals if s.get('max_gain') is not None]
        if not completed:
            lines.append("Henüz tamamlanan sinyal yok")
            return lines
        
        # Best signals
        best = sorted(completed, key=lambda x: x['max_gain'], reverse=True)[:5]
        lines.append("\n🥇 En Başarılı 5 Sinyal:")
        for i, s in enumerate(best, 1):
            lines.append(f"{i}. {s['coin']} - Score: {s['score']:.1f} ({s['confidence']})")
            lines.append(f"   Entry: ${s['entry_price']:.4f} | Max Gain: +{s['max_gain']:.2f}%")
            lines.append(f"   Time: {datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d %H:%M')}")
        
        # Worst signals
        worst = sorted(completed, key=lambda x: x.get('max_loss', 0))[:5]
        lines.append("\n🥉 En Kötü 5 Sinyal:")
        for i, s in enumerate(worst, 1):
            lines.append(f"{i}. {s['coin']} - Score: {s['score']:.1f} ({s['confidence']})")
            lines.append(f"   Entry: ${s['entry_price']:.4f} | Max Loss: {s.get('max_loss', 0):.2f}%")
            lines.append(f"   Time: {datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d %H:%M')}")
        
        return lines
    
    def _time_analysis(self, signals: List[Dict]) -> List[str]:
        """Time-based performance analysis"""
        lines = []
        lines.append("⏱️  ZAMAN BAZLI ANALİZ")
        lines.append("-" * 70)
        
        completed = [s for s in signals if s.get('success') is not None]
        if not completed:
            lines.append("Henüz tamamlanan sinyal yok")
            return lines
        
        # Group by hour
        hour_stats = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        for s in completed:
            hour = datetime.fromisoformat(s['timestamp']).hour
            hour_stats[hour]['total'] += 1
            if s['success']:
                hour_stats[hour]['successful'] += 1
        
        lines.append("\nSaate Göre Başarı Oranı (en az 3 sinyal):")
        for hour in sorted(hour_stats.keys()):
            stats = hour_stats[hour]
            if stats['total'] < 3:
                continue
            accuracy = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            lines.append(f"  • {hour:02d}:00 - {accuracy:.1f}% ({stats['successful']}/{stats['total']})")
        
        return lines
    
    def save_report(self, filename: str = None, hours: int = 24):
        """Save report to file"""
        if filename is None:
            filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        report = self.generate_report(hours)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return None
    
    def get_summary(self) -> Dict:
        """Get quick summary statistics"""
        self.refresh_data()
        
        if not self.signals:
            return {'total_signals': 0}
        
        completed = [s for s in self.signals if s.get('success') is not None]
        
        if not completed:
            return {
                'total_signals': len(self.signals),
                'completed': 0,
                'message': 'Waiting for analysis completion'
            }
        
        successful = sum(1 for s in completed if s.get('success'))
        
        return {
            'total_signals': len(self.signals),
            'completed': len(completed),
            'successful': successful,
            'success_rate': (successful / len(completed) * 100) if completed else 0,
            'avg_change_1h': sum(s['change_1h'] for s in completed if s.get('change_1h')) / len(completed),
            'best_gain': max(s['max_gain'] for s in completed if s.get('max_gain')),
            'worst_loss': min(s['max_loss'] for s in completed if s.get('max_loss'))
        }


# Command-line tool
if __name__ == "__main__":
    import sys
    
    analyzer = PerformanceAnalyzer()
    
    # Parse arguments
    hours = 24
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except:
            pass
    
    # Generate and print report
    report = analyzer.generate_report(hours)
    print(report)
    
    # Save to file
    filename = analyzer.save_report(hours=hours)
    if filename:
        print(f"\n✅ Rapor kaydedildi: {filename}")
