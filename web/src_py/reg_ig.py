import os
import time
import threading
import hashlib
import json
import random
from pathlib import Path
from seleniumwire import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
from time import sleep
import eel

class FirefoxManager:
    """
    🔥 FIREFOX ANTI-DETECT - VIETNAM 4G PROXY VERSION
    
    ✅ Đã FIX:
    - Timezone: Asia/Ho_Chi_Minh (Việt Nam)
    - Language: vi-VN (Tiếng Việt ưu tiên)
    - Locale: vi-VN
    - User-Agent: Giữ Firefox format nhưng phù hợp VN
    - Geo consistency: IP VN + timezone VN + language VN
    
    🎯 Phù hợp: Proxy 4G Việt Nam
    """
    
    # ===== VIETNAM CONFIG - CHUẨN CHO PROXY 4G VN =====
    VN_CONFIG = {
        'timezone': 'Asia/Ho_Chi_Minh',  # GMT+7
        'language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',  # Tiếng Việt ưu tiên
        'locale': 'vi-VN',
        'accept_language_header': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    def __init__(self, data):
        self.data = data
        self.firefox_path = data.get("firefoxPath")
        self.geckodriver_path = data.get("geckodriverPath")
        self.account_count = data.get("accountCount", 10)
        self.thread_count = data.get("threadCount", 3)
        self.delay = data.get("delay", 5)
        self.proxy_list = data.get("proxyList", [])
        
        self.profile_base_dir = Path(data.get("profileDir", "./firefox_profiles"))
        self.profile_base_dir.mkdir(exist_ok=True)
        
        # Cookies cho inboxes.com
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
        
        # Headers cho API requests - ĐÃ FIX CHO VN
        self.headers = {
            'accept': '*/*',
            'accept-language': self.VN_CONFIG['accept_language_header'],  # 🔴 FIX: Tiếng Việt
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

    def _generate_stable_fingerprint(self, profile_id):
        """
        Fingerprint ổn định - CHUẨN CHO VIETNAM
        """
        seed = int(hashlib.md5(str(profile_id).encode()).hexdigest(), 16)
        random.seed(seed)
        
        # Firefox version THẬT (recent versions)
        firefox_versions = [120, 121, 122, 123, 124, 125, 126]
        firefox_version = random.choice(firefox_versions)
        
        # Windows build THẬT (phổ biến ở VN)
        win_builds = ['10.0', '10.0.19045', '11.0.22621']  # Win 10 & 11
        win_build = random.choice(win_builds)
        
        # 🔴 User-Agent: Firefox format CHUẨN
        user_agent = f"Mozilla/5.0 (Windows NT {win_build}; Win64; x64; rv:{firefox_version}.0) Gecko/20100101 Firefox/{firefox_version}.0"
        
        # Hardware variation (phổ biến VN)
        hardware_concurrency = random.choice([4, 6, 8])  # 4-8 cores phổ biến
        
        # Screen resolution phổ biến VN
        screen_configs = [
            {'width': 1920, 'height': 1080},  # Full HD (phổ biến nhất)
            {'width': 1366, 'height': 768},   # Laptop cũ
            {'width': 1536, 'height': 864},   # Laptop mới
            {'width': 1600, 'height': 900},   # Desktop
        ]
        screen = random.choice(screen_configs)
        
        fingerprint = {
            'profile_id': profile_id,
            'user_agent': user_agent,
            'firefox_version': firefox_version,
            'language': self.VN_CONFIG['language'],
            'locale': self.VN_CONFIG['locale'],
            'timezone': self.VN_CONFIG['timezone'],
            'hardware_concurrency': hardware_concurrency,
            'screen': screen,
            'created_at': time.time()
        }
        
        random.seed()
        return fingerprint

    def _save_profile_config(self, profile_id, fingerprint, proxy=None):
        profile_dir = self.profile_base_dir / f"profile_{profile_id}"
        profile_dir.mkdir(exist_ok=True)
        config_file = profile_dir / "fingerprint.json"
        
        config = {
            'fingerprint': fingerprint,
            'proxy': proxy,
            'updated_at': time.time()
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def _load_profile_config(self, profile_id):
        profile_dir = self.profile_base_dir / f"profile_{profile_id}"
        config_file = profile_dir / "fingerprint.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _get_minimal_anti_detect_js(self, fp):
        """
        JS MINIMAL - VIETNAM OPTIMIZED
        
        ✅ Thêm:
        - Timezone override = Asia/Ho_Chi_Minh
        - Language preference = vi-VN
        - Geolocation mock (optional)
        """
        return f"""
(function() {{
    'use strict';
    
    // ============ 1. WEBDRIVER (CRITICAL) ============
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined,
        configurable: true
    }});
    
    if (navigator.__proto__.webdriver !== undefined) {{
        delete navigator.__proto__.webdriver;
    }}
    
    // ============ 2. TIMEZONE - VIETNAM ============
    // Override timezone offset to GMT+7
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {{
        return -420; // GMT+7 = -420 minutes
    }};
    
    // Override Intl.DateTimeFormat
    const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
        const options = originalResolvedOptions.call(this);
        options.timeZone = 'Asia/Ho_Chi_Minh';
        return options;
    }};
    
    // ============ 3. LANGUAGE - VIETNAM ============
    Object.defineProperty(navigator, 'language', {{
        get: () => 'vi-VN',
        configurable: true
    }});
    
    Object.defineProperty(navigator, 'languages', {{
        get: () => ['vi-VN', 'vi', 'en-US', 'en'],
        configurable: true
    }});
    
    // ============ 4. HARDWARE ============
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {fp['hardware_concurrency']},
        configurable: true
    }});
    
    // ============ 5. GEOLOCATION (OPTIONAL - HCM COORDS) ============
    // Uncomment nếu cần fake location
    /*
    const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
    navigator.geolocation.getCurrentPosition = function(success, error, options) {{
        const position = {{
            coords: {{
                latitude: 10.8231,  // Ho Chi Minh City
                longitude: 106.6297,
                accuracy: 100,
                altitude: null,
                altitudeAccuracy: null,
                heading: null,
                speed: null
            }},
            timestamp: Date.now()
        }};
        success(position);
    }};
    */
    
    console.log('[VN Anti-Detect] Loaded - Timezone: Asia/Ho_Chi_Minh, Language: vi-VN');
}})();
"""

    def _init_driver(self, index):
        """
        Khởi tạo Firefox - VIETNAM OPTIMIZED
        """
        profile_id = f"profile_{index}"
        profile_dir = self.profile_base_dir / profile_id
        profile_dir.mkdir(exist_ok=True)
        
        # Load/create fingerprint
        config = self._load_profile_config(index)
        if config:
            fingerprint = config['fingerprint']
            print(f"[INIT] 📂 Load profile: {profile_id}")
        else:
            fingerprint = self._generate_stable_fingerprint(index)
            print(f"[INIT] 🆕 New profile: {profile_id}")
        
        # ===== PROXY SETUP =====
        proxy_str = None
        if self.proxy_list:
            proxy_raw = self.proxy_list[index % len(self.proxy_list)]
            parts = proxy_raw.split(':')
            
            if len(parts) == 4:
                host, port, user, pwd = parts
                proxy_str = f"{user}:{pwd}@{host}:{port}"
            elif '@' in proxy_raw:
                proxy_str = proxy_raw
            else:
                proxy_str = proxy_raw
            
            print(f"[PROXY] 🇻🇳 Thread-{index}: {host}:{port} (Vietnam 4G)")
        
        # Save config
        self._save_profile_config(index, fingerprint, proxy_str)
        
        # ===== FIREFOX OPTIONS =====
        options = Options()
        if self.firefox_path:
            options.binary_location = self.firefox_path
        
        # 🔴 FIX POPUP
        options.set_capability("unhandledPromptBehavior", "dismiss")
        
        # Profile persistent
        options.set_preference("profile", str(profile_dir))
        
        # ===== 1. USER-AGENT (FIREFOX FORMAT) =====
        options.set_preference("general.useragent.override", fingerprint['user_agent'])
        
        # ===== 2. LANGUAGE & LOCALE - VIETNAM =====
        options.set_preference("intl.accept_languages", fingerprint['language'])
        options.set_preference("intl.locale.requested", fingerprint['locale'])
        options.set_preference("intl.regional_prefs.use_os_locales", False)
        
        # 🔴 TẮT POPUP LANGUAGE
        options.set_preference("intl.multilingual.downloadEnabled", False)
        options.set_preference("intl.multilingual.enabled", False)
        options.set_preference("intl.multilingual.liveReload", False)
        options.set_preference("intl.multilingual.liveReloadBidirectional", False)
        
        # ===== 3. TIMEZONE - VIETNAM =====
        # Firefox sẽ dùng system timezone, nhưng JS sẽ override
        options.set_preference("privacy.resistFingerprinting.block_mozAddonManager", True)
        
        # ===== 4. RESIST FINGERPRINTING =====
        options.set_preference("privacy.resistFingerprinting", True)
        options.set_preference("privacy.resistFingerprinting.letterboxing", True)
        
        # ===== 5. WEBRTC BLOCKING =====
        options.set_preference("media.peerconnection.enabled", False)
        options.set_preference("media.navigator.enabled", False)
        
        # ===== 6. GEO PERMISSIONS =====
        options.set_preference("geo.enabled", True)
        options.set_preference("geo.provider.use_geoclue", False)
        
        # ===== 7. MEDIA PERMISSIONS =====
        options.set_preference("permissions.default.camera", 2)  # Block
        options.set_preference("permissions.default.microphone", 2)  # Block
        options.set_preference("permissions.default.desktop-notification", 2)  # Block
        
        # ===== 8. TRACKING PROTECTION =====
        options.set_preference("privacy.trackingprotection.enabled", True)
        options.set_preference("privacy.trackingprotection.socialtracking.enabled", True)
        
        # ===== 9. DISABLE AUTOMATION FLAGS =====
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        # ===== 10. PERFORMANCE =====
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", True)
        
        # ===== INIT DRIVER =====
        service = Service(self.geckodriver_path)
        proxy_conf = {}
        if proxy_str:
            proxy_conf = {
                "proxy": {
                    "http": f"http://{proxy_str}",
                    "https": f"https://{proxy_str}",
                    "no_proxy": "localhost,127.0.0.1"
                }
            }
        
        try:
            driver = webdriver.Firefox(
                service=service, 
                options=options, 
                seleniumwire_options=proxy_conf
            )
            
            # 🔴 Override alert functions
            driver.execute_script("""
                window.alert = function() {};
                window.confirm = function() { return true; };
                window.prompt = function() { return null; };
            """)
            
        except Exception as e:
            print(f"[ERROR] Thread-{index} init failed: {e}")
            return None
            
        # ===== INJECT JS VIETNAM OPTIMIZED =====
        try:
            anti_detect_js = self._get_minimal_anti_detect_js(fingerprint)
            driver.execute_script(anti_detect_js)
            print(f"[JS] ✅ VN Anti-Detect loaded (GMT+7, vi-VN)")
        except Exception as e:
            print(f"[WARN] JS inject failed: {e}")
        
        # ===== WINDOW POSITION =====
        SCREEN_WIDTH = 1920
        WINDOW_WIDTH = 400
        WINDOW_HEIGHT = 600
        COLUMNS = SCREEN_WIDTH // WINDOW_WIDTH

        row = index // COLUMNS
        col = index % COLUMNS

        x_pos = col * WINDOW_WIDTH
        y_pos = row * WINDOW_HEIGHT

        try:
            driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            time.sleep(0.5)
            driver.set_window_position(x_pos, y_pos)
            time.sleep(0.2)
            actual_pos = driver.get_window_position()
            print(f"[WINDOW] Thread-{index}: ({x_pos},{y_pos}) → {actual_pos}")
        except Exception as e:
            print(f"[WARN] Thread-{index} window position failed: {e}")

        print(f"[DRIVER] ✅ Thread-{index} ready")
        print(f"       └─ Firefox {fingerprint['firefox_version']}")
        print(f"       └─ Timezone: Asia/Ho_Chi_Minh (GMT+7)")
        print(f"       └─ Language: vi-VN")
        print(f"       └─ Proxy: Vietnam 4G")
        
        return driver

    # ===== HELPER METHODS - GIỮ NGUYÊN =====
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
        sleep(random.uniform(1, 2))  # 🔴 Random delay

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
        sleep(random.uniform(1, 2))  # 🔴 Random delay

    def wait_and_get_text(self, xpath, timeout=60, driver=None):
        driver = driver or self.driver
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text

    def get_code_inboxes(self, mail, index=0):
        """Lấy mã OTP từ inboxes.com"""
        url = f"https://inboxes.com/api/v2/inbox/{mail}"
        
        proxies = None
        if self.proxy_list:
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
            except:
                proxies = None

        try:
            response = requests.get(url, cookies=self.cookies, headers=self.headers, proxies=proxies, timeout=15)
            data = response.json()
        except Exception as e:
            print(f"[INBOX] ❌ Error: {e}")
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
            print(f"[INBOX] ✅ Code: {code}")
        return code

    def get_mail_inboxes(self, driver):
        """Lấy email từ inboxes.com"""
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get('https://inboxes.com/')
        sleep(3)

        self.wait_and_click('/html/body/div/main/div/div/div/div[1]/button', driver=driver)
        self.wait_and_click('/html/body/div/main/div/div/div/div[1]/div[2]/div/div/div/form/div/div[2]/button', driver=driver)

        mail = self.wait_and_get_text('/html/body/div/main/div/div/div/div[1]/h1/span[2]', driver=driver)
        print(f"[MAIL] ✉️ {mail}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return mail

    def register_account(self, account, index):
        """Đăng ký Instagram"""
        driver = None
        try:
            print(f"[Thread-{index}] 🔹 Start: {account['username']}")

            driver = self._init_driver(index)
            if not driver:
                print(f"[Thread-{index}] ❌ Driver init failed")
                return
                
            driver.get("https://www.instagram.com/accounts/emailsignup/")
            sleep(5)

            mail = self.get_mail_inboxes(driver)

            self.wait_and_send_keys('emailOrPhone', mail, locator_type="name", driver=driver)
            sleep(2)
            self.wait_and_send_keys('password', account['defaultPassword'], locator_type="name", driver=driver)
            sleep(2)
            
            try:
                self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/form/div[9]/div/button', driver=driver, timeout=10)
            except:
                try:
                    self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[2]/div/form/div[7]/div/div/div/button', driver=driver)
                    self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/form/div[9]/div/button', driver=driver)
                except:
                    pass

            sleep(2)
            # Birth date
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[1]/select', driver=driver)
            self.wait_and_click(f'/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[1]/select/option[{random.randint(1, 12)}]', driver=driver)
            
            sleep(2)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[2]/select', driver=driver)
            self.wait_and_click(f'/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[2]/select/option[{random.randint(1, 28)}]', driver=driver)
            
            sleep(2)
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[3]/select', driver=driver)
            self.wait_and_click(f'/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/div/div/span/span[3]/select/option[{random.randint(20, 25)}]', driver=driver)
            
            self.wait_and_click('/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[6]/button', driver=driver)
            sleep(5)

            # OTP confirmation
            code_confirmed = False
            attempt = 0
            max_attempts = 5
            
            while not code_confirmed and attempt < max_attempts:
                attempt += 1
                code = self.get_code_inboxes(mail, index)
                
                if code:
                    try:
                        print(f"[Thread-{index}] 📝 Enter code: {code}")
                        self.wait_and_send_keys('email_confirmation_code', code, locator_type="name", driver=driver, timeout=10)
                        sleep(2)
                        
                        self.wait_and_click(
                            '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div[2]/form/div/div[2]/div',
                            driver=driver,
                            timeout=30
                        )
                        
                        sleep(5)
                        current_url = driver.current_url
                        
                        if "confirmation" not in current_url.lower():
                            code_confirmed = True
                            print(f"[Thread-{index}] ✅ Confirmed!")
                        else:
                            print(f"[Thread-{index}] ⚠️ Still on confirmation page")
                            
                    except Exception as e:
                        print(f"[Thread-{index}] ❌ Code entry error: {e}")
                        sleep(3)
                else:
                    try:
                        self.wait_and_click(
                            '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div[1]/div[2]/span/div',
                            driver=driver,
                            timeout=5
                        )
                        sleep(5)
                    except:
                        sleep(3)

            if not code_confirmed:
                print(f"[Thread-{index}] ❌ Code confirmation failed after {max_attempts} attempts")
                return

            # Wait for main Instagram page
            graphql_req = None
            
            for retry in range(3):
                for i in range(120):
                    current_url = driver.current_url
                    
                    if current_url.startswith("https://www.instagram.com/?nux=1") or current_url == "https://www.instagram.com/":
                        print(f"[Thread-{index}] ✅ Reached main page")
                        self._wait_for_graphql(driver, timeout=20)
                        graphql_req = self._find_graphql_request(driver)
                        break
                    elif "challenge" in current_url or "suspended" in current_url:
                        driver.quit()
                        account_data = {
                            'username': mail.split('@')[0],
                            'email': mail,
                            'password': account['defaultPassword'],
                            'cookie': "died_account"
                        }
                        eel.addAccountToTable(account_data)
                        return

                    sleep(1)
                try:
                    self.wait_and_click(
                        '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div[2]/form/div/div[2]/div',
                        driver=driver,
                        timeout=10
                    )
                except:
                    driver.refresh()

            if graphql_req:
                cookie_header = graphql_req.headers.get("Cookie", "")
                source = driver.page_source
                try:
                    username = source.split('{"user":{"username":"')[1].split('"')[0]
                except:
                    username = mail.split('@')[0]
                    
                print(f"\n[Thread-{index}] ✅ SUCCESS: {username}|{mail}\n")
                
                account_data = {
                    'username': username,
                    'email': mail,
                    'password': account['defaultPassword'],
                    'cookie': cookie_header
                }
                eel.addAccountToTable(account_data)
            else:
                print(f"[Thread-{index}] ⚠️ No graphql request found")
                
                account_data = {
                    'username': mail.split('@')[0],
                    'email': mail,
                    'password': account['defaultPassword'],
                    'cookie': 'NO_COOKIE'
                }
                eel.addAccountToTable(account_data)
            
            sleep(3)
            print(f"[Thread-{index}] 🏁 Done!")
            
        except Exception as e:
            print(f"[Thread-{index}] ❌ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def _wait_for_graphql(self, driver, timeout=15):
        """Wait for graphql request"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for req in driver.requests:
                if "/api/graphql" in req.path and req.response:
                    return True
            time.sleep(0.5)
        return False

    def _find_graphql_request(self, driver):
        """Find last graphql request"""
        graphql_requests = [
            req for req in driver.requests if "/api/graphql" in req.path and req.response
        ]
        if graphql_requests:
            return graphql_requests[-1]
        return None

    def thread_reg(self):
        """Thread manager"""
        accounts = [
            {"id": i + 1, "username": f"test{i + 1}@example.com", "defaultPassword": self.data['defaultPassword']} 
            for i in range(self.account_count)
        ]

        threads = []
        completed = 0
        window_index = 0
        
        for i, acc in enumerate(accounts):
            while len([t for t in threads if t.is_alive()]) >= self.thread_count:
                sleep(0.5)
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

# https://www.instagram.com/accounts/emailsignup/