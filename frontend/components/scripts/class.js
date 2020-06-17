

loadNames(function () {});  // TODO: Check





/**
 * Class popup state management
 * Open and close
 */
function showClass(event_id = undefined) {
    openState = true;
    // document.getElementById('class_popup').style.display = 'block';
    document.getElementById('class_popup').classList.add('active');

    // console.log("Open menu");
    setQueryParam('event_id', event_id);
}

function hideClass() {
    openState = false;
    // document.getElementById('class_popup').style.display = 'none';
    document.getElementById('class_popup').classList.remove('active');
    // console.log("Close menu");
    removeQueryParam('event_id');
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








function startClassLoading() {
    let loader = document.getElementsByClassName('class_popup__loading')[0];
    loader.style.display = 'flex';
    loader.nextElementSibling.style.display = 'none';
}

function endClassLoading() {
    let loader = document.getElementsByClassName('class_popup__loading')[0];
    loader.style.display = 'none';
    loader.nextElementSibling.style.display = 'block';
}



function setupClasses() {
    console.log('setupClasses');
    let class_events = document.querySelectorAll('[active-event]');
    for (let i = 0;  i < class_events.length; ++i) {
        // console.log('setupClass', class_events[i]);

        class_events[i].onclick = function (val) {
            console.log('Clicked on', val);

            if (val.target.tagName == 'BUTTON' || val.target.tagName == 'I') {
                return;  // To not to click on other buttons
            }

            cache['class'] = undefined;
            cache['enrolls'] = undefined;

            console.log('clicked event with id: ', class_events[i].getAttribute('data-id'));

            // Pre setup class title
            console.log('class', class_events[i].getElementsByClassName('event__title')[0])
            document.querySelector('#class_popup .class_popup__header__title').innerText = class_events[i].getElementsByClassName('event__title')[0].textContent;
            document.querySelector('#class_popup .class_popup__dummy_header__title').innerText = class_events[i].getElementsByClassName('event__title')[0].textContent;

            // loadClass(class_events[i].getAttribute('data-id'));
            startClassLoading();
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
            showClass(class_events[i].getAttribute('data-id'));
        }
    }
}


function setupEnrollButtons() {
    if (cache['user'] == null) {
        console.warn('No user');
        document.getElementById('deenroll').style.display = 'none';
        document.getElementById('enroll').style.display = 'none';
        return;
    }

    document.getElementById('enroll').onclick = function (val) {
        createEnroll();
    };
    document.getElementById('deenroll').onclick = function (val) {
        removeEnrollByUser();
    };

    for (let id in cache['enrolls']) {
        if (cache['enrolls'][id].user_id === user.id) {
            document.getElementById('deenroll').style.display = 'block';
            document.getElementById('enroll').style.display = 'none';
            return;
        }
    }

    document.getElementById('deenroll').style.display = 'none';
    document.getElementById('enroll').style.display = 'block';
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
    document.querySelector('#class_popup .class_popup__dummy_header__title').innerText = current_events[class_id].title;

    setupData(document.querySelector('#class_popup .desc').firstElementChild, current_events[class_id].description);
    setupData(document.querySelector('#class_popup .anno').firstElementChild, event_class.annotation);
    setupData(document.querySelector('#class_popup .time').firstElementChild, current_events[class_id].time.replace('\n', ' - '));
    let selected_day = document.querySelector('.selected');
    setupData(document.querySelector('#class_popup .time').lastElementChild, selected_day == null ? getToday() : selected_day.lastElementChild.textContent);
    setupData(document.querySelector('#class_popup .location').firstElementChild, current_events[class_id].place);
    setupData(document.querySelector('#class_popup .host').firstElementChild, current_events[class_id].host);

    document.querySelector('#total').value = event_class.total;  // Admin editable field
    document.querySelector('#anno').value = event_class.annotation;  // Admin editable field

    if (cache['user'] != null && cache['user'].type >= 1) {
        document.querySelector('.anno').parentElement.style.display = 'none';
    }

    document.querySelector('#scan').addEventListener('click', function () {
        window.location = '/admin/scan.html?event=' + event_class['id'];
    });


    endClassLoading();
}




let enrolls;


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


    // Check current user's attendance
    let check_user = false;
    let attend_user = false;
    for (let id in enrolls) {
        try {
            if (enrolls[id].user_id === user.id) {
                check_user = true;
                if (enrolls[id].attendance) {
                    attend_user = true;
                }
                break;
            }
        } catch (e) {

        }
    }


    // Hide when there is no enrollment (total === 0)
    if (cache['class'].total == 0 && (cache['user'] == null || cache['user'].user_type == 0)) {
        document.querySelector('.class_popup__enroll_section').style.display = 'none';
    } else {
        document.querySelector('.class_popup__enroll_section').style.display = 'block';

        if (cache['class'].total != 0) {
            setupData(document.querySelector('#class_popup .count').firstElementChild, Object.keys(enrolls).length + ' / ' + cache['class'].total);
            console.log(Object.keys(enrolls).length, cache['class'].total, Object.keys(enrolls).length / cache['class'].total);
            setupBar(Object.keys(enrolls).length / cache['class'].total);  // Number from 0.0 to 1.0
        } else {
            setupData(document.querySelector('#class_popup .count').firstElementChild, Object.keys(enrolls).length + ' / ∞');
            setupBar(0);  // Number from 0.0 to 1.0
        }

    }



    console.log((check_user ? 'Current user enrolled' : 'Current user NOT enrolled'));
    // setupData(document.querySelector('#class_popup .status').firstElementChild, (check_user ? 'Вы записаны на мероприятие!' : ''));


    // Drop buttons
    document.getElementById('deenroll').style.display = 'none';
    document.getElementById('enroll').style.display = 'none';

    // Set status of enrolls
    for (let e of document.querySelectorAll('.enroll_alert')) {e.style.display = 'none';}

    if (cache['user'] == null) {
        return;
    }

    if (attend_user) {
        document.querySelector('.enroll_visited_alert').style.display = 'block';
    } else

    if (cache['class'].total != 0) {
        let date = cache['days'][cache['events'][cache['class'].id].day_id].date;

        if (cache['today'] == date) {
            console.log('today event!');

            let event_time = cache['events'][cache['class'].id].time.split('\n')[0];
            let date = new Date();
            date.setMinutes(date.getMinutes() + 15);
            let current_time_15 = date.toLocaleTimeString('en-GB', { hour12: false,
                                             hour: "numeric",
                                             minute: "numeric"}).split(':').join('.');

            console.warn('event_time', event_time);
            console.warn('current_time + 15', current_time_15);

            if (check_user) {
                document.querySelector('.enroll_enrolled_alert').style.display = 'block';
                document.getElementById('deenroll').style.display = 'block';
            }
            if (current_time_15 < event_time) {
                document.querySelector('.enroll_15_alert').style.display = 'block';

                document.getElementById('enroll').style.display = 'block';
                if (check_user) {
                    document.getElementById('deenroll').style.display = 'block';
                }
            } else {
                if (!check_user) {
                    document.querySelector('.enroll_close_alert').style.display = 'block';
                } else {
                    document.getElementById('deenroll').style.display = 'none';
                }
            }
        } else if (cache['today'] < date) {
            document.querySelector('.enroll_day_alert').style.display = 'block';
        } else if (cache['today'] > date) {
            if (check_user) {
                if (attend_user) {
                    document.querySelector('.enroll_visited_alert').style.display = 'block';
                } else {
                    document.querySelector('.enroll_lost_alert').style.display = 'block';
                }
            }
        }
    }


    // If not admin - exit
    if (cache['user'] == null || cache['user'].user_type == 0) {
        return;
    }


    // Set up enrolls on this event
    let users_list = '';
    for (let i in enrolls) {
        let name = cache['names'][enrolls[i].user_id];
        let close = '<button class="danger_button"><i class="mobile__item__icon large material-icons">clear</i></button>';
        let checkbox = '<input type="checkbox" ' + (enrolls[i].attendance === false || enrolls[i].attendance === 'false' ? '' : 'checked') + '>';

        users_list += '<div class="enrolled_user" data-id="'+ enrolls[i].id +'" user-id="' + name.id + '">';

        users_list += '<p>'+ name.name + ' [' + name.team +']</p>' + '<div>' + checkbox + close + '</div>';

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
                alert('Запись невозможна. \nНет свободных мест!');
            } else if (this.status === 410) {
                alert('Запись невозможна. \nЭто можно сделать только в день мероприятия. \nЗапись закрывается за 15 минут до времени начала.');
            }
        }
    };

    xhttp.open("POST", "/create_enroll?" + "event_id="+ current_event + "&user_id=" + user.id, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    // xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}


function removeEnrollByUser() {
    let enroll_id = null;
    let enrolls = cache['enrolls'];
    for (let id in enrolls) {
        if (enrolls[id].class_id == cache['class'].id && enrolls[id].user_id == cache['user'].id) {
            enroll_id = id;
            break;
        }
    }

    if (enroll_id == null) {
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
            } else if (this.status === 410) {
                alert('Удалить запись невозможно. \nЭто можно сделать Только за 15 минут до мероприятия.');
            }
        }
    };

    xhttp.open("POST", "/remove_enroll?id=" + enroll_id, true);
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

            let status = (enroll_list[i].children[1].firstChild.checked ? true : false);

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

    xhttp.open("POST", "/mark_enrolls?", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}


function saveClass() {
    console.warn('SaveClass');
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
        alert('Ничего не изменилось. Нужно поменять аннотацию или класс чтобы сохранить класс.')
        return;
    }

    if (total !== '')
        cache['class'].total = total;
    cache['class'].annotation = anno;

    let data = JSON.stringify(cache['class']);

    xhttp.open("POST", "/admin_send_data?" + "table="+'classes', true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}

