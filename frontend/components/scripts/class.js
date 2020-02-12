
loadNames(function () {});



/**
 * Class popup state management
 * Open and close
 */
function showClass() {
    openState = true;
    document.getElementById('class_popup').style.display = 'block';
    // console.log("Open menu");
}

function hideClass() {
    openState = false;
    document.getElementById('class_popup').style.display = 'none';
    // console.log("Close menu");
}




/**
 * Setup progress bar,
 * which display percentage of users enrolled this events
 * https://kimmobrunfeldt.github.io/progressbar.js/
 */
// var ProgressBar = require('scripts/progressbar.js');
function setupBar(val) {
    document.querySelector('#users_progress_bar').innerHTML = '';

    bar = new ProgressBar.Line('#users_progress_bar', {
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

    bar.animate(val);  // Number from 0.0 to 1.0
}









function setupClasses() {
    let class_events = document.querySelectorAll('[active-event]');
    for (let i in class_events) {
        class_events[i].onclick = function (val) {
            cache['class'] = undefined;
            cache['enrolls'] = undefined;

            console.log('clicked event with id: ', class_events[i].getAttribute('data-id'));

            // loadClass(class_events[i].getAttribute('data-id'));
            loadClass(class_events[i].getAttribute('data-id'), function () {checkLoading(function () {
                setEnrolls();
                setClass();
            }, ['class', 'enrolls'])});

            // TODO: Smooth visible

            current_event = class_events[i].getAttribute('data-id');

            // loadEnrolls(class_events[i].getAttribute('data-id'));
            loadEnrollsByClassId(class_events[i].getAttribute('data-id'), function () {checkLoading(function () {
                setEnrolls();
                setClass();
            }, ['class', 'enrolls'])});

            // document.querySelector('#class_popup').style.display = 'block';
            showClass();
        }
    }
}


function setupEnrollButtons() {
    if (user === undefined) {
        document.querySelector('#deenroll').style.display = 'none';
        document.querySelector('#enroll').style.display = 'none';
        return;
    }

    document.querySelector('#enroll').onclick = function (val) {
        createEnroll();
    };
    document.querySelector('#deenroll').onclick = function (val) {
        removeEnrollByUser();
    };

    for (let id in cache['enrolls']) {
        if (cache['enrolls'][id].user_id === user.id) {
            document.querySelector('#deenroll').style.display = 'block';
            document.querySelector('#enroll').style.display = 'none';
            return;
        }
    }

    document.querySelector('#deenroll').style.display = 'none';
    document.querySelector('#enroll').style.display = 'block';
}


function setupData(elem, data) {
    // let elem = document.querySelector(query);
    if (data === '') {
        elem.parentElement.parentElement.style.display = 'none';
    } else {
        elem.innerText = data;
        elem.parentElement.parentElement.style.display = 'flex';
    }
}


/**
 * Set class fields in the popup class info
 */
function setClass() {
    let current_events = cache['events'];
    let event_class = cache['class'];
    let class_id = event_class.id;

    document.querySelector('#class_popup .class_popup__header__title').innerText = current_events[class_id].title;

    setupData(document.querySelector('#class_popup .desc').firstElementChild, current_events[class_id].description);
    setupData(document.querySelector('#class_popup .anno').firstElementChild, event_class.annotation);
    setupData(document.querySelector('#class_popup .time').firstElementChild, current_events[class_id].time.replace('\n', ' - '));
    setupData(document.querySelector('#class_popup .time').lastElementChild, current_events[class_id].date);
    setupData(document.querySelector('#class_popup .location').firstElementChild, current_events[class_id].place);
    setupData(document.querySelector('#class_popup .host').firstElementChild, current_events[class_id].host);

    document.querySelector('#total').value = event_class.total;  // Admin editable field
    document.querySelector('#anno').value = event_class.annotation;  // Admin editable field

    if (cache['user'].type >= 1) {
        document.querySelector('.anno').parentElement.style.display = 'none';
    }

    document.querySelector('#scan').addEventListener('click', function () {
        window.location = '/scan.html?event=' + event_class['id'];
    });
}




let enrolls;
var names;



/**
 * Set enrolls information to class
 * And manage current user attendance
 */
function setEnrolls() {
    let enrolls = cache['enrolls'];

    // Setup buttons enroll/deenroll
    setupEnrollButtons();

    // Count number of attendance
    let attendance = 0;
    for (let i in enrolls) {
        console.log(i, enrolls[i], enrolls[i].attendance);
        attendance += enrolls[i].attendance;
    }
    console.log('enrolls ', enrolls);

    setupData(document.querySelector('#class_popup .count').lastElementChild,attendance + ' посетило; ' + Object.keys(enrolls).length + ' записалсь');


    // TODO: Hide when there is no enrollment (total === 0)
    if (cache['class'].total == 0) {
        document.querySelector('.class_popup__enroll_section').style.display = 'none';
    } else {
        document.querySelector('.class_popup__enroll_section').style.display = 'block';
        

        setupData(document.querySelector('#class_popup .count').firstElementChild, Object.keys(enrolls).length + ' / ' + cache['class'].total);

        console.log(Object.keys(enrolls).length, cache['class'].total, Object.keys(enrolls).length / cache['class'].total);
        setupBar(Object.keys(enrolls).length / cache['class'].total);  // Number from 0.0 to 1.0
    }


    // Check current user's attendance
    let check_user = false;
    for (let id in enrolls) {
        try {
            if (enrolls[id].user_id === user.id) {
                check_user = true;
                break;
            }
        } catch (e) {

        }
    }

    console.log((check_user ? 'Current user enrolled' : 'Current user NOT enrolled'));
    setupData(document.querySelector('#class_popup .status').firstElementChild, (check_user ? 'Вы записаны на мероприятие!' : ''));

    // Set up enrolls on this event
    let users_list = '';
    for (let i in enrolls) {
        let name = names[enrolls[i].user_id];
        let close = '<button class="danger_button"><i class="mobile__item__icon large material-icons">clear</i></button>';
        let checkbox = '<input type="checkbox" ' + (enrolls[i].attendance === 0 || enrolls[i].attendance === '0' ? '' : 'checked') + '>';

        users_list += '<div class="enrolled_user" data-id="'+ enrolls[i].id +'" user-id="' + name.id + '">';

        users_list += '<p>'+ name.name +'</p>' + '<div>' + checkbox + close + '</div>';

        users_list += '</div>';
    }

    document.querySelector('#users_list').innerHTML = users_list;

    let close_list = document.querySelectorAll('#users_list button');
    for (let i = 0; i < close_list.length; ++i) {
        close_list[i].onclick = function (val) {
            if (confirm('You really want to remove user <'+ close_list[i].parentElement.parentElement.firstElementChild.innerText +'> from this event?')) {
                removeEnroll(close_list[i].parentElement.parentElement.getAttribute('data-id'));
            }
        }
    }
}







function createEnroll() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadClass(current_event);
                loadClass(current_event, setClass);
                // loadEnrolls(current_event);
                loadEnrollsByClassId(current_event, setEnrolls);
            } else if (this.status === 401) {
                alert('Невозможно записаться. Нет свободных мест!')
            }
        }
    };

    xhttp.open("POST", "//ihse.tk/create_enroll?" + "event_id="+ current_event + "&user_id=" + user.id, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    // xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}


function removeEnrollByUser() {
    let enroll_id = -1;
    for (let id in enrolls) {
        if (enrolls[id].event_id === current_class.id && enrolls[id].user_id === user.id) {
            enroll_id = id;
        }
    }

    if (enroll_id === -1) {
        alert('Вы не записаны на мероприятие!');
        return;
    }

    removeEnroll(enroll_id);
}


function removeEnroll(enroll_id) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                loadClass(current_event, setClass);
                // loadEnrolls(current_event);
                loadEnrollsByClassId(current_event, setEnrolls);
            }
        }
    };

    xhttp.open("POST", "//ihse.tk/remove_enroll?id=" + enroll_id, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}



