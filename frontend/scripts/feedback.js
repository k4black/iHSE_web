/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



window.addEventListener('load', function () {
    // loadDays(setDays);
    loadDays(function () {checkLoading(function () {setFeedback(); setDays()}, ['feedback', 'days'])});
    loadFeedback(this.lastElementChild.textContent, function () {checkLoading(function () {setFeedback(); setDays()}, ['feedback', 'days'])});

    loadNames(setNames);
});



/**
 * Create topbar day buttons
 */
function setDays() {
    let today = getToday();

    let days_list = Object.values(cache['days']).map(function (currentValue, index, array) {
        return currentValue['date'];
    });

    if (days_list.includes(today)) {
        today = today;
    } else {
        today = days_list[0];
    }

    let topbar_html = '';
    let i = 0;
    for (let day of cache['days']) {
        if (!day['feedback'] || day.id == 0) {
            ++i;
            continue;
        }

        if (day.date === today) {  // TODO: Today
            topbar_html += '<div class="day today selected">'
        } else {
            topbar_html += '<div class="day">'
        }

        topbar_html += '<div class="day__num">' + i + '</div>' +
            '<div class="day__name">' + day.date + '</div>' +
            '</div>';

        ++i;
    }


    document.querySelector('.topbar').innerHTML = topbar_html;


    // Set onclick loading other day
    var days = document.querySelectorAll('.day');
    for (let i = 0; i < days.length; i++) {
        days[i].addEventListener('click', function() {
            document.querySelector('.selected').classList.remove('selected');
            this.classList.add('selected');

            loadFeedback(this.lastElementChild.textContent, setFeedback);
        });
    }
}



/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Loading users in list
 */
function setNames() {
    let datalist_html = "";

    for (let id in cache['names']) {
        datalist_html += '<option value="' + cache['names'][id] + '">';
    }

    document.querySelector('#users_list').innerHTML = datalist_html;
}



function setFeedback() {
    let form = document.querySelector('.feedback_form');

    let template = cache['feedback'].template;
    let data = cache['feedback'].data;
    let feedback_by_event_id = groupBy(Object.values(data), 'event_id');

    let events_html = '';

    for (let event of template) {
        let feedback = feedback_by_event_id[event['id']][0];

        events_html +=
            '<div class="event">' +
                '<h3>' + event.title + '</h3>' +
                '<p class="host">' + event.host + '</p>' +
                '<div class="event_feature">' +
                    '<label for="event' + event.id + 'score">Общее впечатление</label>' +
                    '<div><input type="text" id="event' + event.id + 'score" class="slider"></div>' +
                '</div>' +

                '<div class="event_feature">' +
                    '<label for="event' + event.id + 'entertain">Интересно</label>' +
                    '<div><input type="text" id="event' + event.id + 'entertain" class="slider"></div>' +
                '</div>' +
                '<div class="event_feature">' +
                    '<label for="event' + event.id + 'useful">Полезно</label>' +
                    '<div><input type="text" id="event' + event.id + 'useful" class="slider"></div>' +
                '</div>' +
                '<div class="event_feature">' +
                    '<label for="event' + event.id + 'understand">Весело</label>' +
                    '<div><input type="text" id="event' + event.id + 'understand" class="slider"></div>' +
                '</div>' +

                '<p>Комментарии и отзывы:</p>' +
                '<div class="form__input feedback__input feedback__input__div">' +
                    '<textarea id="event' + event.id + 'comment" placeholder="Что было плохо? Что сделать лучше?"></textarea>' +
                '</div>' +
            '</div>';
    }

    document.querySelector('.events').innerHTML = events_html;

    // Setup sliders
    for (let event of template) {
        let feedback = feedback_by_event_id[event['id']][0];

        // TODO: disabled

        for (let feature of ['score', 'entertain', 'useful', 'understand']) {
            let eventSliders = new rSlider({
                target: '#event' + event['id'] + feature,
                values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                range: false,
                set: [5],
                tooltip: false,
            });
        }

        // TODO: comment
    }
}







/**
 * Setup sliders
 * https://www.cssscript.com/animated-customizable-range-slider-pure-javascript-rslider-js/
 */
var overallSlider = new rSlider({
    target: '#slider',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false, // range slider
    set:    [5], // an array of preselected values
    scale:    true,
    labels:   true,
    tooltip:  false,
    step:     1, // step size
    disabled: false, // is disabled?
    onChange: null // callback
});


var eventSliders = [];

eventSliders[0] = new rSlider({
    target: '#event1feature1',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});

eventSliders[1] = new rSlider({
    target: '#event1feature2',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});

eventSliders[2] = new rSlider({
    target: '#event1feature3',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});
eventSliders[3] = new rSlider({
    target: '#event1feature4',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});




/**
 * Add button event - 'send feedback'
 * Send http POST request to set feedback message
 */
document.querySelector('#btn').addEventListener('click', function() {

    events = document.querySelectorAll('.event');
    users = document.querySelectorAll('.user');

    // Checking full fields
    var flag = false;
    for (let i = 0; !flag && i < events.length; ++i) {
        flag = (events[i].lastElementChild.textContent === '');
    }
    for (let i = 0; !flag && i < users.length; ++i) {
        flag = (users[i].value === '');
    }
    if (flag){ // If some field are empty - do nothing
        alert('You have to fill all fields!');  // TODO: show Html error message
        return;
    }

    var data = JSON.stringify({"overall": overallSlider.getValue(),
                                     "user1": users[0].value,
                                     "user2": users[1].value,
                                     "user3": users[2].value,
                                     "event1": eventSliders[0].getValue(),
                                     "event2": eventSliders[1].getValue(),
                                     "event3": eventSliders[2].getValue(),
                                     "event1_text": events[0].lastElementChild.textContent,
                                     "event2_text": events[1].lastElementChild.textContent,
                                     "event3_text": events[2].lastElementChild.textContent
                              });


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            setLoaded();

            if (this.status === 200) {  // Got it
                location = "../index.html"
            }

            if (this.status === 302) {  // Ok - redir

            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("not!");  // TODO: show Html error message
            }
        }
    };


    var query = "?day=" + document.querySelector('.today').lastElementChild.textContent;
    xhttp.open("POST", "//ihse.tk/feedback" + query, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);

});




/** ===============  ANIMATIONS  =============== */



/**
 * Show and hide loading button
 */
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');
function setLoading() {
    button.style.display = 'none';
    button2.style.display = 'block';
}

function setLoaded() {
    button.style.display = 'block';
    button2.style.display = 'none';
}



