/**
 * @fileoverview Create project page logic
 * File providing all functions which are used to control create.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




window.addEventListener('load', function () {

    loadNames(setNames);

});




/** ===============  LOGIC and REQUESTS  =============== */





/**
 * Add button event - 'create project'
 * Send http POST request to create new project
 */
document.querySelector('#btn').addEventListener('click', function() {
    var form = document.querySelector('.form');


    var title = form.querySelector('#title');
    var type = form.querySelector('#type');
    var dirs = form.querySelector('#dirs');
    var deff = form.querySelector('#deff');
    var desc = form.querySelector('#desc');
    var anno = form.querySelector('#anno');
    var names = Array.from(form.querySelectorAll('#name')).map(function(name) {
        return name.value;
    });

    let user_names_allowed = [];
    for (let user of cache['users']) {
        if (user['project_id'] == 0) {
            user_names_allowed.push(user['name']);
        }
    }

    for (let name of names) {
        if (name in user_names_allowed) {
            // ok
        } else {
            alert('You can not add user <' + name + '> to your project.\nNo such user or user already has project!');
            return;
        }
    }


    if (title.value == "" || type.value == "" || dirs.value == "" || deff.value == "" || names == null || anno.value == "") { // If some field are empty - do nothing
        alert('You have to fill all fields! \n(However, you can fill description field later)');  // TODO: show Html error message
        return;
    }


    let data = JSON.stringify({"title": title.value,
                               "type": type.value,
                               "def_type": deff.value,
                               "direction": dirs.value,
                               "users": names,
                               "description": desc.textContent,
                               "annotation": anno.textContent
                              });


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            setLoaded();

            if (this.status === 200) {  // Got it
                // alert("ok!");

                location = '../projects.html';
            }

            if (this.status === 302) {  // Ok - redir

            }

            if (this.status === 409) {  //  Conflict or already got it
                alert("Cannot create project!");  // TODO: show Html error message
            }
        }
    };


    xhttp.open("POST", "//ihse.tk/project", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
});




/**
 * Loading user names in list (short users description)
 * Send http GET request to get users
 * And save it to `cache['names']`
 */
function loadNames(func) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                let names_raw = JSON.parse(this.responseText);

                let obj = groupByUnique(names_raw, 'id');

                cache['names'] = obj;

                func();
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/names", true);
    xhttp.send();
}


function setNames() {
    let names = cache['names'];

    // For choosing names
    let datalist_html = "";
    for (let user of names) {
        if (user['project_id'] == 0) {  // Can choose Ony if there are no user's project
            datalist_html += '<option value="' + user['name'] + '"></option>';
        }
    }
    document.querySelector('#users_list').innerHTML = datalist_html;

    // Setup first user
    document.querySelector('#name').value = cache['user'].name;
}






/**
 * Add new name field (or remove )
 * TODO: Optimize
 */
var addButton = document.querySelector('.input__icon');
addButton.addEventListener('click', addField);

function addField() {

    if (this.lastElementChild.style.display == 'block') {
        this.parentElement.classList.add('active');

        this.parentElement.style.marginBottom = 0;

        this.firstElementChild.style.display = 'block';
        this.lastElementChild.style.display = 'none';

        var newObj = document.createElement('div');
        newObj.classList = 'form__input active name__input';
        newObj.innerHTML = '<label for="name" class="create__label">Участники</label>'+
                        '<input id="name" type="text" name="name" list="users_list" maxlength=""/>' +
                        '<div class="input__icon">' +
                            '<i style="display:none" class="mobile__item__icon large material-icons">-</i>' +
                            '<i style="display:block" class="mobile__item__icon large material-icons">+</i>' +
                        '</div>';

        this.parentElement.parentElement.insertBefore(newObj, this.parentElement.nextSibling);


        var newField = this.parentElement.nextSibling;
        newField.lastChild.addEventListener('click', addField);

        document.querySelector('#name').removeEventListener('focus', nameActive);
        document.querySelector('#name').removeEventListener('blur', nameDisactive);
    } else {
        if (!this.parentElement.classList.contains('name__input')) {
            this.parentElement.nextElementSibling.classList.remove('name__input');
        }

        this.parentElement.parentNode.removeChild(this.parentElement);
    }
}




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
 * Add title field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var title = document.querySelector('#title');
title.addEventListener('focus', function () {
    title.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('title active');
});

title.addEventListener('blur', function () {
    if (title.value != "")
        return;

    title.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('title inactive');
});


/**
 * Add name field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var name_ = document.querySelector('#name');
name_.addEventListener('focus', nameActive);
function nameActive() {
    name_.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('Name active');
}

name_.addEventListener('blur', nameDisactive);
function nameDisactive() {
    if (name_.value != "")
        return;

    name_.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('Name inactive');
}


/**
 * Add description field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var desc = document.querySelector('#desc');
desc.addEventListener('focus', function () {
    desc.parentElement.querySelector("label").parentElement.classList.add('active');
    console.log('desc active');
});

desc.addEventListener('blur', function () {
    if (desc.textContent != "")
        return;

    desc.parentElement.querySelector("label").parentElement.classList.remove('active');
    console.log('desc inactive');
});



/**
 * Add annotation field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var anno = document.querySelector('#anno');
anno.addEventListener('focus', function () {
    anno.parentElement.querySelector("label").parentElement.classList.add('active');
    console.log('anno active');
});

anno.addEventListener('blur', function () {
    if (anno.textContent != "")
        return;

    anno.parentElement.querySelector("label").parentElement.classList.remove('active');
    console.log('anno inactive');
});

