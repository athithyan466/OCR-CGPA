// =====================================
// ATHVIK EVENTS
// =====================================

// WEBSITE OPENED
function athvikWelcome(){

    //clearAthvik();

    athvikSay(randomMessage(ATHVIK.welcome));

    athvikSay(randomMessage(ATHVIK.welcome));

    athvikSay(randomMessage(ATHVIK.idle));

}

// =====================================
// USER IDLE
// =====================================

let idleTimer;

function startIdleTimer(){

    clearTimeout(idleTimer);

    idleTimer=setTimeout(()=>{

        athvikSay(randomMessage(ATHVIK.idle));

    },15000);

}

document.addEventListener("mousemove",startIdleTimer);

document.addEventListener("keydown",startIdleTimer);

startIdleTimer();

// =====================================
// IMAGE SELECTED
// =====================================

function athvikImageSelected(){

    clearAthvik();

    athvikSay(randomMessage(ATHVIK.upload));

    athvikSay(randomMessage(ATHVIK.ocrStart));

}

// =====================================
// OCR START
// =====================================

function athvikOCRStarted(){

    clearAthvik();

    athvikSay(randomMessage(ATHVIK.ocrStart));

    athvikSay(randomMessage(ATHVIK.ocrProcessing));

    athvikSay(randomMessage(ATHVIK.ocrProcessing));

}

// =====================================
// OCR FAILED
// =====================================

function athvikOCRFailed(){

    clearAthvik();

    athvikSay(randomMessage(ATHVIK.ocrFailed));

}

// =====================================
// OCR SUCCESS
// =====================================
function athvikOCRSuccess(){

    clearAthvik();

    athvikSay(randomMessage(ATHVIK.ocrSuccess));

    athvikSay(
        "🚨 <b style='color:#d90429'>STOP!</b><br><br>" +
        "Before you press <b>Calculate GPA</b>, verify every subject, credit and grade carefully.<br><br>" +
        "OCR is fast, but it can occasionally misread text. One mistake can change your GPA.",
        0
    );

}

// =====================================
// USER EDITS TABLE
// =====================================

function athvikEdited(){

    athvikSay(randomMessage(ATHVIK.edit));

}

// =====================================
// MISSING GRADE
// =====================================

function athvikMissingGrade(){

    athvikSay(randomMessage(ATHVIK.missingGrade));

}

// =====================================
// INVALID GRADE
// =====================================

function athvikInvalidGrade(){

    athvikSay(randomMessage(ATHVIK.invalidGrade));

}

// =====================================
// GPA
// =====================================

function athvikCalculate(){

    clearAthvik();

    athvikSay(randomMessage(ATHVIK.calculate));

}

function athvikResult(gpa){

    if(gpa>=9){

        athvikSay(randomMessage(ATHVIK.gpaHigh));

    }

    else if(gpa>=7){

        athvikSay(randomMessage(ATHVIK.gpaAverage));

    }

    else{

        athvikSay(randomMessage(ATHVIK.gpaLow));

    }

}

// =====================================
// CGPA
// =====================================

function athvikCGPA(){

    athvikSay(randomMessage(ATHVIK.cgpa));

}

// =====================================
// MANUAL ENTRY
// =====================================

function athvikManual(){

    athvikSay(randomMessage(ATHVIK.manual));

}



// =====================================
// RANDOM JOKE
// =====================================

setInterval(()=>{

    if(Math.random()<0.25){

        athvikSay(randomMessage(ATHVIK.jokes));

    }

},60000);

// =====================================

window.onload=()=>{

    setTimeout(()=>{

        athvikWelcome();

    },1000);

};