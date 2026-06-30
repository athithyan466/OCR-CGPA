
const extractBtn = document.getElementById("extractBtn");

extractBtn.addEventListener("click", async function () {
    athvikImageSelected();

    const fileInput = document.getElementById("resultImage");

    if (fileInput.files.length === 0) {

    athvikSay(randomMessage(ATHVIK.wrongImage));

    alert("Please choose an image.");

    return;

}

    const formData = new FormData();

    formData.append("image", fileInput.files[0]);

    document.getElementById("loading").classList.remove("hidden");
    athvikOCRStarted();

    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        console.log(data);

        populateOCRTable(data.subjects);

        athvikOCRSuccess();

    } catch (error) {
        athvikOCRFailed();

        console.error(error);

        alert("OCR Failed.");

    }

    document.getElementById("loading").classList.add("hidden");

});

function populateOCRTable(subjects) {

    const tbody = document.querySelector("#ocrTable tbody");

    tbody.innerHTML = "";

    subjects.forEach(subject => {

        let row = document.createElement("tr");

        row.innerHTML = `
            <td>${subject.code}</td>

            <td>${subject.name}</td>

            <td>
                <input
                    type="number"
                    value="${subject.credit}"
                    class="credit">
            </td>

            <td>
                <select class="grade">

                    <option ${subject.grade=="O"?"selected":""}>O</option>

                    <option ${subject.grade=="A+"?"selected":""}>A+</option>

                    <option ${subject.grade=="A"?"selected":""}>A</option>

                    <option ${subject.grade=="B+"?"selected":""}>B+</option>

                    <option ${subject.grade=="B"?"selected":""}>B</option>

                    <option ${subject.grade=="C"?"selected":""}>C</option>

                    <option ${subject.grade=="U"?"selected":""}>U</option>

                </select>

            </td>
        `;
        row.querySelector(".credit").addEventListener("change", function(){

    athvikEdited();

});
row.querySelector(".grade").addEventListener("change", function(){

    athvikEdited();

});

        tbody.appendChild(row);

    });

    document.getElementById("verificationSection").classList.remove("hidden");
    athvikSay(randomMessage(ATHVIK.verify));

}

document.getElementById("calculateOCR").addEventListener("click", function () {
    athvikCalculate();

    const rows = document.querySelectorAll("#ocrTable tbody tr");

    let totalCredits = 0;
    let totalPoints = 0;

    const gradeMap = {
        "O": 10,
        "A+": 9,
        "A": 8,
        "B+": 7,
        "B": 6,
        "C": 5,
        "U": 0
    };

    rows.forEach(row => {

        const credit = parseFloat(row.querySelector(".credit").value);
        const grade = row.querySelector(".grade").value;

        if (grade !== "U") {
            totalCredits += credit;
            totalPoints += credit * gradeMap[grade];
        }

    });

    if (totalCredits === 0) {

        document.getElementById("ocrResult").innerHTML = "ALL SUBJECTS FAILED";
        athvikSay("💀 Every subject failed... that's one way to avoid calculations. Let's hope the next semester treats you better.");

    } else {

        const gpa = totalPoints / totalCredits;
    
        athvikResult(gpa);
        

        document.getElementById("ocrResult").innerHTML =
            "GPA = " + gpa.toFixed(3);
        playOCRAnimation(gpa);

    }


});
