


window.addEventListener('load', function () {
    loadDays(setDays);

    loadEvents(function () {checkLoading(function () {countHostFeedback(); countDaysFeedback()}, ['events', 'feedback'])});
    loadAllFeedback(function () {checkLoading(function () {countHostFeedback(); countDaysFeedback()}, ['events', 'feedback'])});

    loadTop(function () {checkLoading(countTop, ['users', 'top'])});
    loadUsers(function () {checkLoading(countTop, ['users', 'top'])});
});




function setDays() {
    let days = cache['days'];

    let options_html = '<option selected disabled value="">Выбрать день</option>';

    for (let day_id in days) {
        let day = days[day_id];
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
    let top_self_counter = {};  // self team
    let top_others_counter = {};  //others team
    for (let user_id in users) {
        top_counter[user_id] = 0;
        top_self_counter[user_id] = 0;
        top_others_counter[user_id] = 0;
    }
    for (let top of Object.values(top_by_id)) {
        for (let i of [1, 2, 3]) {
            top_counter[top['chosen_' + i]]++;

            if (users[top['user_id']].team == users[top['chosen_' + i]].team) {
                top_self_counter[top['chosen_' + i]]++;
            } else {
                top_others_counter[top['chosen_' + i]]++;
            }
        }
    }


    let top_counter_not_empty = {};
    let top_self_counter_not_empty = {};
    let top_others_counter_not_empty = {};
    for (let user_id in top_counter) {
        if (top_counter[user_id] != 0) {
            top_counter_not_empty[user_id] = top_counter[user_id];
            top_self_counter_not_empty[user_id] = top_self_counter[user_id];
            top_others_counter_not_empty[user_id] = top_others_counter[user_id];
        }
    }

    let top_counter_not_empty_array = Object.entries(top_counter_not_empty).sort(function (a, b) {return a[1] < b[1] ? 1 : -1});


    var ctx = document.getElementById('top_feedback').getContext('2d');
    var topChart = new Chart(ctx, {
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: top_counter_not_empty_array.map(function (i) {return users[i[0]].name;}),
            datasets: [
                {
                    label: 'Выбранно своим отрядом',
                    data: top_counter_not_empty_array.map(function (i) {return top_self_counter_not_empty[i[0]];}),
                    backgroundColor: '#006cae'
                },
                {
                    label: 'Выбранно другими отрядами',
                    data: top_counter_not_empty_array.map(function (i) {return top_others_counter_not_empty[i[0]];}),
                    backgroundColor: '#ff6384'
                },
            ]
        },

        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    ticks: {
                        min: 0,
                        // max: 100,
                        // stepSize: 1
                        precision: 0
                    },
                    stacked: true,
                }],
                yAxes: [{
                    stacked: true,
                }],
            }
        }
    });
}


function countDaysFeedback() {

    // let feedback_days = Object.values(cache['days']).filter(function (i) {
    //     return i['feedback'] == true;
    // })
    // let feedback_counts = [];
    // for (let day of feedback_days) {
    //     let feedback_arr = Object.values(cache['feedback']).filter(function (i) {
    //         return cache['events'][i['event_id']].day_id == day.id;
    //     });
    //
    //     feedback_counts = feedback_counts.concat(feedback_arr.length)
    // }

    let feedback_days = Object.values(cache['days']);
    let feedback_counts = [];
    for (let day of feedback_days) {
        if (day['feedback'] == true) {
            let feedback_arr = Object.values(cache['feedback']).filter(function (i) {
                return cache['events'][i['event_id']].day_id == day.id;
            });

            feedback_counts = feedback_counts.concat(feedback_arr.length)
        } else {
            feedback_counts = feedback_counts.concat(0)
        }
    }



    var ctx = document.getElementById('count_feedback').getContext('2d');
    document.getElementById('count_feedback').height = 100;
    var chart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
            labels: feedback_days.map(function (i) {return i['date'] + ' ' + i['title']}),
            datasets: [{
                label: 'Количество отзывов',
                // backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56'],
                data: feedback_counts
            }]
        },

        // Configuration options go here
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        // max: 10,  // TODO: Total height
                        // stepSize: 1
                        precision: 0
                    }
                }]
            },
            // responsive: true,
            // maintainAspectRatio: false
        }
    });
}



