/**
 * @fileoverview Register page logic
 * File providing all functions which are used to control register.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */






/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Calculate hash from password
 * TODO: Check security
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
 * Add button event - 'register'
 * Send http POST request to register and automatically login - get session id
 */
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');
button.addEventListener('click', function () {

    var name_ = button.parentElement.querySelector('#name');
    var phone = button.parentElement.querySelector('#phone');
    var pass = button.parentElement.querySelector('#pass');
    var code = button.parentElement.querySelector('#code');


    if (name_.value == "" || pass.value == "" || code.value == "" || phone.value == "") // If some field are empty - do nothing
        return;  // TODO: Message



    // Pass not password but hashcode of it
    // code - registration code
    var query = "?name=" + name_.value + "&phone=" + phone.value + "&pass=" + hashCode(pass.value) + "&code=" + code.value;



    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            button.style.display = 'none';
            button2.style.display = 'block';
        }

        if (this.readyState === 4) {  // When request is done

            button.style.display = 'block';
            button2.style.display = 'none';

            if (this.status === 200) {  // Authorized
                alert("ok reg!");  // TODO: Redirection

                name.value = "";
                phone.value = "";
                pass.value = "";
                code.value = "";
            }

            if (this.status === 403) {  // Authorization error
                alert("Wrong registration code!");  // TODO: show Html error message

                pass.value = "";
                code.value = "";
            }

            if (this.status === 401) {  // Authorization error
                alert("Wrong Login/Password!");  // TODO: show Html error message

                pass.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/register" + query, true);
    xhttp.send();
});




/** ===============  ANIMATIONS  =============== */




/**
 * Add name field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var name_ = document.querySelector('#name');
name_.addEventListener('focus', function () {
    onFocus(true);
    name_.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('Name active');
});

name_.addEventListener('blur', function () {
    onFocus(false);
    if (name_.value != "")
        return;

    name_.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('Name inactive');
});


/**
 * Add phone field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var phone = document.querySelector('#phone');
phone.addEventListener('focus', function () {
    onFocus(true);
    phone.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('phone active');
});

phone.addEventListener('blur', function () {
    onFocus(false);

    if (phone.value == "+") {
        phone.value = "";
    }

    if (phone.value != "")
        return;

    phone.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('phone inactive');
});

/**
 * Add password field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var pass = document.querySelector('#pass');

pass.addEventListener('focus', function () {
    onFocus(true);
    pass.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('Pass active');
});

pass.addEventListener('blur', function () {
    onFocus(false);
    if (pass.value != "")
        return;

    pass.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('Pass inactive');
});


/**
 * Add password hide/show button
 * Change type of password field
 */
var hideButton = pass.parentElement.querySelector('.hide__pass');

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




/**
 * Add code field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var code = document.querySelector('#code');

code.addEventListener('focus', function () {
    onFocus(true);
    code.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('Code active');
});

code.addEventListener('blur', function () {
    onFocus(false);
    if (code.value != "")
        return;

    code.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('Code inactive');
});





/**
 * Add icon field animations
 * Hide icon if there is virtual keyboard
 * TODO: optimize selection
 */

var focus = false;  // Is there virtual keyboard?

var form = document.querySelector('.wrapper');

function onFocus(focus) {

    return;
    if (focus) {
        form.classList.add('close');
    }
    else {
        form.classList.remove('close');
    }
}
