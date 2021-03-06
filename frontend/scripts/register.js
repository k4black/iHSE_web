/**
 * @fileoverview Register page logic
 * File providing all functions which are used to control register.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */






/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Add button event - 'register'
 * Send http POST request to register and automatically login - get session id
 */
document.querySelector('#btn').addEventListener('click', function () {

    var name_ = document.querySelector('#name');
    var surname = document.querySelector('#surname');
    var sex = document.querySelector('#sex');
    var phone = document.querySelector('#phone');
    var pass = document.querySelector('#pass');
    var code = document.querySelector('#code');


    if (name_.value == "" || sex.value == "" || surname.value == "" || pass.value == "" || code.value == "" || phone.value == ""){ // If some field are empty - do nothing
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

                name.value = "";
                sex.value = "";
                phone.value = "";
                pass.value = "";
                code.value = "";
            }

            if (this.status === 302) {  // Ok - redir

            }

            if (this.status === 403) {  // Authorization error
                alert("Неверный код регистрации!");  // TODO: show Html error message

                pass.value = "";
                code.value = "";
            }

            if (this.status === 409) {  // Already exist error
                alert("Пользователь уже существует!");  // TODO: show Html error message

                // location = '../login.html';

                phone.value = "";
                pass.value = "";
                code.value = "";
            }

            if (this.status === 401) {  // Authorization error
                // alert("Неверный Логин/Пароль!");  // TODO: show Html error message

                location = '../login.html';
                pass.value = "";
            }
        }
    };

    // Pass not password but hashcode of it
    // code - registration code
    let user = {'name': name_.value, 'surname': surname.value, 'phone': phone.value, 'sex': sex.value, 'pass': hashCode(pass.value), 'code': code.value};
    let data = JSON.stringify(user);

    xhttp.open("POST", "/register", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.send(data);
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
var name_ = document.querySelector('#name');
name_.addEventListener('focus', function () {
    name_.closest('div').querySelector("label").parentElement.classList.add('active');
});

name_.addEventListener('blur', function () {
    if (name_.value != "")
        return;

    name_.closest('div').querySelector("label").parentElement.classList.remove('active');
});


/**
 * Add surname field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var surname = document.querySelector('#surname');
surname.addEventListener('focus', function () {
    surname.closest('div').querySelector("label").parentElement.classList.add('active');
});

surname.addEventListener('blur', function () {
    if (surname.value != "")
        return;

    surname.closest('div').querySelector("label").parentElement.classList.remove('active');
});


/**
 * Add phone field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var phone = document.querySelector('#phone');
phone.addEventListener('focus', function () {
    phone.closest('div').querySelector("label").parentElement.classList.add('active');
});

phone.addEventListener('blur', function () {
    if (phone.value == "+") {  // Kostyl
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




/**
 * Add code field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var code = document.querySelector('#code');

code.addEventListener('focus', function () {
    code.closest('div').querySelector("label").parentElement.classList.add('active');
});

code.addEventListener('blur', function () {
    if (code.value != "")
        return;

    code.closest('div').querySelector("label").parentElement.classList.remove('active');
});


