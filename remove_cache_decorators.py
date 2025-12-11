#!/usr/bin/env python3
"""移除所有 Streamlit 脚本中的 @st.cache_data 装饰器"""

import os
from pathlib import Path

pages_dir = Path("streamlit_app/pages")

for py_file in pages_dir.glob("*.py"):
    if py_file.name == "1_总体概览.py":
        continue  # 已经处理过了
    
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除 @st.cache_data 行
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip() == '@st.cache_data':
            continue
        new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ {py_file.name}")

print("\n✓ 完成！已移除所有 @st.cache_data 装饰器")
