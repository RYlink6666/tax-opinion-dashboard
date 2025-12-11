# Phase 11 Data Consistency Verification Report

**Check Time**: 2025-12-12 01:20:53  
**Status**: CONSISTENT

---

## Data Overview

| Metric | Value |
|--------|-------|
| Total opinions | 2297 |
| Avg confidence | 0.8795 |
| Neutral % | 63.1% (1450 items) |
| Negative % | 22.4% (515 items) |
| High/Critical risk % | 5.9% (136 items) |

---

## Page-Level Metrics Mapping

| Page | Key Metrics Used | Value |
|------|-----------------|-------|
| P1 Overview | Total opinions | 2297 |
|            | Neutral % | 63.1% |
|            | High-risk % | 5.9% |
|            | Negative % | 22.4% |
|            | Avg confidence | 0.8795 |
| P3 Risk Analysis | High-risk % | 5.9% |
|                 | Avg confidence | 0.8795 |
| P5 Actor Analysis | High-risk % | 5.9% |
|                  | Total opinions | 2297 |
| P6 Policy Recommendation | High-risk % | 5.9% |
| P7 Topic Analysis | Negative % | 22.4% |

---

## Sentiment Distribution (used by P1, P3, P5, P7)

- **neutral**: 1450 items (63.1%)
- **negative**: 515 items (22.4%)
- **positive**: 325 items (14.1%)
- **negative|positive**: 5 items (0.2%)
- **positive|neutral**: 1 items (0.0%)
- **negative|neutral**: 1 items (0.0%)


---

## Risk Distribution (used by P1, P3, P5, P6)

- **low**: 1499 items (65.3%)
- **medium**: 662 items (28.8%)
- **high**: 136 items (5.9%)


---

## Topic Distribution (used by P1, P5, P7) - Top 10

- other: 845
- tax_policy: 611
- business_risk: 310
- compliance: 276
- price_impact: 175
- advocacy: 24
- business_risk|advocacy: 8
- compliance|business_risk: 6
- business_risk|advocacy|other: 6
- price_impact|business_risk: 5


---

## Actor Distribution (used by P1, P5) - Top 10

- consumer: 738
- enterprise: 488
- cross_border_seller: 370
- general_public: 228
- government: 100
- consumer|government: 63
- multiple: 39
- enterprise|cross_border_seller: 37
- enterprise|government: 35
- enterprise|consumer: 32


---

## Conclusion

SUCCESS: All pages display consistent data

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