function countHostFeedback() {
    let events = cache['events'];
    let feedback_by_event_id = groupBy(Object.values(cache['feedback']), 'event_id');

    let hosts_mean = {};  // Why not working?
    let hosts_mean_score = {};
    let hosts_mean_entertain = {};
    let hosts_mean_useful = {};
    let hosts_mean_understand = {};
    let hosts_count = {};

    // for (let event_id in events) {
    //     for (let host of events[event_id].host.split(', ')) {
    //         if (host == '') {
    //             continue;
    //         }
    //
    //         hosts_count[host] = 0;
    //         hosts_mean[host] = {'score': 0, 'entertain': 0, 'useful': 0, 'understand': 0};
    //     }
    // }

    console.log(hosts_count, hosts_mean);

    for (let event_id in feedback_by_event_id) {
        for (let host of events[event_id].host.split(', ')) {
            if (hosts_count[host] == undefined) {
                hosts_count[host] = 0;
                hosts_mean_score[host] = 0.;
                hosts_mean_entertain[host] = 0.;
                hosts_mean_useful[host] = 0.;
                hosts_mean_understand[host] = 0.;
            }

            // Count mean for each score
            hosts_count[host] += feedback_by_event_id[event_id].length;

            for (let feedback_obj of feedback_by_event_id[event_id]) {
                hosts_mean_score[host] += feedback_obj['score'];
                hosts_mean_entertain[host] += feedback_obj['entertain'];
                hosts_mean_useful[host] += feedback_obj['useful'];
                hosts_mean_understand[host] += feedback_obj['understand'];
            }
        }
    }

    console.log(hosts_count, hosts_mean_score);

    for (let host in hosts_count) {
        hosts_mean_score[host] /= hosts_count[host];
        hosts_mean_entertain[host] /= hosts_count[host];
        hosts_mean_useful[host] /= hosts_count[host];
        hosts_mean_understand[host] /= hosts_count[host];
    }

    console.log(hosts_count, hosts_mean_score);

    let host_html = '';
    for (let host in hosts_count) {
        host_html +=
            '<div class="host_feedback">' +
                '<div class="description">' +
                    '<p class="host_title">' + host + '</p>' +
                    '<p class="host_count">' + 'Собрано:' + hosts_count[host] + '</p>' +
                '</div>' +
                '<canvas id="host' + hashCode(host) + '"></canvas>' +
            '</div>';
    }

    document.querySelector('.hosts_feedback').innerHTML = host_html;

    for (let host in hosts_count) {
        // console.log('host', host, 'data_pre', hosts_mean[host], 'data', [hosts_mean[host]['score'], hosts_mean[host]['entertain'], hosts_mean[host]['useful'], hosts_mean[host]['understand']])
        var ctx = document.getElementById('host' + hashCode(host)).getContext('2d');
        var chart = new Chart(ctx, {
            // The type of chart we want to create
            type: 'bar',

            // The data for our dataset
            data: {
                labels: ['Общее', 'Интересно', 'Полезно', 'Понятно'],
                datasets: [{
                    label: 'Средние оценки',
                    backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56'],
                    data: [hosts_mean_score[host], hosts_mean_entertain[host], hosts_mean_useful[host], hosts_mean_understand[host]]
                }]
            },

            // Configuration options go here
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: 10
                        }
                    }]
                },
            }
        });
    }
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
                    '<p class="event_title">' + events[event_id].title + ' [' + events[event_id].host +']</p>' +
                    '<p class="event_count">' + 'Собрано:' + feedback_by_event_id[event_id].length + '</p>' +
                '</div>' +
                '<canvas id="event' + event_id + '"></canvas>' +
                '<div class="spoiler">' +
                    '<input type="checkbox" id="spoiler' + event_id + '">' +
                    '<label for="spoiler' + event_id + '">Комментарии к мероприятию</label>' +
                    '<div id="comments' + event_id + '">' +
                        'Некий текст под спойлером. Тут должны быть коммантарии' +
                    '</div>' +
                '</div>' +
            '</div>';
    }

    document.querySelector('.days_feedback').innerHTML = events_html;

    for (let event_id in feedback_by_event_id) {
        let comments_html = '';
        let mean_score = {'score': 0, 'entertain': 0, 'useful': 0, 'understand': 0};

        // Count mean for each score
        for (let feedback_obj of feedback_by_event_id[event_id]) {
            let len = feedback_by_event_id[event_id].length;

            mean_score['score'] += feedback_obj['score'] / len;
            mean_score['entertain'] += feedback_obj['entertain'] / len;
            mean_score['useful'] += feedback_obj['useful'] / len;
            mean_score['understand'] += feedback_obj['understand'] / len;

            if (feedback_obj['comment'] != '') {
                comments_html += '<p>' + feedback_obj['comment'] + '</p>'
            }
        }

        document.getElementById('comments' + event_id).innerHTML = comments_html == '' ? '[нет комментариев]' : comments_html;

        var ctx = document.getElementById('event' + event_id).getContext('2d');
        var chart = new Chart(ctx, {
            // The type of chart we want to create
            type: 'bar',

            // The data for our dataset
            data: {
                labels: ['Общее', 'Интересно', 'Полезно', 'Понятно'],
                datasets: [{
                    label: 'Средние оценки',
                    backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56'],
                    data: [mean_score['score'], mean_score['entertain'], mean_score['useful'], mean_score['understand']]
                }]
            },

            // Configuration options go here
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: 10
                        }
                    }]
                }
            }
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
            let events_raw;
            try {
                events_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error', e);
                events_raw = [];
            }
            let events = groupByUnique(events_raw, 'id');

            cache['events'] = events;

            func();
        }
    };

    xhttp.open("GET", "/admin_get_table?table=" + 'events', true);
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
                let users;
                try {
                    users = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error', e);
                    users = [];
                }
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
                let top;
                try {
                    top = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error', e);
                    top = [];
                }
                let objs = groupByUnique(top, 'id');

                cache['top'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "/admin_get_table?" + "table=" + 'top', true);
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
            let feedback;
            try {
                feedback = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error', e);
                feedback = [];
            }

            cache['feedback'] = feedback;

            func();
        }
    };

    xhttp.open("GET", "/admin_get_table?" + "table=" + 'feedback', true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}