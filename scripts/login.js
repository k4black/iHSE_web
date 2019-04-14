// TODO: Hide .html
// ihse.tk/login.html -> ihse.tk/login



/**
 * Add navigation button event - 'back'
 */
var mobileNav = document.querySelector('.arrow__button');
mobileNav.addEventListener('click', function back() {

    //alert(document.referrer);

    if (document.referrer == "http://ihse.tk/login.html")
        window.location.href = "http://ihse.tk/";

    else
        window.location.href = document.referrer;
});



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
button.addEventListener('click', function () {

    var name = button.parentElement.querySelector('#name');
    var pass = button.parentElement.querySelector('#pass');


    if (name.value == "" || pass.value == "") // If some field are empty - do nothing
        return


    // Pass not password but hashcode of it
    var query = "?name=" + name.value + "&pass=" + hashCode(pass.value);
    
        
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {  // When request is done

            if (this.status === 200) {  // Authorized
                alert("ok!");  // TODO: Redirection

                name.value = "";
                pass.value = "";
            }

            if (this.status === 401) {  // Authorization error
                alert("not!");  // TODO: show Html error message

                pass.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/login" + query, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
});




/**
 * Add button event - 'register'
 * Send http POST request to register and automatically login - get session id
 * TODO: Register form
 */
var buttonReg = document.querySelector('#btnReg');
buttonReg.addEventListener('click', function () {

    var name_ = button.parentElement.querySelector('#name');
    var pass = button.parentElement.querySelector('#pass');


    if (name_.value == "" || pass.value == "") // If some field are empty - do nothing
        return



    // Pass not password but hashcode of it
    // code - registration code
    var query = "?name=" + name_.value + "&pass=" + hashCode(pass.value) + "&code=" + 0;



    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {  // When request is done

            if (this.status === 200) {  // Authorized
                alert("ok reg!");  // TODO: Redirection

                name.value = "";
                pass.value = "";
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



/**
 * Add name field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
 */
var name_ = document.querySelector('#name');
name_.addEventListener('focus', function () {
    name_.closest('div').querySelector("label").classList.add('active');
    console.log('Name active');
});

name_.addEventListener('blur', function () {
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
    pass.closest('div').querySelector("label").classList.add('active');
    console.log('Pass active');
});

pass.addEventListener('blur', function () {
    if (pass.value != "")
        return;

    pass.closest('div').querySelector("label").classList.remove('active');
    console.log('Pass inactive');
});

