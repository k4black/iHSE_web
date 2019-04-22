/**
 * @fileoverview Account page logic
 * File providing all functions which are used to control account.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */





/** ===============  LOGIC and REQUESTS  =============== */


/**
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 * TODO: optimize selection
 */

var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up fields name and phone

            console.log(this.responseText);
            // var user = JSON.parse( this.responseText );
            // accountName.innerText = user.name;
            // accountPhone.innerText = user.phone;

        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/account", true);
xhttp.withCredentials = true; // To send Cookie;
xhttp.send();
