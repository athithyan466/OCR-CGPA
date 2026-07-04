// static/js/navigation.js

function showPage(pageId, button){

    document.querySelectorAll(".page").forEach(page=>{

        page.classList.remove("active");

    });

    document.querySelectorAll(".nav-btn").forEach(btn=>{

        btn.classList.remove("active");

    });

    document.getElementById(pageId).classList.add("active");

    button.classList.add("active");

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

}
