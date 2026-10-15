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
    getGroup: (id) => apiRequest(`/groups/${id}`),
    createGroup: (data) => apiRequest('/groups', 'POST', data),
    updateGroup: (id, data) => apiRequest(`/groups/${id}`, 'PUT', data),
    deleteGroup: (id) => apiRequest(`/groups/${id}`, 'DELETE'),
    addMember: (groupId, userId) => apiRequest(`/groups/${groupId}/members`, 'POST', { user_id: userId }),
    removeMember: (groupId, userId) => apiRequest(`/groups/${groupId}/members/${userId}`, 'DELETE'),
    joinGroup: (groupId) => apiRequest(`/groups/${groupId}/join`, 'POST'),
    
    // --- Горы ---
    listMountains: (params = '') => apiRequest(`/mountains${params}`),
    getMountain: (id) => apiRequest(`/mountains/${id}`),
    createMountain: (data) => apiRequest('/mountains', 'POST', data),
    updateMountain: (id, data) => apiRequest(`/mountains/${id}`, 'PUT', data),
    deleteMountain: (id) => apiRequest(`/mountains/${id}`, 'DELETE'),
    
    // --- Восхождения ---
    listAscents: () => apiRequest('/ascents'),
    myAscents: () => apiRequest('/ascents/my'),
    getAscent: (id) => apiRequest(`/ascents/${id}`),
    createAscent: (data) => apiRequest('/ascents', 'POST', data),
    updateAscent: (id, data) => apiRequest(`/ascents/${id}`, 'PUT', data),
    deleteAscent: (id) => apiRequest(`/ascents/${id}`, 'DELETE'),
    
    // --- Пользователи ---
    listUsers: () => apiRequest('/users'),
    getUser: (id) => apiRequest(`/users/${id}`),
    updateUser: (id, data) => apiRequest(`/users/${id}`, 'PUT', data),
    deleteUser: (id) => apiRequest(`/users/${id}`, 'DELETE'),
    changeRole: (id, role) => apiRequest(`/users/${id}/role`, 'PUT', { role }),
    
    // --- Отчёты ---
    climbersByMountain: (id) => apiRequest(`/reports/climbers-by-mountain/${id}`),
    successfulAscents: (year) => apiRequest(`/reports/successful-ascents?year=${year}`),
    popularMountains: (limit = 5) => apiRequest(`/reports/popular-mountains?limit=${limit}`),
    userStats: (id) => apiRequest(`/reports/user-stats/${id}`),
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