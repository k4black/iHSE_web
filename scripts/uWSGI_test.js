var accountName = document.querySelector('.mobile__sidebar__name');
var accountPhone = document.querySelector('.mobile__sidebar__phone');


var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) {
            console.log(this.responseText);
            var user = JSON.parse( this.responseText );
            accountName.innerText = user.name;
            accountPhone.innerText = user.phone;
        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/account", true);
xhttp.withCredentials = true; // Send Cookie;
xhttp.send();






function loadDoc() {
    console.log("Change content");

    var xhttp = new XMLHttpRequest();
    /*
    * Events can be called: onfoo()
    * loadstart
    * progress – updated responseText.
    * abort – was called xhr.abort().
    * error
    * load – with no error
    * timeout
    * loadend – success or not
    */

    /*
    *  readyState: 0	UNSENT	Only created; No open() method call
    *              1	OPENED	Just called open().
    *              2	HEADERS_RECEIVED	Method send() was call, headers and status accessible.
    *              3	LOADING	 Loading; responseText is NOT completed.
    *              4	DONE	Ok The end of the operation.
    *
    *  status: http request status
    *
    */
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

    xhttp.timeout = 30000;
    xhttp.ontimeout = function() {
        alert( 'Too loooooong' );
    };

    xhttp.open("GET", "http://ihse.tk:50000/path/resource?param1=value1&param2=value2", true, "user", "pass");

    // xhttp.setRequestHeader("SCRIPT_NAME", '12311');

    var params = "rrrrqqqw";

    // xhttp.setRequestHeader("Content-type", "application/text; charset=utf-8");
    xhttp.setRequestHeader("Content-length", params.length);
    xhttp.setRequestHeader("Connection", "close");

    xhttp.send(params);
}
