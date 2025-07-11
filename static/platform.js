document.addEventListener('DOMContentLoaded', () => {

    const app = {
        // Инициализация всех модулей
        init() {
            // Старые модули
            this.sidebar.init();
            this.viewSwitcher.init();
            this.profileAvatar.init();
            this.courseSidebar.init();
            this.autoResizeTextarea.init();

            // НОВЫЕ модули для чата
            this.imageModal.init();
            this.chatUpload.init();
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
                    this.resize({ target: textarea });
                });
            },
            resize(event) {
                const textarea = event.target;
                textarea.style.height = 'auto';
                textarea.style.height = (textarea.scrollHeight) + 'px';
            }
        },

        // НОВЫЙ МОДУЛЬ: Модальное окно для изображений
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
                    if (event.target.matches('.message-attachment img')) {
                        this.open(event.target.src);
                    }
                });
                this.closeBtn.addEventListener('click', () => this.close());
                this.modal.addEventListener('click', (event) => {
                    if (event.target === this.modal) this.close();
                });
                document.addEventListener('keydown', (event) => {
                    if (event.key === 'Escape' && this.modal.classList.contains('is-open')) {
                        this.close();
                    }
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

        // НОВЫЙ МОДУЛЬ: Предпросмотр загружаемого файла в чате
        chatUpload: {
            init() {
                this.fileInput = document.getElementById('file-upload-input');
                this.previewContainer = document.getElementById('upload-preview-container');
                this.addEventListeners();
            },
            addEventListeners() {
                if (!this.fileInput || !this.previewContainer) return;
                this.fileInput.addEventListener('change', (event) => this.showPreview(event));
            },
            showPreview(event) {
                this.clearPreview(false);
                const file = event.target.files[0];
                if (!file) return;

                const previewElement = document.createElement('div');
                previewElement.className = 'upload-preview';

                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.className = 'upload-preview-image';

                const info = document.createElement('span');
                info.className = 'upload-preview-info';
                info.textContent = file.name;

                const removeBtn = document.createElement('button');
                removeBtn.className = 'upload-preview-remove';
                removeBtn.innerHTML = '&times;';
                removeBtn.type = 'button';
                removeBtn.onclick = () => this.clearPreview(true);

                previewElement.appendChild(img);
                previewElement.appendChild(info);
                previewElement.appendChild(removeBtn);
                this.previewContainer.appendChild(previewElement);
                this.previewContainer.classList.add('visible');
            },
            clearPreview(resetInput) {
                if (resetInput) {
                    this.fileInput.value = '';
                }
                if (this.previewContainer) {
                    this.previewContainer.innerHTML = '';
                    this.previewContainer.classList.remove('visible');
                }
            }
        }
    };

    app.init();
});