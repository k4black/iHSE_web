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

accountName = document.querySelector('.topbar__name');
accountPhone = document.querySelector('.topbar__phone');
accountCredits = document.querySelector('.credits');
title = document.querySelector('.title');

var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up fields name and phone

            // console.log(this.responseText);

            var user = JSON.parse( this.responseText );
            accountName.innerText = user.name;
            accountPhone.innerText = user.phone;
            
            switch (user.type) {
                case 0:
                    title.innerText = 'User';
                    break;
                case 1:
                    title.innerText = 'Host';
                    break;
                case 2:
                    title.innerText = 'Admin';
                    break;
            }

            setProgress(user.credits / user.total);

            accountCredits.querySelector('.credits__title').innerText = user.credits + '/' + user.total;

        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/account", true);
xhttp.withCredentials = true; // To send Cookie;
xhttp.send();






document.querySelector('.header__button').addEventListener('click', function () {

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                alert('LOGOUT!');
                document.referrer = 'http://ihse.tk/';

            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/logout", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();

});






/**
 * Control progress circle
 * Send http POST request to get session id
 */
var progress = document.querySelector('.c100');
var procentage = progress.querySelector('span');
function setProgress(percent) {
    console.log(percent);

    percent = Math.min(100, percent);
    percent = Math.round(percent);

    console.log(percent);

    progress.className = "";
    progress.classList.add('c100');
    progress.classList.add("p" + percent);

    procentage.innerText = percent + "%";
}






/**
 * Add button event - 'code input'
 * Send http POST request to sing up lecture
 */
var button = document.querySelector('#btn');
button.addEventListener('click', function () {

    var code = button.parentElement.querySelector('#code');


    if (code.value == "") // If some field are empty - do nothing
        return;


    // Pass not password but hashcode of it
    var query = "?code=" + code.value;


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {  // When request is done

            if (this.status === 200) {  // Authorized
                alert("ok!");  // TODO: Redirection

                code.value = "";

            }

            if (this.status === 401) {  // Authorization error
                alert("not!");  // TODO: show Html error message

                code.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/credits" + query, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
});