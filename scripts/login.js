/**
 * @fileoverview Login page logic
 * File providing all functions which are used to control login.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




// TODO: Hide .html
// ihse.tk/login.html -> ihse.tk/login






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
 * Add button event - 'login'
 * Send http POST request to get session id
 */
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');
button.addEventListener('click', function () {

    var name = button.parentElement.querySelector('#name');
    var pass = button.parentElement.querySelector('#pass');


    if (name.value == "" || pass.value == "") // If some field are empty - do nothing
        return;


    // Pass not password but hashcode of it
    var query = "?name=" + name.value + "&pass=" + hashCode(pass.value);
    
        
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
                alert("ok!");  // TODO: Redirection

                name.value = "";
                pass.value = "";
            }

            if (this.status === 401) {  // Authorization error
                alert("Wrong Login/Password!");  // TODO: show Html error message

                pass.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/login" + query, true);
    xhttp.withCredentials = true;  // To receive cookie
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




