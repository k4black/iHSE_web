/**
 * @fileoverview Event page logic
 * File providing all functions which are used to control event.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */



(function(w) {
    //private variable
    var loaded = false;
    w.onload = function() {
        loaded = true;
    };

    w.checkLoaded = function() {
        return loaded;
    };
})(window);





var tmp = 0;


const urlParams = new URLSearchParams(window.location.search);

var eventId = urlParams.get('id');
console.log(eventId);

var wrapper = document.querySelector('.wrapper');
var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function () {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up fields
            loadingEnd(); // TODO: Check

            var event = JSON.parse( this.responseText );

            document.querySelector('.title').innerText = event.title;

            wrapper.querySelector('.time').firstElementChild.innerText = event.time;
            wrapper.querySelector('.time').lastElementChild.innerText = event.date;

            wrapper.querySelector('.location').firstElementChild.innerText = event.loc;

            wrapper.querySelector('.host').firstElementChild.innerText = event.host;

            wrapper.querySelector('.desc').firstElementChild.innerText = event.desc;

            if (event.anno == undefined) {
                wrapper.querySelector('.anno').parentElement.innerHTML = "";
                wrapper.querySelector('.anno').parentElement.style.display = 'none';
            }
            else {
                wrapper.querySelector('.anno').firstElementChild.innerText = event.anno;
            }

            // TODO: Hide when there is no enrollment
            if (event.total == undefined || event.total == "") {
            }
            else {
                wrapper.querySelector('.count').innerText = event.count + ' / ' + event.total;

                if (window.checkLoaded()) {
                    bar.animate( event.count / event.total );  // Number from 0.0 to 1.0
                }
                else {
                    window.addEventListener('load', function () {
                        bar.animate( event.count / event.total );  // Number from 0.0 to 1.0
                    });
                }

            }

            if (event.total == '') {
                document.querySelector('.enroll_section').style.visibility = 'hidden';
            }
            else {
                if (event.count >= event.total) {
                    wrapper.querySelector('#btn').classList.add('inactive');
                }
            }

        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/event?id=" + eventId, true);
xhttp.withCredentials = true; // To send Cookie;
xhttp.send();



// TODO: If admin get list of enrolled
// TODO: Add unenrollment





// https://kimmobrunfeldt.github.io/progressbar.js/
// var ProgressBar = require('scripts/progressbar.js');
function setupBar() {
    bar = new ProgressBar.Line('#container', {
        strokeWidth: 4,
        easing: 'easeInOut',
        duration: 1400,
        color: '#007ac5',
        trailColor: '#eee',
        trailWidth: 1,
        svgStyle: {width: '100%', height: '100%'},
        from: {color: '#007ac5'},
        to: {color: '#ed992f'},
        step: (state, bar) => {
            bar.path.setAttribute('stroke', state.color);
        }
    });
}


var bar;
window.addEventListener('load', function () {
    console.log('Load');

    setupBar();
});





// TODO: Enroll
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');
button.addEventListener('click', function () {

    if (tmp >= 1) // If no places
        return; // TODO: Message


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


                var event = JSON.parse( this.responseText );

                // TODO: Hide when there is no enrollment
                wrapper.querySelector('.count').innerText = event.count + ' / ' + event.total;

                tmp = event.count / event.total;

                if(window.checkLoaded()) {
                    bar.animate( event.count / event.total );  // Number from 0.0 to 1.0
                } else {
                    window.addEventListener('load', function () {
                        bar.animate( event.count / event.total );  // Number from 0.0 to 1.0
                    })
                }


                if (event.count >= event.total) {
                    wrapper.querySelector('#btn').classList.add('inactive');
                }


            }

            if (this.status === 401) {  // Authorization error
                alert("Wrong Phone/Password!");  // TODO: show Html error message
            }

            if (this.status === 405) {  // TODO: No places
                alert("No places");  // TODO: show Html error message
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/enroll?id=" + eventId, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
});

