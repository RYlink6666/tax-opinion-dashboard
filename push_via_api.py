#!/usr/bin/env python3
"""
用GitHub API推送文件修改
"""
import requests
import base64
import json

# 配置
OWNER = "RYlink6666"
REPO = "tax-opinion-dashboard"
FILE_PATH = "streamlit_app/utils/data_loader.py"
TOKEN = "github_pat_11ATPVF7A0aJ8Yx1ZG9lHK_gPqR8mMvT2kn4WsL5dEfRhIjKlMnOp1q2r3s4t5u"

# 读取文件内容
with open("streamlit_app/utils/data_loader.py", "r", encoding="utf-8") as f:
    file_content = f.read()

# Base64编码
encoded_content = base64.b64encode(file_content.encode()).decode()

# 获取当前文件SHA（需要先GET）
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

# 获取当前文件SHA
print("正在获取文件当前SHA...")
response = requests.get(url, headers=headers)
if response.status_code == 200:
    current_sha = response.json()["sha"]
    print(f"当前SHA: {current_sha}")
else:
    print(f"错误: {response.status_code}")
    print(response.text)
    exit(1)

# 推送更新
print("正在推送文件更新...")
data = {
    "message": "Fix compound label translation for combined sentiment/topic/actor tags",
    "content": encoded_content,
    "sha": current_sha,
    "branch": "main"
}

response = requests.put(url, headers=headers, json=data)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

if response.status_code == 200:
    print("\n✅ 推送成功！")
    print(f"提交: {response.json()['commit']['sha']}")
else:
    print("\n❌ 推送失败")
