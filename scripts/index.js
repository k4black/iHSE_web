/**
 * @fileoverview Index page logic
 * File providing all functions which are used to control index.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */





/** ===============  LOGIC and REQUESTS  =============== */


// TODO: Loading icon


/**
 * Get day information from server
 * Send http GET request and get today html schedule
 * TODO: optimize selection
 */
var day = document.querySelector('.day');

var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up day field

            var day = JSON.parse( this.responseText );

            console.log(day);
        }
    }
};


// Get today date
var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!

today = mm + '.' + dd;

xhttp.open("GET", "http://ihse.tk:50000/day?day=" + today, true);
xhttp.send();
