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
            this.homeworkUpload.init();
            this.cookieConsent.init();
        },

        // ======================================================
        // НОВИЙ МОДУЛЬ ДЛЯ КЕРУВАННЯ ЗГОДОЮ НА COOKIE
        // ======================================================
        cookieConsent: {
            init() {
                // Ця логіка спрацює, якщо відвідувач вже дав згоду раніше
                if (window.Cookiebot && window.Cookiebot.consented) {
                    this.loadContent();
                }

                // Додаємо слухачів на події від Cookiebot
                window.addEventListener('CookiebotOnAccept', () => this.loadContent(), false);
            },

            // Функція, що "вмикає" заблоковані стилі, шрифти та відео
            loadContent() {
                console.log('Cookie consent is given. Loading external resources...');

                // Активуємо заблоковані стилі (шрифти, іконки)
                document.querySelectorAll('link[data-cookieconsent]').forEach(link => {
                    link.setAttribute('type', 'text/css');
                });

                // Активуємо заблоковані відео
                document.querySelectorAll('iframe[data-cookieconsent]').forEach(iframe => {
                    if (iframe.dataset.src) {
                        iframe.setAttribute('src', iframe.dataset.src);
                    }
                });
            }
        },
        // ======================================================
        // КІНЕЦЬ НОВОГО МОДУЛЯ
        // ======================================================

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
                this.viewInput = document.getElementById('view-mode-input');

                if (!this.container || !this.gridBtn || !this.listBtn || !this.viewInput) {
                    return;
                }

                this.gridBtn.addEventListener('click', () => this.setView('grid'));
                this.listBtn.addEventListener('click', () => this.setView('list'));

                const currentUrlParams = new URLSearchParams(window.location.search);
                const currentView = currentUrlParams.get('view');

                this.setView(currentView === 'grid' ? 'grid' : 'list');
            },
            setView(view) {
                this.container.classList.remove('view-grid', 'view-list');
                this.container.classList.add(`view-${view}`);

                this.gridBtn.classList.toggle('active', view === 'grid');
                this.listBtn.classList.toggle('active', view === 'list');

                if (this.viewInput) {
                   this.viewInput.value = view;
                }

                const paginationLinks = document.querySelectorAll('.pagination .page-link');
                paginationLinks.forEach(link => {
                    if (link.href) {
                        try {
                            const url = new URL(link.href);
                            url.searchParams.set('view', view);
                            link.href = url.toString();
                        } catch (e) {
                            // Ignore invalid URLs
                        }
                    }
                });
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

                this.showPreview = this.showPreview.bind(this);
                this.clearPreview = this.clearPreview.bind(this);

                this.fileInput.addEventListener('change', this.showPreview);
            },
            showPreview(event) {
                const file = event.target.files[0];
                if (!file) return;

                const previewHtml = `
                    <div class="upload-preview">
                        <img src="${URL.createObjectURL(file)}" alt="Preview" class="upload-preview-image">
                        <span class="upload-preview-info">${file.name}</span>
                        <button type="button" class="upload-preview-remove" aria-label="Remove attachment">&times;</button>
                    </div>
                `;

                this.previewContainer.innerHTML = previewHtml;
                this.previewContainer.classList.add('visible');

                this.previewContainer.querySelector('.upload-preview-remove').addEventListener('click', this.clearPreview);
            },
            clearPreview() {
                this.previewContainer.classList.remove('visible');
                this.previewContainer.innerHTML = '';
                this.fileInput.value = '';
            }
        },

        // Модуль: Загрузка домашнего задания на странице курса
        homeworkUpload: {
            init() {
                const uploadArea = document.querySelector('.file-upload-area');
                if (!uploadArea) return;

                const input = uploadArea.querySelector('input[type=file]');
                const p = uploadArea.querySelector('p');
                const defaultText = p.textContent;

                uploadArea.addEventListener('click', () => input.click());

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