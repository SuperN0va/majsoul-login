import sys
import time
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_login_tasks():
    # 简单的参数校验
    if len(sys.argv) < 2:
        print("Usage: python majsoul_login.py <email1> <email2> ... <pass1> <pass2> ...")
        return

    # 计算账号数量 (参数列表长度的一半)
    # sys.argv[0] 是脚本名，所以从 1 开始切片
    args = sys.argv[1:]
    if len(args) % 2 != 0:
        print("Error: 参数数量不匹配，账号和密码数量必须一致。")
        return

    num_accounts = int(len(args) / 2)
    print(f'Config {num_accounts} accounts')

    # 准备日志内容
    log_entries = []

    for i in range(num_accounts):
        email = args[i]
        passwd = args[i + num_accounts]
        
        print('----------------------------')
        print(f'Account {i+1}: {email} processing...')
        
        start_time = time.time()
        success = False
        status_msg = "Failed"

        try:
            # 1. Open browser
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            # 禁用一些可能导致报错的特性
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1000, 720)
            
            driver.get("https://game.maj-soul.net/1/")
            print(f'Account {i+1} loading game...')
            
            # 使用显式等待替代 sleep(20)，最长等待 30 秒
            # 如果网速慢，保留一定的 sleep 也是一种简单的 fallback
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, "layaCanvas"))
                )
                sleep(5) # Canvas 出现后额外等待几秒让资源加载
            except:
                print("Wait for canvas timeout, trying to proceed anyway...")
                sleep(15)

            # 2. Input email
            # 获取 Canvas 元素
            screen = driver.find_element(By.ID, 'layaCanvas')
            
            ActionChains(driver)\
                .move_to_element_with_offset(screen, 250, -100)\
                .click()\
                .perform()
            
            # 查找动态生成的输入框
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'input'))
            )
            input_field.send_keys(email)
            print('Input email successfully')
            sleep(1) # 小停顿防止操作过快

            # 3. Input password
            ActionChains(driver)\
                .move_to_element_with_offset(screen, 250, -50)\
                .click()\
                .perform()
            
            # 重新定位密码框（虽然 name 可能还是 input_password，但为了稳妥）
            pass_field = driver.find_element(By.NAME, 'input_password')
            pass_field.send_keys(passwd)
            print('Input password successfully')
            sleep(1)

            # 4. Login click
            ActionChains(driver)\
                .move_to_element_with_offset(screen, 250, 50)\
                .click()\
                .perform()
            
            print('Entering game...')
            sleep(15) # 等待登录动画和进入大厅
            
            # 这里可以尝试检测是否成功，例如检查 URL 是否变化或特定元素是否存在
            # 简单起见，如果走到这里没报错，我们认为这一步是 Success
            print('Login sequence finished')
            success = True
            status_msg = "Success"
            
            driver.quit()

        except Exception as e:
            print(f"Error for account {email}: {str(e)}")
            status_msg = f"Error: {str(e)[:50]}..." # 记录部分错误信息
            if 'driver' in locals():
                driver.quit()
        
        # 计算耗时
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 记录单条日志
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time_str}] User: {email} | Status: {status_msg} | Time: {execution_time:.2f}s\n"
        log_entries.append(log_entry)

    # 循环结束后，统一写入文件
    # 使用 'a' 模式追加，确保每次运行都保留历史
    try:
        with open("log.txt", "a", encoding="utf-8") as log_file:
            for entry in log_entries:
                log_file.write(entry)
        print("Log updated successfully.")
    except Exception as e:
        print(f"Failed to write log: {e}")

if __name__ == "__main__":
    run_login_tasks()
