# -*- coding: utf-8 -*-
import json
import os

fp = 'data/analysis/analysis_results.json'
print(f"File exists: {os.path.exists(fp)}")
print(f"File size: {os.path.getsize(fp)} bytes")

# Read with errors='replace' to avoid encoding crash
with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
    try:
        data = json.load(f)
        count = len(data.get('data', []))
        print(f"Records loaded: {count}")
    except Exception as e:
        print(f"JSON parse error: {e}")
