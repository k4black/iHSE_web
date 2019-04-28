/**
 * @fileoverview Create project page logic
 * File providing all functions which are used to control create.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */






/** ===============  LOGIC and REQUESTS  =============== */





/**
 * Add button event - 'create project'
 * Send http POST request to create new project
 */
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');

button.addEventListener('click', function() {
    var form = button.parentElement;

    // TODO : USER names list

    var title = button.parentElement.querySelector('#title');
    var type = button.parentElement.querySelector('#type');
    var name = button.parentElement.querySelector('#name');
    var desc = button.parentElement.querySelector('#desc');
    var anno = button.parentElement.querySelector('#anno');


    if (title.value == "" || type.value == "" || name.value == "" || desc.value == "" || anno.value == "") // If some field are empty - do nothing
        return; // TODO: Message



    var data = JSON.stringify({"title": form.querySelector('#title').value,
                               "type": form.querySelector('#type').value,
                               "name": form.querySelector('#name').value,
                               "desc": form.querySelector('#desc').textContent,
                               "anno": form.querySelector('#anno').textContent
                              });


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            button.style.display = 'none';
            button2.style.display = 'block';
        }

        if (this.readyState === 4) {  // When request is done

            button.style.display = 'block';
            button2.style.display = 'none';

            if (this.status === 200) {  // Got it
                alert("ok!");  // TODO: Redirection

            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("not!");  // TODO: show Html error message

            }
        }
    };


    xhttp.open("POST", "http://ihse.tk:50000/project", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');

    xhttp.withCredentials = true;  // To receive cookie

    xhttp.send(data);

});








/** ===============  ANIMATIONS  =============== */




/**
 * Add title field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
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
 * TODO: optimize selection
 */
var name_ = document.querySelector('#name');
name_.addEventListener('focus', function () {
    name_.closest('div').querySelector("label").parentElement.classList.add('active');
    console.log('Name active');
});

name_.addEventListener('blur', function () {
    if (name_.value != "")
        return;

    name_.closest('div').querySelector("label").parentElement.classList.remove('active');
    console.log('Name inactive');
});


/**
 * Add description field animations
 * Hint Rise up when there is some text or cursor inside it
 * TODO: optimize selection
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
 * TODO: optimize selection
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

