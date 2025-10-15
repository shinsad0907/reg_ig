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
    """Tự động tìm hoặc cho phép chọn Firefox thủ công"""
    try:
        # 1. Thử tìm Firefox tự động
        default_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe")
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                print(f"✓ Tìm thấy Firefox tại: {path}")
                return path
        
        # 2. Nếu không tìm thấy, cho người dùng chọn thủ công
        print("Không tìm thấy Firefox tự động. Mở hộp thoại chọn file...")
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Đưa dialog lên trên cùng
        
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
    """Cho phép chọn file geckodriver.exe"""
    try:
        # Thử tìm trong thư mục hiện tại trước
        local_geckodriver = os.path.join(os.getcwd(), "geckodriver.exe")
        if os.path.exists(local_geckodriver):
            print(f"✓ Tìm thấy geckodriver tại: {local_geckodriver}")
            return local_geckodriver
        
        # Mở hộp thoại chọn file
        print("Mở hộp thoại chọn geckodriver.exe...")
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
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