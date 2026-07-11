// manualVerification.js

document.addEventListener("DOMContentLoaded", () => {

    const table = document.querySelector("#ocrTable tbody");

    table.addEventListener("click", function (e) {

        if (!e.target.classList.contains("removeRow"))
            return;

        const row = e.target.closest("tr");

        row.remove();

        athvikSay("Subject removed.");

    });

});
