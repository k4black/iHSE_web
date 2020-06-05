


window.addEventListener('load', function () {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays(function () {checkLoading(function () {setDistribution(); setDays(); setCredits(); setHosts()}, ['vacations', 'users', 'days', 'credits', 'enrolls', 'events'])});
    loadUsers(function () {checkLoading(function () {setDistribution(); setDays(); setCredits(); setHosts()}, ['vacations', 'users', 'days', 'credits', 'enrolls', 'events'])});
    loadVacations(function () {checkLoading(function () {setDistribution(); setDays(); setCredits(); setHosts()}, ['vacations', 'users', 'days', 'credits', 'enrolls', 'events'])});
    loadDaysCredits(function () {checkLoading(function () {setDistribution(); setDays(); setCredits(); setHosts()}, ['vacations', 'users', 'days', 'credits', 'enrolls', 'events'])});
    loadEnrolls(function () {checkLoading(function () {setDistribution(); setDays(); setCredits(); setHosts()}, ['vacations', 'users', 'days', 'credits', 'enrolls', 'events'])});
    loadEvents(function () {checkLoading(function () {setDistribution(); setDays(); setCredits(); setHosts()}, ['vacations', 'users', 'days', 'credits', 'enrolls', 'events'])});

});




var attendanceChart = undefined;
function countDay() {
    let day_id = document.getElementById('days').value;
    setQueryParam('day_id', day_id);

    let enrolls_by_class_id = groupBy(Object.values(cache['enrolls']).filter(function (i) {return cache['events'][i.class_id].day_id == day_id}), 'class_id');
    let events_for_day_by_event_id = Object.values(cache['events']).filter(function (i) {return i.day_id == day_id && i.type != 0});
    events_for_day_by_event_id = groupByUnique(events_for_day_by_event_id, 'id')


    let enrolls_data = [];
    for (let event_id in events_for_day_by_event_id) {
        if (event_id in enrolls_by_class_id) {
            let enrolls_no_attendance = enrolls_by_class_id[event_id].filter(function (i) {
                return i.attendance == false
            }).length;
            let enrolls_with_attendance = enrolls_by_class_id[event_id].filter(function (i) {
                return i.attendance == true
            }).length;

            enrolls_data.push({
                'label': events_for_day_by_event_id[event_id].title,
                'with_attendance': enrolls_with_attendance,
                'no_attendance': enrolls_no_attendance,
                'attendance': enrolls_with_attendance+enrolls_no_attendance,
            });
        } else {
            enrolls_data.push({
                'label': events_for_day_by_event_id[event_id].title,
                'with_attendance': 0,
                'no_attendance': 0,
                'attendance': 0,
            });
        }
    }


    // merge same titles events
    console.log(enrolls_data);
    e = enrolls_data;
    let enrolls_data_tmp = [];
    for (let [key, array] of Object.entries(groupBy(e, 'label'))) {
        let tmp = {
            'label': key,
            'with_attendance': 0,
            'no_attendance': 0,
            'attendance': 0,
        }
        for (let i of array) {
            tmp['attendance'] += i['attendance'];
            tmp['no_attendance'] += i['no_attendance'];
            tmp['with_attendance'] += i['with_attendance'];
        }
        enrolls_data_tmp.push(tmp);
    }
    enrolls_data = enrolls_data_tmp;


    enrolls_data = enrolls_data.sort(function (a, b) {return - a['attendance'] + b['attendance']});


    // attendance
    if (attendanceChart !== undefined) {
        attendanceChart.clear();
        attendanceChart.destroy();
    }

    var style = getComputedStyle(document.body);
    var ctx = document.getElementById('attendance').getContext('2d');
    attendanceChart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: enrolls_data.map(function (i) {return i.label}),
            datasets: [
                {
                    label: 'Количество посещений',
                    data: enrolls_data.map(function (i) {return i.with_attendance}),
                    // backgroundColor: '#006cae'
                    backgroundColor: style.getPropertyValue('--admin-enroll-active').trim(),
                },
                {
                    label: 'Количество записей без посещения',
                    data: enrolls_data.map(function (i) {return i.no_attendance}),
                    // backgroundColor: '#ff6384'
                    backgroundColor: style.getPropertyValue('--admin-enroll-inactive').trim()
                },
            ]
        },

        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    ticks: {
                        min: 0,
                        // max: 100
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




function setDays() {
    let days = cache['days'];

    let options_html = '<option selected disabled value="">Выбрать день</option>';

    for (let day_id in days) {
        let day = days[day_id];
        options_html += '<option value="' + day['id'] + '">' + day['date'] + '</option>'
    }

    document.getElementById('days').innerHTML = options_html;

    let day_id = getQueryParam('day_id');
    if (day_id != null) {
        document.getElementById('days').value = day_id;
        countDay();
    }
}




function setHosts() {
    let events = cache['events'];

    let hosts = {};
    for (let event of Object.values(events)) {
        if (event.host === '') {
            continue;
        }

        for (let host of event.host.split(', ')) {
            if (hosts[host] == undefined) {
                hosts[host] = {'regular': 0, 'master': 0, 'lecture': 0, 'fun': 0, 'sum': 0, 'name': host};
            }

            hosts[host]['sum']++;
            if (event.type == 0) {
                hosts[host]['regular']++;
            } else
            if (event.type == 1) {
                hosts[host]['master']++;
            } else
            if (event.type == 2) {
                hosts[host]['lecture']++;
            } else
            if (event.type == 3) {
                hosts[host]['fun']++;
            }
        }
    }


    hosts = Object.values(hosts).sort(function (a, b) {return - a.sum + b.sum});


    var style = getComputedStyle(document.body);
    var ctx = document.getElementById('hosts').getContext('2d');
    var chart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: hosts.map(function (i) {return i.name}),
            datasets: [
                {
                    label: 'Количество Обычных Занятий',
                    data: hosts.map(function (i) {return i.regular}),
                    // backgroundColor: '#596266'
                    backgroundColor: style.getPropertyValue('--admin-regular-event').trim(),
                },
                {
                    label: 'Количество Мастерклассов',
                    data: hosts.map(function (i) {return i.master}),
                    // backgroundColor: '#006cae'
                    backgroundColor: style.getPropertyValue('--admin-master-event').trim(),
                },
                {
                    label: 'Количество Лекций',
                    data: hosts.map(function (i) {return i.lecture}),
                    // backgroundColor: '#ff6384'
                    backgroundColor: style.getPropertyValue('--admin-lecture-event').trim(),
                },
                {
                    label: 'Количество Развлекательных',
                    data: hosts.map(function (i) {return i.fun}),
                    // backgroundColor: '#ffce56'
                    backgroundColor: style.getPropertyValue('--admin-fun-event').trim(),
                },
            ],
        },

        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    stacked: true,
                    ticks: {
                        min: 0,
                        precision: 0
                    }
                }],
                yAxes: [{
                    stacked: true,
                }],
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
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up day field
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
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
            }
        }
    };

    xhttp.open("GET", "/admin_get_credits", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}



