var table = document.getElementById("table");
var lastSubjectRow = null;
function handleRegulation(){
  let reg = document.getElementById("regulation").value;
  let deptSelect = document.getElementById("dept");

  // Reset UI
  deptSelect.innerHTML = '<option value="">SELECT DEPARTMENT</option>';
  document.getElementById("sem").value="";
  document.getElementById("sem").disabled=true;

  resetTable();
  table.classList.add("hidden");
  document.getElementById("gpaButtons").classList.add("hidden");
  document.getElementById("result").innerHTML="";

  // 🔴 Dynamically load only available departments
  if(subjectsData[reg]){
    let depts = Object.keys(subjectsData[reg]);

    depts.forEach(d=>{
      let option = document.createElement("option");
      option.value = d;
      option.textContent = (d === "AIDS") ? "AI & DS" :
                           (d === "BME") ? "BIOMEDICAL" : d;
      deptSelect.appendChild(option);
    });
  }
}
var semesterCount=0;
var lastSubjectRow=null;
var lastSemesterRow=null;
var previousGPA="";
var previousCGPA="";

function showCGPASection(){
document.getElementById("cgpaSection").classList.remove("hidden");
}

function handleDepartment(){
athvikManual();


var dept=document.getElementById("dept").value;
var sem=document.getElementById("sem");

sem.value="";
resetTable();
table.classList.add("hidden");
document.getElementById("gpaButtons").classList.add("hidden");
document.getElementById("result").innerHTML="";

if(dept===""){
sem.disabled=true;
}else{
sem.disabled=false;
}
}


function resetTable(){
table.innerHTML="<tr><th>SEM</th><th>CODE</th><th>SUBJECT</th><th>CREDITS</th><th>GRADE</th></tr>";
}

function previousSemester(){
var sem=document.getElementById("sem");
if(sem.value>1){
sem.value=parseInt(sem.value)-1;
loadSubjects();
}
}

function loadSubjects(){
  var dept = document.getElementById("dept").value;
  var sem = document.getElementById("sem").value;
  var reg = document.getElementById("regulation").value;

  if(dept==="" || sem==="" || reg===""){
    table.classList.add("hidden");
    return;
  }

  resetTable();
  table.classList.remove("hidden");
  document.getElementById("gpaButtons").classList.remove("hidden");

  let subjects = subjectsData[reg][dept][sem];

  if(!subjects){
    alert("No subjects found!");
    return;
  }

  subjects.forEach(s=>{
    addSubject(sem, s[0], s[1], s[2]);
  });
}

function addSubject(sem,code,name,credit){
var row=table.insertRow();
row.insertCell(0).innerHTML=sem;
row.insertCell(1).innerHTML=code;
row.insertCell(2).innerHTML=name;
row.insertCell(3).innerHTML=credit;
row.insertCell(4).innerHTML='<select><option value="10">O</option><option value="9">A+</option><option value="8">A</option><option value="7">B+</option><option value="6">B</option><option value="5">C</option><option value="0">U</option></select>';
}

function addNewSubject(){
var sem=document.getElementById("sem").value;
if(sem==="") return;

let code=prompt("Enter Subject Code:");
if(code===null) return;

let name=prompt("Enter Subject Name:");
if(name===null) return;

let creditInput=prompt("Enter Credits:");
if(creditInput===null) return;

let credit=parseFloat(creditInput);
if(isNaN(credit)) return;

lastSubjectRow=table.insertRow();
lastSubjectRow.innerHTML="<td>"+sem+"</td><td>"+code+"</td><td>"+name+"</td><td>"+credit+"</td><td><select><option value='10'>O</option><option value='9'>A+</option><option value='8'>A</option><option value='7'>B+</option><option value='6'>B</option><option value='5'>C</option><option value='0'>U</option></select></td>";
}

function undoLastSubject(){
if(lastSubjectRow){
table.deleteRow(lastSubjectRow.rowIndex);
lastSubjectRow=null;
}
}

