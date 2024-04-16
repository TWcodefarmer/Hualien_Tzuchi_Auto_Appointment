#pyinstaller --onefile main.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO
from urllib.request import urlopen
from PIL import Image
import ddddocr
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import uuid
from multiprocessing.dummy import Pool as ThreadPool
import time
import datetime
import re
import threading

# 確認是否得到最新網址
def check_url_in_txt(file_path):
    # 定義簡單的網址正則表達式
    url_pattern = re.compile(r'https?://\S+')
    # 開啟文件，以讀取模式打開
    with open(file_path, 'r') as file:
        # 讀取文件內容
        content = file.read()
        # 使用正則表達式搜尋網址
        matches = url_pattern.findall(content)
        if matches:
            print("文件中包含以下網址：")
            for match in matches:
                print(match)
            return True
        else:
            print("文件中沒有找到網址。")
            return False
    
# 得到最新網址
def get_url_in_txt(file_path):
    # 定義簡單的網址正則表達式
    url_pattern = re.compile(r'https?://\S+')
    # 開啟文件，以讀取模式打開
    with open(file_path, 'r') as file:
        # 讀取文件內容
        content = file.read()
        # 使用正則表達式搜尋網址
        matches = url_pattern.findall(content)
        if matches:
            print("文件中包含以下網址：")
            for match in matches:
                print(match)
            return match
        else:
            print("文件中沒有找到網址。")
            return False

# 隨機png檔名製造
def generate_random_filename(extension=''):
    random_uuid = uuid.uuid4()
    random_filename = str(random_uuid).replace('-', '')

    if extension:
        random_filename += f'.{extension}'
    return random_filename

# 計時器
def timer(target_time_1,target_time_2):
    while True:
        now = datetime.datetime.now().time()
        if target_time_2 >= now >= target_time_1:
            print("!!!時間到開始搶!!!")
            break
        else:
            print(now,"時間還沒到~~~")
            time.sleep(0.01)

# 儲存url至文本
def save_url_to_txt(url, file_path):
    # 開啟文件，以附加模式打開，如果不存在就新建一個
    with open(file_path, 'w') as file:
        # 將網址寫入檔案
        file.write(url)

# 獲得目標掛號門診網址
def get_target_url():
    # 如果沒有最新網址
    if not check_url_in_txt('urls.txt'):
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        url = "https://app.tzuchi.com.tw/tchw/opdreg/OpdTimeShow.aspx?Depart=%E4%B8%AD%E9%86%AB%E7%A7%91&HospLoc=3"
        driver.get(url)
        # 使用bs4解析HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # 預設常數 ###################
        search_text = '林郁甯'
        # search_text = '王健豪'
        # search_text = '吳立工'
        # 找到所有包含指定文本的標籤
        matching_tags = soup.find_all(lambda tag: tag.name == 'a' and search_text in tag.text)
        if len(matching_tags)>0:
            target_url = "https://app.tzuchi.com.tw/tchw/opdreg/" + matching_tags[-1].get('href').split('&')[0] + "&sLoc=3"
            # 呼叫函數，指定網址和文本文件的路徑
            save_url_to_txt(str(target_url), 'urls.txt')
        driver.quit()

# 每一秒執行一次新視窗獲得網站內容更新
def execute_get_target_url_every_second():
    while datetime.time(6, 2, 0) >= datetime.datetime.now().time() >= datetime.time(5, 59, 0) :
    # while True: ###################!
        if not check_url_in_txt('urls.txt'):
            threading.Thread(target=get_target_url).start()  # 使用新的執行緒執行函數
            time.sleep(1) ###################
        else:
            break

