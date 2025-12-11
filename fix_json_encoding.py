import json
import sys

try:
    # 尝试用utf-8-sig读取
    with open('data/analysis/analysis_results.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    print(f"✓ UTF-8-SIG读取成功，共{len(data.get('data', []))}条记录")
except Exception as e:
    print(f"UTF-8-SIG失败，尝试latin-1: {e}")
    try:
        with open('data/analysis/analysis_results.json', 'r', encoding='latin-1') as f:
            content = f.read()
        data = json.loads(content)
        print(f"✓ Latin-1读取成功，正在重新保存为UTF-8...")
        with open('data/analysis/analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 已保存为UTF-8，共{len(data.get('data', []))}条记录")
    except Exception as e2:
        print(f"失败：{e2}")
        sys.exit(1)
