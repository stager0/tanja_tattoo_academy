/* ====================================================================
   --- GodArt Piercing School Scripts
   ==================================================================== */

document.addEventListener('DOMContentLoaded', function () {

    const app = {
        // --- 1. Initialize all functionalities ---
        init() {
            this.handleHeaderScroll();
            this.handleMobileMenu();
            this.handleFaqAccordion();
            this.handleModals();
            this.handleScrollAnimations();
            this.handleScrollToTop();
            this.handleActiveNavOnScroll();
            this.updateCopyrightYear();
            this.handleSmoothScrollForModalButton();
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
        // --- 6. Generic Modal Logic ---
        handleModals() {
            const modalTriggers = document.querySelectorAll('.modal-trigger');
            const videoIframe = document.getElementById('video-iframe');

            const landingData = document.getElementById('landing-data');
            const youtubeVideoId = landingData ? landingData.dataset.videoId : 'dQw4w9WgXcQ';

            let currentOpenModal = null;

            const openModal = (modal) => {
                if (!modal) return;
                modal.classList.add('visible');
                document.body.style.overflow = 'hidden';
                currentOpenModal = modal;

                if (modal.id === 'lesson-modal' && videoIframe) {
                    const videoUrl = `https://www.youtube.com/embed/${youtubeVideoId}?autoplay=1&rel=0`;
                    videoIframe.setAttribute('data-src', videoUrl);
                    if (window.Cookiebot && Cookiebot.consented) {
                        videoIframe.setAttribute('src', videoUrl);
                    }
                }
            };

            const closeModal = () => {
                if (!currentOpenModal) return;

                if (currentOpenModal.id === 'lesson-modal' && videoIframe) {
                    videoIframe.src = '';
                    videoIframe.setAttribute('data-src', '');
                }

                currentOpenModal.classList.remove('visible');
                document.body.style.overflow = '';
                currentOpenModal = null;
            };

            modalTriggers.forEach(trigger => {
                trigger.addEventListener('click', (e) => {
                    e.preventDefault();
                    const modalId = trigger.dataset.modalTarget;
                    const modal = document.getElementById(modalId);
                    openModal(modal);
                });
            });

            document.querySelectorAll('.modal').forEach(modal => {
                modal.addEventListener('click', e => {
                    if (e.target === modal) {
                        closeModal();
                    }
                });
                const closeModalBtn = modal.querySelector('.close-modal');
                if (closeModalBtn) {
                    closeModalBtn.addEventListener('click', closeModal);
                }
            });

            document.addEventListener('keydown', e => {
                if (e.key === 'Escape' && currentOpenModal) {
                    closeModal();
                }
            });

            this.closeModal = closeModal;
        },

        // --- 7. Smooth scrolling for tariff button inside modal ---
        handleSmoothScrollForModalButton() {
            const modalTariffBtn = document.querySelector('.modal-action-btn');
            if (modalTariffBtn) {
                modalTariffBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (this.closeModal) {
                        this.closeModal();
                    }
                    setTimeout(() => {
                        const tariffsSection = document.getElementById('tariffs');
                        if (tariffsSection) {
                            tariffsSection.scrollIntoView({ behavior: 'smooth' });
                        }
                    }, 300);
                });
            }
        },

        // --- 8. Scroll Reveal Animation ---
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
                }, { threshold: 0.1 });
                revealElements.forEach(el => revealObserver.observe(el));
            }
        },

        // --- 9. Scroll to Top Button ---
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
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            }
        },

        // --- 10. Active Navigation Link on Scroll ---
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

        // --- 11. Update Copyright Year ---
        updateCopyrightYear() {
            const yearSpan = document.getElementById('current-year');
            if (yearSpan) {
                yearSpan.textContent = new Date().getFullYear();
            }
        }
    };
    app.init();
});