# 自動輸入資料
def start_keyin(target_url):
    alldone =False
    # 預設常數 ###################
    input_value_ID = 'U212121212'
    input_value_Birth = '0810102'
    # 創建 WebDriver 對象
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(target_url)
    # 找到身分證框
    input_element_ID = driver.find_element("id", "txtMRNo")
    # 輸入
    input_element_ID.send_keys(input_value_ID)
    # 找到 img 元素
    img_element = driver.find_element("id", "imgVI")
    # 获取验证码图片在网页中的位置
    left = int(img_element.location['x'])	# 获取图片左上角坐标x
    top = int(img_element.location['y'])	# 获取图片左上角y
    right = int(img_element.location['x'] + img_element.size['width'])		# 获取图片右下角x
    bottom = int(img_element.location['y'] + img_element.size['height'])	# 获取图片右下角y
    # 生成随机文件名
    random_file = generate_random_filename('png')
    path = random_file
    driver.save_screenshot(path)		# 截取当前窗口并保存图片
    im = Image.open(path)				# 打开图片
    im = im.crop((left, top, right, bottom))	# 截图验证码
    im.save(path)		# 保存验证码图片
    #辨別驗證碼
    ocr = ddddocr.DdddOcr()
    with open(path, 'rb') as f:
        image = f.read()
    VerifyCode = ocr.classification(image)
    conversion_rules = {'U':'0','g':'9','Z':'7','z':'7','s':'5','S':'5','l':'1','L':'1','I':'1','i':'1'}
    # 使用迴圈進行替換
    modified_VerifyCode = ''.join(conversion_rules.get(char, char) for char in VerifyCode)
    # 輸入驗證碼
    input_element_VC = driver.find_element("id", "txtVCode")
    input_element_VC.send_keys(modified_VerifyCode)
    # 找到按鈕元素
    submit_button = driver.find_element("id", "btnRegNo")  # 替換為實際的按鈕 ID
    # 點擊按鈕
    submit_button.click()
    try:
        # 使用 WebDriverWait 等待 input 框元素可見
        input_element_Birth = WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.ID, "TextBox3")))
        keepgo = True
    except TimeoutException:
        print("驗證失敗" + '_' + VerifyCode + '_' + modified_VerifyCode)
        keepgo = False
    if keepgo:
        # 找到 input 框的元素
        input_element_Birth = driver.find_element("id", "TextBox3")
        # 使用 send_keys 方法輸入值
        input_element_Birth.send_keys(input_value_Birth)
        # 找到按鈕元素
        submit_button = driver.find_element("id", "Button2")  # 替換為實際的按鈕 ID
        # 點擊按鈕
        submit_button.click()
        # 切換到確認框
        confirmation_alert = driver.switch_to.alert
        # 點擊確認 ###################
        confirmation_alert.accept()
        # 或者 點擊取消
        # confirmation_alert.dismiss()
        alldone = True
        print("預約完成")
    return alldone

def main_process():
    try:
        # 清空txt
        with open('urls.txt', 'w') as file:
            file.write('')
        # 設定機器人數量
        # howmany = int(input("請輸入數字，一次要開幾個視窗搶，輸入後直接按enter，只可輸入阿拉伯數字:")) ###################
        howmany = int(10) ###################
        pool = ThreadPool(howmany)
        # 指定時間範圍內執行
        timer(target_time_1=datetime.time(6, 0, 0),target_time_2=datetime.time(6, 0, 2)) ###################
        print(f'1___{datetime.datetime.now().time()}')
        print('開始獲取目標網站')
        execute_get_target_url_every_second()
        target_url = get_url_in_txt('urls.txt')
        if target_url:
            print('成功獲取目標網站:',target_url)
            print(f'2___{datetime.datetime.now().time()}')
            # 記錄歷史掛號網址
            with open('urls_history.txt', 'a') as file:
                file.write(target_url+'\n')
            # 機器人開始並行輸入個資與驗證碼
            try:
                result = pool.map(start_keyin, [target_url] * howmany)
                print(result)
                print(f'3___{datetime.datetime.now().time()}')
            except Exception as e:
                print(e)
                print(f'4___{datetime.datetime.now().time()}')
        else:
            print('無法獲取目標網站')
        # 清空txt
        with open('urls.txt', 'w') as file:
            file.write('')    
    except:
        pass

import schedule

# 定時執行
schedule.every().wednesday.at("05:59").do(main_process)
schedule.every().friday.at("05:59").do(main_process)

while True:
    schedule.run_pending()
    time.sleep(1)
    print(datetime.datetime.now())








# 第一個迴圈15秒結束
# 第二個迴圈13秒結束
# 第二個迴圈12秒結束
# 第二個迴圈12秒結束

# 15+13+12+12=52
# 6:00:41秒得到目標網址