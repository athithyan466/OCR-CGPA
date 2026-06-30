var previousGPA = "";

function calculate(){
var previousGPA = "";
athvikCalculate();


    console.log("calculate clicked");

    previousGPA = document.getElementById("result").innerHTML;
previousGPA=document.getElementById("result").innerHTML;

var rows=table.rows;
var totalCredits=0,totalPoints=0;

for(var i=1;i<rows.length;i++){
var credit=parseFloat(rows[i].cells[3].innerHTML);
var grade=parseFloat(rows[i].cells[4].querySelector("select").value);

if(grade!==0){
totalCredits+=credit;
totalPoints+=credit*grade;
}
}

if(totalCredits>0){
let gpa=totalPoints/totalCredits;
athvikResult(gpa);

document.getElementById("result").innerHTML="GPA = "+gpa.toFixed(3);
}else{
document.getElementById("result").innerHTML="ALL SUBJECTS FAILED";
}
}

function undoGPA(){
document.getElementById("result").innerHTML=previousGPA;
}

