let rolSeleccionado = "";

document.addEventListener("DOMContentLoaded", function () {

    // ===== STICKY NAVBAR LOGIC =====
    const mainNavbar = document.getElementById("mainNavbar");
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const navLinks = document.querySelector(".nav-links");

    if (mainNavbar) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 50) {
                mainNavbar.classList.add("scrolled");
            } else {
                mainNavbar.classList.remove("scrolled");
            }
        });
    }

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener("click", () => {
            navLinks.classList.toggle("active");
            mobileMenuBtn.classList.toggle("active");
        });
        
        // Cerrar al hacer click en un link
        document.querySelectorAll(".nav-item").forEach(link => {
            link.addEventListener("click", () => {
                navLinks.classList.remove("active");
                mobileMenuBtn.classList.remove("active");
            });
        });
    }

    // ===== ELEMENTOS =====
    const openLoginBtns = document.querySelectorAll(".open-login");
    const modalUserType = document.getElementById("modalUserType");
    const modalLogin = document.getElementById("modalLogin");
    const closeUserType = document.getElementById("closeUserType");
    const closeLogin = document.getElementById("closeLogin");
    const roleIndicator = document.getElementById("roleIndicator");
    const userOptions = document.querySelectorAll(".user-option");
    const registerBtn = document.querySelector(".register-btn");
    const inputRol = document.getElementById("inputRol");

    // El CTA del contenido se abre después de desplazar la página en móvil.
    // Mantener ese punto de lectura y centrar sus dos pasos en el área visible.
    let heroLogin = null;
    function syncHeroViewport() {
        if (!heroLogin) return;
        const viewport = window.visualViewport;
        [modalUserType, modalLogin].forEach(modal => {
            modal.style.setProperty('--hero-modal-top', (viewport ? viewport.offsetTop : 0) + 'px');
            modal.style.setProperty('--hero-modal-left', (viewport ? viewport.offsetLeft : 0) + 'px');
            modal.style.setProperty('--hero-modal-height', (viewport ? viewport.height : window.innerHeight) + 'px');
            modal.style.setProperty('--hero-modal-width', Math.min(
                viewport ? viewport.width : window.innerWidth, document.documentElement.clientWidth) + 'px');
        });
    }

    function openHeroLogin(opener) {
        const properties = ['position', 'top', 'left', 'right', 'width', 'overflow'];
        const pageWidth = document.documentElement.clientWidth;
        heroLogin = { opener, x: window.scrollX, y: window.scrollY,
            styles: Object.fromEntries(properties.map(key => [key, document.body.style[key]])) };
        Object.assign(document.body.style, { position: 'fixed', top: -heroLogin.y + 'px',
            left: '0', right: '0', width: pageWidth + 'px', overflow: 'hidden' });
        [modalUserType, modalLogin].forEach(modal => modal.classList.add('hero-login-modal'));
        syncHeroViewport();
    }

    function focusHeroModal(modal) {
        if (!heroLogin) return;
        const panel = modal.querySelector('.modal-content');
        panel.tabIndex = -1;
        panel.focus({ preventScroll: true });
    }

    function closeHeroLogin() {
        if (!heroLogin) return;
        const previous = heroLogin;
        heroLogin = null;
        [modalUserType, modalLogin].forEach(modal => {
            modal.classList.remove('hero-login-modal');
            ['top', 'left', 'height', 'width'].forEach(key => modal.style.removeProperty('--hero-modal-' + key));
        });
        Object.assign(document.body.style, previous.styles);
        previous.opener.focus({ preventScroll: true });
        window.scrollTo(previous.x, previous.y);
    }

    window.addEventListener('resize', syncHeroViewport);
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', syncHeroViewport);
        window.visualViewport.addEventListener('scroll', syncHeroViewport);
    }
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && heroLogin) {
            modalUserType.style.display = 'none';
            modalLogin.style.display = 'none';
            closeHeroLogin();
        }
    });

    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", function (e) {

        const rol = inputRol.value;

        if (!rol) {
            e.preventDefault();
            alert("Debes seleccionar un tipo de usuario primero");
        }

    });

    // ===== BOTON REGISTRO =====
    if (registerBtn) {
        registerBtn.addEventListener("click", function (e) {

            e.preventDefault();

            const rol = inputRol.value;

            if (rol === "empresa") {
                window.location.href = "/registro-empresa";
            }
            else if (rol === "candidato") {
                window.location.href = "/registro-candidato";
            }
            else {
                alert("Primero selecciona el tipo de usuario");
            }

        });
    }

    // ===== ABRIR PRIMER MODAL =====
    openLoginBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            if (btn.classList.contains('cta-button') && window.matchMedia('(max-width: 768px)').matches) {
                openHeroLogin(btn);
            }
            modalUserType.style.display = "flex";
            focusHeroModal(modalUserType);
        });
    });

    // ===== CERRAR PRIMER MODAL =====
    if (closeUserType) {
        closeUserType.addEventListener("click", function () {
            modalUserType.style.display = "none";
            closeHeroLogin();
        });
    }

    // ===== CERRAR LOGIN =====
    if (closeLogin) {
        closeLogin.addEventListener("click", function () {
            modalLogin.style.display = "none";
            closeHeroLogin();
        });
    }

    // ===== SELECCIÓN DE ROL =====
    userOptions.forEach(option => {
        option.addEventListener("click", () => {

            const rol = option.dataset.role;

            // poner rol en el input hidden
            inputRol.value = rol;

            // mostrar rol en pantalla
            roleIndicator.innerText = "Rol: " + rol.toUpperCase();

            // Ocultar botón de registro si es administrador
            const registerBtnModal = document.getElementById("registerBtnModal");
            if (registerBtnModal) {
                if (rol === "admin" || rol === "administrador") {
                    registerBtnModal.style.display = "none";
                } else {
                    registerBtnModal.style.display = "block";
                    registerBtnModal.style.margin = "0 auto";
                }
            }

            modalUserType.style.display = "none";
            modalLogin.style.display = "flex";
            syncHeroViewport();
            focusHeroModal(modalLogin);
        });
    });

    // ===== CLICK FUERA =====
    window.addEventListener("click", function (e) {

        if (e.target === modalUserType) {
            modalUserType.style.display = "none";
            closeHeroLogin();
        }

        if (e.target === modalLogin) {
            modalLogin.style.display = "none";
            closeHeroLogin();
        }

    });

    // Regreso desde la recuperación de contraseña.
    if (new URLSearchParams(window.location.search).get('login') === '1') {
        if (/^[1-9][0-9]{0,9}$/.test(document.getElementById('loginVacanteId').value)) {
            inputRol.value = 'candidato';
            roleIndicator.textContent = 'Rol: CANDIDATO';
            modalLogin.style.display = 'flex';
        } else {
            modalUserType.style.display = 'flex';
        }
    }

    // ===== SCROLL 3D ANIMATION FOR HERO (suavizado) =====
    const hero3DWrapper = document.getElementById("hero3DWrapper");
    if (hero3DWrapper) {
        let lastScrollY = 0;
        let ticking = false;

        function updateHeroParallax() {
            const scrollY = lastScrollY;
            const maxScroll = 700;
            
            let progress = Math.min(scrollY / maxScroll, 1);

            // Valores reducidos para evitar temblor
            const scale = 1 + (progress * 0.12);
            const transY = scrollY * 0.25;
            const rotX = progress * 4;
            
            hero3DWrapper.style.transform = `translate3d(0, ${transY}px, 0) scale(${scale}) rotateX(${-rotX}deg)`;
            ticking = false;
        }

        window.addEventListener("scroll", () => {
            lastScrollY = window.scrollY;
            if (!ticking) {
                requestAnimationFrame(updateHeroParallax);
                ticking = true;
            }
        }, { passive: true });
    }

    // ===== TYPEWRITER EFFECT FOR HERO TITLE =====
    const heroTitle = document.querySelector(".hero-title");
    if (heroTitle) {
        const text = "TalentLink";
        heroTitle.innerHTML = "";
        heroTitle.classList.add("typewriter-caret");
        
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                heroTitle.innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, 120); // Velocidad natural del tipeo
            } else {
                // Remove caret after a few seconds
                setTimeout(() => {
                    heroTitle.classList.remove("typewriter-caret");
                }, 4000);
            }
        }
        
        // Empezar tras un pequeño delay para impacto visual
        setTimeout(typeWriter, 600);
    }

});
