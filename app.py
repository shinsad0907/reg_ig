import eel
import json
import os
from pathlib import Path
import time
import threading
from tkinter import Tk, filedialog 
from web.src_py.reg_ig import FirefoxManager
from web.src_py.key import Check_key

# Khởi tạo Eel
eel.init('web')

# Biến toàn cục
is_running = False
registration_thread = None

# Hàm nhận cấu hình từ JavaScript
@eel.expose
def start_registration(config):
    global is_running, registration_thread
    
    if is_running:
        return {'success': False, 'message': 'Đã có tiến trình đang chạy!'}
    
    is_running = True
    
    # ← Sửa thành như này
    try:
        manager = FirefoxManager(config)
        registration_thread = threading.Thread(target=manager.thread_reg)
        registration_thread.start()
        return {'success': True}
    except Exception as e:
        is_running = False
        return {'success': False, 'message': str(e)}


def registration_process(config):
    """
    Quá trình tạo tài khoản chạy trong thread riêng
    """
    global is_running
    
    try:
        account_count = config['accountCount']
        delay = config['delay']
        
        for i in range(account_count):
            if not is_running:
                print("Quá trình tạo tài khoản đã bị dừng!")
                break
            
            print(f"\n[{i+1}/{account_count}] Đang tạo tài khoản...")
            
            # Giả lập tạo tài khoản (thay bằng logic thật của bạn)
            time.sleep(delay)
            
            # Tạo dữ liệu tài khoản mẫu
            account_data = {
                'username': f'user_{int(time.time())}_{i}',
                'email': f'user_{int(time.time())}_{i}@temp-mail.com',
                'password': config['defaultPassword'],
                'cookie': f'sessionid=abc123xyz_{i}; csrftoken=def456uvw_{i}'
            }
            
            # Gửi dữ liệu về JavaScript để hiển thị
            eel.addAccountToTable(account_data)
            
            print(f"✓ Đã tạo tài khoản: {account_data['username']}")
        
        print("\n" + "=" * 50)
        print("HOÀN THÀNH TẠO TÀI KHOẢN!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Lỗi trong registration_process: {e}")
    finally:
        is_running = False


@eel.expose
def stop_registration():
    """
    Dừng quá trình tạo tài khoản
    """
    global is_running
    is_running = False
    print("\nĐã nhận lệnh dừng quá trình tạo tài khoản!")
    return {'success': True}


@eel.expose
def save_config(config):
    """
    Lưu cấu hình vào file JSON
    """
    try:
        config_path = Path('data/config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"Đã lưu cấu hình vào {config_path}")
        return {'success': True}
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình: {e}")
        return {'success': False, 'message': str(e)}


@eel.expose
def test_firefox(firefox_path):
    """
    Test xem Firefox có hoạt động không
    """
    try:
        if not os.path.exists(firefox_path):
            return {
                'success': False,
                'message': 'Đường dẫn Firefox không tồn tại!'
            }
        
        # Thêm logic test Firefox ở đây (mở Firefox, kiểm tra version, etc.)
        print(f"Testing Firefox tại: {firefox_path}")
        time.sleep(1)  # Giả lập quá trình test
        
        return {
            'success': True,
            'message': 'Firefox hoạt động bình thường!'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


@eel.expose
def select_firefox_path():
    """Tự dò đường dẫn Firefox"""
    try:
        default_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        for path in default_paths:
            if os.path.exists(path):
                return path
        return ""
    except Exception as e:
        print(f"Lỗi khi chọn Firefox path: {e}")
        return ""

@eel.expose
def select_geckodriver_path():
    """Cho phép người dùng tự chọn file geckodriver.exe"""
    try:
        root = Tk()
        root.withdraw()  # Ẩn cửa sổ chính của Tkinter
        file_path = filedialog.askopenfilename(
            title="Chọn file geckodriver.exe",
            filetypes=[("Geckodriver", "geckodriver.exe"), ("Tất cả", "*.*")]
        )
        root.destroy()
        return file_path or ""
    except Exception as e:
        print(f"Lỗi khi chọn geckodriver path: {e}")
        return ""

@eel.expose
def export_accounts(accounts):
    """
    Export tài khoản ra file
    """
    try:
        # Tạo thư mục output nếu chưa có
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Tạo tên file với timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Export ra file TXT (format: username|password|email|cookie)
        txt_file = output_dir / f'accounts_{timestamp}.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            for acc in accounts:
                line = f"{acc['username']}|{acc['password']}|{acc['email']}|{acc['cookie']}\n"
                f.write(line)
        
        # Export ra file JSON
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
    with open(r'data/version_client.json', 'r', encoding="utf-8-sig") as f:
        version = json.load(f)
    statuscheckkey = Check_key().check_update(key, version['version_client'])
    if statuscheckkey['data']:
        with open('data/key.json', "w", encoding="utf-8") as f:
            json.dump({'key':key}, f, ensure_ascii=False, indent=4)
        eel.start('index.html', size=(1200, 800))
    return statuscheckkey

# Chạy ứng dụng
if __name__ == '__main__':
    # if Check_key().checK_update():
    #     eel.start('index.html', size=(1200, 800), port=8080)
    # else:
    #     pass
    try:
        with open(r'data/key.json', "r", encoding="utf-8") as f:
            key_data = json.load(f)   # load xong là đóng file
        with open(r'data/version_client.json', 'r', encoding="utf-8-sig") as versiondata:
            version = json.load(versiondata)
        status_checkkey = Check_key().check_update(key_data['key'], version)
        if status_checkkey['data'] == True:
            eel.start('index.html', size=(1200, 800), port=6060)
        else:
            os.remove('data/key.json')
            eel.start('key.html', size=(400, 600), port=6060)

    except Exception as e:
        print(e)
        eel.start('key.html', size=(400, 600), port=6060)