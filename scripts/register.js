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
 * TODO: Register form
 */
var buttonReg = document.querySelector('#btnReg');
buttonReg.addEventListener('click', function () {

    var name_ = buttonReg.parentElement.querySelector('#name');
    var pass = buttonReg.parentElement.querySelector('#pass');
    var code = buttonReg.parentElement.querySelector('#code');


    if (name_.value == "" || pass.value == "" || code.value == "") // If some field are empty - do nothing
        return



    // Pass not password but hashcode of it
    // code - registration code
    var query = "?name=" + name_.value + "&pass=" + hashCode(pass.value) + "&code=" + code.value;



    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {  // When request is done

            if (this.status === 200) {  // Authorized
                alert("ok reg!");  // TODO: Redirection

                name.value = "";
                pass.value = "";
                code.value = "";
            }

            if (this.status === 401) {  // Authorization error
                alert("not reg!");  // TODO: show Html error message

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
    name_.closest('div').querySelector("label").classList.add('active');
    console.log('Name active');
});

name_.addEventListener('blur', function () {
    onFocus(false);
    if (name_.value != "")
        return;

    name_.closest('div').querySelector("label").classList.remove('active');
    console.log('Name inactive');
});


/**
 * Add password field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var pass = document.querySelector('#pass');

pass.addEventListener('focus', function () {
    onFocus(true);
    pass.closest('div').querySelector("label").classList.add('active');
    console.log('Pass active');
});

pass.addEventListener('blur', function () {
    onFocus(false);
    if (pass.value != "")
        return;

    pass.closest('div').querySelector("label").classList.remove('active');
    console.log('Pass inactive');
});



/**
 * Add code field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var code = document.querySelector('#code');

pass.addEventListener('focus', function () {
    onFocus(true);
    code.closest('div').querySelector("label").classList.add('active');
    console.log('Code active');
});

pass.addEventListener('blur', function () {
    onFocus(false);
    if (code.value != "")
        return;

    code.closest('div').querySelector("label").classList.remove('active');
    console.log('Code inactive');
});





/**
 * Add icon field animations
 * Hide icon if there is virtual keyboard
 * TODO: optimize selection
 */

var focus = false;  // Is there virtual keyboard?

var icon = document.querySelector('.register__icon');

function onFocus(focus) {
    if (focus) {
        icon.classList.add('close');
    }
    else {
        icon.classList.remove('close');
    }
}
