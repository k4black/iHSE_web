/**
 * @fileoverview Calendar page logic
 * File providing all functions which are used to control calendar.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */




var today_date = new Date();
var dd = String(today_date.getDate()).padStart(2, '0');
// var dd = String(today_date.getDate());
var mm = String(today_date.getMonth() + 1).padStart(2, '0'); //January is 0!


if (today_date.getDate() < 5 || today_date.getMonth() + 1 < 6)
    today = '05.06';
else
    today = dd + '.' + mm;


startDay = 5;
startMonth = 6;
numOfDays = 14;

topbar_html = "";

for (var i = 0; i < numOfDays; ++i) {
    let day_text = ('' + (startDay + i)).padStart(2, '0') + '.' + ('' + startMonth).padStart(2, '0');
    if ( day_text === today) {  // TODO: Today
        topbar_html += '<div class="day today selected">'
    } else {
        topbar_html += '<div class="day">'
    }

    topbar_html +=          '<div class="day__num">' + i + '</div>' +
        '<div class="day__name">' + day_text + '</div>' +
        '</div>';
}

document.querySelector('.topbar').innerHTML = topbar_html;






/**
 * Get day information from server by day num
 * Send http GET request and get today json schedule
 * than parse of json data and create html
 */
function getDay(dayNum) {

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            loadingEnd(); // TODO: Check

            var day_data = JSON.parse( this.responseText );


            var day_html = "";
            var time_html;
            var event_html;

            for (let time of day_data) {

                time_html = '<div class="time">' +
                    '<div class="bar">' + time.time + '</div>' +
                    '<div class="events">';

                for (let event of time.events) {
                    // TODO: Add color


                    if (event.type === 'regular') {
                        event_html = '<div class="event" data-id="' + event.id + '">' +
                            '<p class="event__title">' + event.title + '</p>' +

                            (event.desc === undefined ? "" : '<p class="event__desc">' + event.desc + '</p>') +

                            ((event.host === undefined || event.host === '') && (event.loc === undefined || event.loc === '') ? "" : '' +
                                '<div class="event__last_line">' +
                                '<span class="event__names">' + (event.host === undefined ? "" : event.host) + '</span>' +
                                '<span class="event__loc">' + (event.loc === undefined ? "" : event.loc) + '</span>' +
                                '</div>') +
                            '</div>';
                    }
                    else {
                        event_html = '<div class="event" data-id="' + event.id + '" active-event>' +
                            '<button class="admin_element remove_event"><i class="fa fa-times"></i></button>' +
                            '<button class="admin_element edit_event"><i class="fa fa-wrench"></i></button>' +

                            '<a href="event.html?id=' + event.id + '">' +
                                '<p class="event__title">' + event.title + '</p>' +

                                (event.desc === undefined ? "" : '<p class="event__desc">' + event.desc + '</p>') +

                                ((event.host === undefined || event.host === '') && (event.loc === undefined || event.loc === '') ? "" : '' +
                                    '<div class="event__last_line">' +
                                    '<span class="event__names">' + (event.host === undefined ? "" : event.host) + '</span>' +
                                    '<span class="event__loc">' + (event.loc === undefined ? "" : event.loc) + '</span>' +
                                    '</div>') +
                            '</a>' + '</div>';
                    }
                    
                    time_html += event_html;
                }

                time_html += '<button class="admin_element add_event_button">+</button>';

                time_html += '</div>' + '</div>' +
                    '<div class="border_wrapper">' + '<hr class="border_line">' + '<button class="admin_element add_time_button">+</button>' + '</div>';

                day_html += time_html;
            }


            document.querySelector('.calendar__day').innerHTML = day_html;  // Set day html


            setupAdminButtons();
        }
    };


    xhttp.open("GET", "http://ihse.tk:50000/day?day=" + dayNum, true);
    xhttp.send();
}




