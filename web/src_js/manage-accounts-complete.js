class ManageAccountsComplete {
    constructor() {
        this.accounts = [];
        this.selectedRows = new Set();
        this.tbody = document.getElementById('manage-tbody');
        this.table = document.getElementById('manage-table');
        this.contextMenu = document.getElementById('context-menu-manage');
        this.currentCheckAction = null;
        
        // Modals
        this.modals = {
            append: document.getElementById('modal-append-account'),
            proxy: document.getElementById('modal-add-proxy'),
            checkSettings: document.getElementById('modal-check-settings'),
            nuoi: document.getElementById('modal-nuoi-account')
        };
        
        this.init();
        this.loadAccountsFromStorage();
        this.loadXPathSettings();
    }

    init() {
        this.initButtons();
        this.initTableEvents();
        this.initContextMenu();
        this.initModals();
        this.initXPathButtons();
    }

    // ============== XPATH SETTINGS ==============
    initXPathButtons() {
        // Load XPath button
        const loadXPathBtn = document.getElementById('load-xpath-btn');
        if (loadXPathBtn) {
            loadXPathBtn.addEventListener('click', () => {
                this.loadXPathFromPython();
            });
        }

        // Save XPath button
        const saveXPathBtn = document.getElementById('save-xpath-btn');
        if (saveXPathBtn) {
            saveXPathBtn.addEventListener('click', () => {
                this.saveXPathToPython();
            });
        }
    }

    async loadXPathFromPython() {
        try {
            if (typeof eel !== 'undefined') {
                const xpaths = await eel.get_xpath_settings()();
                if (xpaths) {
                    document.getElementById('xpath-username-input').value = xpaths.username || '';
                    document.getElementById('xpath-password-input').value = xpaths.password || '';
                    console.log('✓ Đã load XPath từ Python');
                }
            }
        } catch (e) {
            console.error('❌ Lỗi khi load XPath:', e);
            alert('Lỗi khi tải XPath: ' + e);
        }
    }

    async saveXPathToPython() {
        const xpaths = {
            username: document.getElementById('xpath-username-input').value.trim(),
            password: document.getElementById('xpath-password-input').value.trim()
        };

        if (!xpaths.username || !xpaths.password) {
            alert('Vui lòng nhập đầy đủ XPath!');
            return;
        }

        try {
            if (typeof eel !== 'undefined') {
                await eel.save_xpath_settings(xpaths)();
                alert('✓ Đã lưu XPath!');
                console.log('✓ Đã lưu XPath:', xpaths);
            }
        } catch (e) {
            console.error('❌ Lỗi khi lưu XPath:', e);
            alert('Lỗi khi lưu XPath: ' + e);
        }
    }

    async loadXPathSettings() {
        try {
            if (typeof eel !== 'undefined') {
                const xpaths = await eel.get_xpath_settings()();
                if (xpaths) {
                    const usernameInput = document.getElementById('xpath-username-input');
                    const passwordInput = document.getElementById('xpath-password-input');
                    
                    if (usernameInput) usernameInput.value = xpaths.username || '';
                    if (passwordInput) passwordInput.value = xpaths.password || '';
                }
            }
        } catch (e) {
            console.log('Chưa có XPath settings hoặc lỗi:', e);
        }
    }

    // ============== BUTTON EVENTS ==============
    initButtons() {
        // Import button
        document.getElementById('import-accounts-btn').addEventListener('click', () => {
            this.importFromFile();
        });

        // Delete selected button
        document.getElementById('delete-selected-btn').addEventListener('click', () => {
            this.deleteSelected();
        });

        // Export selected button
        document.getElementById('export-selected-btn').addEventListener('click', () => {
            this.exportSelected();
        });

        // Select all checkbox
        document.getElementById('select-all-checkbox').addEventListener('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });
    }

    toggleSelectAll(checked) {
        if (checked) {
            this.accounts.forEach((_, index) => {
                this.selectedRows.add(index);
            });
        } else {
            this.selectedRows.clear();
        }
        this.renderTable();
    }

    // ============== TABLE EVENTS ==============
    initTableEvents() {
        // Table click for checkbox selection
        this.tbody.addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') {
                const row = e.target.closest('tr');
                if (row && row.dataset.index) {
                    this.toggleCheckbox(parseInt(row.dataset.index), e.target.checked);
                }
            }
        });

        // Prevent default context menu
        this.table.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });
    }

    toggleCheckbox(index, checked) {
        if (checked) {
            this.selectedRows.add(index);
        } else {
            this.selectedRows.delete(index);
        }
        this.updateStats();
        this.updateSelectAllCheckbox();
    }

    updateSelectAllCheckbox() {
        const selectAllCheckbox = document.getElementById('select-all-checkbox');
        if (this.accounts.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (this.selectedRows.size === this.accounts.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (this.selectedRows.size > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    clearSelection() {
        this.selectedRows.clear();
        this.updateStats();
        this.updateSelectAllCheckbox();
    }

    // ============== CONTEXT MENU ==============
    initContextMenu() {
        // Show context menu on right click
        this.table.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu(e.pageX, e.pageY);
        });

        // Hide context menu on click outside
        document.addEventListener('click', (e) => {
            if (!this.contextMenu.contains(e.target)) {
                this.hideContextMenu();
            }
        });

        // Handle menu item clicks
        this.contextMenu.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                this.handleContextAction(action);
                this.hideContextMenu();
            });
        });
    }

    showContextMenu(x, y) {
        const menuWidth = 200;
        const menuHeight = 350;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        let posX = x;
        let posY = y;

        if (x + menuWidth > windowWidth) {
            posX = windowWidth - menuWidth - 10;
        }

        if (y + menuHeight > windowHeight) {
            posY = windowHeight - menuHeight - 10;
        }

        this.contextMenu.style.left = posX + 'px';
        this.contextMenu.style.top = posY + 'px';
        this.contextMenu.style.display = 'block';
    }

    hideContextMenu() {
        this.contextMenu.style.display = 'none';
    }

    handleContextAction(action) {
        switch(action) {
            case 'append':
                this.showAppendModal();
                break;
            case 'login':
                this.handleLogin();
                break;
            case 'add-proxy':
                this.handleAddProxy();
                break;
            case 'check-live':
                this.handleCheckLive();
                break;
            case 'check-block':
                this.handleCheckBlock();
                break;
            case 'nuoi':
                this.handleNuoi();
                break;
            case 'export':
                this.exportSelected();
                break;
            case 'delete':
                this.deleteSelected();
                break;
        }
    }

    handleLogin() {
        const selected = this.getSelectedAccounts();
        
        if (selected.length === 0) {
            alert('Vui lòng chọn tài khoản cần login!');
            return;
        }

        if (confirm(`Bắt đầu login ${selected.length} tài khoản để lấy lại cookie?`)) {
            this.showCheckSettingsModal('login');
        }
    }

    handleAddProxy() {
        const selected = this.getSelectedAccounts();
        
        if (selected.length === 0) {
            alert('Vui lòng chọn tài khoản cần thêm proxy!');
            return;
        }

        this.showAddProxyModal();
    }

    handleCheckLive() {
        const selected = this.getSelectedAccounts();
        
        if (selected.length === 0) {
            alert('Vui lòng chọn tài khoản cần check live!');
            return;
        }

        this.showCheckSettingsModal('check-live');
    }

    handleCheckBlock() {
        const selected = this.getSelectedAccounts();
        
        if (selected.length === 0) {
            alert('Vui lòng chọn tài khoản cần check block!');
            return;
        }

        this.showCheckSettingsModal('check-block');
    }

    handleNuoi() {
        const selected = this.getSelectedAccounts();
        
        if (selected.length === 0) {
            alert('Vui lòng chọn tài khoản cần nuôi!');
            return;
        }

        this.showNuoiModal();
    }

    // ============== MODALS ==============
    initModals() {
        // Close modal buttons - X button
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal');
                if (modal) {
                    this.hideModal(modal);
                }
            });
        });

        // Close modal buttons - Hủy button
        document.querySelectorAll('.modal-footer .btn-danger').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal');
                if (modal) {
                    this.hideModal(modal);
                }
            });
        });

        // Click outside modal to close
        Object.values(this.modals).forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal);
                }
            });
        });

        // Append account confirm
        document.getElementById('append-confirm-btn').addEventListener('click', () => {
            this.handleAppendConfirm();
        });

        // Add proxy confirm
        document.getElementById('proxy-confirm-btn').addEventListener('click', () => {
            this.handleProxyConfirm();
        });

        // Check settings confirm
        document.getElementById('check-confirm-btn').addEventListener('click', () => {
            this.handleCheckConfirm();
        });

        // Nuoi confirm
        document.getElementById('nuoi-confirm-btn').addEventListener('click', () => {
            this.handleNuoiConfirm();
        });

        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                Object.values(this.modals).forEach(modal => {
                    if (modal.classList.contains('active')) {
                        this.hideModal(modal);
                    }
                });
            }
        });
    }

    showModal(modal) {
        modal.classList.add('active');
    }

    hideModal(modal) {
        modal.classList.remove('active');
    }

    showAppendModal() {
        this.showModal(this.modals.append);
        document.getElementById('append-data-input').value = '';
        document.getElementById('append-data-input').focus();
    }

    showAddProxyModal() {
        this.showModal(this.modals.proxy);
        document.getElementById('proxy-data-input').value = '';
        document.getElementById('proxy-data-input').focus();
    }

    showCheckSettingsModal(action) {
        this.currentCheckAction = action;
        this.showModal(this.modals.checkSettings);
        
        const titles = {
            'login': 'Cài đặt Login',
            'check-live': 'Cài đặt Check Live',
            'check-block': 'Cài đặt Check Block'
        };
        
        const title = this.modals.checkSettings.querySelector('.modal-header h3');
        title.innerHTML = `<i class="fas fa-cog"></i> ${titles[action] || 'Cài đặt kiểm tra'}`;
    }

    showNuoiModal() {
        this.showModal(this.modals.nuoi);
    }

    handleAppendConfirm() {
        const data = document.getElementById('append-data-input').value.trim();
        
        if (!data) {
            alert('Vui lòng nhập dữ liệu!');
            return;
        }

        const lines = data.split('\n').filter(line => line.trim());
        let addedCount = 0;

        lines.forEach(line => {
            const parts = line.split('|').map(p => p.trim());
            if (parts.length >= 3) {
                // Hỗ trợ cả 2 định dạng: username|password|email|cookie hoặc username|password|email
                this.addAccount(
                    parts[0], 
                    parts[1], 
                    parts[2], 
                    parts[3] || '', 
                    parts[4] || '' // proxy nếu có
                );
                addedCount++;
            }
        });

        if (addedCount > 0) {
            alert(`Đã thêm ${addedCount} tài khoản!`);
            this.hideModal(this.modals.append);
        } else {
            alert('Không có dữ liệu hợp lệ để thêm!\nĐịnh dạng: username|password|email|cookie|proxy (proxy tùy chọn)');
        }
    }

    handleProxyConfirm() {
        const data = document.getElementById('proxy-data-input').value.trim();
        
        if (!data) {
            alert('Vui lòng nhập proxy!');
            return;
        }

        const proxies = data.split('\n')
            .map(line => line.trim())
            .filter(line => line);

        const success = this.addProxyToSelected(proxies);
        
        if (success) {
            alert('Đã thêm proxy cho các tài khoản đã chọn!');
            this.hideModal(this.modals.proxy);
        }
    }

    async handleCheckConfirm() {
        const threads = parseInt(document.getElementById('check-thread-input').value);
        const delay = parseInt(document.getElementById('check-delay-input').value);
        
        if (!threads || !delay || threads < 1 || delay < 1) {
            alert('Vui lòng nhập thông số hợp lệ!');
            return;
        }

        // Lấy XPath settings
        const xpaths = {
            username: document.getElementById('xpath-username-input').value.trim(),
            password: document.getElementById('xpath-password-input').value.trim()
        };

        if (!xpaths.username || !xpaths.password) {
            alert('Vui lòng nhập XPath Username và Password!');
            return;
        }

        const selected = this.getSelectedAccounts();
        
        this.hideModal(this.modals.checkSettings);
        
        switch(this.currentCheckAction) {
            case 'login':
                this.startLogin(selected, threads, delay, xpaths);
                break;
            case 'check-live':
                this.startCheckLive(selected, threads, delay, xpaths);
                break;
            case 'check-block':
                this.startCheckBlock(selected, threads, delay, xpaths);
                break;
        }
    }

    handleNuoiConfirm() {
        const threads = parseInt(document.getElementById('nuoi-thread-input').value);
        const delay = parseInt(document.getElementById('nuoi-delay-input').value);
        const followCount = parseInt(document.getElementById('nuoi-follow-input').value);
        const uploadAvatar = document.getElementById('nuoi-upload-avatar-checkbox').checked;
        const postStatus = document.getElementById('nuoi-post-status-checkbox').checked;
        
        if (!threads || !delay || threads < 1 || delay < 1) {
            alert('Vui lòng nhập thông số hợp lệ!');
            return;
        }

        const selected = this.getSelectedAccounts();
        
        const config = {
            threads,
            delay,
            followCount,
            uploadAvatar,
            postStatus,
            avatarFolder: document.getElementById('nuoi-avatar-folder-input').value,
            statusList: document.getElementById('nuoi-status-input').value.split('\n').filter(s => s.trim()),
            proxy: document.getElementById('nuoi-proxy-input').value.trim()
        };

        this.hideModal(this.modals.nuoi);
        this.startNuoi(selected, config);
    }

    // ============== CHECK PROCESSES ==============
    async startLogin(accounts, threads, delay, xpaths) {
        console.log(`🔄 Bắt đầu login ${accounts.length} tài khoản với ${threads} luồng, delay ${delay}s`);
        console.log('📍 XPath Settings:', xpaths);
        
        Array.from(this.selectedRows).forEach(index => {
            this.updateAccountStatus(index, 'checking');
        });

        if (typeof eel !== 'undefined') {
            try {
                const result = await eel.start_login(accounts, threads, delay, xpaths)();
                console.log('✓ Login hoàn tất:', result);
            } catch (e) {
                console.error('❌ Login thất bại:', e);
                alert('Lỗi khi gọi backend: ' + e);
            }
        } else {
            console.log('⚠️ Demo mode: Simulating login...');
            alert(`[DEMO] Đang login ${accounts.length} tài khoản...`);
            this.simulateProcess(accounts, 'login', delay);
        }
    }

    async startCheckLive(accounts, threads, delay, xpaths) {
        console.log(`🔄 Bắt đầu check live ${accounts.length} tài khoản với ${threads} luồng, delay ${delay}s`);
        console.log('📍 XPath Settings:', xpaths);
        
        Array.from(this.selectedRows).forEach(index => {
            this.updateAccountStatus(index, 'checking');
        });

        if (typeof eel !== 'undefined') {
            try {
                const result = await eel.start_check_live(accounts, threads, delay, xpaths)();
                console.log('✓ Check live hoàn tất:', result);
            } catch (e) {
                console.error('❌ Check live thất bại:', e);
                alert('Lỗi khi gọi backend: ' + e);
            }
        } else {
            console.log('⚠️ Demo mode: Simulating check live...');
            alert(`[DEMO] Đang check live ${accounts.length} tài khoản...`);
            this.simulateProcess(accounts, 'check-live', delay);
        }
    }

    async startCheckBlock(accounts, threads, delay, xpaths) {
        console.log(`🔄 Bắt đầu check block ${accounts.length} tài khoản với ${threads} luồng, delay ${delay}s`);
        console.log('📍 XPath Settings:', xpaths);
        
        Array.from(this.selectedRows).forEach(index => {
            this.updateAccountStatus(index, 'checking');
        });

        if (typeof eel !== 'undefined') {
            try {
                const result = await eel.start_check_block(accounts, threads, delay, xpaths)();
                console.log('✓ Check block hoàn tất:', result);
            } catch (e) {
                console.error('❌ Check block thất bại:', e);
                alert('Lỗi khi gọi backend: ' + e);
            }
        } else {
            console.log('⚠️ Demo mode: Simulating check block...');
            alert(`[DEMO] Đang check block ${accounts.length} tài khoản...`);
            this.simulateProcess(accounts, 'check-block', delay);
        }
    }

    async startNuoi(accounts, config) {
        console.log(`🔄 Bắt đầu nuôi ${accounts.length} tài khoản:`, config);
        
        Array.from(this.selectedRows).forEach(index => {
            this.updateAccountStatus(index, 'checking');
        });

        if (typeof eel !== 'undefined') {
            try {
                const result = await eel.start_nuoi(accounts, config)();
                console.log('✓ Nuôi tài khoản hoàn tất:', result);
            } catch (e) {
                console.error('❌ Nuôi tài khoản thất bại:', e);
                alert('Lỗi khi gọi backend: ' + e);
            }
        } else {
            console.log('⚠️ Demo mode: Simulating nuoi...');
            alert(`[DEMO] Đang nuôi ${accounts.length} tài khoản...`);
            this.simulateProcess(accounts, 'nuoi', config.delay);
        }
    }

    simulateProcess(accounts, type, delay) {
        const indices = Array.from(this.selectedRows);
        let processed = 0;

        const interval = setInterval(() => {
            if (processed >= indices.length) {
                clearInterval(interval);
                alert('Hoàn thành!');
                return;
            }

            const index = indices[processed];
            const status = Math.random() > 0.3 ? 'live' : 'die';
            
            if (status === 'live' && this.accounts[index]) {
                this.accounts[index].followers = Math.floor(Math.random() * 500);
                this.accounts[index].following = Math.floor(Math.random() * 300);
                this.accounts[index].hasAvatar = Math.random() > 0.5;
                this.accounts[index].posts = Math.floor(Math.random() * 20);
            }
            
            this.updateAccountStatus(index, status);
            processed++;
        }, delay * 1000);
    }

    // ============== ACCOUNT MANAGEMENT ==============
    importFromFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.txt';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                const content = event.target.result;
                this.parseAndAddAccounts(content);
            };
            reader.readAsText(file);
        };

        input.click();
    }

    parseAndAddAccounts(content) {
        const lines = content.split('\n').filter(line => line.trim());
        let addedCount = 0;
        
        lines.forEach(line => {
            const parts = line.split('|').map(p => p.trim());
            if (parts.length >= 3) {
                this.accounts.push({
                    username: parts[0],
                    password: parts[1],
                    email: parts[2],
                    cookie: parts[3] || '',
                    proxy: parts[4] || '',
                    status: 'pending',
                    followers: 0,
                    following: 0,
                    hasAvatar: false,
                    posts: 0
                });
                addedCount++;
            }
        });

        if (addedCount > 0) {
            alert(`Đã import ${addedCount} tài khoản!`);
            this.renderTable();
            this.saveAccountsToStorage();
        } else {
            alert('Không tìm thấy dữ liệu hợp lệ trong file!');
        }
    }

    addAccount(username, password, email, cookie = '', proxy = '') {
        this.accounts.push({
            username,
            password,
            email,
            cookie,
            proxy,
            status: 'pending',
            followers: 0,
            following: 0,
            hasAvatar: false,
            posts: 0
        });
        this.renderTable();
        this.saveAccountsToStorage();
    }

    deleteSelected() {
        if (this.selectedRows.size === 0) {
            alert('Vui lòng chọn tài khoản cần xóa!');
            return;
        }

        if (!confirm(`Bạn có chắc muốn xóa ${this.selectedRows.size} tài khoản?`)) {
            return;
        }

        const indices = Array.from(this.selectedRows).sort((a, b) => b - a);
        indices.forEach(index => {
            this.accounts.splice(index, 1);
        });

        this.clearSelection();
        this.renderTable();
        this.saveAccountsToStorage();
    }

    exportSelected() {
        let accountsToExport;
        
        if (this.selectedRows.size === 0) {
            if (!confirm('Không có tài khoản nào được chọn. Xuất tất cả?')) {
                return;
            }
            accountsToExport = this.accounts;
        } else {
            accountsToExport = Array.from(this.selectedRows).map(i => this.accounts[i]);
        }

        if (accountsToExport.length === 0) {
            alert('Không có tài khoản để xuất!');
            return;
        }

        const content = accountsToExport.map(acc => 
            `${acc.username}|${acc.password}|${acc.email}|${acc.cookie}|${acc.proxy}`
        ).join('\n');

        this.downloadFile('instagram_accounts.txt', content);
        alert(`Đã export ${accountsToExport.length} tài khoản!`);
    }

    downloadFile(filename, content) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    getSelectedAccounts() {
        return Array.from(this.selectedRows).map(i => this.accounts[i]);
    }

    updateAccountStatus(index, status) {
        if (this.accounts[index]) {
            this.accounts[index].status = status;
            this.renderTable();
            this.saveAccountsToStorage();
        }
    }

    addProxyToSelected(proxies) {
        const selected = Array.from(this.selectedRows);
        
        if (proxies.length < selected.length) {
            alert('Số lượng proxy không đủ cho số tài khoản đã chọn!');
            return false;
        }

        selected.forEach((index, i) => {
            this.accounts[index].proxy = proxies[i];
        });

        this.renderTable();
        this.saveAccountsToStorage();
        return true;
    }

    // ============== RENDER & UPDATE ==============
    renderTable() {
        if (this.accounts.length === 0) {
            this.tbody.innerHTML = `
                <tr>
                    <td colspan="12" style="text-align: center; padding: 30px; color: #888;">
                        <i class="fas fa-inbox"></i><br>
                        Click chuột phải để thêm tài khoản hoặc Import File
                    </td>
                </tr>
            `;
        } else {
            this.tbody.innerHTML = this.accounts.map((acc, index) => {
                const isSelected = this.selectedRows.has(index);
                const rowClass = acc.status === 'live' ? 'status-live-row' : 
                                acc.status === 'die' ? 'status-die-row' : 
                                'status-pending-row';
                
                return `
                <tr data-index="${index}" class="${rowClass}">
                    <td style="text-align: center;">
                        <input type="checkbox" ${isSelected ? 'checked' : ''}>
                    </td>
                    <td>${index + 1}</td>
                    <td>${this.escapeHtml(acc.username)}</td>
                    <td>${this.escapeHtml(acc.password)}</td>
                    <td>${this.escapeHtml(acc.email)}</td>
                    <td style="text-align: center;">${acc.followers || 0}</td>
                    <td style="text-align: center;">${acc.following || 0}</td>
                    <td style="text-align: center;">
                        ${acc.hasAvatar ? '<i class="fas fa-check-circle" style="color: #28a745;"></i>' : '<i class="fas fa-times-circle" style="color: #dc3545;"></i>'}
                    </td>
                    <td style="text-align: center;">${acc.posts || 0}</td>
                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${this.escapeHtml(acc.proxy)}">
                        ${this.escapeHtml(acc.proxy || '')}
                    </td>
                    <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${this.escapeHtml(acc.cookie)}">
                        ${this.escapeHtml(acc.cookie)}
                    </td>
                    <td>
                        <span class="status-badge status-${acc.status}">
                            ${this.getStatusText(acc.status)}
                        </span>
                    </td>
                </tr>
            `}).join('');
        }

        this.updateStats();
        this.updateSelectAllCheckbox();
    }

    getStatusText(status) {
        const statusMap = {
            'pending': 'Chưa check',
            'live': 'Live',
            'die': 'Die',
            'checking': 'Đang check...',
            'blocked': 'Blocked'
        };
        return statusMap[status] || status;
    }

    updateStats() {
        document.getElementById('manage-stats-total').textContent = this.accounts.length;
        document.getElementById('manage-stats-live').textContent = 
            this.accounts.filter(a => a.status === 'live').length;
        document.getElementById('manage-stats-die').textContent = 
            this.accounts.filter(a => a.status === 'die').length;
        document.getElementById('manage-stats-pending').textContent = 
            this.accounts.filter(a => a.status === 'pending').length;
        document.getElementById('manage-stats-selected').textContent = this.selectedRows.size;
        
        document.getElementById('total-accounts').textContent = this.accounts.length;
        document.getElementById('live-count').textContent = 
            this.accounts.filter(a => a.status === 'live').length;
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    // ============== STORAGE ==============
    async saveAccountsToStorage() {
        try {
            if (typeof eel !== 'undefined') {
                await eel.save_accounts(this.accounts)();
                console.log(`💾 Đã lưu ${this.accounts.length} tài khoản vào data/accounts.json`);
            } else {
                console.log('⚠️ Demo mode: Cannot save to file');
            }
        } catch (e) {
            console.error('❌ Lỗi khi lưu accounts:', e);
        }
    }

    async loadAccountsFromStorage() {
        try {
            if (typeof eel !== 'undefined') {
                const data = await eel.load_accounts()();
                if (data && data.length > 0) {
                    this.accounts = data;
                    this.renderTable();
                    console.log(`📂 Đã load ${data.length} tài khoản từ data/accounts.json`);
                }
            }
        } catch (e) {
            console.error('❌ Lỗi khi load accounts:', e);
        }
    }

    // ============== PUBLIC API ==============
    updateAccountFromBackend(username, status, cookie = null, info = null) {
        const index = this.accounts.findIndex(acc => acc.username === username);
        if (index !== -1) {
            this.accounts[index].status = status;
            if (cookie) {
                this.accounts[index].cookie = cookie;
            }
            if (info) {
                this.accounts[index].followers = info.followers || 0;
                this.accounts[index].following = info.following || 0;
                this.accounts[index].hasAvatar = info.hasAvatar || false;
                this.accounts[index].posts = info.posts || 0;
            }
            this.renderTable();
            this.saveAccountsToStorage();
        }
    }

    getAllAccounts() {
        return this.accounts;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.manageAccountsComplete = new ManageAccountsComplete();
    
    window.updateAccountStatus = (username, status, cookie, info) => {
        window.manageAccountsComplete.updateAccountFromBackend(username, status, cookie, info);
    };
});