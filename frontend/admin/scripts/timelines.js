




var tabs = [];
var current_timeline = 'vacations';




{
    let date = getQueryParam('date');
    if (date == null) {
        loadMainResources(
            [
                loadDays
            ],
            ['days'],
            [function () {current_timeline = Object.values(cache['days'])[0].data; setupTabs(current_timeline); loadAndCreateTimeline(current_timeline)}]
        );
    } else {
        loadMainResources(
            [
                loadDays
            ],
            ['days'],
            [function () {current_timeline = date; setupTabs(current_timeline); loadAndCreateTimeline(current_timeline)}]
        );
    }

    loadDays();
}
runAfterLoading(function () {
    // createBar();
});



window.addEventListener('load', function () {
    let date = getQueryParam('date');
    if (date == null) {
        current_timeline = Object.values(cache['days'])[0].data
    } else {
        current_timeline = date;
    }

    loadDays(function () {setupTabs(current_timeline); loadAndCreateTimeline(current_timeline)});
});




function setupTabs(active_tab = null) {
    let tabs_html = '';
    for (let day of Object.values(cache['days'])) {
        let name = day.date.replace('.', '_');
        tabs_html += '<button ' + (day.date === Object.values(cache['days'])[0].date ? 'class="active_tab"' : '') + ' id="tab_' + name + '">' + day.date + '</button>';
    }
    $('.tabs')[0].innerHTML = tabs_html;
    $('.tabs button').removeClass('active_tab');

    for (let day of Object.values(cache['days'])) {
        let tab_name = day.date;

        let name = tab_name.replace('.', '_');
        console.log('setuping tab: ' + name, $('#tab_' + name));

        $('#tab_' + name)[0].onclick = function () {
            current_timeline = tab_name;
            loadAndCreateTimeline(current_timeline);
            $('.tabs button').removeClass('active_tab');
            $('#tab_' + name).addClass('active_tab');
            // setupClasses();
        };
    }
    if (active_tab != null) {
        console.warn('active_tab', active_tab);
        $('#tab_' + active_tab.replace('.', '_')).addClass('active_tab');
    }
}



function loadAndCreateTimeline(timeline) {  // TODO: refactor
    setQueryParam('date', timeline);

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let day_data;
            try {
                day_data = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error', e);
                day_data = [];
            }


            let current_events = {};
            for (let time of day_data) {
                for (let event of time.events) {
                    current_events[event.id] = event;
                }
            }
            cache['events'] = current_events;



            current_events = {};
            let locations_set = new Set();
            let events = [];

            for (let time of day_data) {
                for (let event of time.events) {
                    current_events[event.id] = event;

                    locations_set.add(event.place);
                    events.push(event);
                }
            }

            let locations = [];
            for (let loc of locations_set) {
                locations.push(loc);
            }

            buildTimeline(locations.sort(), events)
        }
    };

    xhttp.open("GET", "/day?day=" + timeline, true);
    xhttp.send();
}



function buildTimeline(locations, events) {
    console.log('Build timeline from ', locations, events);

    var timetable = new Timetable();


    let start_hours = [];
    let end_hours = [];
    for (let event of events) {
        let [time1, time2] = event.time.split('\n');
        start_hours.push(parseInt(time1.split('.')[0]));

        if (time2 === undefined) {
            let end_time = parseInt(time1.split('.')[0]) + 1;
            end_hours.push(end_time == 24 ? 0 : end_time);
        } else {
            end_hours.push(parseInt(time2.split('.')[0]));
        }
    }

    let start_hour = Math.min.apply(Math, start_hours);
    let end_hour = Math.max.apply(Math, end_hours) + 1 == 23 ? 0 : Math.max.apply(Math, end_hours) + 1;


    console.log(' hour ', start_hours, end_hours, start_hour, end_hour, start_hour == Infinity ? 8 : start_hour, -end_hour == Infinity ? 23 : end_hour);

    timetable.setScope(start_hour == Infinity ? 8 : start_hour, -end_hour == Infinity ? 23 : end_hour);
    timetable.addLocations(locations);

    for (let i in events) {
        let [month, day] = cache['days'][events[i].day_id].date.split('.');
        let [time1, time2] = events[i].time.split('\n');
        // console.log('added event ', time1, time2);

        let [hours1, min1] = time1.split('.');
        let hours2, min2;
        if (time2 === undefined) {
            [hours2, min2] = [parseInt(hours1), parseInt(min1) + 30];
            if (min2 >= 60) {
                min2 -= 60;
                hours2 += 1;
            }
        } else {
            [hours2, min2] = time2.split('.');
        }

        // console.log('added event ', month + '.' + day, hours1 + ':' + min1, hours2 + ':' + min2);

        let event_type = '';
        if (events[i].type === 0) {
            event_type = 'regular-event';
        } else if (events[i].type === 1) {
            event_type = 'master-event';
        } else if (events[i].type === 2) {
            event_type = 'lecture-event';
        } else if (events[i].type === 3) {
            event_type = 'fun-event';
        }

        let options = {
            class: event_type,
            onClick: function (event) {
                if (events[i].type === 1 || events[i].type === 2) {
                    // console.log('clicked event with id: ', events[i].id);

                    // loadClass(events[i].id);
                    loadClass(events[i].id, setClass);

                    // TODO: Smooth visible

                    current_event = events[i].id;

                    // loadEnrolls(events[i].id);
                    loadEnrollsByClassId(events[i].id, setEnrolls);

                    // alert('You clicked on the ' + events[i].id + '=' + events[i].title + ' event in ' + events[i].place + '. This is an example of a click handler');

                    // document.querySelector('#class_popup').style.display = 'block';
                    showClass(events[i].id);
                }
            },
            data: {
                id: events[i].id,
            }
        };
        timetable.addEvent(events[i].title, events[i].place, new Date(2020, month - 1, day, hours1, min1), new Date(2020, month - 1, day, hours2, min2), options);
    }


    var renderer = new Timetable.Renderer(timetable);
    renderer.draw('.timetable');
}
