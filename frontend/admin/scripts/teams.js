


window.addEventListener('load', function () {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays(function () {checkLoading(function () {setTeams()}, ['vacations', 'users', 'days', 'credits'])});
    loadUsers(function () {checkLoading(function () {setTeams()}, ['vacations', 'users', 'days', 'credits'])});
    loadVacations(function () {checkLoading(function () {setTeams()}, ['vacations', 'users', 'days', 'credits'])});
    loadDaysCredits(function () {checkLoading(function () {setTeams()}, ['vacations', 'users', 'days', 'credits'])});
});



function countQueryTeam(team) {
    document.getElementById('teams').value = team;

    countTeam();
}

function countTeam() {
    let team = document.getElementById('teams').value;

    setDistribution(team);

    let options_html = '<option selected disabled value="">Выбрать Участника</option>';
    console.log('Object.values(cache[\'users\'])', Object.values(cache['users']))
    let users = Object.values(cache['users']).filter(function (i) {return i['team'] == team}).sort(function (a, b) {return a['name'] > b['name']});
    for (let user of users) {
        options_html += '<option value="' + user['id'] + '">' + user['name'] + '</option>'
    }
    document.getElementById('users').innerHTML = options_html;
    document.getElementById('users').onchange(function (i) {
        console.log('CHANGE', i);
    })


    setQueryParam('team', team);
    setCredits(team);
}



var user_credits = undefined;
var user_events = undefined;
function countUser() {
    let current_user_id = document.getElementById('users').value;
    if (current_user_id == '') {
        return;
    }

    console.log('current_user_id', current_user_id);
    let current_user = cache['users'][current_user_id];

    console.log('current_user', current_user);

    if (current_user.avatar != null && current_user.avatar != '') {
        document.querySelector('#user_profile img').style.backgroundImage = "url('" + current_user.avatar + "')";
    } else {
        document.querySelector('#user_profile img').style.backgroundImage = '/images/avatar.png';
    }

    document.querySelector('#user_profile a').setAttribute('href', '/account.html?id='+current_user_id);
    let phone = current_user.phone;
    document.querySelector('#user_profile .phone').innerHTML = '+' + phone[0] + ' (' + phone.slice(1, 4) + ') ' + phone.slice(4, 7) + '-' + phone.slice(7);
    document.querySelector('#user_profile .name').innerHTML = current_user.name;

    if (user_credits != undefined) {
        user_credits.clear();
        user_credits.destroy();
    }

    let credits_by_day_id = groupBy(Object.values(cache['credits']).filter(function (i) {return i.user_id == current_user_id}), 'day_id');  // TODO: sql join add date field

    let credits_sum = {};
    let total_sum = 0;
    for (let day_id in cache['days']) {
        let date = cache['days'][day_id].date;
        credits_sum[date] = {'special': 0, 'master': 0, 'lecture': 0, 'fun': 0};

        console.log('credits_by_day_id[day_id]', credits_by_day_id[day_id]);
        if (day_id in credits_by_day_id) {
            for (let credit of credits_by_day_id[day_id]) {
                total_sum += credit.value;

                if (credit.type == 0) {
                    credits_sum[date]['special'] += credit['value'];
                } else if (credit.type == 1) {
                    credits_sum[date]['master'] += credit['value'];
                } else if (credit.type == 2) {
                    credits_sum[date]['lecture'] += credit['value'];
                } else if (credit.type == 3) {
                    credits_sum[date]['fun'] += credit['value'];
                }
            }
        }
    }

    document.querySelector('#user_profile .credits').innerHTML = total_sum + ' / ' + cache['user'].total;

    var style = getComputedStyle(document.body);
    var ctx = document.getElementById('user_credits').getContext('2d');
    user_credits = new Chart(ctx, {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
            labels: Object.keys(credits_sum),
            datasets: [
                {
                    label: 'Особые кредиты',
                    data: Object.values(credits_sum).map(function (i) {return i['special'];}),
                    // backgroundColor: '#cc65fe'
                    backgroundColor: style.getPropertyValue('--admin-special-event').trim(),
                },
                {
                    label: 'Мастерклассы кредиты',
                    data: Object.values(credits_sum).map(function (i) {return i['master'];}),
                    // backgroundColor: '#006cae'
                    backgroundColor: style.getPropertyValue('--admin-master-event').trim(),
                },
                {
                    label: 'Лекционные кредиты',
                    data: Object.values(credits_sum).map(function (i) {return i['lecture'];}),
                    // backgroundColor: '#ff6384'
                    backgroundColor: style.getPropertyValue('--admin-lecture-event').trim(),
                },
                {
                    label: 'Развлекательные кредиты',
                    data: Object.values(credits_sum).map(function (i) {return i['fun'];}),
                    // backgroundColor: '#ffce56'
                    backgroundColor: style.getPropertyValue('--admin-fun-event').trim(),
                },
            ],
        },

        // Configuration options go here
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: false
            },
            title: {
                display: true,
                text: 'Кредиты в день'
            },
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




    if (user_events != undefined) {
        user_events.clear();
        user_events.destroy();
    }


}



