/**
 * @fileoverview Login page logic
 * File providing all functions which are used to control login.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Calculate hash from password
 * @param {string} s - password with which the hash is calculated
 * @return {int}
 */
function hashCode(s) {
    let h;
    for(let i = 0; i < s.length; i++)
        h = Math.imul(31, h) + s.charCodeAt(i) | 0;

    return h;
}



/**
 * Add button event - 'login'
 * Send http POST request to get session id
 */
document.querySelector('#btn').addEventListener('click', function () {

    var phone = document.querySelector('#phone');
    var pass = document.querySelector('#pass');


    if (phone.value == "" || pass.value == "") { // If some field are empty - do nothing
        alert('Вы должны заполнить все поля!');  // TODO: show Html error message
        return;
    }

    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            setLoaded();

            if (this.status === 200) {  // Authorized
                location = '../index.html';

                phone.value = "";
                pass.value = "";
            }

            if (this.status === 302) {  // Ok - redir

            }

            if (this.status === 401) {  // Authorization error
                alert("Неверный Логин/Пароль!");  // TODO: show Html error message

                pass.value = "";
            }
        }
    };

    // Pass not password but hashcode of it
    var query = "?phone=" + phone.value + "&pass=" + hashCode(pass.value);
    xhttp.open("POST", "http://ihse.tk:50000/login" + query, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
});




/** ===============  ANIMATIONS  =============== */



/**
 * Show and hide loading button
 */
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');
function setLoading() {
    button.style.display = 'none';
    button2.style.display = 'block';
}

function setLoaded() {
    button.style.display = 'block';
    button2.style.display = 'none';
}






/**
 * Add name field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var phone = document.querySelector('#phone');
phone.addEventListener('focus', function () {
    phone.closest('div').querySelector("label").parentElement.classList.add('active');
});

phone.addEventListener('blur', function () {
    if (phone.value == "+") {
        phone.value = "";
    }

    if (phone.value != "")
        return;

    phone.closest('div').querySelector("label").parentElement.classList.remove('active');
});


/**
 * Add password field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var pass = document.querySelector('#pass');

pass.addEventListener('focus', function () {
    pass.closest('div').querySelector("label").parentElement.classList.add('active');
});

pass.addEventListener('blur', function () {
    if (pass.value != "")
        return;

    pass.closest('div').querySelector("label").parentElement.classList.remove('active');
});




/**
 * Add password hide/show button
 * Change type of password field
 */
var hideButton = pass.parentElement.querySelector('.input__icon');
hideButton.addEventListener('click', function () {

    if (pass.type == 'password') {
        pass.type = 'text';
        hideButton.firstElementChild.style.display = 'block';
        hideButton.lastElementChild.style.display = 'none';
    }

    else {
        pass.type = 'password';
        hideButton.firstElementChild.style.display = 'none';
        hideButton.lastElementChild.style.display = 'block';
    }

});


