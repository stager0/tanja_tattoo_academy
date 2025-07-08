document.addEventListener('DOMContentLoaded', () => {

    const app = {
        // Инициализация всех модулей
        init() {
            this.sidebar.init();
            this.viewSwitcher.init();
            this.profileAvatar.init();
            this.courseSidebar.init();
            this.autoResizeTextarea.init();
        },

        // Модуль для управления боковой панелью (меню)
        sidebar: {
            init() {
                this.toggleBtn = document.querySelector('.mobile-menu-toggle');
                this.sidebarEl = document.querySelector('.sidebar');
                this.overlay = document.querySelector('.sidebar-overlay');
                this.addEventListeners();
            },
            addEventListeners() {
                if (!this.toggleBtn || !this.sidebarEl || !this.overlay) return;
                this.toggleBtn.addEventListener('click', () => this.toggle());
                this.overlay.addEventListener('click', () => this.toggle());
            },
            toggle() {
                this.sidebarEl.classList.toggle('is-open');
                document.body.classList.toggle('sidebar-open');
            }
        },

        // Модуль для переключателя вида на странице учеников
        viewSwitcher: {
            init() {
                this.container = document.querySelector('.students-container');
                this.gridBtn = document.getElementById('view-grid-btn');
                this.listBtn = document.getElementById('view-list-btn');
                this.addEventListeners();
            },
            addEventListeners() {
                if (!this.container || !this.gridBtn || !this.listBtn) return;
                this.gridBtn.addEventListener('click', () => this.setView('grid'));
                this.listBtn.addEventListener('click', () => this.setView('list'));
            },
            setView(view) {
                this.container.classList.remove('view-grid', 'view-list');
                this.container.classList.add(`view-${view}`);
                this.gridBtn.classList.toggle('active', view === 'grid');
                this.listBtn.classList.toggle('active', view === 'list');
            }
        },

        // Модуль для загрузки аватара в профиле
        profileAvatar: {
            init() {
                this.avatarInput = document.getElementById('avatar-input');
                this.avatarPreview = document.getElementById('avatar-preview');
                this.addEventListeners();
            },
            addEventListeners() {
                if (!this.avatarInput || !this.avatarPreview) return;
                this.avatarInput.addEventListener('change', (event) => {
                    const file = event.target.files[0];
                    if (file) {
                        this.avatarPreview.src = URL.createObjectURL(file);
                    }
                });
            }
        },

        // Модуль для сворачиваемого меню курса на мобильных
        courseSidebar: {
            init() {
                this.toggleButton = document.querySelector('.lessons-toggle-btn');
                this.lessonsList = document.querySelector('.lessons-list');
                this.addEventListeners();
            },
            addEventListeners() {
                if (!this.toggleButton || !this.lessonsList) return;
                this.toggleButton.addEventListener('click', () => {
                    this.lessonsList.classList.toggle('is-open');
                    this.toggleButton.querySelector('i').classList.toggle('rotated');
                });
            }
        },

        // Модуль для авто-изменения высоты текстовых полей
        autoResizeTextarea: {
            init() {
                document.querySelectorAll('.autoresize-textarea').forEach(textarea => {
                    textarea.addEventListener('input', this.resize, false);
                    this.resize({ target: textarea }); // initial resize
                });
            },
            resize(event) {
                const textarea = event.target;
                textarea.style.height = 'auto';
                textarea.style.height = (textarea.scrollHeight) + 'px';
            }
        }
    };

    app.init();
});