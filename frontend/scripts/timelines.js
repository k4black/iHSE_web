




var tabs = [];
var current_timeline = 'vacations';



$(function() {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays();


        // timetable.addEvent('Sightseeing', 'Rotterdam', new Date(2015,7,17,9,00), new Date(2015,7,17,11,30), { url: '#' });
    // timetable.addEvent('Zumba', 'Madrid', new Date(2015,7,17,12), new Date(2015,7,17,13), { url: '#' });
    // timetable.addEvent('Zumbu', 'Madrid', new Date(2015,7,17,13,30), new Date(2015,7,17,15), { url: '#' });
    // timetable.addEvent('Lasergaming', 'London', new Date(2015,7,17,17,45), new Date(2015,7,17,19,30), { class: 'vip-only', data: { maxPlayers: 14, gameType: 'Capture the flag' } });
    // timetable.addEvent('All-you-can-eat grill', 'New York', new Date(2015,7,17,21), new Date(2015,7,18,1,30), { url: '#' });
    // timetable.addEvent('Hackathon', 'Tokyo', new Date(2015,7,17,11,30), new Date(2015,7,17,20)); // options attribute is not used for this event
    // timetable.addEvent('Tokyo Hackathon Livestream', 'Los Angeles', new Date(2015,7,17,12,30), new Date(2015,7,17,16,15)); // options attribute is not used for this event
    // timetable.addEvent('Lunch', 'Jakarta', new Date(2015,7,17,9,30), new Date(2015,7,17,11,45), { onClick: function(event) {
    // window.alert('You clicked on the ' + event.name + ' event in ' + event.location + '. This is an example of a click handler');
    // }});
    // timetable.addEvent('Cocktails', 'Rotterdam', new Date(2015,7,18,00,00), new Date(2015,7,18,02,00), { class: 'vip-only' });

    buildTestTimeline();

    // buildSetsTimeline(['Rotterdam', 'Madrid', 'Los Angeles', 'London', 'New York', 'Jakarta', 'Tokyo'], [
    //     {title: 'Sightseeing', place: 'Rotterdam', date: '07.17', time: '09.00\n11.30'},
    //     {title: 'Zumba', place: 'Madrid', date: '07.17', time: '17.00\n13.00'},
    //     {title: 'Zumba', place: 'Madrid', date: '07.17', time: '13.30\n15.30'},
    //     {title: 'Lasergaming', place: 'London', date: '07.17', time: '17.45\n19.30'},
    // ]);
});


function loadDays() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                days = JSON.parse(this.responseText);


                tabs = ['vacations'];
                for (let day of days) {
                    tabs.push(day.date);
                }

                setupTabs();
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/days", true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


function setupTabs() {
    tabs_html = '';
    for (let tab_name of tabs) {
        let name = tab_name.replace('.', '_');
        tabs_html += '<button ' + (name === 'vacations' ? 'class="active_tab"' : '') + ' id="tab_' + name + '">' + tab_name + '</button>';
    }
    $('.tabs')[0].innerHTML = tabs_html;

    for (let tab_name of tabs) {
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
}




var current_events;



function loadAndCreateTimeline(timeline) {  // TODO: refactor
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field

            var day_data = JSON.parse( this.responseText );


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

    xhttp.open("GET", "//ihse.tk/day?day=" + timeline, true);
    xhttp.send();
}



function buildTestTimeline() {
    var timetable = new Timetable();

    timetable.setScope(6, 2);

    timetable.addLocations(['Rotterdam', 'Madrid', 'Los Angeles', 'London', 'New York', 'Jakarta', 'Tokyo']);

    timetable.addEvent('Sightseeing', 'Rotterdam', new Date(2015,7,17,9, 0), new Date(2015,7,17,11,30), { url: '#' });
    timetable.addEvent('Zumba', 'Madrid', new Date(2015,7,17,12), new Date(2015,7,17,13), { url: '#' });
    timetable.addEvent('Zumbu', 'Madrid', new Date(2015,7,17,13,30), new Date(2015,7,17,15), { url: '#' });
    timetable.addEvent('Lasergaming', 'London', new Date(2015,7,17,17,45), new Date(2015,7,17,19,30), { class: 'vip-only', data: { maxPlayers: 14, gameType: 'Capture the flag' } });
    timetable.addEvent('All-you-can-eat grill', 'New York', new Date(2015,7,17,21), new Date(2015,7,18,1,30), { url: '#' });
    timetable.addEvent('Hackathon', 'Tokyo', new Date(2015,7,17,11,30), new Date(2015,7,17,20)); // options attribute is not used for this event
    timetable.addEvent('Tokyo Hackathon Livestream', 'Los Angeles', new Date(2015,7,17,12,30), new Date(2015,7,17,16,15)); // options attribute is not used for this event
    timetable.addEvent('Lunch', 'Jakarta', new Date(2015,7,17,9,30), new Date(2015,7,17,11,45), { onClick: function(event) {
    window.alert('You clicked on the ' + event.name + ' event in ' + event.location + '. This is an example of a click handler');
    }});
    timetable.addEvent('Cocktails', 'Rotterdam', new Date(2015,7,18,0,0), new Date(2015,7,18,2,0), { class: 'vip-only' });

    var renderer = new Timetable.Renderer(timetable);
    renderer.draw('.timetable');
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
            end_hours.push(parseInt(time1.split('.')[0]) + 1);
        } else {
            end_hours.push(parseInt(time2.split('.')[0]));
        }
    }

    console.log(' hour ', start_hours, end_hours, Math.min.apply(Math, start_hours), Math.max.apply(Math, end_hours));

    timetable.setScope(Math.min.apply(Math, start_hours) - 1, Math.max.apply(Math, end_hours) + 1);

    timetable.addLocations(locations);

    for (let i in events) {
        let [month, day] = events[i].date.split('.');
        let [time1, time2] = events[i].time.split('\n');
        console.log('added event ', time1, time2);

        let [hours1, min1] = time1.split('.');
        let hours2, min2;
        if (time2 === undefined) {
            [hours2, min2] = [parseInt(hours1) + 1, min1];
        } else {
            [hours2, min2] = time2.split('.');
        }

        console.log('added event ', month + '.' + day, hours1 + ':' + min1, hours2 + ':' + min2);

        let options = {
            class: (events[i].type === 1 ? 'class' : 'regular'),
            onClick: function (event) {
                if (events[i].type === 1) {
                    console.log('clicked event with id: ', events[i].id);

                    // loadClass(events[i].id);
                    loadClass(events[i].id, setClass);

                    // TODO: Smooth visible

                    current_event = events[i].id;

                    // loadEnrolls(events[i].id);
                    loadEnrollsByClassId(events[i].id, setEnrolls);

                    alert('You clicked on the ' + events[i].id + '=' + events[i].title + ' event in ' + events[i].place + '. This is an example of a click handler');

                    // document.querySelector('#class_popup').style.display = 'block';
                    showClass();
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
