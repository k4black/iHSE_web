/**
 * @fileoverview Calendar page logic
 * File providing all functions which are used to control calendar.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




// {
//     loadMainResources(
//         [
//             loadDays,
//             function (x) {loadDay('', x)},
//         ],
//         ['events', 'days'],
//         [setDay]
//     );
// }
// runAfterLoading(function () {
//     // setupBar(0.8);
//     // document.querySelector('#save').onclick = function (val) {
//     //     saveEnrolls();
//     //     saveClass();
//     // };
// });



/** ===============  LOGIC and REQUESTS  =============== */





function setUsers() {
    let users = cache['users'];

    let options_html = '';
    for (let user_id in users) {
        if (users[user_id].type != 0) {
            options_html += '<option>' + users[user_id].name + '</option>'
        }
    }
    document.getElementById('names_datalist').innerHTML = options_html;
}






var days;

function addDay() {
    console.log('adding day');
}


setupDays();
function setupDays() {   // TODO: Refactor
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let days_raw = JSON.parse( this.responseText );

            cache['days'] = groupByUnique(days_raw['days'], 'id');
            cache['today'] = days_raw['today'];

            let days_list = [];
            for (let day_id in cache['days']) {
                days_list.push(cache['days'][day_id].date);
            }

            let today = getToday();
            if (days_list.includes(today)) {
                today = today;
            } else {
                today = days_list[0];
            }

            let topbar_html = '';
            let i = 0;
            let full_year = (new Date().getFullYear());
            let days_of_week = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
            for (let day_id in cache['days']) {
                let day = cache['days'][day_id];

                if (day.id == 0) {
                    ++i;
                    continue;
                }


                let selected_date = getQueryParam('date');
                if (selected_date == undefined) {
                    selected_date = today;
                }
                if (day.date === today) {  // TODO: Today
                    topbar_html += '<div class="day today ' + (day.date === selected_date ? 'selected' : '') + '">'
                } else if (day.date < today) {
                    topbar_html += '<div class="day disabled ' + (day.date === selected_date ? 'selected' : '') + '">'
                } else {
                    topbar_html += '<div class="day ' + (day.date === selected_date ? 'selected' : '') + '">'
                }

                let [dd, mm] = day.date.split('.');
                let date = new Date( mm + '.' + dd + '.' + full_year);
                // console.log(mm + '.' + dd + full_year, '=', date);
                topbar_html += '<div class="day__num">' + days_of_week[date.getDay()] + '</div>' +
                    '<div class="day__name">' + day.date + '</div>' +
                    '</div>';

                ++i;
            }


            topbar_html += '<div class="admin_element day add_day"> <div class="day__num">' +
                '<i class="mobile__item__icon large material-icons">add</i>' + '</div>' +
                    '<div class="day__name">' + 'add_day' + '</div>' +
                    '</div>';

            document.querySelector('.topbar').innerHTML = topbar_html;


            // Set onclick loading other day
            var days = document.querySelectorAll('.day');
            for (let i = 0; i < days.length; i++) {
                days[i].addEventListener('click', function() {
                    if (this.classList.contains('selected')) {
                        return;
                    }

                    loadingStart();

                    if (this.classList.contains('add_day')) {
                        addDay();
                    } else {
                        document.querySelector('.selected').classList.remove('selected');
                        this.classList.add('selected');

                        loadDay(this.lastElementChild.textContent, setDay);
                        setQueryParam('date', this.lastElementChild.textContent);
                    }
                });
            }

            let date = getQueryParam('date');
            if (date == undefined) {
                date = today;
                setQueryParam('date', today);
            }
            loadDay(date, setDay);
        }
    };

    xhttp.open("GET", "/days", true);
    xhttp.send();
}


var current_events;



/**
 * Read day data from cache and create html schedule
 */
