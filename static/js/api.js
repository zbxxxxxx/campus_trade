// API基础配置
const API_BASE_URL = '/api';

// 获取认证token
function getToken() {
    return localStorage.getItem('token');
}

// 设置认证token
function setToken(token) {
    localStorage.setItem('token', token);
}

// 移除认证token
function removeToken() {
    localStorage.setItem('token', '');
}

// 检查是否已登录
function isLoggedIn() {
    return !!getToken();
}

// 获取当前用户信息
async function getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (response.status === 401) {
        logout();
        return null;
    }
    
    if (!response.ok) {
        throw new Error('获取用户信息失败');
    }
    
    return await response.json();
}

// ============ 认证相关API ============

async function register(username, email, password, phone = '') {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password, phone })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '注册失败');
    }
    
    return data;
}

async function login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '登录失败');
    }
    
    return data;
}

function logout() {
    removeToken();
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

// ============ 商品相关API ============

async function getItems(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.category) queryParams.append('category', params.category);
    if (params.search) queryParams.append('search', params.search);
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.order) queryParams.append('order', params.order);
    
    const response = await fetch(`${API_BASE_URL}/items?${queryParams.toString()}`);
    
    if (!response.ok) {
        throw new Error('获取商品列表失败');
    }
    
    return await response.json();
}

async function getItem(itemId) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}`);
    
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('商品不存在');
        }
        throw new Error('获取商品详情失败');
    }
    
    return await response.json();
}

async function getCategories() {
    const response = await fetch(`${API_BASE_URL}/items/categories`);
    
    if (!response.ok) {
        throw new Error('获取分类失败');
    }
    
    const data = await response.json();
    return data.data || [];
}

async function getMyItems() {
    const response = await fetch(`${API_BASE_URL}/items/my`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('获取我的商品失败');
    }
    
    const data = await response.json();
    return data.data || [];
}

async function createItem(formData) {
    const response = await fetch(`${API_BASE_URL}/items`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        },
        body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '发布商品失败');
    }
    
    return data;
}

async function updateItem(itemId, formData) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        },
        body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '更新商品失败');
    }
    
    return data;
}

async function deleteItem(itemId) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || '删除商品失败');
    }
    
    return await response.json();
}

async function updateItemStatus(itemId, status) {
    const response = await fetch(`${API_BASE_URL}/items/${itemId}/status`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ status })
    });
    
    if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || '更新商品状态失败');
    }
    
    return await response.json();
}

// ============ 订单相关API ============

async function createOrder(itemId, remark = '') {
    const response = await fetch(`${API_BASE_URL}/orders`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ item_id: itemId, remark })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '创建订单失败');
    }
    
    return data;
}

async function getMyOrders() {
    const response = await fetch(`${API_BASE_URL}/orders`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('获取订单失败');
    }
    
    const data = await response.json();
    return data.orders || [];
}

async function getOrder(orderId) {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('订单不存在');
        }
        throw new Error('获取订单详情失败');
    }
    
    return await response.json();
}

// ============ 消息相关API ============

async function getMyMessages() {
    const response = await fetch(`${API_BASE_URL}/messages`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        throw new Error('获取消息失败');
    }
    
    return await response.json();
}

async function sendMessage(receiverId, content, itemId = null) {
    const response = await fetch(`${API_BASE_URL}/messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            receiver_id: receiverId,
            content: content,
            item_id: itemId
        })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '发送消息失败');
    }
    
    return data;
}

async function getUnreadCount() {
    const response = await fetch(`${API_BASE_URL}/messages/unread`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    if (!response.ok) {
        return 0;
    }
    
    const data = await response.json();
    return data.data?.unread_count || 0;
}

async function markMessageAsRead(messageId) {
    const response = await fetch(`${API_BASE_URL}/messages/${messageId}/read`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    });
    
    return await response.json();
}

// ============ 用户相关API ============

async function updateProfile(userData) {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.detail || '更新失败');
    }
    
    return data;
}

// 导出API
window.API = {
    // 认证
    register,
    login,
    logout,
    getCurrentUser,
    isLoggedIn,
    setToken,
    removeToken,
    
    // 商品
    getItems,
    getItem,
    getCategories,
    getMyItems,
    createItem,
    updateItem,
    updateItemStatus,
    deleteItem,
    
    // 订单
    createOrder,
    getMyOrders,
    getOrder,
    
    // 消息
    getMyMessages,
    sendMessage,
    getUnreadCount,
    markMessageAsRead,
    
    // 用户
    updateProfile
};
