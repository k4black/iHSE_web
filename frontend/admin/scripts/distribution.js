


window.addEventListener('load', function () {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays(function () {checkLoading(function () {setDistribution(); setDays()}, ['vacations', 'users', 'days'])});
    loadUsers(function () {checkLoading(function () {setDistribution(); setDays()}, ['vacations', 'users', 'days'])});
    loadVacations(function () {checkLoading(function () {setDistribution(); setDays()}, ['vacations', 'users', 'days'])});


    loadDaysCredits(function () {checkLoading(setCredits, ['users', 'credits', 'days'])});

    loadEvents(setHosts);
    loadEnrolls(function () {});
});




var attendanceChart = undefined;

function countDay() {
    let day_id = document.getElementById('days').value;

    console.log('day_id', day_id);

    let events_attendance = {};
    for (let event_id in cache['events']) {
        let event = cache['events'][event_id];
        if (event.day_id == day_id && event.type != 0) {
            events_attendance[event_id] = 0;
        }
    }

    let enrolls_by_class_id = groupBy(Object.values(cache['enrolls']), 'class_id');
    for (let event_id in cache['events']) {
        if (enrolls_by_class_id[event_id] == undefined) {
            continue;
        }

        for (let enroll of enrolls_by_class_id[event_id]) {
            if (enroll.attendance == true) {
                events_attendance[event_id]++;
            }
        }
    }

    let processed_events_attendance = {};
    for (let event_id in events_attendance) {
        processed_events_attendance[cache['events'][event_id].title] = events_attendance[event_id];
    }

    console.log('processed_events_attendance', processed_events_attendance);

    // attendance
    if (attendanceChart !== undefined) {
        attendanceChart.clear();
    }
    var ctx = document.getElementById('attendance').getContext('2d');
    attendanceChart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: Object.keys(processed_events_attendance),
            datasets: [{
                label: 'Количество посещений',
                data: Object.values(processed_events_attendance),
                backgroundColor: '#006cae'
            }]
        },

        // Configuration options go here
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        // max: 100
                    }
                }]
            }
        }
    });
}




function setDays() {
    let days = cache['days'];

    let options_html = '<option selected disabled value="">Выбрать день</option>';

    for (let day_id in days) {
        let day = days[day_id];
        options_html += '<option value="' + day['id'] + '">' + day['date'] + '</option>'
    }

    document.getElementById('days').innerHTML = options_html;
}




function setHosts() {
    let events = cache['events'];

    let hosts = {};
    let hosts_total = {};

    for (let event of Object.values(events)) {
        if (event.host === '') {
            continue;
        }

        for (let host of event.host.split(', ')) {

            if (hosts[host] == undefined) {
                hosts[host] = {'master': 0, 'lecture': 0};
                hosts_total[host] = 0;
            }

            hosts_total[host]++;
            if (event.type == 1) {
                hosts[host]['master']++;
            }

            if (event.type == 2) {
                hosts[host]['lecture']++;
            }
        }
    }


    var ctx = document.getElementById('hosts').getContext('2d');
    var chart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: Object.keys(hosts_total),
            datasets: [{
                label: 'Количество занятий',
                data: Object.values(hosts_total),
                backgroundColor: '#006cae'
            }]
        },

        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    ticks: {
                        min: 0,
                        // max: 100
                    }
                }]
            }
        }
    });
}




/**
 * Load from server credits information, witch includes day_id
 */
function loadDaysCredits(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let credits_raw;
            try {
                credits_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error', e)
                credits_raw = [];
            }
            let credits = groupByUnique(credits_raw, 'id');

            cache['credits'] = credits;

            func();
        }
    };

    xhttp.open("GET", "/admin_get_credits", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}