/**
 * Get day information from server (first time)
 * Send http GET request and get today json schedule
 * than parse of json data and create html
 */
const urlParams = new URLSearchParams(window.location.search);
var dayNum = urlParams.get('day');

getDay( (dayNum != null ? dayNum : today) );






/**
 * Add button event - press topbar
 * Set up day feedback form. GET request to get day data
 */
var days = document.querySelectorAll('.day');
for (let i = 0; i < days.length; i++) {

    days[i].addEventListener('click', function() {


        document.querySelector('.selected').classList.remove('selected');
        this.classList.add('selected');

        getDay(this.lastElementChild.textContent);


        // TODO: set today
    });

}


/** ===============  ADMIN EDITING  =============== */


function setupAdminButtons() {
    console.log('setupAdminButtons');
    let popup = document.getElementById('popup');


    let removeButtons = document.getElementsByClassName("remove_event");
    console.log('removeButtons ' + removeButtons.length);

    for (let i = 0; i < removeButtons.length; ++i) {
        removeButtons[i].addEventListener('click', function () {
            // alert('clicked remove');
            console.log('Remove Event ' + removeButtons[i].parentElement.getAttribute('data-id'));
        });
    }


    let editButtons = document.getElementsByClassName("edit_event");
    console.log('removeButtons ' + removeButtons.length);

    for (let i = 0; i < editButtons.length; ++i) {
        editButtons[i].addEventListener('click', function () {
            // alert('clicked remove');
            console.log('Edit Event ' + editButtons[i].parentElement.getAttribute('data-id'));
            let id = editButtons[i].parentElement.getAttribute('data-id');

            let title = editButtons[i].parentElement.getElementsByClassName('event__title')[0].textContent;
            let desc = editButtons[i].parentElement.getElementsByClassName('event__desc');
            desc = desc.length === 0 ? "" : desc[0].textContent;
            let names = editButtons[i].parentElement.getElementsByClassName('event__names');
            names = names.length === 0 ? "" : names[0].textContent;
            let loc = editButtons[i].parentElement.getElementsByClassName('event__loc');
            loc = loc.length === 0 ? "" : loc[0].textContent;

            let times = editButtons[i].parentElement.parentElement.parentElement.getElementsByClassName('bar')[0].textContent.split('\n');

            console.log(id + title + desc + names + loc);

            openEditEvent(id, title, times[0], times[1] === undefined ? "" : times[1], desc, names, loc);
        });
    }


    let createButtons = document.getElementsByClassName("add_event_button");
    console.log('createEventButtons ' + removeButtons.length);

    for (let i = 0; i < createButtons.length; ++i) {
        createButtons[i].addEventListener('click', function () {
            // alert('clicked remove');
            let times = createButtons[i].parentElement.previousElementSibling.textContent.split('\n');
            console.log('Create Event [' + times[0] + "," + times[1] + "]");

            openCreateEvent(times[0], times[1] === undefined ? "" : times[1]);
        });
    }
}


function openEditEvent(id, title, time1, time2, desc, names, location) {
    document.getElementById('id').value = id;
    document.getElementById('title').value = title;
    document.getElementById('time1').value = time1;
    document.getElementById('time2').value = time2;
    document.getElementById('desc').value = desc;
    document.getElementById('names').value = names;
    document.getElementById('location').value = location;

    popup.style.display = 'block';
}

function openCreateEvent(time1, time2) {
    console.log('create event');
    openEditEvent('', '', time1, time2, '', '', '');
}

function saveEvent() {
    console.log('Save event');

    let id = document.getElementById('id').value;
    let title = document.getElementById('title').value;
    let time = document.getElementById('time1').value + '\n' + document.getElementById('time2').value;
    let desc = document.getElementById('desc').value;
    let names = document.getElementById('names').value;
    let location = document.getElementById('location').value;

    alert('Save event: ' + id + ' ' + title + ' ' + time + ' ' + desc + ' ' + names + ' ' + location);
}

