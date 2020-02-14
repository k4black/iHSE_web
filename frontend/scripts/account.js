/**
 * @fileoverview Account page logic
 * File providing all functions which are used to control account.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




window.addEventListener('load', function () {
    createBar();
    // loadAccount();

    // loadDays();

    loadUser(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['days', 'user', 'credits']);});
    loadCredits(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['days', 'user', 'credits']);});
    loadDays(function () {console.log('checkLoading', cache); checkLoading(setAccount, ['days', 'user', 'credits']);});
});






// TODO: chart when 2-3 credits only
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
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 */
function setAccount() {
    console.log('check setAccount ', cache);

    let topbar = document.querySelector('.topbar');

    loadingEnd(); // TODO: Check
    // console.log(this.responseText);

    let user = cache['user'];

    // Setup user bio
    topbar.querySelector('.topbar__name').innerText = user.name;
    let phone = user.phone;
    phone = '+' + phone[0] + ' (' + phone.slice(1, 4) + ') ' + phone.slice(4, 7) + '-' + phone.slice(7);
    topbar.querySelector('.topbar__phone').innerText = phone;

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
 */  // TODO: Add logout button
// document.querySelector('.header__button').addEventListener('click', function () {
//
//     var xhttp = new XMLHttpRequest();
//
//     xhttp.onreadystatechange = function() {
//         if (this.readyState === 4) {
//             if (this.status === 200) {
//
//                 location = 'http://ihse.tk/index.html';  // Refer to start page
//             }
//
//             if (this.status === 302) {  // Ok - redir
//
//             }
//         }
//     };
//
//     xhttp.open("POST", "//ihse.tk/logout", true);
//     xhttp.withCredentials = true; // To send Cookie;
//     xhttp.send();
// });






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
//     xhttp.open("POST", "//ihse.tk/credits?code=" + code.value, true);
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
                                '<p class="' + (credits.value > 0 ? 'credits_positive' : 'credits_negative') + '">' + (credit.value > 0 ? '+' : '-') + credit.value + '</p>' +
                            '</div>';
        }

        html_history += '</div>';
    }

    document.querySelector('.credits__history').innerHTML = html_history;

    console.log(days, data, dataShort);
    setupCreditsChart(days, data, dataShort);
}





/** ===============  ANIMATIONS  =============== */



// /**
//  * Add code field animations
//  * Hint Rise up when there is some text or cursor inside it
//  */
// var code = document.querySelector('#code');
// code.addEventListener('focus', function () {
//     code.closest('div').querySelector("label").classList.add('active');
// });
//
// code.addEventListener('blur', function () {
//     if (code.value != "")
//         return;
//
//     code.closest('div').querySelector("label").classList.remove('active');
// });