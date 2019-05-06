/**
 * @fileoverview Account page logic
 * File providing all functions which are used to control account.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


// TODO: Graph



/** ===============  LOGIC and REQUESTS  =============== */


/**
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 */
{
    let topbar = document.querySelector('.topbar');

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                // console.log(this.responseText);

                let user = JSON.parse(this.responseText);
                topbar.querySelector('.topbar__name').innerText = user.name;
                topbar.querySelector('.topbar__phone').innerText = user.phone;

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


                // TODO: Work?
                window.addEventListener('load', function () {
                    bar.animate(user.credits / user.total);  // Number from 0.0 to 1.0
                });

                document.querySelector('.credits__title').innerText = user.credits + ' / ' + user.total;

                switch (user.type) {
                    case 0:  // User

                        break;

                    case 1:  // Host
                        topbar.querySelector('.topbar__type').innerText = 'Host';
                        break;

                    case 2:  // Admin
                        topbar.querySelector('.topbar__type').innerText = 'Admin';
                        break;
                }
            }

            else if (this.status === 401) {  // No account data
                // TODO: Notification
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/account", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();

}



/**
 * Logout button
 * Send http POST request to clear session id
 */
document.querySelector('.header__button').addEventListener('click', function () {

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {

                alert('LOGOUT!');
                document.referrer = 'http://ihse.tk/';  // Refer to start page

        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/logout", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();

});






/**
 * Add button event - 'code input'
 * Send http POST request to sing up lecture
 */
document.querySelector('#btn').addEventListener('click', function () {

    let code = document.querySelector('#code');

    if (code.value === "")  // If some field are empty - do nothing
        return;


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
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

    xhttp.open("POST", "http://ihse.tk:50000/credits?code=" + code.value, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
});









// https://kimmobrunfeldt.github.io/progressbar.js/
// var ProgressBar = require('scripts/progressbar.js');
var bar;
window.addEventListener('load', function () {
    bar = new ProgressBar.Circle('.progress', {
        color: '#aaaaaa',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 4,
        trailWidth: 1,
        easing: 'bounce',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: {color: '#0085d6', width: 1},
        to: {color: '#ed9324', width: 4},
        // Set default step function for all animate calls
        step: function (state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);

            var value = Math.round(circle.value() * 100);
            if (value === 0) {
                circle.setText('');
            } else {
                circle.setText(value + '%');
            }

        }
    });
    bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    bar.text.style.fontSize = '2rem';
});




/** ===============  ANIMATIONS  =============== */



/**
 * Add code field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var code = document.querySelector('#code');
code.addEventListener('focus', function () {
    code.closest('div').querySelector("label").classList.add('active');
});

code.addEventListener('blur', function () {
    if (code.value != "")
        return;

    code.closest('div').querySelector("label").classList.remove('active');
});