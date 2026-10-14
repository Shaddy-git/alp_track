document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const errorEl = document.getElementById('error');
    errorEl.textContent = '';
    
    const data = {
        username: document.getElementById('username').value.trim(),
        password: document.getElementById('password').value,
    };
    
    try {
        const response = await api.login(data);
        saveToken(response.access_token, response.user);
        window.location.href = 'dashboard.html';
    } catch (err) {
        errorEl.textContent = err.message;
    }
});