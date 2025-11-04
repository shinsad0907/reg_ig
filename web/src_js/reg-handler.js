// File: src_js/reg-handler.js

// Hàm đếm số lượng proxy
function updateProxyCount() {
    const proxyInput = document.getElementById('proxy-list-input');
    if (!proxyInput) return;
    
    const proxyText = proxyInput.value.trim();
    const proxyList = proxyText ? proxyText.split('\n').filter(line => line.trim()) : [];
    
    const proxyCountEl = document.getElementById('proxy-count');
    if (proxyCountEl) {
        proxyCountEl.textContent = proxyList.length;
    }
}

// Hàm lấy dữ liệu cấu hình từ settings panel
function getRegConfig() {
    const proxyInput = document.getElementById('proxy-list-input');
    const proxyText = proxyInput ? proxyInput.value.trim() : '';
    const proxyList = proxyText ? proxyText.split('\n').filter(line => line.trim()) : [];
    
    const config = {
        accountCount: parseInt(document.getElementById('account-count-input')?.value || 10),
        threadCount: parseInt(document.getElementById('account-count-thread-input')?.value || 10),
        delay: parseInt(document.getElementById('delay-input')?.value || 5),
        defaultPassword: document.getElementById('password-input')?.value || 'Instagram@123',
        firefoxPath: document.getElementById('firefox-path-input')?.value || '',
        geckodriverPath: document.getElementById('geckodriver-path-input')?.value || '',
        regMode: document.getElementById('reg-mode-select')?.value || 'auto',
        proxyList: proxyList
    };
    
    return config;
}

// Hàm validate dữ liệu
function validateRegConfig(config) {
    if (config.accountCount < 1 || config.accountCount > 1000) {
        alert('Số lượng tài khoản phải từ 1 đến 1000!');
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
        // Làm sạch dữ liệu trước khi kiểm tra
        const cleanedProxies = config.proxyList
            .map(p => p.trim())
            .filter(p => p !== '');

        const invalidProxies = cleanedProxies.filter(proxy => {
            const parts = proxy.split(':');
            // Hợp lệ nếu:
            // 1. Dạng ip:port
            // 2. Dạng ip:port:user:pass
            // 3. Dạng key (chỉ gồm ký tự chữ + số, không có dấu ':')
            const isIpPort = parts.length === 2;
            const isIpPortUserPass = parts.length === 4;
            const isKey = /^[A-Za-z0-9]+$/.test(proxy); // dạng key

            return !(isIpPort || isIpPortUserPass || isKey);
        });

        if (invalidProxies.length > 0) {
            alert('Có proxy không đúng định dạng (ip:port, ip:port:user:pass, hoặc key):\n' + invalidProxies.join('\n'));
            return false;
        }
    }


    
    return true;
}

// Hàm cập nhật UI khi bắt đầu reg
function updateUIStartReg() {
    const startBtn = document.getElementById('start-reg-btn');
    const stopBtn = document.getElementById('stop-reg-btn');
    const runningCount = document.getElementById('reg-running-count');
    
    if (startBtn) startBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = false;
    if (runningCount) runningCount.textContent = '1';
}

// Hàm cập nhật UI khi dừng reg
function updateUIStopReg() {
    const startBtn = document.getElementById('start-reg-btn');
    const stopBtn = document.getElementById('stop-reg-btn');
    const runningCount = document.getElementById('reg-running-count');
    
    if (startBtn) startBtn.disabled = false;
    if (stopBtn) stopBtn.disabled = true;
    if (runningCount) runningCount.textContent = '0';
}

