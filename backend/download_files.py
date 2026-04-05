import requests
import os
import argparse

# 后端API基础URL
BASE_URL = "http://localhost:8000"

def login(username, password):
    """登录获取认证令牌"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"登录失败: {e}")
        return None

def get_user_files(token):
    """获取用户的文件列表"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/files",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取文件列表失败: {e}")
        return []

def download_file(token, file_id, file_name, save_dir):
    """下载文件"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/files/{file_id}/download",
            headers={"Authorization": f"Bearer {token}"},
            stream=True
        )
        response.raise_for_status()
        
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"文件下载成功: {file_path}")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"下载文件失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="下载FileCloud用户文件")
    parser.add_argument("--username", required=True, help="用户名")
    parser.add_argument("--password", required=True, help="密码")
    parser.add_argument("--save-dir", default="./downloads", help="保存目录")
    parser.add_argument("--file-id", type=int, help="指定文件ID，不指定则下载所有文件")
    
    args = parser.parse_args()
    
    # 登录获取令牌
    token = login(args.username, args.password)
    if not token:
        return
    
    # 获取文件列表
    files = get_user_files(token)
    if not files:
        print("没有找到文件")
        return
    
    # 显示文件列表
    print("文件列表:")
    for file in files:
        print(f"ID: {file['id']}, 名称: {file['name']}, 大小: {file['size']}B, 类型: {file['type']}")
    
    # 下载指定文件或所有文件
    if args.file_id:
        # 查找指定文件
        target_file = next((f for f in files if f['id'] == args.file_id), None)
        if target_file:
            download_file(token, target_file['id'], target_file['name'], args.save_dir)
        else:
            print(f"未找到文件ID: {args.file_id}")
    else:
        # 下载所有文件
        print(f"\n开始下载所有文件到目录: {args.save_dir}")
        for file in files:
            download_file(token, file['id'], file['name'], args.save_dir)

if __name__ == "__main__":
    main()