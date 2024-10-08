import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import urllib
import os

from get_weather_info import get_current_weather, get_weather_suggestion

URL = 'https://jxjyxy.hunnu.edu.cn/xsxw/xwbk.htm'
hash_file_path = 'hash_file.txt'
TO_EMAIL = os.getenv('RECIPIENT_EMAIL')

# 配置邮件发送
def send_email(subject, body, to_email):
    # 从环境变量中获取邮箱信息
    from_email = os.getenv('EMAIL_USER')
    from_password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def get_list_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # 提取 list01 的内容
        start = html.find('<div class="list01">')
        end = html.find('</div>', start)
        if start != -1 and end != -1:
            list_content = html[start:end]
            return list_content
    return None

def calculate_hash(content):
    # 计算内容的哈希值
    return hashlib.md5(content.encode('utf-8')).hexdigest()

# 监控网页并检测更新
def monitor_website(url, hash_file_path, to_email):
    # 如果之前没有保存哈希值文件，则初始化
    if not os.path.exists(hash_file_path):
        with open(hash_file_path, 'w') as f:
            f.write(calculate_hash(get_list_content(url)))

    # 读取之前的哈希值
    with open(hash_file_path, 'r') as f:
        old_hash = f.read()

    # 获取当前网页的哈希值
    current_hash = calculate_hash(get_list_content(url))

    # 如果哈希值不同，说明网页内容更新了
    if current_hash != old_hash:
        # 发送邮件通知
        send_email(
            subject='亲爱的怡宝,报考网站信息更新啦~',
            body=(
                f"网站更新啦！\n请前往查看: {url}\n"
                f"当前天气信息: \n{get_current_weather()}"
                f"天气建议: \n{get_weather_suggestion()}"
            ),
            to_email=to_email
        )
        print('发送成功!')
        # 更新保存的哈希值
        with open(hash_file_path, 'w') as f:
            f.write(current_hash)
    else:
        send_email(
            subject='亲爱的怡宝,报考网站信息还没更新哦~',
            body=(
                "报考网站信息还没更新哦,请耐心等待~\n"
                f"今天天气信息: \n{get_current_weather()}"
                f"相关建议: \n{get_weather_suggestion()}"
            ),
            to_email=to_email
        )
        print('发送成功！未检测到更新。')

# 定时任务
def main():
    monitor_website(URL, hash_file_path, TO_EMAIL)
    

if __name__ == "__main__":
    main()
