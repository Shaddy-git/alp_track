if (!requireAuth()) {
    throw new Error('Not authenticated');
}

// Показываем ссылку Отчёты для admin/instructor
const currentUser = getCurrentUser();
if (currentUser && ['admin', 'instructor'].includes(currentUser.role)) {
    const link = document.getElementById('reportsLink');
    if (link) link.style.display = 'inline';
}

async function loadMountains() {
    const el = document.getElementById('mountainsList');
    el.innerHTML = '<p class="text-muted">Загрузка...</p>';
    
    const minHeight = document.getElementById('minHeight').value;
    const maxDifficulty = document.getElementById('maxDifficulty').value;
    
    const params = new URLSearchParams();
    if (minHeight) params.append('min_height', minHeight);
    if (maxDifficulty) params.append('max_difficulty', maxDifficulty);
    
    const query = params.toString() ? `?${params.toString()}` : '';
    
    try {
        const mountains = await api.listMountains(query);
        
        if (mountains.length === 0) {
            el.innerHTML = '<p class="text-muted text-center py-4">Ничего не найдено. Попробуйте изменить фильтры.</p>';
            return;
        }
        
        el.innerHTML = `
            <p class="text-muted">Найдено: ${mountains.length}</p>
            <div class="row g-3">
                ${mountains.map(m => `
                    <div class="col-md-6 col-lg-4">
                        <div class="card h-100 p-3">
                            <h5 class="mb-1">${m.name}</h5>
                            <p class="text-muted mb-2">${m.country}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span>${m.height} м</span>
                                <span class="badge bg-secondary">Сложность ${m.difficulty_level}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (err) {
        el.innerHTML = `<p class="text-danger">Ошибка: ${err.message}</p>`;
    }
}

function applyFilters() {
    loadMountains();
}

function resetFilters() {
    document.getElementById('minHeight').value = '';
    document.getElementById('maxDifficulty').value = '';
    loadMountains();
}

loadMountains();