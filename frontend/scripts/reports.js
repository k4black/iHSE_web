


window.addEventListener('load', function () {
    loadDays(setDays);

    loadEvents(function () {});
    loadAllFeedback(function () {});

    loadTop(function () {checkLoading(countTop, ['users', 'top'])});
    loadUsers(function () {checkLoading(countTop, ['users', 'top'])});
});




function setDays() {
    let days = cache['days'];

    let options_html = '<option selected disabled value="">Выбрать день</option>';

    for (let day of days) {
        if (day['feedback'] === true) {
            options_html += '<option value="' + day['id'] + '">' + day['date'] + '</option>'
        }
    }

    document.getElementById('days').innerHTML = options_html;
}



function countTop() {
    let users = cache['users'];
    let top_by_id = cache['top'];


    let top_counter = {};
    for (let user_id in users) {
        top_counter[user_id] = 0;
    }
    for (let top of Object.values(top_by_id)) {
        top_counter[top['chosen_1']]++;
        top_counter[top['chosen_2']]++;
        top_counter[top['chosen_3']]++;
    }

    let top_counter_not_empty = {};
    for (let user_id in top_counter) {
        if (top_counter[user_id] != 0) {
            top_counter_not_empty[users[user_id]] = top_counter[user_id];
        }
    }

    var ctx = document.getElementById('top_feedback').getContext('2d');
    var myBarChart = new Chart(ctx, {
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: Object.keys(top_counter_not_empty),  // TODO: sort
            datasets: [{
                label: 'Количество выбранных',
                data: Object.values(top_counter_not_empty)
            }]
        },

        // Configuration options go here
        options: {}
    });
}




function countDayFeedback() {
    let day_id = document.getElementById('days').value;


    let feedback = Object.values(cache['feedback']).filter(function (i) {
        return cache['events'][i['event_id']].day_id == day_id;
    });  // TODO: check filter for this day
    let events = cache['events'];


    let feedback_by_event_id = groupBy(feedback, 'event_id');

    let events_html = '';
    for (let event_id in feedback_by_event_id) {
        events_html +=
            '<div class="day_feedback">' +
                '<div class="description">' +
                    '<p class="event_title">' + events[event_id].title + '</p>' +
                    '<p class="event_count">' + feedback_by_event_id[event_id].length + '</p>' +
                '</div>' +
                '<canvas id="event' + event_id + '"></canvas>' +
            '</div>';
    }
    document.querySelector('.days_feedback').innerHTML = events_html;

    for (let event_id in feedback_by_event_id) {
        let mean_score = {'score': 0, 'entertain': 0, 'useful': 0, 'understand': 0};

        // Count mean for each score
        for (let feedback_obj of feedback_by_event_id[event_id]) {
            let len = feedback_by_event_id[event_id].length;

            mean_score['score'] += feedback_obj['score'] / len;
            mean_score['entertain'] += feedback_obj['entertain'] / len;
            mean_score['useful'] += feedback_obj['useful'] / len;
            mean_score['understand'] += feedback_obj['understand'] / len;
        }


        var ctx = document.getElementById('event' + event_id).getContext('2d');
        var chart = new Chart(ctx, {
            // The type of chart we want to create
            type: 'bar',

            // The data for our dataset
            data: {
                labels: ['Общее', 'Интересно', 'Полезно', 'Понятно'],
                datasets: [{
                    label: 'Средние оценки',
                    backgroundColor: '#006cae',
                    data: [mean_score['score'], mean_score['entertain'], mean_score['useful'], mean_score['understand']]
                }]
            },

            // Configuration options go here
            options: {}
        });
    }
}









/**
 * Load from server events information
 */
function loadEvents(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let events_raw = JSON.parse(this.responseText);
            let events = groupByUnique(events_raw, 'id');

            cache['events'] = events;

            func();
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_table?table=" + 'events', true);
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
                let objs = groupByUnique(users, 'code');

                cache['users'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_table?" + "table=" + 'users', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


/**
 * Get top information from server
 * Save list to global 'cache['users']'
 *
 * Run func on OK status
 */
function loadTop(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                let top = JSON.parse(this.responseText);
                let objs = groupByUnique(top, 'code');

                cache['top'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_table?" + "table=" + 'top', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}





/**
 * Get feedback information from server by date
 * Send http GET request and get projects json schedule
 * Save feedback list to global 'cache['feedback']'
 *
 * Run func on OK status
 */
function loadAllFeedback(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let feedback = JSON.parse(this.responseText);

            cache['feedback'] = feedback;

            func();
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_table?" + "table=" + 'feedback', true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}