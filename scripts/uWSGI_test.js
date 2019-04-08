function loadDoc() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            document.getElementById("demo").innerHTML = this.responseText;
        } else if (this.readyState === 4) {
            document.getElementById("demo").innerHTML = "status: " + this.status.toString();
        } else if (this.status === 200) {
            document.getElementById("demo").innerHTML = "readyState: " + this.readyState.toString();
        }
    };
    xhttp.open("GET", "http://ihse.tk:3030", true);
    xhttp.send();
}
