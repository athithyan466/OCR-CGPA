// ==============================
// ATHVIK MAIN ENGINE
// ==============================

const athvikBubble = document.getElementById("athvikBubble");
const athvikText = document.getElementById("athvikText");

let athvikTimeout = null;
let athvikQueue = [];
let athvikBusy = false;

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

    // Stay forever if duration is 0
   // Stay forever until manually cleared
if(duration === 0){

    athvikBusy = true;

    return;

}
    athvikTimeout = setTimeout(()=>{

        athvikBubble.classList.remove("show");

        setTimeout(()=>{

            athvikBubble.style.display="none";

            athvikBusy=false;

            playQueue();

        },300);

    },duration);

}
// ==============================
// ADD MESSAGE TO QUEUE
// ==============================



// ==============================
// PLAY QUEUE
// ==============================

function playQueue(){

    if(athvikBusy)
        return;

    if(athvikQueue.length===0)
        return;

    athvikBusy=true;

    let msg=athvikQueue.shift();

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
// CLEAR MESSAGE
// ==============================

function clearAthvik(){

    clearTimeout(athvikTimeout);

    athvikQueue = [];

    athvikBusy = false;

    athvikBubble.classList.remove("show");

    athvikBubble.style.display = "none";

}