#!/usr/bin/env python3
"""
修复所有页面中的英文标签显示问题
"""
import os
import re

# 需要修复的文件列表
files_to_fix = [
    'streamlit_app/pages/2_Search.py',
    'streamlit_app/pages/3_Risk_Analysis.py',
    'streamlit_app/pages/4_Pattern_Analysis.py',
    'streamlit_app/pages/5_Actor_Analysis.py',
    'streamlit_app/pages/6_Policy_Recommendations.py',
]

# 导入语句模板
import_template = '''from utils.data_loader import (
    load_analysis_data,
    translate_sentiment,
    translate_risk,
    translate_topic,
    translate_actor
)'''

# 修复列表
fixes = [
    # 显示情感的地方
    (r"st\.write\(f\"🎯 \*\*情感\*\*: \{row\['sentiment'\]\}\"", 
     "st.write(f\"🎯 **情感**: {translate_sentiment(row['sentiment'])}\""),
    
    (r"st\.write\(f\"([^\"]*)\{sentiment\}\"",
     "st.write(f\"\\1{translate_sentiment(sentiment)}\""  ),
    
    # 显示话题的地方
    (r"st\.write\(f\"📌 \*\*话题\*\*: \{row\['topic'\]\}\"",
     "st.write(f\"📌 **话题**: {translate_topic(row['topic'])}\""),
    
    (r"st\.write\(f\"([^\"]*)\{topic\}\"",
     "st.write(f\"\\1{translate_topic(topic)}\""),
    
    # 显示风险的地方
    (r"st\.write\(f\"⚠️ \*\*风险\*\*: \{row\['risk_level'\]\}\"",
     "st.write(f\"⚠️ **风险**: {translate_risk(row['risk_level'])}\""),
    
    (r"st\.write\(f\"([^\"]*)\{risk\}\"",
     "st.write(f\"\\1{translate_risk(risk)}\""),
    
    # 显示参与方的地方
    (r"st\.write\(f\"👥 \*\*参与方\*\*: \{row\['actor'\]\}\"",
     "st.write(f\"👥 **参与方**: {translate_actor(row['actor'])}\""),
    
    (r"st\.write\(f\"([^\"]*)\{actor\}\"",
     "st.write(f\"\\1{translate_actor(actor)}\""),
]

def fix_file(filepath):
    """修复单个文件"""
    print(f"处理 {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已导入翻译函数
    if 'translate_sentiment' not in content:
        # 添加导入
        # 找到第一个 import 语句
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('from utils.data_loader import'):
                # 更新这个导入
                j = i
                while j < len(lines) and ')' not in lines[j]:
                    j += 1
                if j < len(lines):
                    # 插入新的导入
                    lines[i:j+1] = ['from utils.data_loader import (', 
                                   '    load_analysis_data,',
                                   '    translate_sentiment,',
                                   '    translate_risk,',
                                   '    translate_topic,',
                                   '    translate_actor',
                                   ')']
                    break
        content = '\n'.join(lines)
    
    # 应用所有修复
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 完成 {filepath}")

if __name__ == '__main__':
    for file in files_to_fix:
        if os.path.exists(file):
            fix_file(file)
        else:
            print(f"⚠️ 文件不存在: {file}")
    
    print("\n✅ 所有文件已修复！")
