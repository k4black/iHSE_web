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

var accountName = document.querySelector('.topbar__name');
var accountPhone = document.querySelector('.topbar__phone');
var accountCredits = document.querySelector('.credits');
var title = document.querySelector('.title');

if (accountName != null && accountPhone != null) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                // console.log(this.responseText);

                var user = JSON.parse(this.responseText);
                accountName.innerText = user.name;
                accountPhone.innerText = user.phone;

                // switch (user.type) {
                //     case 0:
                //         title.innerText = 'User';
                //         break;
                //     case 1:
                //         title.innerText = 'Host';
                //         break;
                //     case 2:
                //         title.innerText = 'Admin';
                //         break;
                // }

                setProgress(user.credits, user.total);
                accountCredits.querySelector('.credits__title').innerText = user.credits + ' / ' + user.total;

                switch (user.type) {
                    case 0:  // User

                        break;

                    case 1:  // Host
                        accountName.parentElement.parentElement.querySelector('.topbar__type').innerText = 'Host';
                        break;

                    case 2:  // Admin
                        accountName.parentElement.parentElement.querySelector('.topbar__type').innerText = 'Admin';
                        break;
                }
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/account", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();

}




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
function setProgress(value, total) {
    var percent = value / total * 100;

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




/** ===============  ANIMATIONS  =============== */



/**
 * Add code field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var code = document.querySelector('#code');
code.addEventListener('focus', function () {
    code.closest('div').querySelector("label").classList.add('active');
    console.log('COde active');

});

code.addEventListener('blur', function () {
    if (code.value != "")
        return;

    code.closest('div').querySelector("label").classList.remove('active');
    console.log('Code inactive');
});