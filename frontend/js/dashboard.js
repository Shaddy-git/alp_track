// Требуем авторизацию
if (!requireAuth()) {
    throw new Error('Not authenticated');
}
// Показываем блок отчётов для admin/instructor
const user = getCurrentUser();
if (user && ['admin', 'instructor'].includes(user.role)) {
    const reportsCard = document.getElementById('reportsCard');
    if (reportsCard) reportsCard.style.display = 'block';
}

async function loadDashboard() {
    try {
        // 1. Профиль
        await loadProfile();
        
        // 2. Мои восхождения
        await loadMyAscents();
        
        // 3. Группы
        await loadGroups();
        
        // 4. Горы
        await loadMountains();
        
    } catch (err) {
        console.error(err);
    }
}

async function loadProfile() {
    try {
        const user = await api.me();
        document.getElementById('profileInfo').innerHTML = `
            <li><strong>ID:</strong> ${user.id}</li>
            <li><strong>Имя:</strong> ${user.username}</li>
            ${user.full_name ? `<li><strong>ФИО:</strong> ${user.full_name}</li>` : ''}
            <li><strong>Email:</strong> ${user.email}</li>
            <li><strong>Роль:</strong> <span class="badge bg-primary">${user.role}</span></li>
            <li><strong>Уровень подготовки:</strong> ${user.experience_level} / 5</li>
        `;
    } catch (err) {
        console.error('Ошибка загрузки профиля:', err);
    }
}

async function loadMyAscents() {
    const el = document.getElementById('ascentsList');
    try {
        const ascents = await api.myAscents();
        
        if (ascents.length === 0) {
            el.innerHTML = '<p class="text-muted">Пока нет восхождений. Присоединитесь к группе!</p>';
            return;
        }
        
        el.innerHTML = ascents.map(a => `
            <div class="card group-card mb-2">
                <div class="card-body py-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${a.mountain}</strong>
                            <small class="text-muted">(${a.mountain_height} м, сложность ${a.mountain_difficulty})</small>
                            <br>
                            <small class="text-muted">${a.ascent_date} ${a.group ? '| Группа: ' + a.group : ''}</small>
                        </div>
                        <div>
                            ${a.is_successful 
                                ? '<span class="badge bg-success">Успех</span>' 
                                : '<span class="badge bg-warning text-dark">Запланировано</span>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

async function loadGroups() {
    const el = document.getElementById('groupsList');
    try {
        const groups = await api.listGroups();
        
        if (groups.length === 0) {
            el.innerHTML = '<p class="text-muted">Пока нет групп.</p>';
            return;
        }
        
        el.innerHTML = groups.map(g => `
            <div class="card group-card mb-2">
                <div class="card-body py-2">
                    <h6 class="mb-1">${g.name}</h6>
                    <small class="text-muted">${g.start_date} - ${g.end_date}</small>
                    <br>
                    <small class="text-muted">Статус: ${g.status} | Участников: ${g.members_count}</small>
                </div>
            </div>
        `).join('');
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

async function loadMountains() {
    const el = document.getElementById('mountainsList');
    try {
        const mountains = await api.listMountains();
        
        if (mountains.length === 0) {
            el.innerHTML = '<p class="text-muted">Нет доступных гор.</p>';
            return;
        }
        
        // Показываем первые 5
        el.innerHTML = mountains.slice(0, 5).map(m => `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <div>
                    <strong>${m.name}</strong>
                    <small class="text-muted">(${m.country})</small>
                </div>
                <div class="text-end">
                    <small>${m.height} м</small><br>
                    <span class="badge bg-secondary">Сложность ${m.difficulty_level}</span>
                </div>
            </div>
        `).join('');
        
        el.innerHTML += `<div class="text-center mt-2"><a href="mountains.html" class="small">Все горы →</a></div>`;
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

loadDashboard();