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
from urllib.parse import unquote
import eel

class NurtureAccount:
    def __init__(self, data):
        self.data = data
        self.firefox_path = data['config']['xpaths']['firefox']
        self.geckodriver_path = data['config']['xpaths']['geckodriver']
        self.config = data['config']
        self.results = []
        self.lock = threading.Lock()
        self.window_index_counter = 0  # ✅ Counter để tracking vị trí cửa sổ
        self.window_index_lock = threading.Lock()  # ✅ Lock cho counter
        
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

    def _get_next_window_index(self):
        """✅ Lấy index tiếp theo cho cửa sổ browser (thread-safe)"""
        with self.window_index_lock:
            index = self.window_index_counter
            self.window_index_counter += 1
            return index

    def _reset_window_counter(self):
        """✅ Reset counter về 0 khi bắt đầu batch mới"""
        with self.window_index_lock:
            self.window_index_counter = 0
            print(f"🔄 Reset window counter về 0")

    def _init_driver(self, proxy):
        """✅ Khởi tạo driver với vị trí được tính toán tự động"""
        window_index = self._get_next_window_index()
        
        temp_profile = tempfile.mkdtemp(prefix=f"firefox_profile_{window_index}_")

        options = Options()
        if self.firefox_path:
            options.binary_location = self.firefox_path
        options.set_preference("profile", temp_profile)
        options.add_argument("--width=400")
        options.add_argument("--height=600")
        print(f"[Window-{window_index}] Proxy: {proxy}")
        
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

            print(f"[PROXY] 🧩 Gán proxy cho Window-{window_index}: {proxy_str}")
        else:
            proxy_conf = {}

        service = Service(self.geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options, seleniumwire_options=proxy_conf)

        # ✅ Tính toán vị trí dựa trên window_index
        SCREEN_WIDTH = 1920
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH
        
        row = window_index // COLUMNS
        col = window_index % COLUMNS
        
        x_pos = col * WINDOW_WIDTH
        y_pos = row * WINDOW_HEIGHT
        
        print(f"[Window-{window_index}] 📍 Vị trí: ({x_pos}, {y_pos}) - Row {row}, Col {col}")
        
        driver.set_window_position(x_pos, y_pos)
        driver.get('https://www.instagram.com/')
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

        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'center'
                });
            """, element)
            sleep(0.5)
            
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            
            try:
                element.click()
                print(f"✓ Click thành công: {locator[:50]}...")
            except Exception as click_error:
                print(f"⚠️ Click thất bại, dùng JavaScript: {click_error}")
                driver.execute_script("arguments[0].click();", element)
                print(f"✓ JavaScript click thành công")
            
            sleep(1.5)
            
        except Exception as e:
            print(f"❌ Không thể click: {locator}")
            print(f"   Lỗi: {e}")
            raise

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

    def parse_cookie_string(self, cookie_str: str, percent_decode: bool = False) -> dict:
        cookies = {}
        if not cookie_str:
            return cookies
        parts = [p.strip() for p in cookie_str.split(';') if p.strip()]
        for part in parts:
            if '=' in part:
                key, val = part.split('=', 1)
                key = key.strip()
                val = val.strip()
                if percent_decode:
                    val = unquote(val)
                cookies[key] = val
        return cookies
    
    def addcookie(self, driver, cookie):
        cookies = self.parse_cookie_string(cookie, percent_decode=False)
        
        print("Đang set cookies...")
        for name, value in cookies.items():
            driver.add_cookie({
                'name': name,
                'value': value,
                'domain': '.instagram.com'
            })
        driver.refresh()

    def upload_bio(self, driver, username):
        try:
            bio_xpath = self.config['bioFilePath']
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'bio', 'start', None)
            
            with open(bio_xpath, 'r', encoding='utf-8') as f:
                bios = f.readlines()
                bio = random.choice(bios).strip()

            driver.get('https://www.instagram.com/accounts/edit/')
            self.wait_and_send_keys('//*[@id="pepBio"]', bio, driver=driver)
            time.sleep(3)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[3]/div/div/form/div[5]/div', driver=driver)
            time.sleep(5)
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'bio', 'success', {'bio': bio})
            
            return True
        except Exception as e:
            print(f"❌ Lỗi upload_bio: {e}")
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'bio', 'error', {'message': str(e)})
            
            return False

    def upload_status(self, driver, username):
        try:
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'post', 'start', None)
            
            image_path = self.config['statusImageFolder']
            caption_path = self.config['statusFile']

            with open(caption_path, 'r', encoding='utf-8') as f:
                captions = f.readlines()
                caption = random.choice(captions).strip()
            
            file_names = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]
            if not file_names:
                print("⚠️ Thư mục không có file ảnh nào.")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'Không có ảnh'})
                return False
            
            random_file = random.choice(file_names)
            full_image_path = os.path.join(image_path, random_file)
            print(f"🎲 File ảnh được chọn: {random_file}")

            driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(4)

            print("🔘 Đang tìm nút tạo bài viết...")
            
            create_post_selectors = [
                '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/section/main/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/ul/li[3]/div/div/div/div/div[3]'
            ]
            
            create_button = None
            for selector in create_post_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"✓ Tìm thấy nút tạo: {selector[:50]}...")
                        create_button = elements[0]
                        break
                except:
                    continue
            
            if not create_button:
                print("❌ Không tìm thấy nút tạo bài viết!")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'Không tìm thấy nút tạo'})
                return False
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_button)
            time.sleep(1)
            
            try:
                create_button.click()
            except:
                print("⚠️ Click thất bại, dùng JS...")
                driver.execute_script("arguments[0].click();", create_button)
            
            print("✓ Đã click nút tạo bài viết")
            time.sleep(3)

            print("🔍 Đang tìm input file để upload ảnh...")
            
            time.sleep(2)
            
            input_xpaths = [
                "//input[@type='file']",
                "//div[@role='dialog']//input[@type='file']",
                "//*[contains(@class, 'piCib')]//input[@type='file']"
            ]
            
            file_input = None
            
            for xpath in input_xpaths:
                try:
                    print(f"  Thử: {xpath}")
                    inputs = driver.find_elements(By.XPATH, xpath)
                    if inputs:
                        file_input = inputs[-1]
                        print(f"  ✅ Tìm thấy input!")
                        break
                except:
                    continue
            
            if not file_input:
                print("❌ Không tìm thấy input file!")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'Không tìm thấy input'})
                return False
            
            print(f"📤 Đang upload file: {full_image_path}")
            full_image_path = os.path.normpath(full_image_path)
            if not os.path.exists(full_image_path):
                print(f"❌ File không tồn tại: {full_image_path}")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'File không tồn tại'})
                return False
            
            file_input.send_keys(full_image_path)
            print("✅ Đã upload file!")
            
            print("⏳ Đang đợi Instagram xử lý ảnh...")
            time.sleep(8)
            
            print("🔍 Đang click nút Next lần 1...")
            
            result1 = driver.execute_script("""
                var dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return {success: false, message: 'Không tìm thấy dialog'};
                
                var buttons = dialog.querySelectorAll('button, div[role="button"]');
                
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var text = btn.innerText.toLowerCase();
                    
                    if (text.includes('next') || text.includes('tiếp')) {
                        btn.scrollIntoView({block: 'center'});
                        btn.click();
                        return {success: true, message: 'Đã click Next lần 1: ' + btn.innerText};
                    }
                }
                
                var headerButtons = dialog.querySelectorAll('header button, header div[role="button"]');
                if (headerButtons.length > 0) {
                    var lastBtn = headerButtons[headerButtons.length - 1];
                    lastBtn.scrollIntoView({block: 'center'});
                    lastBtn.click();
                    return {success: true, message: 'Đã click button cuối trong header (lần 1)'};
                }
                
                return {success: false, message: 'Không tìm thấy nút Next lần 1'};
            """)
            
            if not result1 or not result1.get('success'):
                print("❌ Không thể click nút Next lần 1!")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'Không click được Next lần 1'})
                return False
            
            print(f"✅ {result1.get('message')}")
            time.sleep(3)
            
            print("🔍 Đang click nút Next lần 2...")
            
            result2 = driver.execute_script("""
                var dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return {success: false, message: 'Không tìm thấy dialog'};
                
                var attempts = 0;
                var maxAttempts = 5;
                
                function tryClickNext() {
                    attempts++;
                    
                    var buttons = dialog.querySelectorAll('button, div[role="button"]');
                    console.log('Số lượng buttons tìm thấy:', buttons.length);
                    
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var text = btn.innerText.toLowerCase().trim();
                        console.log('Button', i, ':', text);
                        
                        if (text === 'next' || text === 'tiếp' || text.includes('next') || text.includes('tiếp')) {
                            var style = window.getComputedStyle(btn);
                            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                                btn.scrollIntoView({block: 'center', behavior: 'smooth'});
                                setTimeout(function() { btn.click(); }, 100);
                                return {success: true, message: 'Đã click Next lần 2 (theo text): ' + btn.innerText};
                            }
                        }
                    }
                    
                    var headerButtons = dialog.querySelectorAll('header button, header div[role="button"]');
                    console.log('Số buttons trong header:', headerButtons.length);
                    
                    if (headerButtons.length > 0) {
                        var lastBtn = headerButtons[headerButtons.length - 1];
                        var lastStyle = window.getComputedStyle(lastBtn);
                        
                        if (lastStyle.display !== 'none' && lastStyle.visibility !== 'hidden') {
                            lastBtn.scrollIntoView({block: 'center', behavior: 'smooth'});
                            setTimeout(function() { lastBtn.click(); }, 100);
                            return {success: true, message: 'Đã click button cuối trong header (lần 2): ' + lastBtn.innerText};
                        }
                    }
                    
                    var allButtons = dialog.querySelectorAll('button');
                    for (var j = 0; j < allButtons.length; j++) {
                        var b = allButtons[j];
                        var rect = b.getBoundingClientRect();
                        var dialogRect = dialog.getBoundingClientRect();
                        
                        if (rect.right > dialogRect.right - 100 && rect.top < dialogRect.top + 100) {
                            var bStyle = window.getComputedStyle(b);
                            if (bStyle.display !== 'none' && bStyle.visibility !== 'hidden') {
                                b.scrollIntoView({block: 'center', behavior: 'smooth'});
                                setTimeout(function() { b.click(); }, 100);
                                return {success: true, message: 'Đã click button góc phải (lần 2): ' + b.innerText};
                            }
                        }
                    }
                    
                    if (attempts < maxAttempts) {
                        return null;
                    }
                    
                    return {success: false, message: 'Không tìm thấy nút Next lần 2 sau ' + attempts + ' lần thử'};
                }
                
                var result = tryClickNext();
                return result || {success: false, message: 'Không thể click Next lần 2'};
            """)
            
            if not result2 or not result2.get('success'):
                print("❌ Không thể click nút Next lần 2!")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'Không click được Next lần 2'})
                return False
            
            print(f"✅ {result2.get('message')}")
            time.sleep(3)
            
            print("📝 Đang nhập caption...")
            
            caption_xpaths = [
                "//textarea[@placeholder='Write a caption...']",
                "//textarea[@aria-label='Write a caption...']",
                "//div[@contenteditable='true'][@aria-label='Write a caption...']",
                "//div[@role='textbox']"
            ]
            
            caption_input = None
            
            for xpath in caption_xpaths:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements and elements[0].is_displayed():
                        caption_input = elements[0]
                        break
                except:
                    continue
            
            if caption_input:
                try:
                    caption_input.click()
                    time.sleep(0.5)
                    caption_input.clear()
                    
                    for char in caption:
                        caption_input.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    
                    print(f"✅ Đã nhập caption: {caption[:30]}...")
                except Exception as e:
                    print(f"⚠️ Lỗi nhập caption: {e}")
                    driver.execute_script("""
                        arguments[0].focus();
                        arguments[0].textContent = arguments[1];
                        arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                    """, caption_input, caption)
                    print("✅ Đã nhập caption bằng JS")
            else:
                print("⚠️ Không tìm thấy ô nhập caption, tiếp tục...")
            
            time.sleep(3)
            
            print("🔍 Đang tìm nút Share...")
            
            result3 = driver.execute_script("""
                var dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) return {success: false, message: 'Không tìm thấy dialog'};
                
                var buttons = dialog.querySelectorAll('button, div[role="button"]');
                
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var text = btn.innerText.toLowerCase();
                    
                    if (text.includes('share') || text.includes('chia sẻ')) {
                        btn.scrollIntoView({block: 'center'});
                        btn.click();
                        return {success: true, message: 'Đã click Share bằng JS'};
                    }
                }
                
                var headerButtons = dialog.querySelectorAll('header button, header div[role="button"]');
                if (headerButtons.length > 0) {
                    var lastBtn = headerButtons[headerButtons.length - 1];
                    lastBtn.scrollIntoView({block: 'center'});
                    lastBtn.click();
                    return {success: true, message: 'Đã click button cuối cùng (Share)'};
                }
                
                return {success: false, message: 'Không tìm thấy nút Share'};
            """)
            
            if not result3 or not result3.get('success'):
                print("❌ Không thể click nút Share!")
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'post', 'error', {'message': 'Không click được Share'})
                return False
            
            print(f"✅ {result3.get('message')}")
            print("✅ Đã click Share, đang đợi upload hoàn tất...")
            time.sleep(10)
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'post', 'success', None)
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi upload_status: {e}")
            import traceback
            traceback.print_exc()
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'post', 'error', {'message': str(e)})
            
            return False

    def addAvata(self, driver, username):
        try:
            folder_path = fr"{self.config['avatarFolder']}"

            file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

            if not file_names:
                print("⚠️ Thư mục không có file nào.")
                return False
            
            random_file = random.choice(file_names)
            print("🎲 File ngẫu nhiên được chọn là:")
            print(random_file)
            
            image_path = os.path.join(folder_path, random_file)

            driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(4)
            
            print("Đang tìm input file trong nút avatar...")
            
            avatar_button_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/section/main/div/div/header/div/section[1]/div/div/div/div[2]/span/div/div/div/button"
            
            input_xpaths = [
                avatar_button_xpath + "//input[@type='file']",
                avatar_button_xpath + "/input[@type='file']",
                "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/section/main/div/div/header/div/section[1]/div/div/div/div[2]/span//input[@type='file']",
                "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/section/main/div/div/header/div/section[1]//input[@type='file']"
            ]
            
            file_input = None
            
            for xpath in input_xpaths:
                try:
                    print(f"Thử XPath: {xpath}")
                    inputs = driver.find_elements(By.XPATH, xpath)
                    if inputs:
                        print(f"  ✅ Tìm thấy {len(inputs)} input!")
                        file_input = inputs[0]
                        break
                except Exception as e:
                    print(f"  ❌ Không tìm thấy: {e}")
                    continue
            
            if not file_input:
                print("\n❌ Không tìm thấy input file có sẵn!")
                print("Đang dùng JavaScript để tìm...")
                
                inputs_info = driver.execute_script("""
                    var inputs = document.querySelectorAll('input[type="file"]');
                    var result = [];
                    inputs.forEach(function(input, index) {
                        result.push({
                            index: index,
                            id: input.id,
                            name: input.name,
                            accept: input.accept,
                            parentTag: input.parentElement ? input.parentElement.tagName : 'none',
                            isVisible: input.offsetParent !== null
                        });
                    });
                    return result;
                """)
                
                print(f"\nTìm thấy {len(inputs_info)} input file trên trang:")
                for info in inputs_info:
                    print(f"  - Input {info['index']}: id={info['id']}, name={info['name']}, accept={info['accept']}, visible={info['isVisible']}")
                
                if inputs_info:
                    all_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                    if all_inputs:
                        file_input = all_inputs[0]
                        print(f"\n✅ Sử dụng input đầu tiên")
            
            if file_input:
                print("\n✅ Đã tìm thấy input file!")
                
                driver.execute_script("""
                    var input = arguments[0];
                    input.style.display = 'block';
                    input.style.visibility = 'visible';
                    input.style.opacity = '1';
                    input.style.position = 'relative';
                    input.style.zIndex = '99999';
                    input.removeAttribute('hidden');
                """, file_input)
                
                print("Đang upload file...")
                image_path = os.path.normpath(image_path)
                if not os.path.exists(image_path):
                    print(f"❌ File không tồn tại: {image_path}")
                    return False

                print(f"📁 Upload file: {image_path}")
                file_input.send_keys(image_path)

                print("✅ Đã send file!")
                
                time.sleep(3)
                
                driver.execute_script("""
                    var input = arguments[0];
                    if (input.files && input.files.length > 0) {
                        console.log('File uploaded:', input.files[0].name);
                        
                        var changeEvent = new Event('change', { bubbles: true });
                        input.dispatchEvent(changeEvent);
                        
                        var inputEvent = new Event('input', { bubbles: true });
                        input.dispatchEvent(inputEvent);
                    }
                """, file_input)
                return True
            else:
                print("\n❌ KHÔNG TÌM THẤY INPUT FILE NÀO!")
                return False

        except Exception as e:
            print(f"\n❌ LỖI: {e}")
            import traceback
            traceback.print_exc()
            return False

    def nurture(self, acc):
        """✅ Xử lý 1 account - không cần index nữa"""
        driver = None
        try:
            # ✅ Tự động lấy vị trí từ counter
            driver = self._init_driver(acc['proxy'])
            self.addcookie(driver, acc['cookie'])
            
            username = acc['username']
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(username, 'start', 'checking', None)
            
            # ===== UPLOAD AVATAR =====
            if self.config['uploadAvatar']:
                print(f"[{username}] 📸 Đang upload avatar...")
                
                if callable(getattr(eel, 'updateNurtureProgress', None)):
                    eel.updateNurtureProgress(username, 'avatar', 'start', None)
                
                if self.addAvata(driver, username):
                    print(f"[{username}] ✅ Upload avatar thành công!")
                    
                    if callable(getattr(eel, 'updateNurtureProgress', None)):
                        eel.updateNurtureProgress(username, 'avatar', 'success', None)
                    
                    with self.lock:
                        self.results.append({
                            "status": True,
                            "username": username,
                            "hasAvatar": True
                        })
                else:
                    print(f"[{username}] ❌ Upload avatar thất bại!")
                    
                    if callable(getattr(eel, 'updateNurtureProgress', None)):
                        eel.updateNurtureProgress(username, 'avatar', 'error', None)
                    
                    with self.lock:
                        self.results.append({
                            "status": False,
                            "username": username,
                            "hasAvatar": False
                        })
            
            # ===== UPLOAD STATUS =====
            if self.config['postStatus']:
                print(f"[{username}] 📝 Đang upload status...")
                
                if self.upload_status(driver, username):
                    print(f"[{username}] ✅ Upload status thành công!")
                else:
                    print(f"[{username}] ❌ Upload status thất bại!")
            
            # ===== UPLOAD BIO =====
            bio_text = None
            if self.config['updateBio']:
                print(f"[{username}] 📋 Đang upload bio...")
                
                bio_result = self.upload_bio(driver, username)
                if bio_result:
                    print(f"[{username}] ✅ Upload bio thành công!")
                    try:
                        with open(self.config['bioFilePath'], 'r', encoding='utf-8') as f:
                            bios = f.readlines()
                            bio_text = random.choice(bios).strip()
                    except:
                        bio_text = "Updated"
                else:
                    print(f"[{username}] ❌ Upload bio thất bại!")
            
            # ✅ Hoàn tất
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                final_data = {
                    'hasAvatar': self.config['uploadAvatar'],
                    'posts': 1 if self.config['postStatus'] else 0,
                    'bio': bio_text if self.config['updateBio'] else None,
                    'following': 0
                }
                eel.updateNurtureProgress(username, 'complete', 'success', final_data)
            
            return {
                "status": True,
                "username": username,
                "bio": bio_text
            }
            
        except Exception as e:
            print(f"❌ Lỗi nurture {acc['username']}: {e}")
            import traceback
            traceback.print_exc()
            
            if callable(getattr(eel, 'updateNurtureProgress', None)):
                eel.updateNurtureProgress(acc['username'], 'complete', 'error', {'message': str(e)})
            
            with self.lock:
                self.results.append({
                    "status": False,
                    "username": acc['username'],
                    "error": str(e)
                })
            
            return {
                "status": False,
                "username": acc['username'],
                "error": str(e)
            }
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
    def thread_get_cookie(self):
        accounts = self.data.get('accounts', [])
        if not accounts:
            print("❌ Không có tài khoản nào!")
            return []

        max_threads = int(self.data['config'].get('threads', 2))
        delay = float(self.data['config'].get('delay', 0))

        print(f"\n{'='*60}")
        print(f"🔥 BẮT ĐẦU XỬ LÝ {len(accounts)} TÀI KHOẢN")
        print(f"⚙️  Luồng: {max_threads} | Delay: {delay}s")
        print(f"{'='*60}\n")

        # ✅ Reset counter về 0 trước khi bắt đầu batch mới
        self._reset_window_counter()

        active_threads = []
        for i, acc in enumerate(accounts):
            while len(active_threads) >= max_threads:
                active_threads = [t for t in active_threads if t.is_alive()]
                time.sleep(0.1)

            # ✅ Không truyền index nữa, hàm nurture tự lấy từ counter
            t = threading.Thread(target=self.nurture, args=(acc,), daemon=True)
            t.start()
            active_threads.append(t)
            
            print(f"[MAIN] 🚀 Đã khởi động Thread cho {acc['username']}")
            
            time.sleep(delay)

        # ✅ Đợi tất cả threads hoàn thành
        for t in active_threads:
            t.join()
        
        print(f"\n{'='*60}")
        print(f"✅ HOÀN TẤT TẤT CẢ {len(accounts)} TÀI KHOẢN")
        print(f"📊 Kết quả: {len(self.results)} accounts đã xử lý")
        print(f"{'='*60}\n")
        
        return self.results