function _median(values){
    if(values.length ===0) {
        return 0;
    }
    values.sort(function(a,b){return a-b;});
    let half = Math.floor(values.length / 2);

    if (values.length % 2) {
        return values[half];
    }

    return (values[half - 1] + values[half]) / 2.0;
}

function setCredits() {
    let credits_by_id = cache['credits'];
    let credits_by_day_id = groupBy(Object.values(credits_by_id), 'day_id');

    let days = cache['days'];

    let sum_for_days = {};
    let mean_for_days = {};
    let median_for_days = {};
    for (let day_id in days) {
        sum_for_days[days[day_id].date] = 0;
        mean_for_days[days[day_id].date] = 0;
    }

    let users = Object.values(cache['users']).filter(function (i) {return i['user_type'] == 0});
    let users_counter = users.length;
    // for (let user_id in cache['users']) {
    //     if (cache['users'][user_id].type != 0) {
    //         ++users_counter;
    //     }
    // }

    let last_day = undefined;
    for (let day_id in credits_by_day_id) {
        let credits_by_user_id = groupBy(credits_by_day_id[day_id], 'user_id');

        let users_credits = [];
        let counter_for_day = 0;

        for (let user_id of users.map(function (i) {return i.id})) {
            let sum_for_user = 0;
            if (user_id in credits_by_user_id) {
                for (let credit of credits_by_user_id[user_id]) {
                    sum_for_user += credit.value;
                    mean_for_days[days[day_id].date] += credit.value;
                }
            }

            users_credits.push(sum_for_user);
            if (sum_for_user >= cache['user'].total) {
                ++counter_for_day;
            }
        }

        console.log('users_credits', users_credits);
        let current_day = days[day_id].date;

        sum_for_days[current_day] = 100.0 * counter_for_day / users_counter;
        mean_for_days[current_day] = credits_by_day_id[day_id].length === 0 ? 0 : mean_for_days[current_day] / users_counter;
        median_for_days[current_day] = _median(users_credits);

        if (last_day !== undefined) {
            mean_for_days[current_day] += mean_for_days[last_day];
            median_for_days[current_day] += median_for_days[last_day];  // TODO: Check/ It's wrong
        }
        last_day = current_day;
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
            datasets: [
                {
                    label: 'Среднее кредиты',
                    backgroundColor: '#006cae',
                    data: Object.values(mean_for_days)
                },
                {
                    label: 'Медианные кредиты',
                    backgroundColor: '#ff6384',
                    data: Object.values(median_for_days)
                },
            ]
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
        var style = getComputedStyle(document.body);

        var ctx = document.getElementById('team' + team).getContext('2d');
        var myDoughnutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [male_total - male_vacations, female_total - female_vacations, male_vacations, female_vacations],
                    // backgroundColor: ['#4177e4', '#c954ec', '#5969b5', '#9e61a9']
                    backgroundColor: [
                        style.getPropertyValue('--admin-male-sex').trim(),
                        style.getPropertyValue('--admin-female-sex').trim(),
                        style.getPropertyValue('--admin-male-sex-dark').trim(),
                        style.getPropertyValue('--admin-female-sex-dark').trim(),
                    ]
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
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
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
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
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
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up day field
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
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
            }
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
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up day field
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
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
            }
        }
    };

    xhttp.open("GET", "/admin_get_table?table=" + 'enrolls', true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}
