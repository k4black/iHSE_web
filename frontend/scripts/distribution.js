


window.addEventListener('load', function () {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays(function () {checkLoading(setDistribution, ['vacations', 'users', 'days'])});
    loadUsers(function () {checkLoading(setDistribution, ['vacations', 'users', 'days'])});
    loadVacations(function () {checkLoading(setDistribution, ['vacations', 'users', 'days'])});


    loadDaysCredits(function () {checkLoading(setCredits, ['credits', 'days'])});

    // buildTestTimeline();
});


/**
 * Load from server credits information, witch includes day_id
 */
function loadDaysCredits(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let credits_raw = JSON.parse(this.responseText);
            let credits = groupByUnique(credits_raw, 'id');

            cache['credits'] = credits;

            func();
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_credits", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}



function setCredits() {
    let credits_by_id = cache['credits'];

    let credits = [{'id': 1, 'user_id': 1, 'day_id': 3, 'value': 12}, {'id': 2, 'user_id': 1, 'day_id': 2, 'value': 3}, {'id': 3, 'user_id': 1, 'day_id': 5, 'value': 6}, {'id': 4, 'user_id': 2, 'day_id': 1, 'value': 5}, {'id': 5, 'user_id': 2, 'day_id': 3, 'value': 12}, {'id': 6, 'user_id': 3, 'day_id': 2, 'value': 7}, {'id': 7, 'user_id': 3, 'day_id': 5, 'value': 21}]
    let credits_by_day_id = groupBy(credits, 'day_id');
    // TODO: make true 
    // let credits_by_day_id = groupBy(Object.values(credits_by_id), 'day_id');

    let days = cache['days'];

    let sum_for_days = {};
    for (let day_id in days) {
        sum_for_days[days[day_id].date] = 0;
    }


    for (let day_id in credits_by_day_id) {
        let credits_by_user_id = groupBy(credits_by_day_id[day_id], 'user_id');

        let counter_for_day = 0;
        for (let user_id in credits_by_user_id) {
            let sum_for_user = 0;
            for (let credit of credits_by_user_id[user_id]) {
                sum_for_user += credit.value;
            }

            if (sum_for_user >= cache['user'].total) {
                ++counter_for_day;
            }
        }

        sum_for_days[days[day_id].date] = counter_for_day;
    }



    var ctx = document.getElementById('credits').getContext('2d');
    var chart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
            labels: Object.keys(sum_for_days),
            datasets: [{
                label: 'My First dataset',
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: Object.keys(sum_for_days)
            }]
        },

        // Configuration options go here
        options: {}
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
                    text: (team == 0 ? 'Вожатые' : 'Отряд #' + team)
                }
            }
        });
    }
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
                let vacations = JSON.parse(this.responseText);
                let objs = groupByUnique(vacations, 'code');

                cache['vacations'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_table?" + "table=" + 'vacations', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}
