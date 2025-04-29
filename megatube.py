import os
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import shutil
import time

# 设置基础URL
base_url = "https://www.megatube.xxx"

# 清空images文件夹（保留以防其他用途）
def cleanup_images_folder():
    if os.path.exists("images"):
        shutil.rmtree("images")
    os.makedirs("images", exist_ok=True)

# 1. 清空images文件夹（不再清空pic.txt）
cleanup_images_folder()

# 2. 随机选择1-357的整数
random_page = random.randint(1, 357)
target_url = f"{base_url}/albums/most-popular/{random_page}/"
print(f"随机选择的页面: {target_url}")

# 请求重试机制
def safe_request(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(1)

# 3. 获取带title属性的<a>标签
try:
    response = safe_request(target_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取所有带title属性的<a>标签
    a_tags = soup.find_all('a', title=True)
    hrefs = [a['href'] for a in a_tags if a.has_attr('href')]
    
    if not hrefs:
        print("未找到带title属性的<a>标签")
        exit()
    
    # 4. 随机选择12个链接
    selected_links = random.sample(hrefs, min(12, len(hrefs)))
    print("\n随机选择的12个链接:")
    for i, link in enumerate(selected_links, 1):
        print(f"{i}. {link}")
    
    # 5. 对每个链接处理（追加模式写入）
    print("\n处理每个链接中的图片:")
    with open("pic.txt", "a+") as pic_file:  # 追加模式
        pic_file.seek(0)
        existing_links = set(pic_file.read().splitlines())
        
        for link in selected_links:
            full_link = urljoin(base_url, link)
            print(f"\n处理链接: {full_link}")
            
            try:
                link_response = safe_request(full_link)
                link_soup = BeautifulSoup(link_response.text, 'html.parser')
                
                img_links = [
                    a['href'] for a in link_soup.find_all('a', href=True)
                    if 'get_image' in a['href'] and a['href'].endswith('jpg/')
                ]
                
                if img_links:
                    selected_img = random.choice(img_links)
                    print(f"找到的图片链接: {selected_img}")
                    if selected_img not in existing_links:
                        pic_file.write(selected_img + "\n")
                        existing_links.add(selected_img)  # 避免同一批次重复
                else:
                    print("未找到符合条件的图片链接")
                    
            except Exception as e:
                print(f"处理链接时出错: {e}")
                
except requests.exceptions.RequestException as e:
    print(f"请求出错: {e}")
except Exception as e:
    print(f"发生错误: {e}")

# 新增：清理空行
def remove_empty_lines(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))

# 执行清理
remove_empty_lines("pic.txt")

time.sleep(3)  # 模拟长时间运行