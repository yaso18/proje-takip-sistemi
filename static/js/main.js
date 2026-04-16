let currentPage = 1;
let allProjects = [];
const itemsPerPage = 2; // ⬅️ Sayfa limiti 2 olarak ayarlandı
let currentLanguage = 'tr';
let currentTheme = 'light';
let currentEditingId = null; 

const translations = {
    tr: {
        searchPlaceholder: "Proje ara...",
        newProjectBtn: "+ Yeni Proje",
        newProjectTitle: "Yeni Proje Ekle",
        editProjectTitle: "Projeyi Düzenle", 
        projectNamePlaceholder: "Proje adı...",
        projectLanguagePlaceholder: "Kodlama dili (Örn: Python, Node.js, mc...)",
        projectDescriptionPlaceholder: "Açıklama...",
        saveBtn: "Kaydet",
        cancelBtn: "İptal",
        noProjects: "Proje bulunamadı",
        completed: "Tamamlandı",
        pending: "Bitmemiş",
        complete: "Bitir", 
        undoComplete: "Geri Çevir", 
        editBtn: "Düzenle", 
        delete: "Sil",
        status: "Durum",
        emptyName: "Proje adı boş olamaz!",
        statusLabel: "Durum:",
        lightTheme: "Açık Tema",
        darkTheme: "Koyu Tema"
    },
    en: {
        searchPlaceholder: "Search project...",
        newProjectBtn: "+ New Project",
        newProjectTitle: "Add New Project",
        editProjectTitle: "Edit Project",
        projectNamePlaceholder: "Project name...",
        projectLanguagePlaceholder: "Programming language (Ex: Python, Node.js, mc...)",
        projectDescriptionPlaceholder: "Description...",
        saveBtn: "Save",
        cancelBtn: "Cancel",
        noProjects: "No projects found",
        completed: "Completed",
        pending: "Pending",
        complete: "Complete",
        undoComplete: "Undo Complete", 
        editBtn: "Edit",
        delete: "Delete",
        status: "Status",
        emptyName: "Project name cannot be empty!",
        statusLabel: "Status:",
        lightTheme: "Light Theme",
        darkTheme: "Dark Theme"
    }
};

function updateLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    
    document.getElementById('searchInput').placeholder = translations[lang].searchPlaceholder;
    document.getElementById('newProjectBtn').textContent = translations[lang].newProjectBtn;
    
    document.getElementById('modalTitle').textContent = currentEditingId === null 
        ? translations[lang].newProjectTitle 
        : translations[lang].editProjectTitle; 
        
    document.getElementById('projectName').placeholder = translations[lang].projectNamePlaceholder;
    document.getElementById('projectLanguage').placeholder = translations[lang].projectLanguagePlaceholder;
    document.getElementById('projectDescription').placeholder = translations[lang].projectDescriptionPlaceholder;

    document.getElementById('saveProjectBtn').textContent = translations[lang].saveBtn;
    document.getElementById('closeModalBtn').textContent = translations[lang].cancelBtn;
    document.getElementById('completedLabel').textContent = translations[lang].completed;
    document.getElementById('pendingLabel').textContent = translations[lang].pending;
    document.getElementById('statusFilterLabel').textContent = translations[lang].statusLabel;
    document.getElementById('themeToggleBtn').textContent = currentTheme === 'light' ? translations[lang].darkTheme : translations[lang].lightTheme;
    
    displayProjects();
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
    document.documentElement.setAttribute('data-theme', currentTheme);
    document.getElementById('themeToggleBtn').textContent = currentTheme === 'light' ? translations[currentLanguage].darkTheme : translations[currentLanguage].lightTheme;
}

function initializeSettings() {
    const savedLanguage = localStorage.getItem('language') || 'tr';
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    currentLanguage = savedLanguage;
    currentTheme = savedTheme;
    
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.value = savedLanguage;
    }

    document.documentElement.setAttribute('data-theme', savedTheme);
    
    updateLanguage(savedLanguage);
}

