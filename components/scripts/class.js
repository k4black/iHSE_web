


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
            console.log('clicked event with id: ', class_events[i].getAttribute('data-id'));

            loadClass(class_events[i].getAttribute('data-id'));
            // TODO: Smooth visible

            current_event = class_events[i].getAttribute('data-id');

            // loadEnrolls(class_events[i].getAttribute('data-id'));
            loadEnrollsByClassId(class_events[i].getAttribute('data-id'), setEnrolls);

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

    for (let id in enrolls) {
        if (enrolls[id].user_id === user.id) {
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

function loadClass(class_id) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                let event_class = JSON.parse( this.responseText );
                console.log(event_class, current_events[class_id]);

                document.querySelector('#class_popup .class_popup__header__title').innerText = current_events[class_id].title;

                setupData(document.querySelector('#class_popup .desc').firstElementChild, current_events[class_id].description);
                setupData(document.querySelector('#class_popup .time').firstElementChild, current_events[class_id].time.replace('\n', ' - '));
                setupData(document.querySelector('#class_popup .time').lastElementChild, current_events[class_id].date);
                setupData(document.querySelector('#class_popup .location').firstElementChild, current_events[class_id].place);
                setupData(document.querySelector('#class_popup .host').firstElementChild, current_events[class_id].host);
                // if (event_class.anno === undefined) {
                //     document.querySelector('#class_popup .anno').parentElement.innerHTML = "";
                //     document.querySelector('#class_popup .anno').parentElement.style.display = 'none';
                // }
                // else {
                //     document.querySelector('#class_popup .anno').firstElementChild.innerText = event_class.anno;
                // }
                setupData(document.querySelector('#class_popup .count').firstElementChild, event_class.count + ' / ' + event_class.total);

                // setupData(document.querySelector('#class_popup .count').lastElementChild, '2 было; 6 записалсь');

                document.querySelector('#total').value = event_class.total;

                current_class = event_class;

                // // TODO: Hide when there is no enrollment
                // if (event_class.total == undefined || event_class.total == "" || event_class.total === '0' || event_class.total === '0') {
                //     document.querySelector('.enroll_section').style.visibility = 'hidden';
                // } else {
                //     document.querySelector('#class_popup .count').innerText = event_class.count + ' / ' + event_class.total;
                //
                console.log(event_class.count , event_class.total, event_class.count / event_class.total);
                setupBar(event_class.count / event_class.total);  // Number from 0.0 to 1.0
                //
                //     if (event_class.count >= event_class.total) {
                //         document.querySelector('#btn').classList.add('inactive');
                //     }
                // }
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/class?id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


let enrolls;
var names;




function setEnrolls() {
    let enrolls = cache['enrolls'];

    setupEnrollButtons();

    // Count number of attendance
    let attendance = 0;
    for (let i in enrolls_raw) {
        attendance += enrolls_raw[i].attendance;
    }

    setupData(document.querySelector('#class_popup .count').lastElementChild,attendance + ' посетило; ' + enrolls_raw.length + ' записалсь');

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
    for (let i in enrolls_raw) {
        let name = names[enrolls_raw[i].user_id];
        let close = '<button class="danger_button"><i class="mobile__item__icon large material-icons">clear</i></button>';
        let checkbox = '<input type="checkbox" ' + (enrolls_raw[i].attendance === 0 || enrolls_raw[i].attendance === '0' ? '' : 'checked') + '>';

        users_list += '<div class="enrolled_user" data-id="'+ enrolls_raw[i].id +'" user-id="' + name.id + '">';

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



function _loadEnrolls(class_id) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                let enrolls_raw = JSON.parse(this.responseText);
                enrolls = groupByUnique(enrolls_raw, 'id');
                cache['enrolls'] = enrolls;


                setupEnrollButtons();


                let attendance = 0;
                for (let i in enrolls_raw) {
                    attendance += enrolls_raw[i].attendance;
                }

                setupData(document.querySelector('#class_popup .count').lastElementChild,attendance + ' посетило; ' + enrolls_raw.length + ' записалсь');


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


                let users_list = '';


                for (let i in enrolls_raw) {
                    let name = names[enrolls_raw[i].user_id];
                    let close = '<button class="danger_button"><i class="mobile__item__icon large material-icons">clear</i></button>';
                    let checkbox = '<input type="checkbox" ' + (enrolls_raw[i].attendance === 0 || enrolls_raw[i].attendance === '0' ? '' : 'checked') + '>';

                    users_list += '<div class="enrolled_user" data-id="'+ enrolls_raw[i].id +'" user-id="' + name.id + '">';

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
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/enrolls?event_id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


function loadNames() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                let names_raw = JSON.parse(this.responseText);
                names = groupByUnique(names_raw, 'id');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/names", true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}




function createEnroll() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                loadClass(current_event);
                // loadEnrolls(current_event);
                loadEnrollsByClassId(current_event, setEnrolls);
            } else if (this.status === 401) {
                alert('Невозможно записаться. Нет свободных мест!')
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/create_enroll?" + "event_id="+ current_event + "&user_id=" + user.id, true);
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

                loadClass(current_event);
                // loadEnrolls(current_event);
                loadEnrollsByClassId(current_event, setEnrolls);
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/remove_enroll?id=" + enroll_id, true);
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

    xhttp.open("POST", "http://ihse.tk:50000/mark_enrolls?", true);
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
                loadClass(current_event);
                // loadEnrolls(current_event);
            }
        }
    };

    let total = document.querySelector('#total').value;

    if (current_class.total === total) {
        return;
    }

    if (total !== '')
        current_class.total = total;
    let data = JSON.stringify(current_class);

    xhttp.open("POST", "http://ihse.tk:50000/admin_send_data?" + "table="+'classes', true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}

