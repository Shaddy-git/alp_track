document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const errorEl = document.getElementById('error');
    errorEl.textContent = '';
    
    const data = {
        username: document.getElementById('username').value.trim(),
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
        experience_level: parseInt(document.getElementById('experience_level').value, 10),
    };
    
    try {
        await api.register(data);
        alert('Регистрация успешна! Теперь войдите.');
        window.location.href = 'login.html';
    } catch (err) {
        errorEl.textContent = err.message;
    }
});