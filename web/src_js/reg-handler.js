// File: src_js/reg-handler.js

// Hàm đếm số lượng proxy
function updateProxyCount() {
    const proxyText = document.getElementById('proxy-list-input').value.trim();
    const proxyList = proxyText ? proxyText.split('\n').filter(line => line.trim()) : [];
    document.getElementById('proxy-count').textContent = proxyList.length;
}

// Hàm lấy dữ liệu cấu hình từ settings panel
function getRegConfig() {
    const proxyText = document.getElementById('proxy-list-input').value.trim();
    const proxyList = proxyText ? proxyText.split('\n').filter(line => line.trim()) : [];
    
    const config = {
        accountCount: parseInt(document.getElementById('account-count-input').value) || 10,
        threadCount: parseInt(document.getElementById('account-count-thread-input').value) || 10,
        delay: parseInt(document.getElementById('delay-input').value) || 5,
        defaultPassword: document.getElementById('password-input').value || 'Instagram@123',
        firefoxPath: document.getElementById('firefox-path-input').value || '',
        geckodriverPath: document.getElementById('geckodriver-path-input').value || '',
        regMode: document.getElementById('reg-mode-select').value || 'auto',
        proxyList: proxyList
    };
    
    return config;
}

// Hàm validate dữ liệu
function validateRegConfig(config) {
    if (config.accountCount < 1 || config.accountCount > 100) {
        alert('Số lượng tài khoản phải từ 1 đến 100!');
        return false;
    }
    
    if (config.threadCount < 1 || config.threadCount > 100) {
        alert('Số lượng luồng phải từ 1 đến 100!');
        return false;
    }
    
    if (config.delay < 1 || config.delay > 60) {
        alert('Delay phải từ 1 đến 60 giây!');
        return false;
    }
    
    if (!config.defaultPassword) {
        alert('Vui lòng nhập mật khẩu mặc định!');
        return false;
    }
    
    if (!config.firefoxPath) {
        alert('Vui lòng chọn đường dẫn Firefox!');
        return false;
    }
    
    // Validate proxy format (optional)
    if (config.proxyList.length > 0) {
        const invalidProxies = config.proxyList.filter(proxy => {
            const parts = proxy.split(':');
            return parts.length !== 4; // host:port:user:pass
        });
        
        if (invalidProxies.length > 0) {
            alert('Có proxy không đúng định dạng (host:port:user:pass):\n' + invalidProxies.join('\n'));
            return false;
        }
    }
    
    return true;
}

// Hàm cập nhật UI khi bắt đầu reg
function updateUIStartReg() {
    document.getElementById('start-reg-btn').disabled = true;
    document.getElementById('stop-reg-btn').disabled = false;
    document.getElementById('reg-running-count').textContent = '1';
}

// Hàm cập nhật UI khi dừng reg
function updateUIStopReg() {
    document.getElementById('start-reg-btn').disabled = false;
    document.getElementById('stop-reg-btn').disabled = true;
    document.getElementById('reg-running-count').textContent = '0';
}

// Hàm thêm tài khoản vào bảng
function addAccountToTable(accountData) {
    const tbody = document.getElementById('reg-accounts-tbody');
    
    // Xóa dòng "Chưa có tài khoản" nếu đây là tài khoản đầu tiên
    if (tbody.querySelector('td[colspan="6"]')) {
        tbody.innerHTML = '';
    }
    
    const rowCount = tbody.rows.length + 1;
    const row = tbody.insertRow();
    
    row.innerHTML = `
        <td>${rowCount}</td>
        <td>${accountData.username || ''}</td>
        <td>${accountData.email || ''}</td>
        <td>${accountData.password || ''}</td>
        <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${accountData.cookie || ''}">
            ${accountData.cookie || ''}
        </td>
        <td>
            <button class="btn btn-danger" style="padding: 4px 8px; font-size: 10px;" onclick="deleteRegAccount(this)">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    // Cập nhật thống kê
    updateRegStats();
}

// Hàm xóa tài khoản trong bảng
function deleteRegAccount(button) {
    const row = button.closest('tr');
    row.remove();
    
    // Cập nhật lại STT
    const tbody = document.getElementById('reg-accounts-tbody');
    const rows = tbody.querySelectorAll('tr');
    rows.forEach((row, index) => {
        row.cells[0].textContent = index + 1;
    });
    
    // Nếu không còn tài khoản nào, hiển thị thông báo
    if (rows.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 30px; color: #888;">
                    <i class="fas fa-inbox"></i><br>
                    Chưa có tài khoản nào được tạo
                </td>
            </tr>
        `;
    }
    
    updateRegStats();
}

