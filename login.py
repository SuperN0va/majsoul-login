import sys
import time
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def write_log(message):
    """辅助函数：写入日志到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    try:
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def attempt_login(email, passwd, driver):
    """单次登录尝试的核心逻辑"""
    driver.get("https://game.maj-soul.net/1/")
    
    # 1. 等待 Canvas 加载 (最多等待40秒，应对网络波动)
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.ID, "layaCanvas"))
    )
    # 增加额外的硬等待，确保游戏引擎内的登录 UI 渲染完毕
    sleep(10) 

    screen = driver.find_element(By.ID, 'layaCanvas')

    # 2. 输入账号
    ActionChains(driver).move_to_element_with_offset(screen, 250, -100).click().perform()
    input_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, 'input'))
    )
    input_field.send_keys(email)
    sleep(1)

    # 3. 输入密码
    ActionChains(driver).move_to_element_with_offset(screen, 250, -50).click().perform()
    # 为密码框也加上显式等待，防止上一步操作后 DOM 刷新丢失焦点
    pass_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'input_password'))
    )
    pass_field.send_keys(passwd)
    sleep(1)

    # 4. 点击登录
    ActionChains(driver).move_to_element_with_offset(screen, 250, 50).click().perform()
    
    # 等待登录响应及大厅加载
    sleep(15) 

def run_login():
    args = sys.argv[1:]
    if len(args) < 2 or len(args) % 2 != 0:
        write_log("Error: Arguments mismatch. Check secrets configuration.")
        return

    num_accounts = int(len(args) / 2)
    write_log(f"Starting login task for {num_accounts} accounts.")

    for i in range(num_accounts):
        email = args[i]
        passwd = args[i + num_accounts]
        
        start_time = time.time()
        success = False
        status = "Failed"
        max_retries = 3  # 最大重试次数设定为 3 次
        
        for attempt in range(1, max_retries + 1):
            driver = None
            try:
                print(f"Account: {email}, Attempt {attempt}/{max_retries}...")
                
                options = webdriver.ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                # 伪装 user-agent 降低被墙的概率
                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                driver = webdriver.Chrome(options=options)
                driver.set_window_size(1000, 720) 
                
                # 执行登录逻辑
                attempt_login(email, passwd, driver)
                
                success = True
                status = "Success"
                print(f"Login success on attempt {attempt}.")
                break # 成功则跳出重试循环

            except Exception as e:
                # 提取干净的错误信息，抛弃冗长的 C++ 堆栈
                error_type = type(e).__name__
                error_msg = str(e).splitlines()[0] if str(e) else "Unknown Error"
                print(f"Attempt {attempt} failed: {error_type} - {error_msg}")
                status = f"Error: {error_type}"
                
                sleep(5) # 失败后稍微冷却一下再重试
                
            finally:
                if driver:
                    driver.quit()
        
        duration = time.time() - start_time
        
        # 如果重试多次仍失败，记录带有重试标记的日志
        if not success:
            status += f" (after {max_retries} retries)"
            
        write_log(f"User: {email} | Status: {status} | Duration: {duration:.2f}s")

if __name__ == "__main__":
    run_login()
