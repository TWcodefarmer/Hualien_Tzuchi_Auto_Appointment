import requests
import time

url = 'https://ticketplus.com.tw/activity/e79352d85215d03eadb7a0618c200c85'

start_time = time.time()
response = requests.get(url)
end_time = time.time()

response_time = end_time - start_time
print(f'本地到指定網站的反應時間為 : {response_time} 秒')

import socket

# 获取本地主机名
host_name = socket.gethostname()

# 通过主机名获取本地IP地址
local_ip = socket.gethostbyname(host_name)

print(f'本地IP地址是 : {local_ip}')

# 167 192.168.50.13 0.133 秒
# 165 192.168.50.13 0.140 秒
