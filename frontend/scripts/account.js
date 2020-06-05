/**
 * @fileoverview Account page logic
 * File providing all functions which are used to control account.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




window.addEventListener('load', function () {
    createBar();

    let id = getQueryParam('id');

    if (id == null) {
        // Load self user
        loadUser(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits']);});
        loadCredits(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits']);});
        loadDays(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits']);});
        loadNames(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits']);});
    } else {
        // Load other user
        loadOtherUser(id, function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits', 'other']);});
        loadUser(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits', 'other']);});
        loadOtherCredits(id, function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits', 'other']);});
        loadDays(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits', 'other']);});
        loadNames(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['names', 'days', 'user', 'credits', 'other']);});
    }
});





(function(w) {
    //private variable
    var loaded = false;
    w.onload = function() {
        loaded = true;
    };

    w.checkLoaded = function() {
        return loaded;
    };
})(window);



/** ===============  LOGIC and REQUESTS  =============== */



/**
 * Get project information from cache
 * And set up it to html
 */
function setProject(user) {
    console.log('check setProject ', cache['project']);

    if (user.project_id == 0) {
        // Create  project button

        document.querySelector('.account__project__create').addEventListener('click', function () {
            console.log('Create project');
            window.location.href = "/create.html";
        });
        return;
    }

    let project_elem = document.querySelector('.account__project');
    project_elem.setAttribute('project-id', user.project_id );

    project_elem.classList.remove('no_project');

    let project = cache['project'];

    document.querySelector('.project__title').innerHTML = project.title;
    let image = (project.type === 'science' ? 'science.png' : (project.type === 'project' ? 'project.png': 'other.png'));
    document.querySelector('.account__project__info img').src = 'images/' + image;
    document.querySelector('.project__def_type').innerHTML = (project.def_type === 'TED' ? 'TED' : 'Презентация');
    let names_test = '';
    for (let user_id in cache['names']) {
        let current_user = cache['names'][user_id];

        if (current_user.project_id == project.id) {
            names_test += current_user.name + '; ';
        }
    }
    document.querySelector('.project__names').innerHTML = names_test;
    document.querySelector('.project__desc').innerHTML = project.description;
    document.querySelector('.project__anno').innerHTML = project.annotation;

    // Edit button
    if (cache['user'].id == user.id || cache['user'].user_type != 0) {
        document.querySelector('.project__edit_button').onclick = function () {editProject(project['id'])};
    } else {
        document.querySelector('.project__edit_button').onclick = function () {editOthersProject(project['id'])};
    }
}


/**
 * Get account information from cache
 * And set up it to html
 */
function setAccount() {
    console.log('check setAccount ', cache);

    let topbar = document.querySelector('.topbar');

    loadingEnd(); // TODO: Check
    // console.log(this.responseText);

    const urlParams = new URLSearchParams(window.location.search);
    let id = urlParams.get('id');
    let user
    if (id == null) {
        user = cache['user'];
    } else {
        user = cache['other'];
    }

    // Load project
    startProjectLoading();
    loadProject(user['project_id'], function () {setProject(user)});

    // Setup user bio
    topbar.querySelector('.topbar__name').innerText = user.name;
    let phone = user.phone;
    phone = '+' + phone[0] + ' (' + phone.slice(1, 4) + ') ' + phone.slice(4, 7) + '-' + phone.slice(7);
    topbar.querySelector('.topbar__phone').innerText = phone;

    document.querySelector('.team__title').innerText = user.team;

    //setup.sh avatar
    if (user.avatar != null && user.avatar != undefined && user.avatar != '')
        topbar.querySelector('.topbar__avatar').style.backgroundImage = "url('" + user.avatar + "')";

    // Setup user type label
    switch (user['user_type']) {
        case 0:  // User
            // pass
            break;

        case 1:  // Host
            topbar.querySelector('.topbar__type').innerText = 'Moderator';
            break;

        case 2:  // Admin
            topbar.querySelector('.topbar__type').innerText = 'Admin';
            break;
    }


    setCredits();
}



/**
 * Logout button
 * Send http POST request to clear session id
 */
function logout() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {

                location = '/index.html';  // Refer to start page
            }

            if (this.status === 302) {  // Ok - redir

            }
        }
    };

    xhttp.open("POST", "/logout", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}






// /**
//  * Add button event - 'code input'
//  * Send http POST request to sing up lecture
//  */
// document.querySelector('#btn').addEventListener('click', function () {
//
//     let code = document.querySelector('#code');
//
//     if (code.value === "")  // If some field are empty - do nothing
//         return;
//
//
//     var xhttp = new XMLHttpRequest();
//
//     xhttp.onreadystatechange = function () {
//         if (this.readyState === 4) {  // When request is done
//
//             if (this.status === 200) {  // Authorized
//                 alert("ok!");
//                 loadAccount();
//
//                 code.value = "";
//
//             }
//
//             if (this.status === 401) {  // Authorization error
//                 alert("Wrong code!");  // TODO: show Html error message
//
//                 code.value = "";
//             }
//         }
//     };
//
//     xhttp.open("POST", "/credits?code=" + code.value, true);
//     xhttp.withCredentials = true;  // To receive cookie
//     xhttp.send();
// });








/**
 * Setup barchart - credits circle
 * https://kimmobrunfeldt.github.io/progressbar.js/
 */
