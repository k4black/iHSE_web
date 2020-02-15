


window.addEventListener('load', function () {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays(function () {checkLoading(setDistribution, ['vacations', 'users', 'days'])});
    loadUsers(function () {checkLoading(setDistribution, ['vacations', 'users', 'days'])});
    loadVacations(function () {checkLoading(setDistribution, ['vacations', 'users', 'days'])});

    // buildTestTimeline();
});




function setDistribution() {
    let users_by_id = cache['users'];

    let users = groupBy(Object.values(users_by_id), 'team');
    let vacations = cache['vacations'];


    console.log('teams dist', users);
    users[1] = [];  // TODO: Real values
    users[2] = [];  // TODO: Real values


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
                    // data: [male_total - male_vacations, female_total - female_vacations, male_vacations, female_vacations]
                    data: [12, 23, 3, 0]  // TODO: Real values
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