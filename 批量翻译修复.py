#!/usr/bin/env python3
"""
批量修复所有页面中的英文字段显示
"""
import os
import re

def fix_file(filepath):
    """修复文件中的英文字段显示"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 添加导入
    if 'translate_sentiment' not in content and 'from utils.data_loader import' in content:
        # 查找现有的导入块
        import_pattern = r'from utils\.data_loader import ([^)]*)'
        match = re.search(import_pattern, content)
        if match:
            existing_imports = match.group(1)
            if 'translate_' not in existing_imports:
                # 多行导入
                if '(' in content[match.start():match.start()+200]:
                    # 已经是多行格式，添加到列表
                    old_import = match.group(0)
                    new_import = old_import.replace(')', ',\n    translate_sentiment,\n    translate_risk,\n    translate_topic,\n    translate_actor\n)')
                    content = content.replace(old_import, new_import)
                else:
                    # 单行格式，转换为多行
                    old_import = match.group(0)
                    new_import = f'''from utils.data_loader import (
    {existing_imports.replace(',', ',\n    ')},
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)'''
                    content = content.replace(old_import, new_import)
    
    # 2. 修复显示：sentiment
    content = re.sub(
        r'st\.write\(f"([^"]*)\{sent(?:iment)?\}',
        r'st.write(f"\1{translate_sentiment(sent)}',
        content
    )
    
    # 3. 修复显示：topic
    content = re.sub(
        r'st\.write\(f"([^"]*)\{topic\}',
        r'st.write(f"\1{translate_topic(topic)}',
        content
    )
    content = re.sub(
        r'labels=([a-z_]+)\.index,',
        lambda m: f'labels=[translate_topic(x) for x in {m.group(1)}.index],' if 'topic' in m.group(1).lower() else m.group(0),
        content
    )
    
    # 4. 修复显示：actor
    content = re.sub(
        r'st\.write\(f"([^"]*)\{actor\}',
        r'st.write(f"\1{translate_actor(actor)}',
        content
    )
    
    # 5. 修复显示：risk
    content = re.sub(
        r'st\.write\(f"([^"]*)\{risk\}',
        r'st.write(f"\1{translate_risk(risk)}',
        content
    )
    
    # 保存如果有变化
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复: {filepath}")
        return True
    else:
        print(f"⏭️  跳过: {filepath}")
        return False

# 处理所有页面文件
pages_dir = 'streamlit_app/pages'
if os.path.exists(pages_dir):
    count = 0
    for filename in os.listdir(pages_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(pages_dir, filename)
            if fix_file(filepath):
                count += 1
    print(f"\n✅ 共修复 {count} 个文件")
else:
    print(f"❌ 目录不存在: {pages_dir}")
