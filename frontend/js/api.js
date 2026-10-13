// Общая обёртка над fetch для работы с API AlpTrack

const API_URL = 'http://localhost:5000/api';

/**
 * Обёртка над fetch с автоматической подстановкой JWT.
 * 
 * @param {string} endpoint - путь относительно /api (например, '/auth/login')
 * @param {string} method - HTTP-метод (GET, POST, PUT, DELETE)
 * @param {object|null} data - тело запроса (для POST/PUT)
 * @returns {Promise<object>} - JSON-ответ от сервера
 * @throws {Error} - если ответ не 2xx
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
    };
    
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = { method, headers };
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    
    // Если токен истёк или невалиден - разлогиниваем
    if (response.status === 401 && token) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
        throw new Error('Сессия истекла. Войдите заново.');
    }
    
    const json = await response.json();
    
    if (!response.ok) {
        throw new Error(json.error || json.msg || `Ошибка ${response.status}`);
    }
    
    return json;
}


// ==================== API-функции ====================

const api = {
    // --- Авторизация ---
    register: (data) => apiRequest('/auth/register', 'POST', data),
    login: (data) => apiRequest('/auth/login', 'POST', data),
    me: () => apiRequest('/auth/me'),
    
    // --- Группы ---
    listGroups: () => apiRequest('/groups'),
    createGroup: (data) => apiRequest('/groups', 'POST', data),
    addMember: (groupId, userId) => apiRequest(`/groups/${groupId}/members`, 'POST', { user_id: userId }),
};


// ==================== Работа с пользователем ====================

function saveToken(token, user) {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

function getCurrentUser() {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function requireAuth() {
    if (!localStorage.getItem('access_token')) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}