function setTeams() {
    let users = cache['users'];
    let unique_teams = [...new Set(Object.values(users).map(function (i) {return i['team']}))].sort();
    if (unique_teams[0] == 0) {
        unique_teams.shift()
    }

    let options_html = '<option selected disabled value="">Выбрать отряд</option>';
    for (let team of unique_teams) {
        options_html += '<option value="' + team + '">' + team + '</option>'
    }
    document.getElementById('teams').innerHTML = options_html;

    console.log('options_html', options_html)


    const urlParams = new URLSearchParams(window.location.search);
    let team = urlParams.get('team');
    countQueryTeam(team);
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



// ['id', 'user_id', 'event_id', 'value', 'type', 'title', 'day_id']
var credits_chart = undefined;



function setCredits(team) {

    let credits_by_user_id = groupBy(Object.values(cache['credits']).filter(function (i) {return cache['users'][i['user_id']].team == team}), 'user_id');

    let users = Object.values(cache['users']).filter(function (i) {return i['team'] == team});

    let sum_for_users = {};
    let sum_for_users_split = {};
    for (let user of users) {
        let user_id = user.id;
        sum_for_users[user_id] = 0;
        sum_for_users_split[user_id] = {'special': 0, 'master': 0, 'lecture': 0, 'fun': 0};

        console.log('credits_by_user_id[user_id]', credits_by_user_id[user_id])
        if (user_id in credits_by_user_id) {
            for (let credit of credits_by_user_id[user_id]) {
                sum_for_users[user_id] += credit['value'];

                if (credit.type == 0) {
                    sum_for_users_split[user_id]['special'] += credit['value'];
                } else
                if (credit.type == 1) {
                    sum_for_users_split[user_id]['master'] += credit['value'];
                } else
                if (credit.type == 2) {
                    sum_for_users_split[user_id]['lecture'] += credit['value'];
                } else
                if (credit.type == 3) {
                    sum_for_users_split[user_id]['fun'] += credit['value'];
                }
            }
        }
    }

    console.log('sum_for_users', sum_for_users)

    let total = cache['user'].total;
    let users_credits_array = Object.entries(sum_for_users).sort(function (a, b) {return a[1] < b[1] ? 1 : -1});

    if (credits_chart != undefined) {
        credits_chart.clear();
        credits_chart.destroy();
    }
    var style = getComputedStyle(document.body);
    var ctx = document.getElementById('credits').getContext('2d');
    credits_chart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'horizontalBar',

        // The data for our dataset
        data: {
            labels: users_credits_array.map(function (i) {return cache['users'][i[0]].name;}),
            datasets: [
                // {
                //     label: 'Сумма кредитов',  // Remove
                //     backgroundColor: '#006cae',
                //     data: users_credits_array.map(function (i) {return i[1];})
                // },
                {
                    label: 'Особые кредиты',
                    data: users_credits_array.map(function (i) {return sum_for_users_split[i[0]]['special'];}),
                    // backgroundColor: '#cc65fe'
                    backgroundColor: style.getPropertyValue('--admin-special-event').trim(),
                },
                {
                    label: 'Мастерклассы кредиты',
                    data: users_credits_array.map(function (i) {return sum_for_users_split[i[0]]['master'];}),
                    // backgroundColor: '#006cae'
                    backgroundColor: style.getPropertyValue('--admin-master-event').trim(),
                },
                {
                    label: 'Лекционные кредиты',
                    data: users_credits_array.map(function (i) {return sum_for_users_split[i[0]]['lecture'];}),
                    // backgroundColor: '#ff6384'
                    backgroundColor: style.getPropertyValue('--admin-lecture-event').trim(),
                },
                {
                    label: 'Развлекательные кредиты',
                    data: users_credits_array.map(function (i) {return sum_for_users_split[i[0]]['fun'];}),
                    // backgroundColor: '#ffce56'
                    backgroundColor: style.getPropertyValue('--admin-fun-event').trim(),
                },
            ]
        },

        // Configuration options go here

        options: {
            scales: {
                xAxes: [{
                    ticks: {
                        min: 0,
                        // max: 10
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


var distribution_pie = undefined;
function setDistribution(team) {
    let users_by_id = cache['users'];

    let users = groupBy(Object.values(users_by_id), 'team');
    let vacations = cache['vacations'];

    let total_users = 0;
    let total_vacations = 0;

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
    if (distribution_pie !== undefined) {
        distribution_pie.clear();
        distribution_pie.destroy();
    }
    var style = getComputedStyle(document.body);
    var ctx = document.getElementById('team_pie').getContext('2d');
    distribution_pie = new Chart(ctx, {
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

    document.getElementById('counter').innerText = ' ' + (total_users- total_vacations);
    document.getElementById('counter_total').innerText = ' ' + (total_users);

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


