// static/js/script.js

document.addEventListener("DOMContentLoaded",()=>{

    console.log("WISTFUL Loaded");

    const firstTab=document.querySelector(".nav-btn");

    if(firstTab){

        showPage("ocrPage",firstTab);

    }

});