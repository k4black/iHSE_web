var mobileNav = document.querySelector('.arrow__button');
mobileNav.addEventListener('click', back);

function back() {
    //alert(document.referrer);
    window.location.href = document.referrer;
}






console.log("!!!");

var button = document.querySelector('#btn');

button.addEventListener('click', btn);

function btn() {
    console.log("result_form");
    // sendAjaxForm('result_form', 'ajax_form', 'action_ajax_form.php');

    xhttp.open("POST", "http://ihse.tk:50000/login?name=value1&pass=value2", true, "USR", "PSS");
    xhttp.send();

    return false;
}


function sendAjaxForm(result_form, ajax_form, url) {

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.status === 200) {
            console.log("200 ok!");
        } else {
            console.log("Smth else!");
        }
    };

    xhttp.timeout = 30000;
    xhttp.ontimeout = function() {
        alert( 'Too loooooong' );
    };

    xhttp.open("POST", "http://ihse.tk:50000/path/resource?param1=value1&param2=value2", true, "user", "pass");
    xhttp.send();
}






console.log('Login form');

var name = document.querySelector('#name');
var pass = document.querySelector('#pass');


pass.addEventListener('focus', function () {
    pass.closest('div').querySelector("label").classList.add('active');
    console.log('Pass active');
});

pass.addEventListener('blur', function () {
    if (pass.value != "")
        return;

    pass.closest('div').querySelector("label").classList.remove('active');
    console.log('Pass inactive');
});


name.addEventListener('focus', function () {
    name.closest('div').querySelector("label").classList.add('active');
    console.log('Name active');
});

name.addEventListener('blur', function () {
    name.closest('div').querySelector("label").classList.remove('active');
    console.log('Name inactive');
});

