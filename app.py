import eel
import json
import os
import sys
from pathlib import Path
import time
import threading
from tkinter import Tk, filedialog 
from web.src_py.reg_ig import FirefoxManager
from web.src_py.key import Check_key

# === FIX: Lấy đường dẫn thực khi chạy EXE ===
def get_base_path():
    """Trả về đường dẫn gốc (khác nhau giữa dev và EXE)"""
    if getattr(sys, 'frozen', False):
        # Đang chạy từ EXE (PyInstaller)
        return sys._MEIPASS
    else:
        # Đang chạy từ Python script
        return os.path.dirname(os.path.abspath(__file__))

# === FIX: Đảm bảo geckodriver được copy vào EXE ===
def get_geckodriver_path():
    """Tìm geckodriver trong EXE hoặc thư mục hiện tại"""
    base_path = get_base_path()
    
    # Các vị trí có thể có geckodriver
    possible_paths = [
        os.path.join(base_path, "geckodriver.exe"),
        os.path.join(os.getcwd(), "geckodriver.exe"),
        os.path.join(base_path, "drivers", "geckodriver.exe"),
        "geckodriver.exe"  # Trong PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Tìm thấy geckodriver tại: {path}")
            return path
    
    print("❌ KHÔNG TÌM THẤY GECKODRIVER!")
    return None

# Khởi tạo Eel
eel.init('web')

# Biến toàn cục
is_running = False
registration_thread = None

@eel.expose
def start_registration(config):
    global is_running, registration_thread
    
    if is_running:
        return {'success': False, 'message': 'Đã có tiến trình đang chạy!'}
    
    # === KIỂM TRA FIREFOX ===
    if not config.get('firefoxPath') or not os.path.exists(config['firefoxPath']):
        return {
            'success': False, 
            'message': '❌ Không tìm thấy Firefox! Vui lòng chọn đường dẫn Firefox.'
        }
    
    # === KIỂM TRA GECKODRIVER ===
    geckodriver = config.get('geckodriverPath') or get_geckodriver_path()
    
    if not geckodriver or not os.path.exists(geckodriver):
        return {
            'success': False,
            'message': '❌ Không tìm thấy geckodriver.exe! Vui lòng đặt file vào cùng thư mục với EXE.'
        }
    
    config['geckodriverPath'] = geckodriver
    
    is_running = True
    
    try:
        manager = FirefoxManager(config)
        registration_thread = threading.Thread(target=manager.thread_reg, daemon=True)
        registration_thread.start()
        return {'success': True}
    except Exception as e:
        is_running = False
        return {'success': False, 'message': f'Lỗi khởi tạo: {str(e)}'}


@eel.expose
def stop_registration():
    global is_running
    is_running = False
    print("\nĐã nhận lệnh dừng quá trình tạo tài khoản!")
    return {'success': True}


@eel.expose
def save_config(config):
    try:
        config_path = Path('data/config.json')
        config_path.parent.mkdir(exist_ok=True)  # Tạo thư mục data nếu chưa có
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"Đã lưu cấu hình vào {config_path}")
        return {'success': True}
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình: {e}")
        return {'success': False, 'message': str(e)}


@eel.expose
def test_firefox(firefox_path):
    """Test Firefox - Cải tiến"""
    try:
        if not firefox_path:
            return {'success': False, 'message': 'Chưa chọn đường dẫn Firefox!'}
        
        if not os.path.exists(firefox_path):
            return {
                'success': False,
                'message': f'File không tồn tại: {firefox_path}'
            }
        
        # Kiểm tra có phải file .exe không
        if not firefox_path.lower().endswith('.exe'):
            return {
                'success': False,
                'message': 'File phải có đuôi .exe'
            }
        
        # Test khởi động Firefox (chỉ test nhanh, không mở browser)
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        
        options = Options()
        options.binary_location = firefox_path
        options.add_argument('--headless')  # Chạy ẩn
        
        geckodriver = get_geckodriver_path()
        if not geckodriver:
            return {
                'success': False,
                'message': 'Không tìm thấy geckodriver.exe! Đặt file vào cùng thư mục với EXE.'
            }
        
        service = Service(geckodriver)
        
        # Test khởi tạo
        from seleniumwire import webdriver
        driver = webdriver.Firefox(service=service, options=options)
        driver.quit()
        
        print(f"✓ Test Firefox thành công: {firefox_path}")
        return {'success': True, 'message': 'Firefox hoạt động bình thường!'}
        
    except Exception as e:
        print(f"❌ Test Firefox thất bại: {e}")
        return {'success': False, 'message': f'Lỗi: {str(e)}'}


