var mobileNav = document.querySelector('.arrow__button');
mobileNav.addEventListener('click', back);

function back() {
    //alert(document.referrer);
    window.location.href = document.referrer;
}






console.log("!!!");

var button = document.querySelector('#btn');

button.addEventListener('click', function () {
    console.log("result_form");
   

    var name = button.parentElement.querySelector('#name').value;
    var pass = button.parentElement.querySelector('#pass').value;
    
    if (name == "" || pass == "")
        return
    
    var query = "?name=" + name + "&pass=" + pass;
    
        
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('OK');
            }

            if (this.status === 401) {
                alert('NOT');
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/login" + query, true);
    xhttp.send();
});


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

