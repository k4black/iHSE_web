/**
 * @fileoverview Index page logic
 * File providing all functions which are used to control index.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


// TODO: Hide .html
// ihse.tk/login.html -> ihse.tk/login





/** ===============  LOGIC and REQUESTS  =============== */




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

    bar.animate( 0.8 );  // Number from 0.0 to 1.0
}


var bar;


window.addEventListener('load', function () {
    console.log('Load');

    // Get today date
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!

    if (today.getDate() < 5 || today.getMonth() + 1 < 6)
        today = '05.06';
    else
        today = dd + '.' + mm;


    loadDay(today);

    // setupBar(0.8);
});


function setupClasses() {
    let class_events = document.querySelectorAll('[data-id]');
    for (let i in class_events) {
        class_events[i].onclick = function (val) {
            console.log('clicked event with id: ', class_events[i].getAttribute('data-id'));

            loadClass(class_events[i].getAttribute('data-id'));
            document.querySelector('#class_popup').style.display = 'block';

            // TODO: Smooth visible
        }
    }
}


function loadClass(class_id) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                let event_class = JSON.parse( this.responseText );
                console.log(event_class);

                document.querySelector('#class_popup .title').innerText = current_events[class_id].title;
                wrapper.querySelector('#class_popup .time').firstElementChild.innerText = current_events[class_id].time;
                wrapper.querySelector('#class_popup .time').lastElementChild.innerText = current_events[class_id].date;
                wrapper.querySelector('#class_popup .location').firstElementChild.innerText = current_events[class_id].place;
                wrapper.querySelector('#class_popup .host').firstElementChild.innerText = current_events[class_id].host;
                wrapper.querySelector('#class_popup .desc').firstElementChild.innerText = current_events[class_id].description;


                if (event_class.anno === undefined) {
                    wrapper.querySelector('#class_popup .anno').parentElement.innerHTML = "";
                    wrapper.querySelector('#class_popup .anno').parentElement.style.display = 'none';
                }
                else {
                    wrapper.querySelector('#class_popup .anno').firstElementChild.innerText = event_class.anno;
                }

                // TODO: Hide when there is no enrollment
                if (event_class.total == undefined || event_class.total == "" || event_class.total === '0' || event_class.total === '0') {
                    document.querySelector('.enroll_section').style.visibility = 'hidden';
                } else {
                    wrapper.querySelector('#class_popup .count').innerText = event_class.count + ' / ' + event_class.total;

                    setupBar(event_class.count / event_class.total);  // Number from 0.0 to 1.0

                    if (event_class.count >= event_class.total) {
                        wrapper.querySelector('#btn').classList.add('inactive');
                    }
                }

            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/class?id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


let enrolls_raw;
function loadEnrolls(class_id) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                loadingEventEnd();

                enrolls_raw = JSON.parse( this.responseText );
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/enrolls?id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}






var current_events;

/**
 * Get day information from server
 * Send http GET request and get today json schedule
 * than parse of json data and create html
 */
function loadDay(day) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            loadingEnd(); // TODO: Check

            var day_data = JSON.parse( this.responseText );

            current_events = {};
            for (let time of day_data) {
                for (let event of time.events) {
                    current_events[event.id] = event;
                }
            }


            var day_html = "";
            var time_html;
            var event_html;

            for (let time of day_data) {
                time_html = '<div class="time">' +
                                '<div class="bar">' + time.time + '</div>' +
                                    '<div class="events">';

                for (let event of time.events) {
                    event_html =
                        '<div class="event" data-id="' + event.id + '" ' + (event.type === 0 || event.type === '0' ? '' : 'active-event') + '>' +
                            // (event.type === 0 || event.type === '0' ? '' : '<a href="event.html?id=' + event.id + '">') +
                                '<p class="event__title">' + event.title + '</p>' +

                                (event.desc === undefined ? "" : '<p class="event__desc">' + event.desc + '</p>') +

                                ((event.host === undefined || event.host === '') && (event.loc === undefined || event.loc === '') ? "" : '<div class="event__last_line">' +
                                    '<span class="event__names">' + (event.host === undefined ? "" : event.host) + '</span>' +
                                    '<span class="event__loc">' + (event.loc === undefined ? "" : event.loc) + '</span>' +
                                '</div>') +
                            // (event.type === 0 || event.type === '0' ? '' : '</a>') +
                        '</div>';

                    time_html += event_html;
                }

                time_html += '</div>' + '</div>';
                time_html += '<hr class="border_line">';

                day_html += time_html;
            }

            document.querySelector('.calendar__day').innerHTML = day_html;  // Set day html


            setupClasses();
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/day?day=" + day, true);
    xhttp.send();
}

