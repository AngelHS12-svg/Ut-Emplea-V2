document.addEventListener("DOMContentLoaded", function(){

    // ===== ELEMENTOS =====
    const openLoginBtns = document.querySelectorAll(".open-login");
    const modalUserType = document.getElementById("modalUserType");
    const modalLogin = document.getElementById("modalLogin");
    const closeUserType = document.getElementById("closeUserType");
    const closeLogin = document.getElementById("closeLogin");
    const roleIndicator = document.getElementById("roleIndicator");
    const userOptions = document.querySelectorAll(".user-option");

    // ===== ABRIR PRIMER MODAL =====
    openLoginBtns.forEach(btn => {
    btn.addEventListener("click", function(e){
        e.preventDefault();
        modalUserType.style.display = "flex";
    });
});

    // ===== CERRAR PRIMER MODAL =====
    if(closeUserType){
        closeUserType.addEventListener("click", function(){
            modalUserType.style.display = "none";
        });
    }

    // ===== CERRAR LOGIN =====
    if(closeLogin){
        closeLogin.addEventListener("click", function(){
            modalLogin.style.display = "none";
        });
    }

    // ===== SELECCIÓN DE ROL =====
    userOptions.forEach(option => {

        option.addEventListener("click", function(){

            const role = this.dataset.role;

            let roleText = "";

            if(role === "admin") roleText = "ADMINISTRADOR";
            if(role === "empresa") roleText = "EMPRESA";
            if(role === "candidato") roleText = "CANDIDATO";

            roleIndicator.textContent = "Iniciando como: " + roleText;

            modalUserType.style.display = "none";
            modalLogin.style.display = "flex";

        });

    });

    // ===== CLICK FUERA =====
    window.addEventListener("click", function(e){

        if(e.target === modalUserType){
            modalUserType.style.display = "none";
        }

        if(e.target === modalLogin){
            modalLogin.style.display = "none";
        }

    });

});
