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
        this.initEelCallbacks(); // ✅ THÊM: Khởi tạo callback từ Python
        this.injectStyles(); // ✅ THÊM: Inject CSS cho toast notifications
    }

    init() {
        this.initButtons();
        this.initTableEvents();
        this.initContextMenu();
        this.initModals();
        this.initXPathButtons();
    }

    // ============== ✅ THÊM: EEL CALLBACKS ==============
    initEelCallbacks() {
        if (typeof eel !== 'undefined') {
            // Callback cho login/check live
            eel.expose(this.updateAccountFromBackend.bind(this), 'updateAccountStatus');
            
            // ✅ Callback riêng cho nuôi
            eel.expose(this.updateNurtureProgress.bind(this), 'updateNurtureProgress');
            
            console.log('✓ Đã đăng ký callbacks với Python');
        } else {
            console.warn('⚠️ Eel chưa được khởi tạo. Chạy trong demo mode.');
        }
    }
    showCustomNotification(message, type) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: ${this.getStatusColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
            min-width: 300px;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        `;
        toast.innerHTML = `
            <i class="fas ${this.getStatusIcon(type)}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        // Tự động xóa sau 4s
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
    updateNurtureProgress(username, action, status, data = null) {
        console.log(`📥 Nuôi update: ${username} - ${action} - ${status}`);
        
        const index = this.accounts.findIndex(acc => acc.username === username);
        
        if (index === -1) {
            console.warn(`⚠️ Không tìm thấy tài khoản: ${username}`);
            return;
        }

        const account = this.accounts[index];

        // Xử lý theo action
        switch(action) {
            case 'start':
                account.status = 'checking';
                this.showNotification(username, 'checking');
                break;
                
            case 'avatar':
                if (status === 'success') {
                    account.hasAvatar = true;
                    this.showCustomNotification(`✅ ${username} - Upload avatar thành công!`, 'live');
                } else {
                    this.showCustomNotification(`❌ ${username} - Upload avatar thất bại!`, 'die');
                }
                break;
                
            case 'post':
                if (status === 'success' && data) {
                    account.posts = (account.posts || 0) + 1;
                    this.showCustomNotification(`📝 ${username} - Đã đăng status: "${data.preview}"`, 'live');
                } else {
                    this.showCustomNotification(`❌ ${username} - Đăng status thất bại!`, 'die');
                }
                break;
            
            // ← THÊM CASE BIO
            case 'bio':
                if (status === 'success' && data) {
                    account.bio = data.bio || ''; // Lưu bio vào account
                    const preview = data.bio.length > 30 ? data.bio.substring(0, 30) + '...' : data.bio;
                    this.showCustomNotification(`📋 ${username} - Đã cập nhật bio: "${preview}"`, 'live');
                } else {
                    this.showCustomNotification(`❌ ${username} - Cập nhật bio thất bại!`, 'die');
                }
                break;
                
            case 'follow':
                if (status === 'success' && data) {
                    account.following = (account.following || 0) + data.followCount;
                    this.showCustomNotification(`👥 ${username} - Đã follow ${data.followCount} người`, 'live');
                }
                break;
                
            case 'complete':
                account.status = status === 'success' ? 'live' : 'die';
                
                // Cập nhật thông tin chi tiết nếu có
                if (data) {
                    if (data.hasAvatar !== undefined) account.hasAvatar = data.hasAvatar;
                    if (data.posts !== undefined) account.posts = data.posts;
                    if (data.following !== undefined) account.following = data.following;
                    if (data.bio !== undefined) account.bio = data.bio; // ← THÊM BIO
                }
                
                this.showNotification(username, account.status);
                break;
                
            default:
                console.warn(`⚠️ Unknown action: ${action}`);
        }

        // Render lại table
        this.renderTable();

        // Lưu vào storage
        this.saveAccountsToStorage();

        // Scroll đến row được update
        this.scrollToAccount(index);
    }

    // ============== ✅ THÊM: INJECT STYLES ==============
    injectStyles() {
        if (document.getElementById('toast-animations')) return; // Tránh inject nhiều lần

        const style = document.createElement('style');
        style.id = 'toast-animations';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            @keyframes highlight {
                0%, 100% {
                    background-color: transparent;
                }
                50% {
                    background-color: rgba(33, 150, 243, 0.2);
                }
            }

            .highlight-update {
                animation: highlight 2s ease-in-out;
            }

            .toast {
                cursor: pointer;
                transition: transform 0.2s;
            }

            .toast:hover {
                transform: scale(1.05);
            }

            #toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 350px;
            }
        `;
        document.head.appendChild(style);
    }

    // ============== XPATH SETTINGS ==============
    initXPathButtons() {
        const loadXPathBtn = document.getElementById('load-xpath-btn');
        if (loadXPathBtn) {
            loadXPathBtn.addEventListener('click', () => {
                this.loadXPathFromPython();
            });
        }

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
        document.getElementById('import-accounts-btn').addEventListener('click', () => {
            this.importFromFile();
        });

        document.getElementById('delete-selected-btn').addEventListener('click', () => {
            this.deleteSelected();
        });

        document.getElementById('export-selected-btn').addEventListener('click', () => {
            this.exportSelected();
        });

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
        this.tbody.addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') {
                const row = e.target.closest('tr');
                if (row && row.dataset.index) {
                    this.toggleCheckbox(parseInt(row.dataset.index), e.target.checked);
                }
            }
        });

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
        this.table.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu(e.pageX, e.pageY);
        });

        document.addEventListener('click', (e) => {
            if (!this.contextMenu.contains(e.target)) {
                this.hideContextMenu();
            }
        });

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
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal');
                if (modal) {
                    this.hideModal(modal);
                }
            });
        });

        document.querySelectorAll('.modal-footer .btn-danger').forEach(btn => {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal');
                if (modal) {
                    this.hideModal(modal);
                }
            });
        });

        Object.values(this.modals).forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal);
                }
            });
        });

        document.getElementById('append-confirm-btn').addEventListener('click', () => {
            this.handleAppendConfirm();
        });

        document.getElementById('proxy-confirm-btn').addEventListener('click', () => {
            this.handleProxyConfirm();
        });

        document.getElementById('check-confirm-btn').addEventListener('click', () => {
            this.handleCheckConfirm();
        });

        document.getElementById('nuoi-confirm-btn').addEventListener('click', () => {
            this.handleNuoiConfirm();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                Object.values(this.modals).forEach(modal => {
                    if (modal.classList.contains('active')) {
                        this.hideModal(modal);
                    }
                });
            }
        });
        document.getElementById('nuoi-avatar-folder-btn').addEventListener('click', () => {
            this.selectAvatarFolder();
        });

        // ✅ Chọn folder Status text
        document.getElementById('nuoi-status-file-btn').addEventListener('click', () => {
            this.selectStatusFile();
        });

        // ✅ Chọn folder ảnh Status
        document.getElementById('nuoi-status-image-folder-btn').addEventListener('click', () => {
            this.selectStatusImageFolder();
        });

        // ✅ Import Bio từ file
        document.getElementById('nuoi-bio-file-btn').addEventListener('click', () => {
            this.importBioFile();
        });

    }
    // ============== ✅ THÊM: CHỌN AVATAR FOLDER ==============
    async selectAvatarFolder() {
        try {
            if (typeof eel !== 'undefined') {
                // Gọi Python để chọn folder
                const folderPath = await eel.select_folder_dialog('Chọn thư mục chứa Avatar')();
                
                if (folderPath) {
                    document.getElementById('nuoi-avatar-folder-input').value = folderPath;
                    console.log('✓ Đã chọn folder Avatar:', folderPath);
                }
            } else {
                alert('[DEMO MODE] Chức năng này cần Python backend');
            }
        } catch (e) {
            console.error('❌ Lỗi khi chọn folder:', e);
            alert('Lỗi: ' + e);
        }
    }
    
    // ============== ✅ THÊM: CHỌN FOLDER STATUS TEXT ==============
    async selectStatusFile() {
        try {
            if (typeof eel !== 'undefined') {
                const result = await eel.select_status_file_dialog()();
                
                if (result && result.file_path) {
                    document.getElementById('nuoi-status-file-input').value = result.file_path;
                    
                    if (result.line_count) {
                        document.getElementById('status-count').textContent = result.line_count;
                        alert(`✓ Đã load ${result.line_count} dòng status từ file!`);
                        console.log('✓ Đã chọn file Status:', result.file_path);
                    }
                }
            } else {
                alert('[DEMO MODE] Chức năng này cần Python backend');
            }
        } catch (e) {
            console.error('❌ Lỗi khi chọn file:', e);
            alert('Lỗi: ' + e);
        }
    }

    // ============== ✅ THÊM: CHỌN FOLDER ẢNH STATUS ==============
    async selectStatusImageFolder() {
        try {
            if (typeof eel !== 'undefined') {
                const result = await eel.select_image_folder_dialog('Chọn thư mục ảnh Status')();
                
                if (result && result.folder) {
                    document.getElementById('nuoi-status-image-folder-input').value = result.folder;
                    
                    if (result.image_count) {
                        document.getElementById('status-image-count').textContent = result.image_count;
                        alert(`✓ Đã tìm thấy ${result.image_count} ảnh trong folder!`);
                        console.log('✓ Đã chọn folder ảnh Status:', result.folder);
                    }
                }
            } else {
                alert('[DEMO MODE] Chức năng này cần Python backend');
            }
        } catch (e) {
            console.error('❌ Lỗi khi chọn folder:', e);
            alert('Lỗi: ' + e);
        }
    }

    // ============== ✅ THÊM: IMPORT BIO FILE ==============
    async importBioFile() {
        try {
            if (typeof eel !== 'undefined') {
                const result = await eel.select_bio_file_dialog()();
                
                if (result && result.file_path) {
                    document.getElementById('nuoi-bio-file-input').value = result.file_path;
                    
                    if (result.bio_count) {
                        document.getElementById('bio-count').textContent = result.bio_count;
                        alert(`✓ Đã load ${result.bio_count} bio từ file!`);
                        console.log('✓ Đã chọn file Bio:', result.file_path);
                    }
                }
            } else {
                alert('[DEMO MODE] Chức năng này cần Python backend');
            }
        } catch (e) {
            console.error('❌ Lỗi khi chọn file:', e);
            alert('Lỗi: ' + e);
        }
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
                this.addAccount(
                    parts[0], 
                    parts[1], 
                    parts[2], 
                    parts[3] || '', 
                    parts[4] || ''
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

        const xpaths = {
            firefox: document.getElementById('xpath-username-input').value.trim(),
            geckodriver: document.getElementById('xpath-password-input').value.trim()
        };

        if (!xpaths.firefox || !xpaths.geckodriver) {
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
        const updateBio = document.getElementById('nuoi-update-bio-checkbox').checked;
        
        const xpaths = {
            firefox: document.getElementById('xpath-username-input').value.trim(),
            geckodriver: document.getElementById('xpath-password-input').value.trim()
        };
        
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
            updateBio,
            avatarFolder: document.getElementById('nuoi-avatar-folder-input').value,
            statusFile: document.getElementById('nuoi-status-file-input').value,  // ← ĐÃ SỬA
            statusImageFolder: document.getElementById('nuoi-status-image-folder-input').value,
            bioFilePath: document.getElementById('nuoi-bio-file-input').value,
            xpaths: xpaths
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

    // 3. SỬA HÀM addAccount - Thêm trường bio
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
            posts: 0,
            bio: '' // ← THÊM TRƯỜNG BIO
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
    // 2. SỬA HÀM renderTable - Thêm cột Bio
    renderTable() {
        if (this.accounts.length === 0) {
            this.tbody.innerHTML = `
                <tr>
                    <td colspan="13" style="text-align: center; padding: 30px; color: #888;">
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
                
                // Cắt bio nếu quá dài
                const bioPreview = acc.bio ? 
                    (acc.bio.length > 30 ? acc.bio.substring(0, 30) + '...' : acc.bio) : 
                    '';
                
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
                    <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${this.escapeHtml(acc.bio || '')}">
                        ${this.escapeHtml(bioPreview)}
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

    // ============== ✅ THÊM: TOAST NOTIFICATIONS ==============
    showNotification(username, status) {
        const statusMessages = {
            'checking': `🔄 Đang kiểm tra ${username}...`,
            'live': `✅ ${username} - LIVE!`,
            'die': `❌ ${username} - DIE`,
            'blocked': `🚫 ${username} - BLOCKED`
        };

        const message = statusMessages[status] || `📥 ${username} - ${status}`;
        this.createToast(message, status);
    }

    createToast(message, status) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${status}`;
        toast.style.cssText = `
            background: ${this.getStatusColor(status)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-out;
            min-width: 300px;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        `;
        toast.innerHTML = `
            <i class="fas ${this.getStatusIcon(status)}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    getStatusColor(status) {
        const colors = {
            'checking': '#2196F3',
            'live': '#28a745',
            'die': '#dc3545',
            'blocked': '#ffc107'
        };
        return colors[status] || '#6c757d';
    }

    getStatusIcon(status) {
        const icons = {
            'checking': 'fa-spinner fa-spin',
            'live': 'fa-check-circle',
            'die': 'fa-times-circle',
            'blocked': 'fa-ban'
        };
        return icons[status] || 'fa-info-circle';
    }

    // ============== ✅ THÊM: SCROLL TO UPDATED ROW ==============
    scrollToAccount(index) {
        const row = this.tbody.querySelector(`tr[data-index="${index}"]`);
        if (row) {
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            row.classList.add('highlight-update');
            setTimeout(() => {
                row.classList.remove('highlight-update');
            }, 2000);
        }
    }

    // ============== ✅ CẢI TIẾN: PUBLIC API - UPDATE FROM BACKEND ==============
    updateAccountFromBackend(username, status, cookie = null, info = null) {
        console.log(`📥 Update từ Python: ${username} - ${status}`);
        
        const index = this.accounts.findIndex(acc => acc.username === username);
        
        if (index === -1) {
            console.warn(`⚠️ Không tìm thấy tài khoản: ${username}`);
            return;
        }

        const account = this.accounts[index];

        // Cập nhật status
        account.status = status;

        // Cập nhật cookie nếu có
        if (cookie) {
            account.cookie = cookie;
            console.log(`🍪 Đã cập nhật cookie cho ${username}`);
        }

        // Cập nhật thông tin bổ sung
        if (info) {
            if (info.followers !== undefined) account.followers = info.followers;
            if (info.following !== undefined) account.following = info.following;
            if (info.hasAvatar !== undefined) account.hasAvatar = info.hasAvatar;
            if (info.posts !== undefined) account.posts = info.posts;
            
            console.log(`📊 Đã cập nhật thông tin cho ${username}:`, info);
        }

        // Render lại table
        this.renderTable();

        // Lưu vào storage
        this.saveAccountsToStorage();

        // Hiển thị notification
        this.showNotification(username, status);

        // Scroll đến row được update
        this.scrollToAccount(index);
    }

    // ============== ✅ THÊM: BATCH UPDATE ==============
    batchUpdateAccounts(updates) {
        console.log(`📥 Batch update ${updates.length} accounts`);
        
        updates.forEach(update => {
            this.updateAccountFromBackend(
                update.username,
                update.status,
                update.cookie,
                update.info
            );
        });
    }

    getAllAccounts() {
        return this.accounts;
    }
}

// ============== ✅ KHỞI TẠO KHI DOM READY ==============
document.addEventListener('DOMContentLoaded', function() {
    window.manageAccountsComplete = new ManageAccountsComplete();
    
    // Expose method để Python có thể gọi trực tiếp
    window.updateAccountStatus = (username, status, cookie, info) => {
        window.manageAccountsComplete.updateAccountFromBackend(username, status, cookie, info);
    };
    
    console.log('✓ ManageAccountsComplete đã sẵn sàng');
    console.log('✓ updateAccountStatus đã được expose cho Python');
});