function setCredits() {
    let credits_by_id = cache['credits'];
    let credits_by_day_id = groupBy(Object.values(credits_by_id), 'day_id');

    let days = cache['days'];

    let sum_for_days = {};
    let mean_for_days = {};
    for (let day_id in days) {
        sum_for_days[days[day_id].date] = 0;
        mean_for_days[days[day_id].date] = 0;
    }

    let users_counter = 0;
    for (let user_id in cache['users']) {
        if (cache['users'][user_id].type != 0) {
            ++users_counter;
        }
    }

    for (let day_id in credits_by_day_id) {
        let credits_by_user_id = groupBy(credits_by_day_id[day_id], 'user_id');

        let counter_for_day = 0;
        for (let user_id in credits_by_user_id) {
            let sum_for_user = 0;
            for (let credit of credits_by_user_id[user_id]) {
                sum_for_user += credit.value;
                mean_for_days[days[day_id].date] += credit.value;
            }

            if (sum_for_user >= cache['user'].total) {
                ++counter_for_day;
            }
        }

        sum_for_days[days[day_id].date] = 100.0 * counter_for_day / Object.keys(cache['users']).length;
        mean_for_days[days[day_id].date] = credits_by_day_id[day_id].length === 0 ? 0 : mean_for_days[days[day_id].date] / users_counter;
    }

    console.log('sum_for_days', sum_for_days);



    var ctx = document.getElementById('percentage').getContext('2d');
    var percentageChart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
            labels: Object.keys(sum_for_days),
            datasets: [{
                label: 'Процент сдавших',
                backgroundColor: '#006cae',
                data: Object.values(sum_for_days)
            }]
        },

        // Configuration options go here
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        // max: 10
                    }
                }]
            }
        }
    });



    var ctx = document.getElementById('credits').getContext('2d');
    var creditsChart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'line',

        // The data for our dataset
        data: {
            labels: Object.keys(mean_for_days),
            datasets: [{
                label: 'Среднее кредиты',
                backgroundColor: '#006cae',
                data: Object.values(mean_for_days)
            }]
        },

        // Configuration options go here
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        // max: 10
                    }
                }]
            }
        }
    });

}

function setDistribution() {
    let users_by_id = cache['users'];

    let users = groupBy(Object.values(users_by_id), 'team');
    let vacations = cache['vacations'];


    console.log('teams dist', users);
    // users[1] = [];  // TODO: Real values
    // users[2] = [];  // TODO: Real values


    let teams_html = '';
    for (let team in users) {
        teams_html += '<div class="team_pie"><canvas id="team' + team + '"></canvas></div>'
    }

    document.getElementById('teams').innerHTML = teams_html;

    let total_users = 0;
    let total_vacations = 0;
    for (let team in users) {
        let male_total = 0;
        let female_total = 0;
        for (let user of users[team]) {
            if (user.sex) {
                ++male_total;
            } else {
                ++female_total;
            }
        }

        let male_vacations = 0;
        let female_vacations = 0;

        for (let user of users[team]) {
            for (let v_id in vacations) {
                if (vacations[v_id].user_id == user.id && vacations[v_id].date_from <= getToday() && getToday() <= vacations[v_id].date_to) {
                    if (user.sex) {
                        ++male_vacations;
                    } else {
                        ++female_vacations;
                    }
                }
            }
        }

        console.log('male_total', male_total, 'female_total', female_total);
        console.log('male_vacations', male_vacations, 'female_vacations', female_vacations);

        total_users += male_total + female_total;
        total_vacations += male_vacations + female_vacations;

        var ctx = document.getElementById('team' + team).getContext('2d');
        var myDoughnutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [male_total - male_vacations, female_total - female_vacations, male_vacations, female_vacations],
                    // data: [12, 23, 3, 0],  // TODO: Real values
                    backgroundColor: ['#4177e4', '#c954ec', '#5969b5', '#9e61a9']
                }],

                // These labels appear in the legend and in the tooltips when hovering different arcs
                labels: [
                    'Male',
                    'Female',
                    'Male Vacations',
                    'Female Vacations',
                ]
            },
            options: {
                title: {
                    display: true,
                    text: (team == 0 ? 'Вожатые' : 'Отряд #' + team) + '[' + (male_total - male_vacations + female_total - female_vacations) + '/' + (male_total + female_total) + ']'
                }
            }
        });
    }

    document.getElementById('counter').innerText = '' + (total_users- total_vacations);
    document.getElementById('counter_total').innerText = '' + (total_users);

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
                    console.log('error', e)
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
 * Get vacatios information from server
 * Save list to global 'cache['vacations']'
 *
 * Run func on OK status
 */
function loadVacations(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                let vacations;
                try {
                    vacations = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error', e)
                    vacations = [];
                }
                let objs = groupByUnique(vacations, 'code');

                cache['vacations'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "/admin_get_table?" + "table=" + 'vacations', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
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
                console.log('error', e)
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
 * Load from server events information
 */
function loadEnrolls(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let enrolls_raw;
            try {
                enrolls_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error', e)
                enrolls_raw = [];
            }
            let enrolls = groupByUnique(enrolls_raw, 'id');

            cache['enrolls'] = enrolls;

            func();
        }
    };

    xhttp.open("GET", "/admin_get_table?table=" + 'enrolls', true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}