// Hàm cập nhật thống kê
function updateRegStats() {
    const tbody = document.getElementById('reg-accounts-tbody');
    const rows = tbody.querySelectorAll('tr:not([colspan])');
    const createdCount = rows.length;
    
    document.getElementById('reg-created-count').textContent = createdCount;
    
    // Tính tỷ lệ thành công
    const totalAttempts = createdCount + parseInt(document.getElementById('reg-failed-count').textContent || 0);
    const successRate = totalAttempts > 0 ? Math.round((createdCount / totalAttempts) * 100) : 0;
    document.getElementById('reg-success-rate').textContent = successRate + '%';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Cập nhật số lượng proxy khi nhập
    const proxyInput = document.getElementById('proxy-list-input');
    proxyInput.addEventListener('input', updateProxyCount);
    
    // Nút xóa proxy
    document.getElementById('clear-proxy-btn').addEventListener('click', function() {
        document.getElementById('proxy-list-input').value = '';
        updateProxyCount();
    });
    
    // Nút import proxy từ file
    document.getElementById('import-proxy-btn').addEventListener('click', async function() {
        try {
            const content = await eel.import_proxy_file()();
            if (content) {
                document.getElementById('proxy-list-input').value = content;
                updateProxyCount();
            }
        } catch (error) {
            console.error('Lỗi khi import proxy:', error);
            alert('Không thể import file proxy!');
        }
    });
    
    // Nút bắt đầu tạo
    document.getElementById('start-reg-btn').addEventListener('click', async function() {
        const config = getRegConfig();
        
        if (!validateRegConfig(config)) {
            return;
        }
        
        // Hiển thị thông tin proxy
        if (config.proxyList.length > 0) {
            console.log(`Sử dụng ${config.proxyList.length} proxy`);
        } else {
            console.log('Không sử dụng proxy');
        }
        
        try {
            updateUIStartReg();
            
            // Gọi hàm Python qua Eel
            const result = await eel.start_registration(config)();
            
            if (result.success) {
                console.log('Bắt đầu tạo tài khoản thành công!');
            } else {
                alert('Lỗi: ' + result.message);
                updateUIStopReg();
            }
        } catch (error) {
            console.error('Lỗi khi gọi Python:', error);
            alert('Không thể kết nối với Python backend!');
            updateUIStopReg();
        }
    });
    
    // Nút dừng
    document.getElementById('stop-reg-btn').addEventListener('click', async function() {
        try {
            await eel.stop_registration()();
            updateUIStopReg();
            console.log('Đã dừng quá trình tạo tài khoản');
        } catch (error) {
            console.error('Lỗi khi dừng:', error);
        }
    });
    
    // Nút lưu cấu hình
    document.getElementById('save-config-btn').addEventListener('click', async function() {
        const config = getRegConfig();
        
        try {
            await eel.save_config(config)();
            alert('Đã lưu cấu hình thành công!');
        } catch (error) {
            console.error('Lỗi khi lưu cấu hình:', error);
            alert('Không thể lưu cấu hình!');
        }
    });
    
    // Nút test Firefox
    document.getElementById('test-firefox-btn').addEventListener('click', async function() {
        const firefoxPath = document.getElementById('firefox-path-input').value;
        
        if (!firefoxPath) {
            alert('Vui lòng chọn đường dẫn Firefox trước!');
            return;
        }
        
        try {
            const result = await eel.test_firefox(firefoxPath)();
            
            if (result.success) {
                alert('Test Firefox thành công! ✓');
            } else {
                alert('Test Firefox thất bại: ' + result.message);
            }
        } catch (error) {
            console.error('Lỗi khi test Firefox:', error);
            alert('Không thể test Firefox!');
        }
    });
    
    // Nút chọn Firefox
    document.getElementById('firefox-path-btn').addEventListener('click', async function() {
        try {
            const path = await eel.select_firefox_path()();
            if (path) {
                document.getElementById('firefox-path-input').value = path;
            } else {
                alert("⚠️ Không tìm thấy Firefox. Hãy cài đặt hoặc chọn thủ công.");
            }
        } catch (error) {
            console.error('Lỗi khi chọn đường dẫn Firefox:', error);
        }
    });

    // Nút chọn Geckodriver
    document.getElementById('geckodriver-path-btn').addEventListener('click', async function() {
        try {
            const path = await eel.select_geckodriver_path()();
            if (path) {
                document.getElementById('geckodriver-path-input').value = path;
            }
        } catch (error) {
            console.error('Lỗi khi chọn đường dẫn Geckodriver:', error);
        }
    });
    
    // Nút export
    document.getElementById('export-reg-btn').addEventListener('click', async function() {
        const tbody = document.getElementById('reg-accounts-tbody');
        const rows = tbody.querySelectorAll('tr:not([colspan])');
        
        if (rows.length === 0) {
            alert('Không có tài khoản nào để export!');
            return;
        }
        
        const accounts = [];
        rows.forEach(row => {
            const rawCookie = row.cells[4].textContent || '';
            const cleanCookie = rawCookie.replace(/[\r\n]+/g, '').trim();

            accounts.push({
                username: row.cells[1].textContent,
                email: row.cells[2].textContent,
                password: row.cells[3].textContent,
                cookie: cleanCookie
            });
        });
        
        try {
            await eel.export_accounts(accounts)();
            alert('Export thành công!');
        } catch (error) {
            console.error('Lỗi khi export:', error);
            alert('Không thể export tài khoản!');
        }
    });
    
    // Nút xóa hết bảng reg
    document.getElementById('clear-reg-table').addEventListener('click', function() {
        if (confirm('Bạn có chắc muốn xóa hết tài khoản đã tạo?')) {
            const tbody = document.getElementById('reg-accounts-tbody');
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 30px; color: #888;">
                        <i class="fas fa-inbox"></i><br>
                        Chưa có tài khoản nào được tạo
                    </td>
                </tr>
            `;
            document.getElementById('reg-created-count').textContent = '0';
            document.getElementById('reg-success-rate').textContent = '0%';
        }
    });
});

// Expose hàm để Python có thể gọi từ Eel
eel.expose(addAccountToTable);
eel.expose(updateRegStats);