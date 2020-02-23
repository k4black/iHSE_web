/**
 * @fileoverview Index page logic
 * File providing all functions which are used to control index.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


// TODO: Hide .html
// ihse.tk/login.html -> ihse.tk/login

var current_event = 0;





/** ===============  LOGIC and REQUESTS  =============== */





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

    // loadNames(function () {});
    loadDay(today, setDay);

    // setupBar(0.8);

    document.querySelector('#save').onclick = function (val) {
        saveEnrolls();
        saveClass();
    };
});




var current_class;


/**
 * Read day data from cache and create html schedule
 */
function setDay() {
    loadingEnd(); // TODO: Check

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

        time_html = '<div class="time">' +
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

            event_html =
                '<div class="event" data-id="' + event.id + '" ' + (event.type === 0 ? '' : 'active-event') + ' ' + event_type + ' >' +
                    // (event.type === 0 || event.type === '0' ? '' : '<a href="class.html?id=' + event.id + '">') +
                        '<p class="event__title">' + event.title + '</p>' +

                        (event.description === undefined ? "" : '<p class="event__desc">' + event.description + '</p>') +

                        ((event.host === undefined || event.host === '') && (event.place === undefined || event.place === '') ? "" : '<div class="event__last_line">' +
                            '<span class="event__names">' + (event.host === undefined ? "" : event.host) + '</span>' +
                            '<span class="event__loc">' + (event.place === undefined ? "" : event.place) + '</span>' +
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

