document.addEventListener('DOMContentLoaded', () => {

    const app = {
        // Инициализация всех модулей
        init() {
            this.sidebar.init();
            this.viewSwitcher.init();
            this.profileAvatar.init();
            this.courseSidebar.init();
            this.autoResizeTextarea.init();
            this.imageModal.init();
            this.chatUpload.init();
            this.homeworkUpload.init(); // <-- Добавлен модуль для загрузки ДЗ
        },

        // Модуль для управления боковой панелью (меню)
        sidebar: {
            init() {
                this.toggleBtn = document.querySelector('.mobile-menu-toggle');
                this.sidebarEl = document.querySelector('.sidebar');
                this.overlay = document.querySelector('.sidebar-overlay');
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
                    this.resize({ target: textarea });
                });
            },
            resize(event) {
                const textarea = event.target;
                textarea.style.height = 'auto';
                textarea.style.height = (textarea.scrollHeight) + 'px';
            }
        },

        // Модуль: Модальное окно для изображений
        imageModal: {
            init() {
                this.modal = document.getElementById('imageModal');
                if (!this.modal) return;
                this.modalImage = document.getElementById('modalImage');
                this.closeBtn = this.modal.querySelector('.modal-close-btn');
                this.addEventListeners();
            },
            addEventListeners() {
                document.body.addEventListener('click', (event) => {
                    if (event.target.matches('.message-attachment img, .submission-preview img, .submission-image-viewer img')) {
                        this.open(event.target.src);
                    }
                });
                this.closeBtn.addEventListener('click', () => this.close());
                this.modal.addEventListener('click', (event) => {
                    if (event.target === this.modal) this.close();
                });
                document.addEventListener('keydown', (event) => {
                    if (event.key === 'Escape' && this.modal.classList.contains('is-open')) this.close();
                });
            },
            open(src) {
                this.modalImage.src = src;
                this.modal.classList.add('is-open');
                document.body.style.overflow = 'hidden';
            },
            close() {
                this.modal.classList.remove('is-open');
                document.body.style.overflow = '';
            }
        },

        // Модуль: Предпросмотр загружаемого файла в чате
        chatUpload: {
            init() {
                this.fileInput = document.getElementById('file-upload-input');
                this.previewContainer = document.getElementById('upload-preview-container');
                if (!this.fileInput || !this.previewContainer) return;
                this.fileInput.addEventListener('change', (event) => this.showPreview(event));
            },
            showPreview(event) { /* ... код ... */ },
            clearPreview(resetInput) { /* ... код ... */ }
        },

        // НОВЫЙ МОДУЛЬ: Загрузка домашнего задания на странице курса
        homeworkUpload: {
            init() {
                const uploadArea = document.querySelector('.file-upload-area');
                if (!uploadArea) return;

                const input = uploadArea.querySelector('input[type=file]');
                const p = uploadArea.querySelector('p');
                const defaultText = p.textContent;

                // Обработчик клика по области
                uploadArea.addEventListener('click', () => input.click());

                // Обработчик изменения инпута (когда файл выбран)
                input.addEventListener('change', () => {
                    if (input.files.length > 0) {
                        p.textContent = `Выбран файл: ${input.files[0].name}`;
                    } else {
                        p.textContent = defaultText;
                    }
                });
            }
        }
    };

    app.init();
});