function setDay() {
    loadingEnd(); // TODO: Check

    // TODO: refactor
    // load for admin
    if (cache['user'] != null && cache['user'].user_type != 0){
        loadUsers(setUsers);
        loadPlaces(setPlaces);
    }

    let enrolled_classes_id;
    let attended_classes_id;
    try{
        enrolled_classes_id = Object.values(cache['user'].enrolls).map(function (x) {return x.class_id});
        attended_classes_id = Object.values(cache['user'].enrolls).filter(function (x) {return x.attendance}).map(function (x) {return x.class_id});
    } catch (e) {
        enrolled_classes_id = [];
        attended_classes_id = [];
    }

    let events = Object.values(cache['events']);

    var day_html = "";
    var time_html;
    var event_html;

    let times = groupBy(events, 'time');
    let times_arr = Object.keys(times);
    let processed_times_arr = times_arr.map(function (i) {return (i.length === 4 || i[4] == '\n') ? '0'+i : i}).map(function (i) {return i.length === 10 ? i.slice(0, 6)+'0'+i.slice(6) : i});

    for (let processed_time of processed_times_arr.sort()) {
        let time = processed_time[6] == '0' && processed_time[7] != '0' ? processed_time.slice(0, 6) + processed_time.slice(7) : processed_time;
        time = time[0] === '0' && time[1] !== '0' ? time.slice(1) : time;

        time_html = '<div class="time loading__resource">' +
                        '<div class="bar">' + time + '</div>' +
                            '<div class="events">';

        for (let event of times[time]) {
            let event_type = '';
            if (event.type === 0) {
                event_type = 'regular-event';
            } else if (event.type === 1) {
                event_type = 'master-event';
            } else if (event.type === 2) {
                event_type = 'lecture-event';
            } else if (event.type === 3) {
                event_type = 'fun-event';
            }

            let enrolled = enrolled_classes_id.includes(event.id);
            let attended = attended_classes_id.includes(event.id);
            // TODO: add missed


            event_html =
                '<div class="event" data-id="' + event.id + '" ' + (event.type === 0 || event.type === 3 ? '' : 'active-event') + ' ' + event_type + '>' +
                    // '<button class="admin_element remove_event"><i class="fa fa-times"></i></button>' +
                    '<button class="admin_element remove_event"><i class="material-icons">close</i></button>' +
                    // '<button class="admin_element edit_event"><i class="fa fa-wrench"></i></button>' +
                    '<button class="admin_element edit_event"><i class="material-icons" style="font-size:20px">build</i></button>' +
                    '<button class="admin_element copy_event"><i class="material-icons" style="font-size:20px">file_copy</i></button>' +
                    (enrolled || attended ? '<i class="enroll_icon mobile__item__icon large material-icons">' + (attended ? 'alarm_on' : 'alarm') + '</i>' : '') +

                    '<p class="event__title">' + event.title + '</p>' +

                    (event.description === undefined ? "" : '<p class="event__desc">' + event.description + '</p>') +

                    ((event.host === undefined || event.host === '') && (event.place === undefined || event.place === '') ? "" : '<div class="event__last_line">' +
                        '<span class="event__names">' + (event.host === undefined ? "" : event.host) + '</span>' +
                        '<span class="event__loc">' + (event.place === undefined ? "" : event.place) + '</span>' +
                    '</div>') +
                '</div>';


            time_html += event_html;
        }

        time_html += '<button class="admin_element add_event_button"><i class="material-icons">add</i></button>';
        time_html += '</div>' + '</div>';

        time_html += '<div class="border_wrapper">' + '<hr class="border_line">' + '<button class="admin_element add_time_button"><i class="material-icons">add</i></button>' + '</div>';

        day_html += time_html;
    }

    if (Object.keys(cache['events']).length === 0) {
        day_html = '<div class="border_wrapper">' + '<hr class="border_line">' + '<button class="admin_element add_time_button"><i class="material-icons">add</i></button>' + '</div>';
    }

    document.querySelector('.calendar__day').innerHTML = day_html;  // Set day html

    setupClasses();
    if (cache['user'] != null && cache['user'].user_type == 2) {
        console.warn('ADMIN');
        setupAdminButtons();
    }
}









/** ===============  ADMIN EDITING  =============== */


