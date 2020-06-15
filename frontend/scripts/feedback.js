/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


loadMainResources(
    [
        loadDays,
        loadNames,
        function (x) {loadFeedback('05.06', x)},
    ],
    ['feedback', 'days'],
    [setFeedback, setDays, setNames]
);
runAfterLoading(function () {
    // loadingStart();  // TODO: Check

    document.querySelector('.feedback_title').innerHTML = '05.06'; // TODO: load title from cache
    // TODO: remove '05.06'

    document.querySelector('#btn').addEventListener('click', saveFeedback);
});



/** ===============  LOGIC and REQUESTS  =============== */



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
    let full_year = (new Date().getFullYear());
    let days_of_week = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
    for (let day_id in cache['days']) {  // TODO: Sort years
        let day = cache['days'][day_id];

        if (!day['feedback'] || day_id == 0) {
            ++i;
            continue;
        }

        if (day.date === '05.06') {  // TODO: Today
            topbar_html += '<div class="day today selected">'
        } else if (day.date >= today) {
            topbar_html += '<div class="day disabled">'
        } else {
            topbar_html += '<div class="day">'
        }

        let [dd, mm] = day.date.split('.');
        let date = new Date( mm + '.' + dd + '.' + full_year);
        topbar_html += '<div class="day__num">' + days_of_week[date.getDay()] + '</div>' +
            '<div class="day__name">' + day.date + '</div>' +
            '</div>';

        ++i;
    }


    document.querySelector('.topbar').innerHTML = topbar_html;

    let days_by_date = groupByUnique(Object.values(cache['days']), 'date');

    // Set onclick loading other day
    var days = document.querySelectorAll('.day');
    for (let i = 0; i < days.length; i++) {
        if (days[i].classList.contains('disabled')) {
            continue;
        }

        days[i].addEventListener('click', function() {
            if (this.classList.contains('selected')) {
                return;
            }

            loadingStart();

            let selected = document.querySelector('.selected');
            if (selected != null) {
                selected.classList.remove('selected');
            }

            this.classList.add('selected');

            loadFeedback(this.lastElementChild.textContent, setFeedback);
            document.querySelector('.feedback_title').innerHTML = days_by_date[this.lastElementChild.textContent].date + (days_by_date[this.lastElementChild.textContent].title != '' ? ': ' + days_by_date[this.lastElementChild.textContent].title : '')  // this.lastElementChild.textContent; // TODO: load title from cache
        });
    }
}



/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Loading users in list
 */
function setNames() {
    let names = Object.values(cache['names'])
        .filter(function (x) {return x.id != cache['user'].id})
        .map(function (x) {return x.team + ' ' + x.name})
        .sort();

    let datalist_html = "";
    for (let name of names) {
        datalist_html += '<option value="' + name + '">';
    }

    document.querySelector('#users_list').innerHTML = datalist_html;
}



function setFeedback() {
    let form = document.querySelector('.feedback_form');

    let template = cache['feedback'].template;
    let data = cache['feedback'].data;
    let top = cache['feedback'].top;
    let feedback_by_event_id = groupByUnique(Object.values(data), 'event_id');

    let events_html = '';

    for (let event of template) {
        let feedback = feedback_by_event_id[event['id']];

        console.log('feedback data for event ' + event, feedback);

        events_html +=
            '<div class="event loading__resource" event-id="' + event.id + '">' +
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

    if (events_html == '') {
        events_html = '<div class="no_event"><p>Кажется, что вы не посетили ни одного мероприятия в этот день. Очень жаль</p> &#128549;</div>'
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

    if (top != null) {
        for (let i of [1, 2, 3]) {
            let user = cache['names'][top['chosen_' + i]];
            if (user != null) {
                document.getElementById('user' + i).value = user.team + ' ' + user.name;
            } else {
                document.getElementById('user' + i).value = '# Пользователь Неизвестен';
            }
            document.getElementById('user' + i).disabled = true;
        }
    } else {
        for (let i of [1, 2, 3]) {
            document.getElementById('user' + i).value = '';
            document.getElementById('user' + i).disabled = false;
        }
    }

    if (top == null || data == null) {
        document.getElementById('btn').disabled = false;
        document.getElementById('btn').style.display = 'block';
    } else {
        document.getElementById('btn').disabled = true;
        document.getElementById('btn').style.display = 'none';
    }


    loadingEnd();
}




/**
 * Add button event - 'send feedback'
 * Send http POST request to set feedback message
 */
function saveFeedback() {
    events = document.querySelectorAll('.event');
    users = document.querySelectorAll('.user');

    // Checking full fields
    let flag = false;
    for (let i = 0; !flag && i < events.length; ++i) {
        for (let feature of events[i].querySelectorAll('.event_feature')) {
            let mark = feature.querySelector('input').value;
            console.log(mark);

            if (mark != '5') {
                flag = true;
                break;
            }
        }
    }
    if (!flag) {
        alert('Пожалуйста, оцените все мерприятия!');  // TODO: show Html error message
        return;
    }

    for (let i = 0; !flag && i < users.length; ++i) {
        if (users[i].value === '') {
            alert('Вы должны выбрать 3х человек!');  // TODO: show Html error message
            return;
        }
    }

    // Process names
    let existed_names = Object.values(cache['names']).map(function (x) {return x.name})

    let chosen_names = [];
    for (let user of users) {
        let name = user.value.split(' ').slice(1).join(' ');

        if (name == cache['user'].name) {
            alert('Невозможно выбрать пользователя <' + name + '>. Нельзя выбирать себя.');
            return;
        }

        if (chosen_names.includes(name)) {
            alert('Невозможно выбрать пользователя <' + name + '>. Уже выбран.');
            return;
        }

        if (existed_names.includes(name)) {
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
            'event_id': event_elem.getAttribute('event-id'),
            'score': event_features[0].lastElementChild.firstElementChild.value,
            'entertain': event_features[1].lastElementChild.firstElementChild.value,
            'useful': event_features[2].lastElementChild.firstElementChild.value,
            'understand': event_features[3].lastElementChild.firstElementChild.value,
            'comment': event_elem.querySelector('textarea').value,
        };

        chosen_events.push(score);
    }


    let data = JSON.stringify({"users": chosen_names, "events": chosen_events});



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
                alert("Вы уже отправляли отзыв в на этот день.");  // TODO: show Html error message
            }
        }
    };


    let date = document.querySelector('.selected').lastElementChild.textContent;
    xhttp.open("POST", "/feedback?date=" + date, true);
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



