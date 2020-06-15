/**
 * @fileoverview Index page logic
 * File providing all functions which are used to control index.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


// TODO: Hide .html
// ihse.tk/login.html -> ihse.tk/login

var current_event = 0;


{
    loadMainResources(
        [
            function (x) {loadDay('', x)},
        ],
        ['events'],
        [setDay]
    );
}
runAfterLoading(function () {
    // setupBar(0.8);
    // document.querySelector('#save').onclick = function (val) {
    //     saveEnrolls();
    //     saveClass();
    // };
});




/** ===============  LOGIC and REQUESTS  =============== */



var current_class;


/**
 * Read day data from cache and create html schedule
 */
function setDay() {
    let current_time = new Date().toLocaleTimeString('en-US', { hour12: false,
                                             hour: "numeric",
                                             minute: "numeric"});
    current_time = current_time.slice(0, 2) + '.' + current_time.slice(3);
    console.log('CURRENT TIME', current_time);

    let enrolled_classes_id = Object.values(cache['user'].enrolls).map(function (x) {return x.class_id});
    let attended_classes_id = Object.values(cache['user'].enrolls).filter(function (x) {return x.attendance}).map(function (x) {return x.class_id});


    let events = Object.values(cache['events']);

    var day_html = "";
    var time_html;
    var event_html;

    let times = groupBy(events, 'time');
    let times_arr = Object.keys(times);
    let processed_times_arr = times_arr.map(function (i) {return (i.length === 4 || i[4] == '\n') ? '0'+i : i}).map(function (i) {return i.length === 10 ? i.slice(0, 6)+'0'+i.slice(6) : i});

    for (let processed_time of processed_times_arr.sort()) {
        let time = processed_time[6] == '0' && processed_time[7] != '0' ? processed_time.slice(0, 6) + processed_time.slice(7) : processed_time;
        let active_time_bool = time.slice(0, 5) > current_time;
        time = time[0] === '0' && time[1] !== '0' ? time.slice(1) : time;


        time_html = (active_time_bool ? '<div class="time active_time">' : '<div class="time inactive_time">')+
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
                '<div class="event" data-id="' + event.id + '" ' + (event.type === 0 || event.type === 3 ? '' : 'active-event') + ' ' + event_type + ' >' +
                    // (event.type === 0 || event.type === '0' ? '' : '<a href="class.html?id=' + event.id + '">') +
                        (enrolled || attended ? '<i class="enroll_icon mobile__item__icon large material-icons">' + (attended ? 'alarm_on' : 'alarm') + '</i>' : '') +

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

    // Scroll to active event time
    try {
        document.getElementsByClassName('active_time')[0].scrollIntoViewIfNeeded(true);
    } catch (e) {
        document.getElementsByClassName('active_time')[0].getElementById('myID').scrollIntoView({
            behavior: 'auto',
            block: 'center',
            inline: 'center'
        });
    }

    loadingEnd(); // TODO: Check
}

