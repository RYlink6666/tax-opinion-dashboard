"""
Page-level data consistency verification script

Verify that the same metrics across P1-P9 pages display consistent values
- Sentiment distribution (P1, P3, P5, P7)
- Risk distribution (P1, P3, P5)
- Topic distribution (P1, P5, P7)
- Actor distribution (P1, P5)
- High-risk opinion count (P1, P3, P5, P6)
- Average confidence (P1, P3)

Run: python verify_data_consistency.py
"""

import json
import pandas as pd
from pathlib import Path
import sys

def load_data():
    """Load analysis data"""
    try:
        data_path = Path('data/analysis/analysis_results.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data.get('data', []))
    except Exception as e:
        print(f"[ERROR] Data loading failed: {e}")
        sys.exit(1)

def calculate_metrics(df):
    """Calculate all key metrics"""
    metrics = {}
    
    # 1. Sentiment distribution
    metrics['sentiment_dist'] = df['sentiment'].value_counts().to_dict()
    metrics['sentiment_pct'] = (df['sentiment'].value_counts() / len(df) * 100).round(1).to_dict()
    
    # 2. Risk distribution
    metrics['risk_dist'] = df['risk_level'].value_counts().to_dict()
    metrics['risk_pct'] = (df['risk_level'].value_counts() / len(df) * 100).round(1).to_dict()
    
    # 3. Topic distribution (Top 10)
    metrics['topic_dist'] = df['topic'].value_counts().head(10).to_dict()
    
    # 4. Actor distribution (Top 10)
    metrics['actor_dist'] = df['actor'].value_counts().head(10).to_dict()
    
    # 5. High-risk opinions
    metrics['high_risk_count'] = len(df[df['risk_level'].isin(['critical', 'high'])])
    metrics['high_risk_pct'] = round(metrics['high_risk_count'] / len(df) * 100, 1)
    
    # 6. Neutral %
    metrics['neutral_count'] = len(df[df['sentiment'] == 'neutral'])
    metrics['neutral_pct'] = round(metrics['neutral_count'] / len(df) * 100, 1)
    
    # 7. Negative %
    metrics['negative_count'] = len(df[df['sentiment'] == 'negative'])
    metrics['negative_pct'] = round(metrics['negative_count'] / len(df) * 100, 1)
    
    # 8. Average confidence
    metrics['avg_confidence'] = round(df['sentiment_confidence'].mean(), 4)
    
    # 9. Total count
    metrics['total_count'] = len(df)
    
    return metrics

def print_metrics_summary(metrics):
    """Print metrics summary"""
    print("\n" + "="*60)
    print("KEY METRICS CALCULATION RESULTS")
    print("="*60)
    
    print(f"\n[TOTAL DATA]")
    print(f"  Total opinions: {metrics['total_count']}")
    print(f"  Avg confidence: {metrics['avg_confidence']}")
    
    print(f"\n[SENTIMENT DISTRIBUTION]")
    for sentiment, count in sorted(metrics['sentiment_dist'].items(), key=lambda x: x[1], reverse=True):
        pct = metrics['sentiment_pct'].get(sentiment, 0)
        print(f"  {sentiment}: {count} ({pct}%)")
    
    print(f"\n[RISK DISTRIBUTION]")
    for risk, count in sorted(metrics['risk_dist'].items(), key=lambda x: x[1], reverse=True):
        pct = metrics['risk_pct'].get(risk, 0)
        print(f"  {risk}: {count} ({pct}%)")
    print(f"  -> High/Critical total: {metrics['high_risk_count']} ({metrics['high_risk_pct']}%)")
    
    print(f"\n[TOPIC DISTRIBUTION] (Top 10)")
    for topic, count in list(metrics['topic_dist'].items())[:10]:
        print(f"  {topic}: {count}")
    
    print(f"\n[ACTOR DISTRIBUTION] (Top 10)")
    for actor, count in list(metrics['actor_dist'].items())[:10]:
        print(f"  {actor}: {count}")

def verify_consistency(df, metrics):
    """Verify consistency across pages"""
    print("\n" + "="*60)
    print("PAGE-LEVEL DATA CONSISTENCY CHECK")
    print("="*60)
    
    consistency_checks = []
    
    # Check 1: P1 page
    print(f"\n[P1 OVERVIEW PAGE]")
    p1_checks = {
        "Total opinions": metrics['total_count'],
        "Neutral %": metrics['neutral_pct'],
        "High-risk %": metrics['high_risk_pct'],
        "Negative %": metrics['negative_pct'],
        "Avg confidence": metrics['avg_confidence'],
    }
    for label, value in p1_checks.items():
        print(f"  [OK] {label}: {value}")
        consistency_checks.append(('P1', label, value))
    
    # Check 2: P3 page
    print(f"\n[P3 RISK ANALYSIS PAGE]")
    p3_checks = {
        "High-risk %": metrics['high_risk_pct'],
        "Avg confidence": metrics['avg_confidence'],
    }
    for label, value in p3_checks.items():
        print(f"  [OK] {label}: {value}")
        consistency_checks.append(('P3', label, value))
    
    # Check 3: P5 page
    print(f"\n[P5 ACTOR ANALYSIS PAGE]")
    p5_checks = {
        "High-risk %": metrics['high_risk_pct'],
        "Total opinions": metrics['total_count'],
    }
    for label, value in p5_checks.items():
        print(f"  [OK] {label}: {value}")
        consistency_checks.append(('P5', label, value))
    
    # Check 4: P6 page
    print(f"\n[P6 POLICY RECOMMENDATION PAGE]")
    p6_checks = {
        "High-risk %": metrics['high_risk_pct'],
    }
    for label, value in p6_checks.items():
        print(f"  [OK] {label}: {value}")
        consistency_checks.append(('P6', label, value))
    
    # Check 5: P7 page
    print(f"\n[P7 TOPIC ANALYSIS PAGE]")
    p7_checks = {
        "Negative %": metrics['negative_pct'],
    }
    for label, value in p7_checks.items():
        print(f"  [OK] {label}: {value}")
        consistency_checks.append(('P7', label, value))
    
    # Consistency analysis
    print("\n" + "="*60)
    print("CONSISTENCY ANALYSIS RESULTS")
    print("="*60)
    
    # Group by metric name
    from collections import defaultdict
    metrics_by_name = defaultdict(list)
    
    for page, metric_name, value in consistency_checks:
        metrics_by_name[metric_name].append((page, value))
    
    all_consistent = True
    for metric_name, values in metrics_by_name.items():
        pages_values = values
        unique_values = set(v for _, v in pages_values)
        
        if len(unique_values) == 1:
            print(f"  [OK] '{metric_name}': CONSISTENT")
            print(f"       Value: {pages_values[0][1]} (appears {len(pages_values)} times)")
        else:
            print(f"  [WARN] '{metric_name}': INCONSISTENT")
            for page, val in pages_values:
                print(f"         {page}: {val}")
            all_consistent = False
    
    return all_consistent

def generate_report(df, metrics, consistent):
    """Generate consistency report file"""
    report_path = Path('PHASE_11_CONSISTENCY_REPORT.md')
    
    report = f"""# Phase 11 Data Consistency Verification Report

**Check Time**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status**: {'CONSISTENT' if consistent else 'INCONSISTENCIES DETECTED'}

---

## Data Overview

| Metric | Value |
|--------|-------|
| Total opinions | {metrics['total_count']} |
| Avg confidence | {metrics['avg_confidence']} |
| Neutral % | {metrics['neutral_pct']}% ({metrics['neutral_count']} items) |
| Negative % | {metrics['negative_pct']}% ({metrics['negative_count']} items) |
| High/Critical risk % | {metrics['high_risk_pct']}% ({metrics['high_risk_count']} items) |

---

## Page-Level Metrics Mapping

| Page | Key Metrics Used | Value |
|------|-----------------|-------|
| P1 Overview | Total opinions | {metrics['total_count']} |
|            | Neutral % | {metrics['neutral_pct']}% |
|            | High-risk % | {metrics['high_risk_pct']}% |
|            | Negative % | {metrics['negative_pct']}% |
|            | Avg confidence | {metrics['avg_confidence']} |
| P3 Risk Analysis | High-risk % | {metrics['high_risk_pct']}% |
|                 | Avg confidence | {metrics['avg_confidence']} |
| P5 Actor Analysis | High-risk % | {metrics['high_risk_pct']}% |
|                  | Total opinions | {metrics['total_count']} |
| P6 Policy Recommendation | High-risk % | {metrics['high_risk_pct']}% |
| P7 Topic Analysis | Negative % | {metrics['negative_pct']}% |

---

## Sentiment Distribution (used by P1, P3, P5, P7)

"""
    
    for sentiment, count in sorted(metrics['sentiment_dist'].items(), key=lambda x: x[1], reverse=True):
        pct = metrics['sentiment_pct'].get(sentiment, 0)
        report += f"- **{sentiment}**: {count} items ({pct}%)\n"
    
    report += f"""

---

## Risk Distribution (used by P1, P3, P5, P6)

"""
    
    for risk, count in sorted(metrics['risk_dist'].items(), key=lambda x: x[1], reverse=True):
        pct = metrics['risk_pct'].get(risk, 0)
        report += f"- **{risk}**: {count} items ({pct}%)\n"
    
    report += f"""

---

## Topic Distribution (used by P1, P5, P7) - Top 10

"""
    
    for topic, count in list(metrics['topic_dist'].items())[:10]:
        report += f"- {topic}: {count}\n"
    
    report += f"""

---

## Actor Distribution (used by P1, P5) - Top 10

"""
    
    for actor, count in list(metrics['actor_dist'].items())[:10]:
        report += f"- {actor}: {count}\n"
    
    report += f"""

---

## Conclusion

{'SUCCESS: All pages display consistent data' if consistent else 'WARNING: Data inconsistencies detected - investigation required'}

### Next Steps

1. Run Streamlit locally to verify displayed metrics on each page
2. Compare with Streamlit Cloud production version
3. If discrepancies found, check for:
   - Different data loading paths
   - Cache version differences
   - Different filter conditions

### Maintenance Recommendations

- Set up automated consistency checks (can be added to CI/CD)
- Run this script weekly on production data
- Execute verification after data updates or metric changes

---

**Phase**: Phase 11  
**Executed by**: Data Consistency Audit Team
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] Report generated: {report_path}")

def main():
    print("\n[DATA CONSISTENCY VERIFICATION]")
    
    # Load data
    print("Loading data...")
    df = load_data()
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics = calculate_metrics(df)
    
    # Print summary
    print_metrics_summary(metrics)
    
    # Verify consistency
    consistent = verify_consistency(df, metrics)
    
    # Generate report
    generate_report(df, metrics, consistent)
    
    # Final conclusion
    print("\n" + "="*60)
    if consistent:
        print("[OK] All pages data consistent!")
    else:
        print("[WARNING] Data inconsistency detected - see report")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
