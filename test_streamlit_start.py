# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from utils.data_loader import load_analysis_data

try:
    df = load_analysis_data()
    print(f"✓ Data loaded successfully: {len(df)} records")
    print(f"✓ Columns: {list(df.columns)}")
    print(f"✓ First row sample:")
    print(df.iloc[0].to_dict())
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
