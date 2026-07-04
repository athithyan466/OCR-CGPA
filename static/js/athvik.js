// ==============================
// ATHVIK MAIN ENGINE
// ==============================

const athvik = document.getElementById("athvik");
const athvikBubble = document.getElementById("athvikBubble");
const athvikText = document.getElementById("athvikText");

let athvikTimeout = null;
let athvikQueue = [];
let athvikBusy = false;

// ==============================
// Restore Saved Position
// ==============================

window.addEventListener("load", () => {

    const x = localStorage.getItem("athvikX");
    const y = localStorage.getItem("athvikY");

    if(x && y){

        athvik.style.left = x + "px";
        athvik.style.top = y + "px";

        athvik.style.right = "auto";
        athvik.style.bottom = "auto";

    }

});

// ==============================
// Drag Chatbot
// ==============================

let dragging = false;

let offsetX = 0;
let offsetY = 0;

athvik.addEventListener("pointerdown", (e)=>{

    dragging = true;

    const rect = athvik.getBoundingClientRect();

    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;

    athvik.setPointerCapture(e.pointerId);

});

athvik.addEventListener("pointermove",(e)=>{

    if(!dragging) return;

    let x = e.clientX - offsetX;
    let y = e.clientY - offsetY;

    x = Math.max(0, Math.min(window.innerWidth - athvik.offsetWidth, x));
    y = Math.max(0, Math.min(window.innerHeight - athvik.offsetHeight, y));

    athvik.style.left = x + "px";
    athvik.style.top = y + "px";

    athvik.style.right = "auto";
    athvik.style.bottom = "auto";

});

athvik.addEventListener("pointerup",(e)=>{

    dragging = false;

    athvik.releasePointerCapture(e.pointerId);

    localStorage.setItem("athvikX", parseInt(athvik.style.left));
    localStorage.setItem("athvikY", parseInt(athvik.style.top));

});

// ==============================
// SHOW MESSAGE
// ==============================

function showAthvikMessage(message, duration = 4000) {

    clearTimeout(athvikTimeout);

    athvikText.innerHTML = message;

    athvikBubble.style.display = "block";

    athvikBubble.classList.remove("show");

    void athvikBubble.offsetWidth;

    athvikBubble.classList.add("show");

    if(duration === 0){

        athvikBusy = true;

        return;

    }

    athvikTimeout = setTimeout(()=>{

        athvikBubble.classList.remove("show");

        setTimeout(()=>{

            athvikBubble.style.display = "none";

            athvikBusy = false;

            playQueue();

        },300);

    },duration);

}

// ==============================
// Queue
// ==============================

function playQueue(){

    if(athvikBusy) return;

    if(athvikQueue.length===0) return;

    athvikBusy=true;

    let msg = athvikQueue.shift();

    showAthvikMessage(msg.text,msg.time);

}

function athvikSay(message,duration=4000){

    athvikQueue.push({

        text:message,

        time:duration

    });

    playQueue();

}

function randomMessage(list){

    return list[Math.floor(Math.random()*list.length)];

}

// ==============================
// Clear
// ==============================

function clearAthvik(){

    clearTimeout(athvikTimeout);

    athvikQueue=[];

    athvikBusy=false;

    athvikBubble.classList.remove("show");

    athvikBubble.style.display="none";

}
// ==============================
// MOBILE FRIENDLY DRAG
// ==============================

let isDragging = false;

let startX = 0;
let startY = 0;

function dragStart(e){

    isDragging = true;

    const touch = e.touches ? e.touches[0] : e;

    const rect = athvik.getBoundingClientRect();

    startX = touch.clientX - rect.left;
    startY = touch.clientY - rect.top;

}

function dragMove(e){

    if(!isDragging) return;

    e.preventDefault();

    const touch = e.touches ? e.touches[0] : e;

    let x = touch.clientX - startX;
    let y = touch.clientY - startY;

    x = Math.max(0, Math.min(window.innerWidth - athvik.offsetWidth, x));
    y = Math.max(0, Math.min(window.innerHeight - athvik.offsetHeight, y));

    athvik.style.left = x + "px";
    athvik.style.top = y + "px";

    athvik.style.right = "auto";
    athvik.style.bottom = "auto";

}

function dragEnd(){

    if(!isDragging) return;

    isDragging = false;

    localStorage.setItem("athvikX", parseInt(athvik.style.left));
    localStorage.setItem("athvikY", parseInt(athvik.style.top));

}

athvik.addEventListener("touchstart", dragStart, { passive:false });
document.addEventListener("touchmove", dragMove, { passive:false });
document.addEventListener("touchend", dragEnd);

athvik.addEventListener("mousedown", dragStart);
document.addEventListener("mousemove", dragMove);
document.addEventListener("mouseup", dragEnd);