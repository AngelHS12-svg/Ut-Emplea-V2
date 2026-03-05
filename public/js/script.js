let rolSeleccionado = "";

document.addEventListener("DOMContentLoaded", function(){

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

loginForm.addEventListener("submit", function(e){

    const rol = inputRol.value;

    if(!rol){
        e.preventDefault();
        alert("Debes seleccionar un tipo de usuario primero");
    }

});

     // ===== BOTON REGISTRO =====
    if(registerBtn){
    registerBtn.addEventListener("click", function(e){

        e.preventDefault();

        const rol = localStorage.getItem("rol");

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
    option.addEventListener("click", () => {

        const rol = option.dataset.role;

        // poner rol en el input hidden
        inputRol.value = rol;

        // mostrar rol en pantalla
        roleIndicator.innerText = "Rol: " + rol.toUpperCase();

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
