#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

with open('data/analysis/analysis_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data['data'])

# 拆分复合标签
all_actors = []
for actors_str in df['actor']:
    if pd.notna(actors_str):
        actors = [a.strip() for a in str(actors_str).split('|')]
        all_actors.extend(actors)

actor_series = pd.Series(all_actors)
actor_dist = actor_series.value_counts()

print(f"参与方总数（去重）: {len(actor_dist)}\n")
print("参与方分布:")
print("-" * 50)

for actor, count in actor_dist.items():
    pct = count / len(df) * 100
    print(f"  {actor:25s}: {count:4d}条 ({pct:5.1f}%)")
