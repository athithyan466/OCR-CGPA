var semesterCount = 0;
var lastSemesterRow = null;
var previousCGPA = "";
function addSemester(){
semesterCount++;
lastSemesterRow=document.getElementById("cgpaTable").insertRow();
lastSemesterRow.innerHTML="<td>SEMESTER "+semesterCount+"</td><td><input type='number' step='0.001' id='gpa"+semesterCount+"'></td><td><input type='number' id='credit"+semesterCount+"'></td>";
}

function undoSemester(){
if(lastSemesterRow){
document.getElementById("cgpaTable").deleteRow(lastSemesterRow.rowIndex);
semesterCount--;
lastSemesterRow=null;
}
}
function generateSemesterInputs(){

let count = document.getElementById("semesterSelect").value;

let table = document.getElementById("cgpaTable");

table.innerHTML = `
<tr>
<th>SEMESTER</th>
<th>GPA</th>
</tr>
`;

semesterCount = parseInt(count);

for(let i=1; i<=count; i++){

let row = table.insertRow();

row.innerHTML = `
<td>SEMESTER ${i}</td>
<td><input type="number" step="0.001" id="gpa${i}"></td>
`;

}
}


function calculateCGPA(){
    

previousCGPA=document.getElementById("combinedResult").innerHTML;

let totalWeighted=0;
let totalCredits=0;

for(let i=1;i<=semesterCount;i++){

let g=document.getElementById("gpa"+i);

if(g){

let gv=parseFloat(g.value);

let cv=24; // Fixed credits

if(!isNaN(gv)){

totalWeighted += gv * cv;
totalCredits += cv;

}

}

}

if(totalCredits===0){

document.getElementById("combinedResult").innerHTML="PLEASE ENTER VALID DATA!";
return;

}

let cgpa=totalWeighted/totalCredits;

document.getElementById("combinedResult").innerHTML=
"YOUR COMBINED CGPA IS: " + cgpa.toFixed(2);

}

function undoCGPA(){
document.getElementById("combinedResult").innerHTML=previousCGPA;

athvikCGPA();
}
