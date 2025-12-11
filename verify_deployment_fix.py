#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署修复验证脚本 - Phase 8

用途：验证数据文件路径检测是否正常工作
可以在本地或部署环境中运行
"""

import os
import sys
import json
from pathlib import Path

# 修复Windows的UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

def test_path_resolution():
    """测试路径检测逻辑"""
    print("=" * 60)
    print("[Phase 8] 部署修复验证脚本")
    print("=" * 60)
    
    # 模拟 data_loader.py 中的路径检测
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n[位置] 脚本位置: {script_dir}")
    print(f"[位置] 工作目录: {os.getcwd()}")
    
    # 候选项目根目录
    project_candidates = [
        script_dir,  # 如果脚本在项目根
        os.path.dirname(script_dir),  # 上一级
    ]
    
    # 构建所有可能的路径
    possible_paths = []
    for base_dir in project_candidates:
        possible_paths.extend([
            os.path.join(base_dir, 'data', 'analysis', 'analysis_results.json'),
            os.path.join(base_dir, 'streamlit_app', 'data', 'analysis', 'analysis_results.json'),
        ])
    
    # 相对路径
    possible_paths.extend([
        'data/analysis/analysis_results.json',
        '../data/analysis/analysis_results.json',
        '../../data/analysis/analysis_results.json',
    ])
    
    print(f"\n[搜索] 正在搜索数据文件...")
    print(f"[路径] 尝试的路径 (共 {len(possible_paths)} 个):\n")
    
    filepath = None
    found_index = -1
    
    for i, path in enumerate(possible_paths, 1):
        abs_path = os.path.abspath(path)
        exists = os.path.exists(abs_path)
        status = "[OK]   " if exists else "[SKIP] "
        print(f"  [{i:2d}] {status} {abs_path}")
        
        if exists and filepath is None:
            filepath = abs_path
            found_index = i
    
    print("\n" + "=" * 60)
    
    if filepath:
        print(f"[成功] 找到数据文件 (第 {found_index} 个路径)")
        print(f"[路径] 实际位置: {filepath}")
        
        # 验证文件内容
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            results = data.get('data', [])
            print(f"\n[验证] 数据文件信息:")
            print(f"       总数据条数: {len(results)}")
            
            # 采样检查
            if results:
                sample = results[0]
                print(f"       样本字段: {list(sample.keys())}")
                print(f"\n[验证] 数据文件格式正确，可正常使用")
            
            return True, filepath
        
        except json.JSONDecodeError as e:
            print(f"[错误] JSON解析失败: {e}")
            return False, filepath
        except Exception as e:
            print(f"[错误] 读取文件失败: {e}")
            return False, filepath
    
    else:
        print("[失败] 数据文件未找到")
        print("\n请检查:")
        print("  1. 数据文件是否存在: <项目根>/data/analysis/analysis_results.json")
        print("  2. 是否在项目根目录运行此脚本")
        print("  3. 文件名是否正确")
        return False, None

def test_imports():
    """测试主要导入是否成功"""
    print("\n" + "=" * 60)
    print("[测试] 模块导入检查")
    print("=" * 60)
    
    imports_to_test = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'pandas'),
        ('plotly', 'plotly'),
        ('bertopic', 'BERTopic'),
        ('sentence_transformers', 'sentence-transformers'),
    ]
    
    all_ok = True
    for module_name, display_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"[OK]   {display_name:25s} 已安装")
        except ImportError:
            print(f"[FAIL] {display_name:25s} 未安装")
            all_ok = False
    
    return all_ok

def test_streamlit_app():
    """测试Streamlit入口点"""
    print("\n" + "=" * 60)
    print("[测试] Streamlit入口点检查")
    print("=" * 60)
    
    # 检查 streamlit_app.py 是否存在
    streamlit_app_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'streamlit_app.py'
    )
    
    if os.path.exists(streamlit_app_path):
        print(f"[OK]   streamlit_app.py 存在")
        print(f"       位置: {streamlit_app_path}")
        return True
    else:
        print(f"[FAIL] streamlit_app.py 未找到")
        print(f"       应该在: {streamlit_app_path}")
        return False

def main():
    """主测试函数"""
    print("\n")
    
    # 运行所有测试
    path_ok, filepath = test_path_resolution()
    imports_ok = test_imports()
    app_ok = test_streamlit_app()
    
    # 总结
    print("\n" + "=" * 60)
    print("[总结] 测试结果汇总")
    print("=" * 60)
    
    tests = [
        ("数据文件检测", path_ok),
        ("模块导入检查", imports_ok),
        ("入口点检查", app_ok),
    ]
    
    print()
    for name, result in tests:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} | {name}")
    
    all_passed = all(result for _, result in tests)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[成功] 所有检查都通过!")
        print("\n可以运行以下命令启动应用:")
        print("  streamlit run streamlit_app.py")
        return 0
    else:
        print("[警告] 存在未通过的检查，请解决上述问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
