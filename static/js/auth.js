// Toast通知
function showToast(message, type = 'success') {
    // 移除已有的toast容器
    const existingContainer = document.querySelector('.toast-container');
    if (existingContainer) {
        existingContainer.remove();
    }
    
    // 创建toast容器
    const container = document.createElement('div');
    container.className = 'toast-container';
    
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    document.body.appendChild(container);
    
    // 3秒后移除
    setTimeout(() => {
        container.remove();
    }, 3000);
}

// 确认对话框
function showConfirm(message) {
    return confirm(message);
}

// 格式化价格
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

// 格式化时间
function formatTime(dateString) {
    const date = new Date(dateString);
    
    // 加快7小时（中国时区）
    date.setHours(date.getHours() + 7);
    
    // 直接显示具体日期时间
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 获取URL参数
function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// 设置URL参数
function setUrlParam(param, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(param, value);
    window.history.pushState({}, '', url);
}

// 跳转到登录页
function redirectToLogin() {
    localStorage.setItem('redirectUrl', window.location.href);
    window.location.href = '/login.html';
}

// 检查登录状态
async function checkAuth() {
    if (!API.isLoggedIn()) {
        return false;
    }
    
    try {
        const user = await API.getCurrentUser();
        if (user) {
            localStorage.setItem('user', JSON.stringify(user));
            return true;
        }
    } catch (e) {
        console.error('验证登录状态失败:', e);
    }
    
    API.logout();
    return false;
}

// 获取当前用户
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        return JSON.parse(userStr);
    }
    return null;
}

// 更新导航栏用户状态
async function updateNavbarAuth() {
    const authNav = document.getElementById('auth-nav');
    if (!authNav) return;
    
    const isLoggedIn = await checkAuth();
    
    if (isLoggedIn) {
        const user = getCurrentUser();
        const unreadCount = await API.getUnreadCount().catch(() => 0);
        
        authNav.innerHTML = `
            <a href="/post-item.html" class="btn btn-primary btn-sm">
                发布商品
            </a>
            <a href="/dashboard.html" class="nav-link ${window.location.pathname.includes('dashboard') ? 'active' : ''}">
                个人中心
            </a>
            <a href="/chat.html" class="nav-link ${window.location.pathname.includes('chat') ? 'active' : ''}">
                消息 ${unreadCount > 0 ? `<span class="nav-badge">${unreadCount}</span>` : ''}
            </a>
            <span class="nav-link" style="cursor: pointer;" onclick="API.logout()">
                退出
            </span>
        `;
    } else {
        authNav.innerHTML = `
            <a href="/login.html" class="nav-link ${window.location.pathname.includes('login') ? 'active' : ''}">
                登录
            </a>
            <a href="/register.html" class="btn btn-primary btn-sm">
                注册
            </a>
        `;
    }
}

// 渲染商品卡片
function renderItemCard(item) {
    const imageUrl = item.image_url || 'https://via.placeholder.com/300x200?text=暂无图片';
    
    return `
        <div class="card" onclick="window.location.href='/product.html?id=${item.id}'">
            <img src="${imageUrl}" alt="${item.title}" class="card-img" onerror="this.src='https://via.placeholder.com/300x200?text=暂无图片'">
            <div class="card-body">
                <h3 class="card-title">${item.title}</h3>
                <div class="card-price">${formatPrice(item.price)}</div>
                <div class="card-meta">
                    <span>${item.condition}</span>
                    <span>${formatTime(item.created_at)}</span>
                </div>
            </div>
        </div>
    `;
}

// 渲染商品列表
function renderItemsGrid(items, container) {
    if (!items || items.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <h3 class="empty-title">暂无商品</h3>
                <p class="empty-desc">还没有发布商品，快来发布吧！</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = items.map(item => renderItemCard(item)).join('');
}

// 渲染分类列表
function renderCategories(categories, container, onCategoryClick) {
    container.innerHTML = `
        <div class="category-item active" data-category="">
            <span class="category-icon">🏠</span>
            <span class="category-name">全部</span>
        </div>
        ${categories.map(cat => `
            <div class="category-item" data-category="${cat.id}">
                <span class="category-icon">${cat.icon}</span>
                <span class="category-name">${cat.name}</span>
            </div>
        `).join('')}
    `;
    
    // 添加点击事件
    container.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', () => {
            container.querySelectorAll('.category-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const category = item.dataset.category;
            onCategoryClick(category);
        });
    });
}

// 图片上传预览
function handleImageUpload(input, previewContainer) {
    const file = input.files[0];
    if (!file) return;
    
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast('只能上传图片文件(JPEG, PNG, GIF, WebP)', 'error');
        return;
    }
    
    // 验证文件大小(5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('图片大小不能超过5MB', 'error');
        return;
    }
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = function(e) {
        previewContainer.innerHTML = `
            <img src="${e.target.result}" alt="预览">
        `;
    };
    reader.readAsDataURL(file);
}

// 显示加载状态
function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 更新导航栏
    await updateNavbarAuth();
});

// 公共工具函数
window.Utils = {
    showToast,
    showConfirm,
    formatPrice,
    formatTime,
    getUrlParam,
    setUrlParam,
    redirectToLogin,
    checkAuth,
    getCurrentUser,
    updateNavbarAuth,
    renderItemCard,
    renderItemsGrid,
    renderCategories,
    handleImageUpload,
    showLoading
};
