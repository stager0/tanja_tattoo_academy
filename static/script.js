/* ====================================================================
   --- Tanja Tattoo Academy Scripts ---
   ==================================================================== */

document.addEventListener('DOMContentLoaded', function () {

    const app = {
        // --- 1. Initialize all functionalities ---
        init() {
            this.handlePreloader();
            this.handleHeaderScroll();
            this.handleMobileMenu();
            this.handleFaqAccordion();
            this.handleModal();
            this.handleScrollAnimations();
            this.handleScrollToTop();
            this.handleActiveNavOnScroll();
            this.updateCopyrightYear();
            this.handleSmoothScrollForModalButton();
            this.handlePricingToggle();
            this.handleCourseLessonsToggle();
        },

        // --- 2. Preloader ---
        handlePreloader() {
            const preloader = document.getElementById('preloader');
            if (preloader) {
                window.addEventListener('load', () => {
                    preloader.classList.add('hidden');
                });
            }
        },

        handleCourseLessonsToggle() {
            const toggleButton = document.querySelector('.lessons-toggle-btn');
            const navContainer = document.querySelector('.course-lessons-nav-mobile');

            if (toggleButton && navContainer) {
                toggleButton.addEventListener('click', () => {
                    const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';

                    navContainer.classList.toggle('active');
                    toggleButton.setAttribute('aria-expanded', !isExpanded);

                    // Меняем иконку (опционально)
                    const icon = toggleButton.querySelector('i');
                    if (icon) {
                        if (navContainer.classList.contains('active')) {
                            icon.classList.remove('fa-list');
                            icon.classList.add('fa-times'); // Или fa-chevron-up, fa-arrow-up
                        } else {
                            icon.classList.remove('fa-times');
                            icon.classList.add('fa-list'); // Или fa-chevron-down, fa-arrow-down
                        }
                    }
                });
            }
        },

        // --- 3. Header Scroll Effect & Parallax ---
        handleHeaderScroll() {
            const header = document.getElementById('main-header');
            const heroBg = document.querySelector('.hero-bg-parallax');
            if (header) {
                window.addEventListener('scroll', () => {
                    if (window.scrollY > 50) {
                        header.classList.add('scrolled');
                    } else {
                        header.classList.remove('scrolled');
                    }
                    if (heroBg) {
                        const offset = window.pageYOffset;
                        heroBg.style.transform = `translateY(${offset * 0.4}px)`;
                    }
                });
            }
        },

        // --- 4. Mobile Menu ---
        handleMobileMenu() {
            const menuToggle = document.getElementById('menu-toggle');
            const mainNav = document.getElementById('main-nav');
            if (menuToggle && mainNav) {
                menuToggle.addEventListener('click', () => {
                    const isActive = mainNav.classList.toggle('active');
                    menuToggle.classList.toggle('active');
                    menuToggle.setAttribute('aria-expanded', isActive);
                    document.body.style.overflow = isActive ? 'hidden' : '';
                });

                mainNav.querySelectorAll('a').forEach(link => {
                    link.addEventListener('click', () => {
                        if (mainNav.classList.contains('active')) {
                            mainNav.classList.remove('active');
                            menuToggle.classList.remove('active');
                            menuToggle.setAttribute('aria-expanded', 'false');
                            document.body.style.overflow = '';
                        }
                    });
                });
            }
        },

        // --- 5. FAQ Accordion ---
        handleFaqAccordion() {
            const faqItems = document.querySelectorAll('.faq-item');
            faqItems.forEach(item => {
                const question = item.querySelector('.faq-question');
                if (question) {
                    question.addEventListener('click', () => {
                        const answer = item.querySelector('.faq-answer');
                        const wasActive = item.classList.contains('active');

                        faqItems.forEach(i => {
                            i.classList.remove('active');
                            i.querySelector('.faq-answer').style.maxHeight = 0;
                        });

                        if (!wasActive) {
                            item.classList.add('active');
                            answer.style.maxHeight = answer.scrollHeight + 'px';
                        }
                    });
                }
            });
        },

        // --- 6. Modal Logic ---
        handleModal() {
            const modal = document.getElementById('lesson-modal');
            const closeModalBtn = document.getElementById('close-modal');
            const openFirstLessonBtn = document.getElementById('open-first-lesson');
            const playPreviewVideoBtn = document.getElementById('play-preview-video');
            const videoIframe = document.getElementById('video-iframe');
            const youtubeVideoId = 'dQw4w9WgXcQ'; // Placeholder video

            if (!modal) return;

            const openModal = () => {
                if (videoIframe) {
                    videoIframe.src = `https://www.youtube.com/embed/${youtubeVideoId}?autoplay=1&rel=0`;
                }
                modal.classList.add('visible');
                document.body.style.overflow = 'hidden';
            };

            const closeModal = () => {
                if (videoIframe) {
                    videoIframe.src = '';
                }
                modal.classList.remove('visible');
                document.body.style.overflow = '';
            };

            if (openFirstLessonBtn) openFirstLessonBtn.addEventListener('click', openModal);
            if (playPreviewVideoBtn) playPreviewVideoBtn.addEventListener('click', openModal);
            if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);

            modal.addEventListener('click', e => {
                if (e.target === modal) closeModal();
            });

            document.addEventListener('keydown', e => {
                if (e.key === 'Escape' && modal.classList.contains('visible')) closeModal();
            });

            this.modalInstance = {openModal, closeModal};
        },

        // --- 7. Smooth scrolling for tariff button inside modal ---
        handleSmoothScrollForModalButton() {
            const modalTariffBtn = document.querySelector('.modal-action-btn');
            if (modalTariffBtn) {
                modalTariffBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (this.modalInstance) {
                        this.modalInstance.closeModal();
                    }
                    setTimeout(() => {
                        const tariffsSection = document.getElementById('tariffs');
                        if (tariffsSection) {
                            tariffsSection.scrollIntoView({behavior: 'smooth'});
                        }
                    }, 300);
                });
            }
        },

        // --- 8. Pricing Toggle for Tariffs --- NEW FUNCTION ---
        handlePricingToggle() {
            const pricingSwitch = document.getElementById('pricing-switch');
            const tariffsSection = document.getElementById('tariffs');
            if (pricingSwitch && tariffsSection) {
                pricingSwitch.addEventListener('change', () => {
                    if (pricingSwitch.checked) {
                        tariffsSection.classList.add('parts-active');
                    } else {
                        tariffsSection.classList.remove('parts-active');
                    }
                });
            }
        },

        // --- 9. Scroll Reveal Animation ---
        handleScrollAnimations() {
            const revealElements = document.querySelectorAll('.animate-on-scroll');
            if (revealElements.length > 0) {
                const revealObserver = new IntersectionObserver((entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const delay = entry.target.dataset.delay || 0;
                            setTimeout(() => {
                                entry.target.classList.add('is-visible');
                            }, delay);
                            observer.unobserve(entry.target);
                        }
                    });
                }, {threshold: 0.1});

                revealElements.forEach(el => revealObserver.observe(el));
            }
        },

        // --- 10. Scroll to Top Button ---
        handleScrollToTop() {
            const scrollToTopBtn = document.getElementById('scroll-to-top');
            if (scrollToTopBtn) {
                window.addEventListener('scroll', () => {
                    if (window.scrollY > 300) {
                        scrollToTopBtn.classList.add('visible');
                    } else {
                        scrollToTopBtn.classList.remove('visible');
                    }
                });
                scrollToTopBtn.addEventListener('click', e => {
                    e.preventDefault();
                    window.scrollTo({top: 0, behavior: 'smooth'});
                });
            }
        },

        // --- 11. Active Navigation Link on Scroll ---
        handleActiveNavOnScroll() {
            const sections = document.querySelectorAll('section[id]');
            const navLinks = document.querySelectorAll('.main-nav a');
            if (sections.length > 0 && navLinks.length > 0) {
                window.addEventListener('scroll', () => {
                    let current = '';
                    sections.forEach(section => {
                        const sectionTop = section.offsetTop;
                        const sectionHeight = section.clientHeight;
                        if (pageYOffset >= sectionTop - sectionHeight / 3) {
                            current = section.getAttribute('id');
                        }
                    });

                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href').substring(1) === current) {
                            link.classList.add('active');
                        }
                    });
                });
            }
        },

        // --- 12. Update Copyright Year ---
        updateCopyrightYear() {
            const yearSpan = document.getElementById('current-year');
            if (yearSpan) {
                yearSpan.textContent = new Date().getFullYear();
            }
        }
    };

    app.init();
});