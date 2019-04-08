function loadDoc() {
    console.log("Change content");

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            document.getElementById("demo").innerHTML = this.responseText;

        } else if (this.readyState === 4) {
            document.getElementById("demo").innerHTML = "status: " + this.status.toString();

        } else if (this.status === 200) {
            document.getElementById("demo").innerHTML = "readyState: " + this.readyState.toString();

        } else {
            document.getElementById("demo").innerHTML = "Some other";
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/path/resource?param1=value1&param2=value2", true);
    xhttp.send();
}