function setupAdminButtons() {
    // document.getElementsByTagName('body')[0].classList.add('admin');

    console.log('setupAdminButtons');
    let popup = document.getElementById('popup');

    let selectedDay = document.getElementsByClassName("day selected")[0].children[1].textContent;


    let removeButtons = document.getElementsByClassName("remove_event");
    console.log('removeButtons ' + removeButtons.length);

    for (let i = 0; i < removeButtons.length; ++i) {
        removeButtons[i].onclick = function () {
            // alert('clicked remove');
            if (confirm('Удалить мероприятие <' + removeButtons[i].parentElement.querySelector('.event__title').innerHTML + '>')) {
                removeEvent(removeButtons[i].parentElement.getAttribute('data-id'));
            }
        }
    }


    let editButtons = document.getElementsByClassName("edit_event");
    for (let i = 0; i < editButtons.length; ++i) {
        editButtons[i].onclick = function () {
            // alert('clicked remove');
            console.log('Edit Event ' + editButtons[i].parentElement.getAttribute('data-id'));
            let id = editButtons[i].parentElement.getAttribute('data-id');

            let type = "0";
            let attributes = Object.values(editButtons[i].parentElement.attributes).map(function (i) {return i.name});
            // console.log('attributes', 'class' in attributes);
            if (attributes.includes('master-event')) {
                type = "1";
            } else if (attributes.includes('lecture-event')) {
                type = "2";
            } else if (attributes.includes('fun-event')) {
                type = "3";
            }

            let title = editButtons[i].parentElement.getElementsByClassName('event__title')[0].textContent;
            let desc = editButtons[i].parentElement.getElementsByClassName('event__desc');
            desc = desc.length === 0 ? "" : desc[0].textContent;
            let names = editButtons[i].parentElement.getElementsByClassName('event__names');
            names = names.length === 0 ? "" : names[0].textContent;
            let loc = editButtons[i].parentElement.getElementsByClassName('event__loc');
            loc = loc.length === 0 ? "" : loc[0].textContent;

            let times = editButtons[i].parentElement.parentElement.parentElement.getElementsByClassName('bar')[0].textContent.split('\n');

            console.log(id + title + desc + names + loc);

            openEditEvent(id, title, type, selectedDay, times[0], times[1] === undefined ? "" : times[1], desc, names, loc);
        }
    }


    let copyButtons = document.getElementsByClassName("copy_event");
    for (let i = 0; i < copyButtons.length; ++i) {
        copyButtons[i].onclick = function () {
            // alert('clicked remove');
            console.log('Copy Event ' + copyButtons[i].parentElement.getAttribute('data-id'));

            let type = "0";
            let attributes = Object.values(editButtons[i].parentElement.attributes).map(function (i) {return i.name});
            // console.log('attributes', 'class' in attributes);
            if (attributes.includes('master-event')) {
                type = "1";
            } else if (attributes.includes('lecture-event')) {
                type = "2";
            } else if (attributes.includes('fun-event')) {
                type = "3";
            }

            let title = copyButtons[i].parentElement.getElementsByClassName('event__title')[0].textContent;
            let desc = copyButtons[i].parentElement.getElementsByClassName('event__desc');
            desc = desc.length === 0 ? "" : desc[0].textContent;
            let names = copyButtons[i].parentElement.getElementsByClassName('event__names');
            names = names.length === 0 ? "" : names[0].textContent;
            let loc = copyButtons[i].parentElement.getElementsByClassName('event__loc');
            loc = loc.length === 0 ? "" : loc[0].textContent;

            let times = copyButtons[i].parentElement.parentElement.parentElement.getElementsByClassName('bar')[0].textContent.split('\n');

            console.log(id + title + desc + names + loc);

            openEditEvent('', title, type, selectedDay, times[0], times[1] === undefined ? "" : times[1], desc, names, loc);
        }
    }


    let createButtons = document.getElementsByClassName("add_event_button");

    for (let i = 0; i < createButtons.length; ++i) {
        createButtons[i].addEventListener('click', function () {
            let times = createButtons[i].parentElement.previousElementSibling.textContent.split('\n');

            let type = "0";
            let attributes = Object.values(createButtons[i].previousElementSibling.attributes).map(function (i) {return i.name});
            // console.log('attributes', 'class' in attributes);
            if (attributes.includes('master-event')) {
                type = "1";
            } else if (attributes.includes('lecture-event')) {
                type = "2";
            } else if (attributes.includes('fun-event')) {
                type = "3";
            }
            console.log('Create Event. type:' + type + ' [' + times[0] + "," + times[1] + "]");

            openCreateEvent(selectedDay, type, times[0], times[1] === undefined ? "" : times[1]);
        });
    }


    let addTimeButtons = document.getElementsByClassName("add_time_button");
    for (let i = 0; i < addTimeButtons.length; ++i) {
        let startTime;
        try {
            if (addTimeButtons[i].parentElement.previousSibling.classList[0] === 'time') {
                let times = addTimeButtons[i].parentElement.previousSibling.children[0].textContent.split('\n');
                startTime = times === undefined || times.length < 2 ? '' : times[1];
            } else {
                startTime = '';
            }
        } catch (err) {
            startTime = '';
        }

        addTimeButtons[i].addEventListener('click', function () {
            openCreateEvent(selectedDay, '0', startTime, '');
        });
    }
}


