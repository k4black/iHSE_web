/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



window.addEventListener('load', function () {
    // loadDays(setDays);
    loadDays(function () {checkLoading(function () {setFeedback(); setDays()}, ['feedback', 'days'])});
    loadFeedback('05.06', function () {checkLoading(function () {setFeedback(); setDays()}, ['feedback', 'days'])});
    // TODO: remove '05.06'
    loadNames(setNames);


    document.querySelector('#btn').addEventListener('click', saveFeedback);

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
    for (let day_id in cache['days']) {
        let day = cache['days'][day_id];

        if (!day['feedback'] || day_id == 0) {
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
            document.querySelector('.feedback_title').innerHTML = this.lastElementChild.textContent; // TODO: load title from cache
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
        datalist_html += '<option value="' + cache['names'][id].name + '">';
    }

    document.querySelector('#users_list').innerHTML = datalist_html;
}



function setFeedback() {
    let form = document.querySelector('.feedback_form');

    let template = cache['feedback'].template;
    let data = cache['feedback'].data;
    let feedback_by_event_id = groupByUnique(Object.values(data), 'event_id');

    let events_html = '';

    for (let event of template) {
        let feedback = feedback_by_event_id[event['id']];

        console.log('feedback data for event ' + event, feedback);

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
        let feedback = feedback_by_event_id[event['id']];

        // TODO: check disabled
        for (let feature of ['score', 'entertain', 'useful', 'understand']) {
            let eventSliders = new rSlider({
                target: '#event' + event['id'] + feature,
                values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                range: false,
                set: [(feedback == null ? 5 : feedback[feature])],
                tooltip: false,
                disabled: (feedback == null ? false : true)
            });
        }

        // TODO: check comment
        if (feedback != null) {
            document.querySelector('#event' + event.id + 'comment').disabled = true;
            document.querySelector('#event' + event.id + 'comment').value = feedback['comment'];
        } else {
            document.querySelector('#event' + event.id + 'comment').disabled = false;
            document.querySelector('#event' + event.id + 'comment').value = '';
        }
    }
}




/**
 * Add button event - 'send feedback'
 * Send http POST request to set feedback message
 */
function saveFeedback() {
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

    // Process names
    let names = [];
    for (let user in cache['names']) {
        names.push(user.name);
    }

    let chosen_names = [];
    for (let user of users) {
        let name = user.value;

        if (name in chosen_names) {
            alert('Невозможно выбрать пользователя <' + name + '>. Уже выбран.');
            return;
        }

        if (name in names) {
            chosen_names.push(name);
        } else {
            alert('Невозможно выбрать пользователя <' + name + '>. Нет пользователя.');
            return;
        }
    }

    // Events
    let chosen_events = [];
    for (let event_elem of events) {
        let event_features = event_elem.querySelectorAll('.event_feature');

        let score = {
            'score': event_features[0].lastElementChild.firstElementChild.value,
            'entertain': event_features[1].lastElementChild.firstElementChild.value,
            'useful': event_features[2].lastElementChild.firstElementChild.value,
            'understand': event_features[3].lastElementChild.firstElementChild.value,
            'comment': event_elem.querySelector('textarea').value,
        };

        chosen_events.push(score);
    }


    let data = JSON.stringify({
                                     "users": chosen_names,
                                     "events": chosen_events,
                              });



    let xhttp = new XMLHttpRequest();

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


    let today = document.querySelector('.today').lastElementChild.textContent;
    xhttp.open("POST", "/feedback?date=" + today, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}




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



