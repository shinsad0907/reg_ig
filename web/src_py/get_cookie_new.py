import os
import time
import threading
import tempfile
from seleniumwire import webdriver
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

class CookieGetter:
    def __init__(self, data):
        self.data = data
        self.firefox_path = data['xpath_settings']['firefox']
        self.geckodriver_path = data['xpath_settings']['geckodriver']
        self.results = []  # ✅ Lưu kết quả
        self.lock = threading.Lock()  # ✅ Lock cho thread-safe
        
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
        }

    def _init_driver(self, index, proxy):
        temp_profile = tempfile.mkdtemp(prefix=f"firefox_profile_{index}_")

        options = Options()
        if self.firefox_path:
            options.binary_location = self.firefox_path
        options.set_preference("profile", temp_profile)
        options.add_argument("--width=400")
        options.add_argument("--height=600")
        print(proxy)
        
        proxy_conf = None
        if proxy:
            parts = proxy.split(':')
            if len(parts) == 4:
                host, port, user, pwd = parts
                proxy_str = f"{user}:{pwd}@{host}:{port}"
            elif '@' in proxy:
                proxy_str = proxy
            else:
                proxy_str = proxy

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

        service = Service(self.geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options, seleniumwire_options=proxy_conf)

        SCREEN_WIDTH = 1920
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH
        row = index // COLUMNS
        col = index % COLUMNS
        driver.set_window_position(col * WINDOW_WIDTH, row * WINDOW_HEIGHT)

        return driver

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
        url = f"https://inboxes.com/api/v2/inbox/{mail}"
        print(url)
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

        code = None
        if data and "msgs" in data:
            pattern = re.compile(r"\b\d{4,8}\b")
            for msg in data["msgs"]:
                text = msg.get("s") or msg.get("body") or ""
                match = pattern.search(str(text))
                if match:
                    code = match.group(0)
                    break

        if code:
            print(f"[INBOX] ✅ Tìm thấy mã: {code}")
            return code
        else:
            print("[INBOX] ⚠️ Không tìm thấy mã OTP.")
            return None

    def check_die(self, driver):
        if "suspended" in driver.current_url:
            return False
        else:
            return True

    def _wait_for_graphql(self, driver, timeout=15):
        start_time = time.time()
        while time.time() - start_time < timeout:
            for req in driver.requests:
                if "/api/graphql" in req.path and req.response:
                    return True
            time.sleep(0.5)
        return False

    def _find_graphql_request(self, driver):
        graphql_requests = [
            req for req in driver.requests if "/graphql/query" in req.path and req.response
        ]
        if graphql_requests:
            return graphql_requests[-1]
        return None
    
    def get_mail_inboxes(self, mail, index=0):
        url = f"https://inboxes.com/api/v2/inbox/{mail}"

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

        try:
            response = requests.get(
                url,
                cookies=self.cookies,
                headers=self.headers,
                proxies=proxies,
                timeout=15
            ).json()
            print(response)
            response_getcode = requests.get(f'https://inboxes.com/read/{response['msgs'][0]['uid']}',
                cookies=self.cookies,
                headers=self.headers,
                proxies=proxies,
                timeout=15
            ).text

        except Exception as e:
            print(f"[INBOX] ❌ Lỗi khi request đến inboxes.com: {e}")
            return None

        print(response_getcode)
        code = response_getcode.split('<font size="6">')[1].split('</font>')[0]
        print(code)
        
        if code:
            print(f"[INBOX] ✅ Tìm thấy mã: {code}")
            return code
        else:
            print("[INBOX] ⚠️ Không tìm thấy mã OTP.")
            return None

    def getcookie(self, driver):
        driver.re
        self._wait_for_graphql(driver, timeout=20)
        graphql_req = self._find_graphql_request(driver)
        if graphql_req:
            cookie_header = graphql_req.headers.get("Cookie", "")
            return cookie_header

    def get_cookie(self, account, index):
        print(f"\n[Thread-{index}] 🚀 Bắt đầu xử lý account: {account['username']}")
        print(f"[Thread-{index}] 📍 Proxy: {account['proxy']}")
        
        driver = None
        result = None
        
        try:
            driver = self._init_driver(index=index, proxy=account['proxy'])
            driver.get("https://www.instagram.com/")
            
            # ✅ Gửi thông báo về frontend
            self._update_frontend(account['username'], 'checking', None)
            
            self.wait_and_send_keys(
                '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form/div[1]/div[1]/div/label/input', 
                account['username'], 
                driver=driver
            )
            
            self.wait_and_send_keys(
                '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form/div[1]/div[2]/div/label/input', 
                account['password'], 
                driver=driver
            )
            
            self.wait_and_click(
                '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form/div[1]/div[3]', 
                driver=driver
            )
            
            sleep(10)
            
            if self.check_die(driver):
                if "auth_platform" in driver.current_url:
                    code_mail = self.get_mail_inboxes(account['email'])
                    self.wait_and_send_keys('//*[@id="_r_7_"]', code_mail, driver=driver)
                    self.wait_and_click(
                        '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[3]/div/div[2]/div/div/div', 
                        driver=driver
                    )
                    
                    for i in range(60):
                        if "accounts" in driver.current_url:
                            cookie = self.getcookie(driver)
                            print(f"✅ [Thread-{index}] Cookie: {cookie}")
                            
                            result = {
                                "username": account['username'],
                                "status": True,
                                "message": cookie
                            }
                            
                            # ✅ Cập nhật frontend
                            self._update_frontend(account['username'], 'live', cookie)
                            break
                        else:
                            sleep(1)
                else:
                    for i in range(60):
                        if "accounts" in driver.current_url:
                            cookie = self.getcookie(driver)
                            print(f"✅ [Thread-{index}] Cookie: {cookie}")
                            
                            result = {
                                "username": account['username'],
                                "status": True,
                                "message": cookie
                            }
                            
                            # ✅ Cập nhật frontend
                            self._update_frontend(account['username'], 'live', cookie)
                            break
                        else:
                            sleep(1)
            else:
                result = {
                    "username": account['username'],
                    "status": False,
                    "message": "die"
                }
                
                # ✅ Cập nhật frontend
                self._update_frontend(account['username'], 'die', None)
            
        except Exception as e:
            print(f"[Thread-{index}] ❌ Lỗi: {e}")
            result = {
                "username": account['username'],
                "status": False,
                "message": str(e)
            }
            
            # ✅ Cập nhật frontend
            self._update_frontend(account['username'], 'die', None)
            
        finally:
            if driver:
                driver.quit()
                print(f"[Thread-{index}] 🔒 Đã đóng driver")
            
            # ✅ Lưu kết quả
            if result:
                with self.lock:
                    self.results.append(result)

    def _update_frontend(self, username, status, cookie):
        """Gửi cập nhật về frontend qua eel"""
        try:
            import eel
            eel.updateAccountStatus(username, status, cookie, None)
        except Exception as e:
            print(f"⚠️ Không thể cập nhật frontend: {e}")

    def thread_get_cookie(self):
        accounts = self.data.get('accounts', [])
        if not accounts:
            print("❌ Không có tài khoản nào!")
            return

        max_threads = int(self.data.get('threads', 2))
        delay = float(self.data.get('delay', 0))

        print(f"\n{'='*60}")
        print(f"🔥 BẮT ĐẦU XỬ LÝ {len(accounts)} TÀI KHOẢN")
        print(f"⚙️  Luồng: {max_threads} | Delay: {delay}s")
        print(f"{'='*60}\n")

        active_threads = []
        for i, acc in enumerate(accounts):
            while len(active_threads) >= max_threads:
                active_threads = [t for t in active_threads if t.is_alive()]
                time.sleep(0.1)

            t = threading.Thread(target=self.get_cookie, args=(acc, i), daemon=True)
            t.start()
            active_threads.append(t)
            
            print(f"[MAIN] 🚀 Đã khởi động Thread-{i}")
            
            time.sleep(delay)

        for t in active_threads:
            t.join()
        
        print(f"\n{'='*60}")
        print(f"✅ HOÀN TẤT TẤT CẢ {len(accounts)} TÀI KHOẢN")
        print(f"{'='*60}\n")
        
        # ✅ Trả về kết quả
        return self.results