@eel.expose
def select_firefox_path():
    """Tìm Firefox - CẢI TIẾN ĐỂ HOẠT ĐỘNG TRONG EXE"""
    try:
        print("🔍 Đang tìm Firefox...")
        
        # 1. Các đường dẫn mặc định
        default_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                print(f"✓ Tìm thấy Firefox tại: {path}")
                return path
        
        # 2. Tìm trong Registry (Windows)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"
            )
            path = winreg.QueryValue(key, None)
            if os.path.exists(path):
                print(f"✓ Tìm thấy Firefox từ Registry: {path}")
                return path
        except:
            pass
        
        # 3. Cho người dùng chọn thủ công
        print("⚠️ Không tìm thấy Firefox tự động. Mở hộp thoại chọn file...")
        
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()  # ← QUAN TRỌNG: Force update để dialog xuất hiện
        
        file_path = filedialog.askopenfilename(
            title="Chọn file firefox.exe",
            filetypes=[
                ("Firefox", "firefox.exe"),
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ],
            initialdir="C:\\Program Files"
        )
        
        root.destroy()
        
        if file_path:
            print(f"✓ Đã chọn Firefox: {file_path}")
            return file_path
        else:
            print("⚠ Người dùng hủy chọn file")
            return ""
            
    except Exception as e:
        print(f"❌ Lỗi khi chọn Firefox: {e}")
        return ""


@eel.expose
def select_geckodriver_path():
    """Chọn geckodriver - Cải tiến"""
    try:
        # Thử tìm tự động trước
        auto_path = get_geckodriver_path()
        if auto_path:
            return auto_path
        
        # Mở hộp thoại
        print("Mở hộp thoại chọn geckodriver.exe...")
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()
        
        file_path = filedialog.askopenfilename(
            title="Chọn file geckodriver.exe",
            filetypes=[
                ("Geckodriver", "geckodriver.exe"),
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        root.destroy()
        
        if file_path:
            print(f"✓ Đã chọn geckodriver: {file_path}")
            return file_path
        else:
            print("⚠ Người dùng hủy chọn file")
            return ""
            
    except Exception as e:
        print(f"❌ Lỗi khi chọn geckodriver: {e}")
        return ""


@eel.expose
def import_proxy_file():
    """Import file proxy"""
    try:
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()
        
        file_path = filedialog.askopenfilename(
            title="Chọn file proxy",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        root.destroy()
        
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✓ Đã import proxy từ: {file_path}")
            return content
        else:
            print("⚠ Người dùng hủy chọn file")
            return ""
            
    except Exception as e:
        print(f"❌ Lỗi khi import proxy: {e}")
        return ""


@eel.expose
def export_accounts(accounts):
    """Export tài khoản"""
    try:
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Export TXT
        txt_file = output_dir / f'accounts_{timestamp}.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            for acc in accounts:
                line = f"{acc['username']}|{acc['password']}|{acc['email']}|{acc['cookie']}\n"
                f.write(line)
        
        # Export JSON
        json_file = output_dir / f'accounts_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=4, ensure_ascii=False)
        
        print(f"✓ Đã export {len(accounts)} tài khoản:")
        print(f"  - TXT: {txt_file}")
        print(f"  - JSON: {json_file}")
        
        return {'success': True}
    except Exception as e:
        print(f"Lỗi khi export: {e}")
        return {'success': False, 'message': str(e)}


@eel.expose
def main_check_key(key):
    try:
        with open(r'data/version_client.json', 'r', encoding="utf-8-sig") as f:
            version = json.load(f)
        
        statuscheckkey = Check_key().check_update(key, version['version_client'])
        
        if statuscheckkey['data']:
            with open('data/key.json', "w", encoding="utf-8") as f:
                json.dump({'key': key}, f, ensure_ascii=False, indent=4)
            eel.start('index.html', size=(1200, 800))
        
        return statuscheckkey
    except Exception as e:
        print(f"Lỗi check key: {e}")
        return {'data': False, 'message': str(e)}


# === CHẠY ỨNG DỤNG ===
if __name__ == '__main__':
    try:
        # Tạo thư mục data nếu chưa có
        Path('data').mkdir(exist_ok=True)
        
        # Kiểm tra key
        try:
            with open(r'data/key.json', "r", encoding="utf-8") as f:
                key_data = json.load(f)
            
            with open(r'data/version_client.json', 'r', encoding="utf-8-sig") as versiondata:
                version = json.load(versiondata)
            
            status_checkkey = Check_key().check_update(key_data['key'], version)
            
            if status_checkkey['data'] == True:
                eel.start('index.html', size=(1200, 800), port=6060)
            else:
                os.remove('data/key.json')
                eel.start('key.html', size=(400, 600), port=6060)
        
        except FileNotFoundError:
            print("⚠️ Chưa có file key.json, mở màn hình nhập key")
            eel.start('key.html', size=(400, 600), port=6060)
        
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            eel.start('key.html', size=(400, 600), port=6060)
    
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {e}")
        input("Nhấn Enter để thoát...")