// Hàm thêm tài khoản vào bảng
function addAccountToTable(accountData) {
    const tbody = document.getElementById('reg-accounts-tbody');
    if (!tbody) {
        console.error('Không tìm thấy reg-accounts-tbody');
        return;
    }
    
    // Xóa dòng "Chưa có tài khoản" nếu đây là tài khoản đầu tiên
    const emptyRow = tbody.querySelector('td[colspan]');
    if (emptyRow) {
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
    if (!row) return;
    
    row.remove();
    
    // Cập nhật lại STT
    const tbody = document.getElementById('reg-accounts-tbody');
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    rows.forEach((row, index) => {
        const firstCell = row.cells[0];
        if (firstCell) {
            firstCell.textContent = index + 1;
        }
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
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    // Loại bỏ các row có colspan (empty message)
    const dataRows = Array.from(rows).filter(row => !row.querySelector('td[colspan]'));
    const createdCount = dataRows.length;
    
    const createdEl = document.getElementById('reg-created-count');
    const failedEl = document.getElementById('reg-failed-count');
    const rateEl = document.getElementById('reg-success-rate');
    
    if (createdEl) {
        createdEl.textContent = createdCount;
    }
    
    // Tính tỷ lệ thành công
    const failedCount = parseInt(failedEl?.textContent || 0);
    const totalAttempts = createdCount + failedCount;
    const successRate = totalAttempts > 0 ? Math.round((createdCount / totalAttempts) * 100) : 0;
    
    if (rateEl) {
        rateEl.textContent = successRate + '%';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Cập nhật số lượng proxy khi nhập
    const proxyInput = document.getElementById('proxy-list-input');
    if (proxyInput) {
        proxyInput.addEventListener('input', updateProxyCount);
        updateProxyCount(); // Init count
    }
    
    // Nút xóa proxy
    const clearProxyBtn = document.getElementById('clear-proxy-btn');
    if (clearProxyBtn) {
        clearProxyBtn.addEventListener('click', function() {
            const proxyInput = document.getElementById('proxy-list-input');
            if (proxyInput) {
                proxyInput.value = '';
                updateProxyCount();
            }
        });
    }
    
    // Nút import proxy từ file
    const importProxyBtn = document.getElementById('import-proxy-btn');
    if (importProxyBtn) {
        importProxyBtn.addEventListener('click', async function() {
            try {
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    return;
                }
                const content = await eel.import_proxy_file()();
                if (content) {
                    const proxyInput = document.getElementById('proxy-list-input');
                    if (proxyInput) {
                        proxyInput.value = content;
                        updateProxyCount();
                    }
                }
            } catch (error) {
                console.error('Lỗi khi import proxy:', error);
                alert('Không thể import file proxy!');
            }
        });
    }
    
    // Nút bắt đầu tạo
    const startRegBtn = document.getElementById('start-reg-btn');
    if (startRegBtn) {
        startRegBtn.addEventListener('click', async function() {
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
                
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    updateUIStopReg();
                    return;
                }
                
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
    }
    
    // Nút dừng
    const stopRegBtn = document.getElementById('stop-reg-btn');
    if (stopRegBtn) {
        stopRegBtn.addEventListener('click', async function() {
            try {
                if (typeof eel !== 'undefined') {
                    await eel.stop_registration()();
                }
                updateUIStopReg();
                console.log('Đã dừng quá trình tạo tài khoản');
            } catch (error) {
                console.error('Lỗi khi dừng:', error);
            }
        });
    }
    
    // Nút lưu cấu hình
    const saveConfigBtn = document.getElementById('save-config-btn');
    if (saveConfigBtn) {
        saveConfigBtn.addEventListener('click', async function() {
            const config = getRegConfig();
            
            try {
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    return;
                }
                await eel.save_config(config)();
                alert('Đã lưu cấu hình thành công!');
            } catch (error) {
                console.error('Lỗi khi lưu cấu hình:', error);
                alert('Không thể lưu cấu hình!');
            }
        });
    }
    
    // Nút test Firefox
    const testFirefoxBtn = document.getElementById('test-firefox-btn');
    if (testFirefoxBtn) {
        testFirefoxBtn.addEventListener('click', async function() {
            const firefoxInput = document.getElementById('firefox-path-input');
            const firefoxPath = firefoxInput?.value;
            
            if (!firefoxPath) {
                alert('Vui lòng chọn đường dẫn Firefox trước!');
                return;
            }
            
            try {
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    return;
                }
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
    }
    
    // Nút chọn Firefox
    const firefoxPathBtn = document.getElementById('firefox-path-btn');
    if (firefoxPathBtn) {
        firefoxPathBtn.addEventListener('click', async function() {
            try {
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    return;
                }
                const path = await eel.select_firefox_path()();
                const firefoxInput = document.getElementById('firefox-path-input');
                if (path && firefoxInput) {
                    firefoxInput.value = path;
                } else {
                    alert("⚠️ Không tìm thấy Firefox. Hãy cài đặt hoặc chọn thủ công.");
                }
            } catch (error) {
                console.error('Lỗi khi chọn đường dẫn Firefox:', error);
            }
        });
    }

    // Nút chọn Geckodriver
    const geckodriverPathBtn = document.getElementById('geckodriver-path-btn');
    if (geckodriverPathBtn) {
        geckodriverPathBtn.addEventListener('click', async function() {
            try {
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    return;
                }
                const path = await eel.select_geckodriver_path()();
                const geckodriverInput = document.getElementById('geckodriver-path-input');
                if (path && geckodriverInput) {
                    geckodriverInput.value = path;
                }
            } catch (error) {
                console.error('Lỗi khi chọn đường dẫn Geckodriver:', error);
            }
        });
    }
    
    // Nút export
    const exportRegBtn = document.getElementById('export-reg-btn');
    if (exportRegBtn) {
        exportRegBtn.addEventListener('click', async function() {
            const tbody = document.getElementById('reg-accounts-tbody');
            if (!tbody) {
                console.error('Không tìm thấy reg-accounts-tbody');
                return;
            }
            
            const rows = tbody.querySelectorAll('tr');
            const dataRows = Array.from(rows).filter(row => !row.querySelector('td[colspan]'));
            
            if (dataRows.length === 0) {
                alert('Không có tài khoản nào để export!');
                return;
            }
            
            const accounts = [];
            dataRows.forEach(row => {
                const cells = row.cells;
                if (!cells || cells.length < 5) return;
                
                const rawCookie = cells[4]?.textContent || '';
                const cleanCookie = rawCookie.replace(/[\r\n]+/g, '').trim();

                accounts.push({
                    username: cells[1]?.textContent || '',
                    email: cells[2]?.textContent || '',
                    password: cells[3]?.textContent || '',
                    cookie: cleanCookie
                });
            });
            
            try {
                if (typeof eel === 'undefined') {
                    alert('Backend chưa sẵn sàng!');
                    return;
                }
                await eel.export_accounts(accounts)();
                alert('Export thành công!');
            } catch (error) {
                console.error('Lỗi khi export:', error);
                alert('Không thể export tài khoản!');
            }
        });
    }
    
    // Nút xóa hết bảng reg
    const clearRegTableBtn = document.getElementById('clear-reg-table');
    if (clearRegTableBtn) {
        clearRegTableBtn.addEventListener('click', function() {
            if (confirm('Bạn có chắc muốn xóa hết tài khoản đã tạo?')) {
                const tbody = document.getElementById('reg-accounts-tbody');
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 30px; color: #888;">
                                <i class="fas fa-inbox"></i><br>
                                Chưa có tài khoản nào được tạo
                            </td>
                        </tr>
                    `;
                }
                const createdEl = document.getElementById('reg-created-count');
                const rateEl = document.getElementById('reg-success-rate');
                if (createdEl) createdEl.textContent = '0';
                if (rateEl) rateEl.textContent = '0%';
            }
        });
    }
});

// Expose hàm để Python có thể gọi từ Eel
if (typeof eel !== 'undefined') {
    eel.expose(addAccountToTable);
    eel.expose(updateRegStats);
}