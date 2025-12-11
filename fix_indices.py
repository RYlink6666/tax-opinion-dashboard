#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复数据索引 - 确保所有2297条都有连续的索引"""

import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

analysis_file = Path("data/analysis/analysis_results.json")

print("Loading data...")
with open(analysis_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['data']
print(f"   Original records: {len(results)}")

# Reorder indices
print("Reorganizing indices...")
for idx, record in enumerate(results):
    record['index'] = idx

print(f"   New index range: 0-{len(results)-1}")

# Save
print("Saving...")
data['data'] = results
with open(analysis_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done!")
print(f"   Total records: {len(results)}")
