// ================================
// OCR GPA Animation
// ================================

const ocrCircle = document.getElementById("ocrProgress");
const ocrValue = document.getElementById("ocrAnimatedValue");
const ocrAnimation = document.getElementById("ocrAnimation");

const ocrRadius = 110;
const ocrCircumference = 2 * Math.PI * ocrRadius;

ocrCircle.style.strokeDasharray = ocrCircumference;
ocrCircle.style.strokeDashoffset = ocrCircumference;

function playOCRAnimation(gpa){

    ocrAnimation.classList.remove("hidden");

    ocrCircle.style.strokeDashoffset = ocrCircumference;

    let current = 0;

    const target = Math.min(gpa / 10, 1);

    const timer = setInterval(()=>{

        current += 0.01;

        if(current >= target){

            current = target;

            clearInterval(timer);

        }

        const value = gpa * (current / target);

        ocrValue.innerHTML = value.toFixed(3);

        ocrCircle.style.strokeDashoffset =
            ocrCircumference -
            (ocrCircumference * current);

    },15);

}