function saveEnrolls() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadClass(current_event);
                // loadEnrolls(current_event);
                loadEnrollsByClassId(current_event, setEnrolls);
            }
        }
    };

    let data_raw = [];

    let enroll_list = document.querySelectorAll('#class_popup .users_list .user');
    for (let i = 0; i < enroll_list.length; ++i) {
        console.log(i, enroll_list[i]);

        if (enrolls[enroll_list[i].getAttribute('data-id')].attendance != enroll_list[i].children[1].firstChild.checked) {
            // Enroll status changed

            console.log('New status for ', enroll_list[i].getAttribute('user-id'), ' is ', enroll_list[i].children[1].firstChild.checked);

            let status = (enroll_list[i].children[1].firstChild.checked ? 1 : 0);

            data_raw.push({
                'id': enroll_list[i].getAttribute('data-id'),
                'event_id': current_event,
                'user_id': enroll_list[i].getAttribute('user-id'),
                'attendance': status
            });
        }

    }

    if (data_raw.length === 0) {
        return;
    }


    let data = JSON.stringify(data_raw);

    xhttp.open("POST", "//ihse.tk/mark_enrolls?", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}


function saveClass() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                loadClass(current_event, setClass);
                // loadEnrolls(current_event);
            }
        }
    };

    let total = document.querySelector('#total').value;
    let anno = document.querySelector('#anno').value;

    if (cache['class'].annotation === anno && cache['class'].total === total) {
        return;
    }

    if (total !== '')
        cache['class'].total = total;
    if (total !== '')
        cache['class'].annotation = anno;
    let data = JSON.stringify(cache['class']);

    xhttp.open("POST", "//ihse.tk/admin_send_data?" + "table="+'classes', true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}