function fetchProjects(page = 1, search = '') {
    const completedChecked = document.getElementById('completedFilter').checked;
    const pendingChecked = document.getElementById('pendingFilter').checked;
    
    // Durum filtresini API'ye göndermek için tek bir string oluşturma
    let status = 'all';
    if (completedChecked && !pendingChecked) {
        status = 'completed';
    } else if (pendingChecked && !completedChecked) {
        status = 'pending';
    }
    
    const url = `/api/projects?page=${page}&search=${search}&status=${status}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            allProjects = data.projects;
            currentPage = data.current_page; // API'den gelen doğru sayfa numarasını kullan
            displayProjects();
            
            // total_pages ve pagination doğru bir şekilde ayarlanıyor.
            setupPagination(data.total_pages);
            
        })
        .catch(error => console.error('Hata:', error));
}


function displayProjects() {
    const projectsList = document.getElementById('projectsList');
    projectsList.innerHTML = '';
    
    if (allProjects.length === 0) {
        projectsList.innerHTML = `<p style="text-align: center; color: var(--text-secondary);">${translations[currentLanguage].noProjects}</p>`;
        return;
    }
    
    const projectsPage = allProjects; 
    
    projectsPage.forEach(project => {
        const projectDiv = document.createElement('div');
        projectDiv.className = 'project-item';
        
        const projectLanguage = project.language || 'Bilinmiyor'; 
        const projectDescription = project.description || 'Açıklama yok'; 
        
        const statusText = project.status ? translations[currentLanguage].completed : translations[currentLanguage].pending;
        const statusSymbol = project.status ? '✓' : '✗';
        
        const statusButtonText = project.status ? translations[currentLanguage].undoComplete : translations[currentLanguage].complete;
        const statusButtonClass = project.status ? 'btn-undo' : 'btn-complete';

        projectDiv.innerHTML = `
            <div class="project-info">
                <div class="project-name">${project.name}</div>
                <div class="project-language" style="font-size: 0.95em; color: cyan;">Dil: ${projectLanguage}</div>
                <div class="project-description" style="font-style: italic; font-size: 0.9em; margin-top: 3px;">${projectDescription}</div>
                <div class="project-status">${translations[currentLanguage].statusLabel} ${statusSymbol} ${statusText}</div>
            </div>
            <div class="project-actions">
                <button class="btn btn-edit" onclick="openEditModal(${project.id})">${translations[currentLanguage].editBtn}</button> 
                <button class="btn ${statusButtonClass}" onclick="toggleProjectStatus(${project.id})">${statusButtonText}</button>
                <button class="btn btn-delete" onclick="deleteProject(${project.id})">${translations[currentLanguage].delete}</button>
            </div>
        `;
        projectsList.appendChild(projectDiv);
    });
}

function setupPagination(totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
        btn.textContent = i;
        btn.onclick = () => {
            // Sayfa değişiminde yeni sayfa numarasını ve mevcut arama metnini gönderir.
            fetchProjects(i, document.getElementById('searchInput').value); 
        };
        pagination.appendChild(btn);
    }
}

function handleSearch() {
    currentPage = 1; // Arama değiştiğinde her zaman 1. sayfadan başla
    const search = document.getElementById('searchInput').value;
    fetchProjects(currentPage, search);
}

function handleStatusFilter() {
    currentPage = 1; // Filtre değiştiğinde her zaman 1. sayfadan başla
    fetchProjects(currentPage, document.getElementById('searchInput').value);
}

function toggleProjectStatus(projectId) {
    fetch(`/api/projects/${projectId}/toggle-status`, {
        method: 'PUT'
    })
        .then(response => response.json())
        .then(() => {
            fetchProjects(currentPage, document.getElementById('searchInput').value); 
        })
        .catch(error => console.error('Hata:', error));
}


function deleteProject(projectId) {
    fetch(`/api/projects/${projectId}`, {
        method: 'DELETE'
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Silme hatası'); });
            }
            return response.json();
        })
        .then(() => {
            fetchProjects(currentPage, document.getElementById('searchInput').value); 
        })
        .catch(error => console.error('Hata:', error));
}


function openNewProjectModal() {
    currentEditingId = null;
    document.getElementById('projectName').value = '';
    document.getElementById('projectLanguage').value = '';
    document.getElementById('projectDescription').value = '';
    
    updateLanguage(currentLanguage); 
    document.getElementById('modal').classList.remove('hidden');
}


function openEditModal(projectId) {
    currentEditingId = projectId;
    
    const project = allProjects.find(p => p.id === projectId);
    
    if (!project) {
        alert("Proje detayları bulunamadı.");
        return;
    }

    document.getElementById('projectName').value = project.name;
    document.getElementById('projectLanguage').value = project.language || ''; 
    document.getElementById('projectDescription').value = project.description || ''; 

    updateLanguage(currentLanguage); 
    document.getElementById('modal').classList.remove('hidden');
}


function handleSaveProject() {
    const projectName = document.getElementById('projectName').value;
    const projectLanguage = document.getElementById('projectLanguage').value; 
    const projectDescription = document.getElementById('projectDescription').value; 
    
    if (!projectName.trim()) {
        alert(translations[currentLanguage].emptyName);
        return;
    }

    const projectData = { 
        name: projectName,
        language: projectLanguage, 
        description: projectDescription 
    };

    let url = '/api/projects';
    let method = 'POST';

    if (currentEditingId !== null) {
        url = `/api/projects/${currentEditingId}`;
        method = 'PUT';
    } 

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(projectData)
    })
        .then(response => {
            if (!response.ok) {
                console.error('API isteği başarısız oldu:', response.status);
                throw new Error(currentEditingId !== null ? 'Güncelleme başarısız' : 'Ekleme başarısız');
            }
            return response.json();
        })
        .then(() => {
            document.getElementById('modal').classList.add('hidden');
            currentEditingId = null; 
            fetchProjects(currentPage); 
        })
        .catch(error => console.error('Hata:', error));
}

// ----------------------------------------------------------------------
// * OLAY DİNLEYİCİLERİ (EVENT LISTENERS)
// ----------------------------------------------------------------------

document.getElementById('newProjectBtn').addEventListener('click', openNewProjectModal);

document.getElementById('closeModalBtn').addEventListener('click', () => {
    document.getElementById('modal').classList.add('hidden');
    currentEditingId = null; 
});

document.getElementById('searchInput').addEventListener('keyup', handleSearch);
document.getElementById('saveProjectBtn').addEventListener('click', handleSaveProject);
document.getElementById('completedFilter').addEventListener('change', handleStatusFilter);
document.getElementById('pendingFilter').addEventListener('change', handleStatusFilter);

document.getElementById('languageSelect').addEventListener('change', (e) => {
    updateLanguage(e.target.value);
});

document.getElementById('themeToggleBtn').addEventListener('click', toggleTheme);


initializeSettings();
fetchProjects();