// var ProgressBar = require('scripts/progressbar.js');
var bar;
function createBar() {
    bar = new ProgressBar.Circle('.progress', {
        color: '#aaaaaa',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 4,
        trailWidth: 1,
        easing: 'bounce',
        duration: 1400,
        text: {
            autoStyleContainer: false
        },
        from: {color: '#0085d6', width: 1},
        to: {color: '#ed9324', width: 4},
        // Set default step function for all animate calls
        step: function (state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);

            var value = Math.round(circle.value() * 100);
            if (value === 0) {
                circle.setText('');
            } else {
                circle.setText(value + '%');
            }

        }
    });
    bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    bar.text.style.fontSize = '2rem';
}





// TODO: get days from server
var days = ['05.06', '06.06', '07.06', '08.06', '09.06', '10.06', '11.06', '12.06', '13.06', '14.06', '15.06', '16.06', '17.06', '18.06'];

var data = [30, 40, 35, 0, 9, 16, 30, 21, 12, 0, 0];
var dataShort = [30, 40, 35, 0, 9, 16, 30, 21, 12];


/**
 * Setup linechart - credits for days
 * https://apexcharts.com/
 */
// import ApexCharts from 'apexcharts'
function setupCreditsChart(days, data, dataShort) {
    var options = {
        chart: {
            height: '105%',
            width: Math.min(data.length * 50, 450) ,
            // type: 'line',
            zoom: {
                enabled: false
            },
            toolbar: {
                show: false
            }
        },
        colors: ['#007ac5', "#e39100"],
        // title: {
        //   text: 'Credits story'
        // },
        legend: {
            show: false
        },
        tooltip: {
            enabled: false,
            // enabledOnSeries: [0]
        },
        fill: {
            colors: ['#007ac5']
        },
        dataLabels: {
            // enabled: true,
            enabledOnSeries: [1]
        },
        stroke: {
            // curve: 'straight',
            curve: ['smooth', 'straight'],
            colors: ['#007ac500', "#e39100"]
        },
        series: [{
          name: 'Credits',
          type: 'column',
          data: data
        }, {
          type: 'line',
          data: dataShort
        }],
        animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800,
            animateGradually: {
                enabled: true,
                delay: 150
            },
            dynamicAnimation: {
                enabled: true,
                speed: 350
            }
        },
        background: '#fff',
        grid: {
            // borderColor: '#111',
            row: {
                // colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
                opacity: 0.5
            },
        },
        // labels: series.monthDataSeries1.dates,
        xaxis: {
            categories: days,
        },
    };

    document.getElementById('credits__chart').innerHTML = '';
    var chart = new ApexCharts(document.querySelector('#credits__chart'), options);
    chart.render();
}





/**
 * Read credits data from cache and create html graph
 */
function setCredits() {
    console.log('check setCredits ', cache);
    let credits_by_id = cache['credits'];

    let credits = groupBy(Object.values(credits_by_id), 'day_id');  // TODO: sql join add date field

    // Count sum for each date
    let data_pre = {};
    for (let day_id in cache['days']) {  // TODO: load days
        data_pre[cache['days'][day_id].date] = 0;
    }

    let total_sum = 0;
    for (let day_id in credits) {
        let sum = 0;
        let date = cache['days'][day_id].date;

        for (let credit of credits[day_id]) {
            sum += (credit.value === undefined ? 0 : credit.value);
        }

        data_pre[date] = sum;
        total_sum += sum;
    }

    // Setup progress bar
    console.log(total_sum +" - "+ cache['user'].total);
    bar.animate(total_sum / cache['user'].total );  // Number from 0.0 to 1.0

    document.querySelector('.credits__title').innerText = total_sum + ' / ' + cache['user'].total;

    // Correct setup.sh of zeros values (future days)
    data = [];
    dataShort = [];
    days = [];
    let flag = false;
    for (let day_id of Object.keys(cache['days']).reverse()) {
        console.log(day_id);
        let date = cache['days'][day_id].date;

        if (data_pre[date] !== 0) {
            flag = true;
        }

        if (flag) {
            dataShort.unshift(data_pre[date]);
        }
        data.unshift(data_pre[date]);
        days.unshift(cache['days'][day_id].date);
    }


    // Load text data of credits
    let html_history = '';
    for (let day_id in credits) {
        html_history += '<div class="credits__history_day img-div">';

        html_history += '<h3>' + cache['days'][day_id].date + '</h3>';

        for (let credit of credits[day_id]) {
            html_history += '<div class="credits__history_item">' +
                                '<div>'+
                                    '<i class="mobile__item__icon large material-icons">' + (credit.type == 1 ? 'edit' : credits.type == 2 ? 'school' : 'event') + '</i>' +
                                    '<p>' + credit.title + '</p>' +
                                '</div>' +
                                '<p class="' + (credit.value > 0 ? 'credits_positive' : 'credits_negative') + '">' + (credit.value > 0 ? '+' : '-') + credit.value + '</p>' +
                            '</div>';
        }

        html_history += '</div>';
    }

    document.querySelector('.credits__history').innerHTML = html_history;

    console.log(days, data, dataShort);
    setupCreditsChart(days, data, dataShort);
}





/**
 * Get credits information from server by user cookies
 * Send http GET request and get projects json schedule
 * Save enrolls list to global 'cache['credits']'
 *
 * Run func on OK status
 */
function loadOtherCredits(user_id, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let credits_raw;
            try {
               credits_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                credits_raw = [];
            }

            let credits = groupByUnique(credits_raw, 'id');

            cache['credits'] = credits;

            func();
        }
    };

    xhttp.open("GET", "/credits?id=" + user_id, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}