function openEditEvent(id, title, type, date, time1, time2, desc, names, location) {
    document.getElementById('id').value = id;
    document.getElementById('title').value = title;
    document.getElementById('type').value = type;
    document.getElementById('date').value = date;
    document.getElementById('time1').value = time1;
    document.getElementById('time2').value = time2;
    document.getElementById('desc').value = desc;
    document.getElementById('names').value = names;
    document.getElementById('location').value = location;

    popup.style.display = 'block';
}

function openCreateEvent(date, type, time1, time2) {
    console.log('create event');
    openEditEvent('', '', type, date, time1, time2, '', '', '');
}

function saveEvent() {
    console.log('Save event');

    let id = document.getElementById('id').value;
    let title = document.getElementById('title').value;
    let type = document.getElementById('type').value;
    let date = document.getElementById('date').value;
    let time = document.getElementById('time1').value + (document.getElementById('time2').value === '' ? '' : '\n') + document.getElementById('time2').value;
    let desc = document.getElementById('desc').value;
    let names = document.getElementById('names').value;
    let location = document.getElementById('location').value;

    // alert('Saving event: ' + id + ' ' + title + ' ' + type + ' ' + date + ' ' + time + ' ' + desc + ' ' + names + ' ' + location);

    if (title === '' || date === '' || time === '') {
        alert('Cannot save with empty TITLE or DATE or TIME');
        return;
    }

    let data = JSON.stringify({
                                "id": id,
                                "title": title,
                                "type": type === '' ? 0 : type,
                                "date": date,
                                "time": time,
                                "description": desc,
                                "host": names,
                                "place": location,
                                });


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            // setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            // setLoaded();
            let selectedDay = document.getElementsByClassName("day selected")[0].children[1].textContent;

            if (this.status === 200) {  // Got it
                console.log("Event created;");
            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("Cannot save event! NO PERMISSIONS");  // TODO: show Html error message
            }

            loadDay(selectedDay, setDay);
            setQueryParam('date', selectedDay);
        }
    };

    xhttp.open("POST", "/admin_send_data?" + "table="+'events', true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}


function removeEvent(id) {
    console.log('Remove event _ ' + id);

    if (id === undefined || id === '') {
        console.log('Cannot delete event with empty ID');
        alert('Cannot delete event with empty ID');
        return;
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            // setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            // setLoaded();
            let selectedDay = document.getElementsByClassName("day selected")[0].children[1].textContent;

            if (this.status === 200) {  // Got it
                alert("ok!");
            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("Cannot remove event! NO PERMISSIONS");  // TODO: show Html error message
            }

            loadDay(selectedDay, setDay);
            setQueryParam('date', selectedDay);
        }
    };


    xhttp.open("POST", "/admin_remove_data?" + "table="+'events' + "&id=" + id, true);
    // xhttp.open("GET", "/remove_event" + "?id=" + id, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}







/**
 * Get user information from server
 * Save list to global 'cache['users']'
 *
 * Run func on OK status
 */
function loadUsers(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                let users = JSON.parse(this.responseText);
                let objs = groupByUnique(users, 'id');

                cache['users'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "/admin_get_table?" + "table=" + 'users', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}

/**
 * Get places information from server
 * Save list to global 'cache['places']'
 *
 * Run func on OK status
 */
function loadPlaces(func) {
    console.log('LOAD PLACES')
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                let places;
                try {
                    places = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error', e);
                    places = []
                }

                cache['places'] = places;

                func();
            }
        }
    };

    xhttp.open("GET", "/admin_get_places", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


/**
 * Loading places in list
 */
function setPlaces() {
    let datalist_html = "";

    for (let place of cache['places']) {
        datalist_html += '<option value="' + place + '">';
    }

    document.querySelector('#places_datalist').innerHTML = datalist_html;
}
