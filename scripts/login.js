var mobileNav = document.querySelector('.arrow__button');
mobileNav.addEventListener('click', back);

function back() {
    //alert(document.referrer);
    if (document.referrer == "http://ihse.tk/login.html")
        window.location.href = "http://ihse.tk/";
    else
        window.location.href = document.referrer;
}




function hashCode(s) {
    let h;
    for(let i = 0; i < s.length; i++)
        h = Math.imul(31, h) + s.charCodeAt(i) | 0;

    return h;
}




console.log("!!!");

var button = document.querySelector('#btn');

button.addEventListener('click', function () {
    console.log("result_form");
   

    var name = button.parentElement.querySelector('#name');
    var pass = button.parentElement.querySelector('#pass');
    
    if (name.value == "" || pass.value == "")
        return
    
    var query = "?name=" + name.value + "&pass=" + hashCode(pass.value);
    
        
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert("ok!");

                name.value = "";
                pass.value = "";
            }

            if (this.status === 401) {
                alert("not!");

                pass.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/login" + query, true);
    xhttp.send();
});





var buttonReg = document.querySelector('#btnReg');

buttonReg.addEventListener('click', function () {


    var name = button.parentElement.querySelector('#name');
    var pass = button.parentElement.querySelector('#pass');

    if (name.value == "" || pass.value == "")
        return

    var query = "?name=" + name.value + "&pass=" + hashCode(pass.value) + "&code=" + 0;


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert("ok reg!");

                name.value = "";
                pass.value = "";
            }

            if (this.status === 403) {
                alert("not reg!");

                pass.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/register" + query, true);
    xhttp.send();
});





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

