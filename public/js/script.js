let rolSeleccionado = "";

document.addEventListener("DOMContentLoaded", function () {

    // ===== STICKY NAVBAR LOGIC =====
    const mainNavbar = document.getElementById("mainNavbar");
    if (mainNavbar) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 50) {
                mainNavbar.classList.add("scrolled");
            } else {
                mainNavbar.classList.remove("scrolled");
            }
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
            modalUserType.style.display = "flex";
        });
    });

    // ===== CERRAR PRIMER MODAL =====
    if (closeUserType) {
        closeUserType.addEventListener("click", function () {
            modalUserType.style.display = "none";
        });
    }

    // ===== CERRAR LOGIN =====
    if (closeLogin) {
        closeLogin.addEventListener("click", function () {
            modalLogin.style.display = "none";
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
        });
    });

    // ===== CLICK FUERA =====
    window.addEventListener("click", function (e) {

        if (e.target === modalUserType) {
            modalUserType.style.display = "none";
        }

        if (e.target === modalLogin) {
            modalLogin.style.display = "none";
        }

        // Close forgot password modal on outside click
        const modalForgot = document.getElementById("modalForgot");
        if (modalForgot && e.target === modalForgot) {
            modalForgot.style.display = "none";
        }
    });

    // ===== FORGOT PASSWORD MODAL =====
    const openForgotBtn = document.getElementById("openForgotPassword");
    const modalForgot = document.getElementById("modalForgot");
    const closeForgot = document.getElementById("closeForgot");

    if (openForgotBtn && modalForgot) {
        openForgotBtn.addEventListener("click", function(e) {
            e.preventDefault();
            modalLogin.style.display = "none";
            modalForgot.style.display = "flex";
        });
    }
    if (closeForgot && modalForgot) {
        closeForgot.addEventListener("click", function() {
            modalForgot.style.display = "none";
        });
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
        const text = "UT Oriental Emplea";
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
