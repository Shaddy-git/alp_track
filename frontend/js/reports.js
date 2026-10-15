if (!requireAuth()) {
    throw new Error('Not authenticated');
}

// Проверка роли: отчёты доступны только instructor/admin
const currentUser = getCurrentUser();
if (!currentUser || !['admin', 'instructor'].includes(currentUser.role)) {
    alert('Доступ к отчётам только для инструкторов и администраторов');
    window.location.href = 'dashboard.html';
    throw new Error('Forbidden');
}

// ============ Топ гор ============
async function loadPopularMountains() {
    const el = document.getElementById('popularMountains');
    try {
        const mountains = await api.popularMountains(5);
        
        if (mountains.length === 0) {
            el.innerHTML = '<p class="text-muted">Пока нет данных о восхождениях.</p>';
            return;
        }
        
        el.innerHTML = mountains.map((m, i) => `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <div>
                    <span class="badge bg-primary me-2">${i + 1}</span>
                    <strong>${m.name}</strong>
                    <small class="text-muted">(${m.height} м, сложность ${m.difficulty_level})</small>
                </div>
                <div>
                    <span class="badge bg-secondary">${m.ascents_count} восхождений</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

// ============ Статистика за год ============
async function loadYearStats() {
    const el = document.getElementById('yearStats');
    const year = document.getElementById('yearInput').value;
    
    el.innerHTML = '<p class="text-muted">Загрузка...</p>';
    
    try {
        const stats = await api.successfulAscents(year);
        
        el.innerHTML = `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="p-3 bg-light rounded">
                        <h3 class="mb-0">${stats.total_ascents}</h3>
                        <small class="text-muted">Всего</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <div class="p-3" style="background: #d1fae5; border-radius: 8px;">
                        <h3 class="mb-0 text-success">${stats.successful_ascents}</h3>
                        <small class="text-muted">Успешных</small>
                    </div>
                </div>
                <div class="col-6">
                    <div class="p-3" style="background: #fee2e2; border-radius: 8px;">
                        <h3 class="mb-0 text-danger">${stats.failed_ascents}</h3>
                        <small class="text-muted">Провальных</small>
                    </div>
                </div>
                <div class="col-6">
                    <div class="p-3" style="background: #e0e7ff; border-radius: 8px;">
                        <h3 class="mb-0" style="color: var(--primary);">${stats.success_rate}%</h3>
                        <small class="text-muted">Успешность</small>
                    </div>
                </div>
            </div>
        `;
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

// ============ Покорители горы ============
async function loadMountainOptions() {
    const select = document.getElementById('mountainSelect');
    try {
        const mountains = await api.listMountains();
        
        select.innerHTML = '<option value="">- Выберите гору -</option>' +
            mountains.map(m => `<option value="${m.id}">${m.name} (${m.height} м)</option>`).join('');
    } catch (err) {
        select.innerHTML = '<option value="">Ошибка загрузки</option>';
    }
}

async function loadClimbers() {
    const el = document.getElementById('climbersResult');
    const mountainId = document.getElementById('mountainSelect').value;
    
    if (!mountainId) {
        el.innerHTML = '<p class="text-warning">Сначала выберите гору.</p>';
        return;
    }
    
    el.innerHTML = '<p class="text-muted">Загрузка...</p>';
    
    try {
        const data = await api.climbersByMountain(mountainId);
        
        if (data.unique_climbers === 0) {
            el.innerHTML = `<p class="text-muted">Пока никто не покорил гору «${data.mountain.name}».</p>`;
            return;
        }
        
        el.innerHTML = `
            <div class="mb-3">
                <h6>${data.mountain.name} (${data.mountain.height} м, сложность ${data.mountain.difficulty_level})</h6>
                <p class="text-muted mb-0">
                    Всего восхождений: <strong>${data.total_ascents}</strong> | 
                    Уникальных альпинистов: <strong>${data.unique_climbers}</strong>
                </p>
            </div>
            <div class="row g-2">
                ${data.climbers.map(c => `
                    <div class="col-md-6">
                        <div class="p-3 border rounded">
                            <strong>${c.full_name || c.username}</strong>
                            <br>
                            <small class="text-muted">
                                @${c.username} | Уровень: ${c.experience_level}<br>
                                Первое восхождение: ${c.first_ascent_date}
                            </small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

// ============ Инициализация ============
loadPopularMountains();
loadYearStats();
loadMountainOptions();