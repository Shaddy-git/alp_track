// Требуем авторизацию - если токена нет, редирект на login
if (!requireAuth()) {
    throw new Error('Not authenticated');
}

async function loadDashboard() {
    try {
        // 1. Загружаем профиль
        const user = await api.me();
        document.getElementById('userInfo').textContent = `Привет, ${user.username}!`;
        
        const profileEl = document.getElementById('profileInfo');
        profileEl.innerHTML = `
            <li><strong>ID:</strong> ${user.id}</li>
            <li><strong>Имя:</strong> ${user.username}</li>
            <li><strong>Email:</strong> ${user.email}</li>
            <li><strong>Роль:</strong> ${user.role}</li>
            <li><strong>Уровень подготовки:</strong> ${user.experience_level}</li>
        `;
        
        // 2. Загружаем группы
        const groups = await api.listGroups();
        
        const groupsEl = document.getElementById('groupsList');
        if (groups.length === 0) {
            groupsEl.innerHTML = '<p class="text-muted">Пока нет групп.</p>';
            return;
        }
        
        groupsEl.innerHTML = groups.map(g => `
            <div class="card group-card mb-3">
                <div class="card-body">
                    <h6 class="card-title">${g.name}</h6>
                    <p class="card-text small text-muted mb-2">
                        ${g.start_date} - ${g.end_date} | Статус: ${g.status}
                    </p>
                    <p class="card-text small">Участников: ${g.members_count}</p>
                </div>
            </div>
        `).join('');
        
    } catch (err) {
        console.error(err);
        alert('Ошибка загрузки данных: ' + err.message);
    }
}

// Запускаем загрузку
loadDashboard();