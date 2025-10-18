import os
import time
import threading
import tempfile
from seleniumwire import webdriver  # pip install selenium-wire
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
from time import sleep
import random
import json
import eel  # ← Thêm dòng này

class FirefoxManager:
    def __init__(self, data):
        self.data = data
        self.firefox_path = data.get("firefoxPath")
        self.geckodriver_path = data.get("geckodriverPath")
        self.account_count = data.get("accountCount", 10)
        self.thread_count = data.get("threadCount", 3)
        self.delay = data.get("delay", 5)
        self.proxy_list = data.get("proxyList", [])
        self.cookies = {
            '_ga': 'GA1.1.32425121.1758029713',
            'user_id': '588d655f-89d6-492d-b427-58b851b32ef6',
            'cto_bundle': '6G0p5F8yTGlMY3JZVUNkTEJZUUtuemxCa3VSJTJGcDNJZ3JyUnA0OGRFZUJKQzdTWlVZR1hLaWRxV3cyQWdRaUZ5cjdJU3NCZTg3Y2tOWEZDeDFMMVlPUmFiZlJ2TXMyOEVobyUyRmdleFlGZzAlMkZtVGJXJTJCZVVNVkNRbVRMb0tHcmclMkZ1cFhvZERhVlhtZVV6c3ROR2ZpaiUyQlRtTnNQaWclM0QlM0Q',
            'cto_bidid': 'Dw6GzF9HbXk1Q3BTQUtNJTJCMml6QyUyQnJ5R3V1b1ElMkI5d3lzeWZJTjM0S213eGdZWFQ5TW55dUo2ZTdPNE4yME5xNVJ2NFRFMFRsdXNDU3Q4Rk04Q1ZaazJUUExoSlBsbW0wZU5xV3RIdmhtRkNteEpsUnBYJTJGREJtWWtYTjJ5RDJkbHBWR3l1',
            '_pbjs_userid_consent_data': '3524755945110770',
            '_ga_4TBVMLYBBP': 'GS2.1.s1758079326$o4$g1$t1758079345$j41$l0$h0',
            '__gads': 'ID=7622753cf5bf69f8:T=1758029716:RT=1758080739:S=ALNI_MZFIDWsHp_hZY3MkI7dwOBpsCEwIQ',
            '__gpi': 'UID=0000114995a45b45:T=1758029716:RT=1758080739:S=ALNI_MYVHS4hT3c2xX-t1p-KZCuo7OXvYA',
            '__eoi': 'ID=3e8de482b5ed8267:T=1758029716:RT=1758080739:S=AA-AfjZ8ZT1VjwxYo6PY8BMW8TCT',
            '_ga_MSFG3B015Z': 'GS2.1.s1760467989$o6$g1$t1760469468$j59$l0$h0',
        }

        self.headers = {
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'priority': 'u=1, i',
            'referer': 'https://inboxes.com/',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            # 'cookie': '_ga=GA1.1.32425121.1758029713; user_id=588d655f-89d6-492d-b427-58b851b32ef6; cto_bundle=6G0p5F8yTGlMY3JZVUNkTEJZUUtuemxCa3VSJTJGcDNJZ3JyUnA0OGRFZUJKQzdTWlVZR1hLaWRxV3cyQWdRaUZ5cjdJU3NCZTg3Y2tOWEZDeDFMMVlPUmFiZlJ2TXMyOEVobyUyRmdleFlGZzAlMkZtVGJXJTJCZVVNVkNRbVRMb0tHcmclMkZ1cFhvZERhVlhtZVV6c3ROR2ZpaiUyQlRtTnNQaWclM0QlM0Q; cto_bidid=Dw6GzF9HbXk1Q3BTQUtNJTJCMml6QyUyQnJ5R3V1b1ElMkI5d3lzeWZJTjM0S213eGdZWFQ5TW55dUo2ZTdPNE4yME5xNVJ2NFRFMFRsdXNDU3Q4Rk04Q1ZaazJUUExoSlBsbW0wZU5xV3RIdmhtRkNteEpsUnBYJTJGREJtWWtYTjJ5RDJkbHBWR3l1; _pbjs_userid_consent_data=3524755945110770; _ga_4TBVMLYBBP=GS2.1.s1758079326$o4$g1$t1758079345$j41$l0$h0; __gads=ID=7622753cf5bf69f8:T=1758029716:RT=1758080739:S=ALNI_MZFIDWsHp_hZY3MkI7dwOBpsCEwIQ; __gpi=UID=0000114995a45b45:T=1758029716:RT=1758080739:S=ALNI_MYVHS4hT3c2xX-t1p-KZCuo7OXvYA; __eoi=ID=3e8de482b5ed8267:T=1758029716:RT=1758080739:S=AA-AfjZ8ZT1VjwxYo6PY8BMW8TCT; _ga_MSFG3B015Z=GS2.1.s1760467989$o6$g1$t1760469468$j59$l0$h0',
        }


    # ===================== KHỞI TẠO TRÌNH DUYỆT ===================== #
    def _init_driver(self, index):
        temp_profile = tempfile.mkdtemp(prefix=f"firefox_profile_{index}_")

        options = Options()
        if self.firefox_path:
            options.binary_location = self.firefox_path
        options.set_preference("profile", temp_profile)
        options.add_argument("--width=400")
        options.add_argument("--height=600")

        # 🔹 Cấu hình proxy nếu có
        proxy_conf = None
        if self.proxy_list:
            proxy_raw = self.proxy_list[index % len(self.proxy_list)]

            # Tự động nhận dạng và chuyển định dạng proxy
            parts = proxy_raw.split(':')
            if len(parts) == 4:
                host, port, user, pwd = parts
                proxy_str = f"{user}:{pwd}@{host}:{port}"
            elif '@' in proxy_raw:
                proxy_str = proxy_raw  # đã đúng dạng USER:PASS@HOST:PORT
            else:
                proxy_str = proxy_raw  # dạng IP:PORT

            proxy_conf = {
                "proxy": {
                    "http": f"http://{proxy_str}",
                    "https": f"https://{proxy_str}",
                    "no_proxy": "localhost,127.0.0.1"
                }
            }

            print(f"[PROXY] 🧩 Gán proxy cho Thread-{index}: {proxy_str}")
        else:
            proxy_conf = {}

        # 🔹 Khởi tạo driver với selenium-wire
        service = Service(self.geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options, seleniumwire_options=proxy_conf)

        # 🔹 Sắp xếp vị trí cửa sổ
        SCREEN_WIDTH = 1920
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH
        row = index // COLUMNS
        col = index % COLUMNS
        driver.set_window_position(col * WINDOW_WIDTH, row * WINDOW_HEIGHT)

        return driver

    # ===================== REG ACCOUNT ===================== #

    def wait_and_click(self, locator, locator_type="xpath", timeout=60, driver=None):
        driver = driver or self.driver
        if locator_type.lower() == "xpath":
            by = By.XPATH
        elif locator_type.lower() == "id":
            by = By.ID 
        elif locator_type.lower() == "name":
            by = By.NAME
        else:
            raise ValueError("Unsupported locator type")

        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        element.click()
        sleep(1.5)


    def wait_and_send_keys(self, locator, keys, locator_type="xpath", timeout=60, driver=None):
        driver = driver or self.driver

        def human_typing(element, text, delay_range=(0.1, 0.3)):
            for char in text:
                element.send_keys(char)
                sleep(random.uniform(*delay_range))

        if locator_type.lower() == "xpath":
            by = By.XPATH
        elif locator_type.lower() == "id":
            by = By.ID 
        elif locator_type.lower() == "name":
            by = By.NAME
        else:
            raise ValueError("Unsupported locator type")

        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        element.clear()
        human_typing(element, keys)
        sleep(1.5)


    def wait_and_get_text(self, xpath, timeout=60, driver=None):
        driver = driver or self.driver
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text

    

    def get_code_inboxes(self, mail, index=0):
        """
        Gửi request đến inboxes.com để lấy mail,
        rồi trích xuất mã Instagram (OTP) từ nội dung.
        Có hỗ trợ proxy (luân phiên trong danh sách).
        """
        url = f"https://inboxes.com/api/v2/inbox/{mail}"

        # 🔹 Lấy proxy nếu có
        proxies = None
        if getattr(self, "proxy_list", None):
            try:
                proxy_raw = self.proxy_list[index % len(self.proxy_list)]
                parts = proxy_raw.split(":")
                if len(parts) == 4:
                    host, port, user, pwd = parts
                    proxy_str = f"{user}:{pwd}@{host}:{port}"
                elif '@' in proxy_raw:
                    proxy_str = proxy_raw
                else:
                    proxy_str = proxy_raw

                proxies = {
                    "http": f"http://{proxy_str}",
                    "https": f"http://{proxy_str}"
                }

                print(f"[PROXY-INBOX] 🧩 Dùng proxy: {proxy_str}")

            except Exception as e:
                print(f"[PROXY-INBOX] ⚠️ Lỗi khi xử lý proxy: {e}")
                proxies = None

        # --- Gửi request ---
        try:
            response = requests.get(
                url,
                cookies=self.cookies,
                headers=self.headers,
                proxies=proxies,
                timeout=15
            )

            data = response.json()
        except Exception as e:
            print(f"[INBOX] ❌ Lỗi khi request đến inboxes.com: {e}")
            return None

        # --- Tách mã OTP ---
        code = None
        if data and "msgs" in data:
            pattern = re.compile(r"\b\d{4,8}\b")  # tìm dãy số 4–8 chữ số
            for msg in data["msgs"]:
                text = msg.get("s") or msg.get("body") or ""
                match = pattern.search(str(text))
                if match:
                    code = match.group(0)
                    break

        # --- Kết quả ---
        if code:
            print(f"[INBOX] ✅ Tìm thấy mã: {code}")
            return code
        else:
            print("[INBOX] ⚠️ Không tìm thấy mã OTP.")
            return None

    # {'msgs': [{'uid': 'C3Sa7iVoP5o2G5ooQsRYFReUNX0YbV', 'f': 'Instagram', 's': '359076 là mã Instagram của bạn', 'd': False, 'at': [], 'cr': '2025-10-14T19:16:49.344Z', 'r': 1760469409, 'ph': '[https://www.facebook.com/email_open_...', 'rr': '6 secs ago', 'ib': 'vequca5666@getairmail.com'}]}
    def get_mail_inboxes(self, driver):
        # Mở tab mới và chuyển sang
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

        # Vào inboxes.com
        driver.get('https://inboxes.com/')
        sleep(3)

        # Nhấn “Get my inbox”
        self.wait_and_click('/html/body/div/main/div/div/div/div[1]/button', driver=driver)

        # Nhấn “Choose for me”
        self.wait_and_click('/html/body/div/main/div/div/div/div[1]/div[2]/div/div/div/form/div/div[2]/button', driver=driver)

        # Lấy địa chỉ email
        mail = self.wait_and_get_text('/html/body/div/main/div/div/div/div[1]/h1/span[2]', driver=driver)

        print(f"[MAIL] ✉️ Lấy được mail: {mail}")

        # Đóng tab inboxes và quay lại tab Instagram
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return mail


    def register_account(self, account, index):
        driver = None  # Khởi tạo driver = None
        try:
            print(f"[Thread-{index}] 🔹 Bắt đầu đăng ký cho: {account['username']}")

            driver = self._init_driver(index)
            driver.get("https://www.instagram.com/accounts/emailsignup/")
            sleep(5)

            # --- Lấy mail ---
            mail = self.get_mail_inboxes(driver)

            # --- Nhập form đăng ký ---
            self.wait_and_send_keys('emailOrPhone', mail, locator_type="name", driver=driver)
            sleep(2)
            self.wait_and_send_keys('password', account['defaultPassword'], locator_type="name", driver=driver)
            # Nhấn "Sign up"
            sleep(2)
            try:
                self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/form/div[9]/div/button', driver=driver, timeout=10)

            except Exception as e:
                self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[2]/div/form/div[7]/div/div/div/button', driver=driver)
                self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/form/div[9]/div/button', driver=driver)

            # Chọn tháng sinh
            sleep(2)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[1]/select', driver=driver)
            self.wait_and_click(f'/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[1]/select/option[{random.randint(1, 12)}]', driver=driver)
            # Chọn ngày
            sleep(2)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[2]/select', driver=driver)
            self.wait_and_click(f'/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[2]/select/option[{random.randint(1, 31)}]', driver=driver)
            
            # Chọn năm
            sleep(2)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[3]/select', driver=driver)
            self.wait_and_click(f'/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[3]/select/option[{random.randint(25, 26)}]', driver=driver)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[6]/button', driver=driver)
            sleep(5)

            # === Lặp cho đến khi có mã xác nhận ===
            code_confirmed = False
            attempt = 0
            max_attempts = 5
            
            while not code_confirmed and attempt < max_attempts:
                attempt += 1
                code = self.get_code_inboxes(mail)
                
                if code:
                    try:
                        # Nhập mã xác nhận email
                        print(f"[Thread-{index}] 📝 Đang nhập mã xác nhận {code}...")
                        self.wait_and_send_keys('email_confirmation_code', code, locator_type="name", driver=driver, timeout=10)
                        sleep(2)
                        
                        # Nhấn nút xác nhận
                        print(f"[Thread-{index}] 🔘 Nhấn nút xác nhận...")
                        self.wait_and_click(
                            '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div[2]/form/div/div[2]/div',
                            driver=driver,
                            timeout=30
                        )
                        print(f"[Thread-{index}] ✅ Đã nhập và xác nhận mã {code}")
                        
                        # Chờ URL thay đổi để xác nhận đã chuyển trang
                        print(f"[Thread-{index}] ⏳ Chờ trang chuyển tiếp...")
                        sleep(5)
                        
                        current_url = driver.current_url
                        print(f"[Thread-{index}] 🔗 URL hiện tại: {current_url}")
                        
                        # Kiểm tra xem đã chuyển trang chưa
                        if "confirmation" not in current_url.lower():
                            code_confirmed = True
                            print(f"[Thread-{index}] ✅ Đã xác nhận thành công, trang đã chuyển!")
                        else:
                            print(f"[Thread-{index}] ⚠️ Vẫn ở trang xác nhận, thử lại...")
                            
                    except Exception as e:
                        print(f"[Thread-{index}] ❌ Lỗi khi nhập mã: {e}")
                        sleep(3)
                else:
                    # Chưa có mã, nhấn gửi lại
                    try:
                        print(f"[Thread-{index}] ⏳ Lần thử {attempt}/{max_attempts}: Chưa thấy mã, đang nhấn gửi lại...")
                        self.wait_and_click(
                            '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div[1]/div[2]/span/div',
                            driver=driver,
                            timeout=5
                        )
                        sleep(5)
                    except Exception as e:
                        print(f"[Thread-{index}] ⚠️ Không thể nhấn gửi lại: {e}")
                        sleep(3)

            if not code_confirmed:
                print(f"[Thread-{index}] ❌ Không thể xác nhận mã sau {max_attempts} lần thử!")
                return  # Đảm bảo driver được đóng trong finally

            # === Chờ đến khi Instagram load về trang chính ===
            print(f"[Thread-{index}] 🔍 Bắt đầu chờ trang chính Instagram...")
            graphql_req = None

            for i in range(120):
                current_url = driver.current_url
                print(f"[Thread-{index}] 🔗 [{i+1}/120] Checking URL: {current_url}")

                if current_url.startswith("https://www.instagram.com/?nux=1") or current_url == "https://www.instagram.com/":
                    print(f"[Thread-{index}] ✅ Đã vào trang chính, chờ request /api/graphql ...")
                    self._wait_for_graphql(driver, timeout=20)
                    graphql_req = self._find_graphql_request(driver)
                    break
                elif "challenge" in current_url or "suspended" in current_url:
                    driver.quit()  # Dừng tiến trình nếu bị challenge hoặc suspended
                    account_data = {
                        'username': mail.split('@')[0],
                        'email': mail,
                        'password': account['defaultPassword'],
                        'cookie': "died_account"
                    }
                    eel.addAccountToTable(account_data)
            # https://www.instagram.com/accounts/suspended/?next=https%3A%2F%2Fwww.instagram.com%2F%3Fnux%3D1%26__coig_ufac%3D1

                sleep(1)

            # === Kiểm tra và in cookie ===
            if graphql_req:
                cookie_header = graphql_req.headers.get("Cookie", "")
                source = driver.page_source
                username = source.split('{"user":{"username":"')[1].split('"')[0]
                print(f"\n[Thread-{index}] 📋 RESULT: {username}|{mail}|{account['defaultPassword']}|{cookie_header}\n")
                
                account_data = {
                    'username': username,
                    'email': mail,
                    'password': account['defaultPassword'],
                    'cookie': cookie_header
                }
                eel.addAccountToTable(account_data)
                
            else:
                print(f"[Thread-{index}] ⚠️ Không tìm thấy request /api/graphql")
                print(f"\n[Thread-{index}] 📋 RESULT (No Cookie): {mail}|{account['defaultPassword']}|NO_COOKIE\n")
                
                account_data = {
                    'username': mail.split('@')[0],
                    'email': mail,
                    'password': account['defaultPassword'],
                    'cookie': 'NO_COOKIE'
                }
                eel.addAccountToTable(account_data)
            
            sleep(3)
            print(f"[Thread-{index}] 🏁 Hoàn tất!")
            
        except Exception as e:
            print(f"[Thread-{index}] ❌ LỖI NGHIÊM TRỌNG: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # ĐẢM BẢO driver luôn được đóng
            if driver:
                try:
                    driver.quit()
                    print(f"[Thread-{index}] 🔒 Đã đóng driver")
                except:
                    pass


    # ===================== BẮT REQUEST GRAPHQL ===================== #
    def _wait_for_graphql(self, driver, timeout=15):
        """Đợi đến khi thấy request /api/graphql xuất hiện."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for req in driver.requests:
                if "/api/graphql" in req.path and req.response:
                    return True
            time.sleep(0.5)
        return False

    def _find_graphql_request(self, driver):
        """Tìm request /api/graphql cuối cùng."""
        graphql_requests = [
            req for req in driver.requests if "/api/graphql" in req.path and req.response
        ]
        if graphql_requests:
            return graphql_requests[-1]
        return None

    # ===================== QUẢN LÝ LUỒNG ===================== #
    # ===================== QUẢN LÝ LUỒNG ===================== #
    def thread_reg(self):
        accounts = [
            {"id": i + 1, "username": f"test{i + 1}@example.com", "defaultPassword": self.data['defaultPassword']} 
            for i in range(self.account_count)
        ]

        threads = []
        completed = 0
        window_index = 0  # Đếm vị trí cửa sổ độc lập
        
        for i, acc in enumerate(accounts):
            # Chờ cho đến khi có slot trống (số thread đang chạy < thread_count)
            while len([t for t in threads if t.is_alive()]) >= self.thread_count:
                sleep(0.5)
                # Dọn dẹp các thread đã hoàn thành
                for t in threads:
                    if not t.is_alive() and not hasattr(t, '_cleaned'):
                        t._cleaned = True
                        completed += 1
                        print(f"[MAIN] ✅ Một thread hoàn thành ({completed}/{len(accounts)})")
            
            # Tạo thread mới với window_index
            t = threading.Thread(target=self.register_account, args=(acc, window_index), daemon=True)
            t.start()
            threads.append(t)
            
            print(f"[MAIN] 🚀 Đã khởi chạy thread {i+1}/{len(accounts)} (vị trí cửa sổ: {window_index})")
            
            # Tăng window_index và reset về 0 khi vượt quá số luồng
            window_index = (window_index + 1) % self.thread_count
            
            # Delay giữa các lần tạo thread
            if i < len(accounts) - 1:
                sleep(self.delay)

        # Chờ tất cả thread hoàn thành
        print(f"\n[MAIN] ⏳ Đang chờ {len(threads)} thread hoàn thành...")
        
        for t in threads:
            if t.is_alive():
                t.join(timeout=300)  # Timeout 5 phút mỗi thread
                if t.is_alive():
                    print(f"[MAIN] ⚠️ Thread vẫn đang chạy sau 5 phút!")
                elif not hasattr(t, '_cleaned'):
                    completed += 1
                    print(f"[MAIN] ✅ Thread hoàn thành ({completed}/{len(accounts)})")

        print(f"\n✅ [MAIN] Hoàn tất toàn bộ đăng ký. Tổng: {completed}/{len(accounts)} tài khoản")

# ===================== CHẠY DEMO ===================== #
# if __name__ == "__main__":
#     data = {
#         "accountCount": 10,
#         "threadCount": 5,
#         "delay": 5,
#         "firefoxPath": r"C:\Program Files\Mozilla Firefox\firefox.exe",
#         "geckodriverPath": r"C:\Users\pc\Desktop\shin\reg_ig\firefox\geckodriver.exe"
#         ,
#         "defaultPassword": "pn30042007@",
#         "proxyList": [
#             "sp06v2-03.proxygiare1k.shop:37616:sp06v205-37616:WTLCO",
#             "sp06v2-03.proxygiare1k.shop:37615:sp06v205-37615:UAGSL",
#             "sp06v2-03.proxygiare1k.shop:37613:sp06v205-37613:MAQUE"
#         ]
#     }


#     mgr = FirefoxManager(data)
#     mgr.thread_reg()

