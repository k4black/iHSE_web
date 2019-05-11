/**
 * @fileoverview Account page logic
 * File providing all functions which are used to control account.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


(function(w) {
    //private variable
    var loaded = false;
    w.onload = function() {
        loaded = true;
    };

    w.checkLoaded = function() {
        alert(loaded);
    };
})(window);



/** ===============  LOGIC and REQUESTS  =============== */


/**
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 */
window.addEventListener('load', loadAccount);
function loadAccount() {
    let topbar = document.querySelector('.topbar');

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                // console.log(this.responseText);

                let user = JSON.parse(this.responseText);
                topbar.querySelector('.topbar__name').innerText = user.name;
                topbar.querySelector('.topbar__phone').innerText = user.phone;

                // switch (user.type) {
                //     case 0:
                //         title.innerText = 'User';
                //         break;
                //     case 1:
                //         title.innerText = 'Host';
                //         break;
                //     case 2:
                //         title.innerText = 'Admin';
                //         break;
                // }

                //setup avatar
                if (user.avatar != null)
                    topbar.querySelector('.topbar__avatar').style.backgroundImage = "url('" + user.avatar + "')";


                if(window.checkLoaded()) {
                    bar.animate( event.count / event.total );  // Number from 0.0 to 1.0
                } else {
                    window.addEventListener('load', function () {
                        bar.animate( event.count / event.total );  // Number from 0.0 to 1.0
                    })
                }
                

                document.querySelector('.credits__title').innerText = user.credits + ' / ' + user.total;

                switch (user.type) {
                    case 0:  // User

                        break;

                    case 1:  // Host
                        topbar.querySelector('.topbar__type').innerText = 'Host';
                        break;

                    case 2:  // Admin
                        topbar.querySelector('.topbar__type').innerText = 'Admin';
                        break;
                }
            }

            else if (this.status === 401) {  // No account data
                alert('Please, login!');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/account", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();

}



/**
 * Logout button
 * Send http POST request to clear session id
 */
document.querySelector('.header__button').addEventListener('click', function () {

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {

                location = 'http://ihse.tk/index.html';  // Refer to start page
            }

            if (this.status === 302) {  // Ok - redir

            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/logout", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();

});






/**
 * Add button event - 'code input'
 * Send http POST request to sing up lecture
 */
document.querySelector('#btn').addEventListener('click', function () {

    let code = document.querySelector('#code');

    if (code.value === "")  // If some field are empty - do nothing
        return;


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {  // When request is done

            if (this.status === 200) {  // Authorized
                alert("ok!");
                loadAccount();

                code.value = "";

            }

            if (this.status === 401) {  // Authorization error
                alert("Wrong code!");  // TODO: show Html error message

                code.value = "";
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/credits?code=" + code.value, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
});








/**
 * Setup barchart - credits circle
 * https://kimmobrunfeldt.github.io/progressbar.js/
 */
// var ProgressBar = require('scripts/progressbar.js');
var bar;
if(document.readyState === 'complete') {
    createBar();
} else {
    window.addEventListener('load', function () {
        createBar();
    })
}
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






/**
 * Setup linechart - credits for days
 * https://apexcharts.com/docs/installation/
 */
startDay = 5;
startMonth = 6;
numOfDays = 14;

topbar_html = "";

var days = [];
for (var i = 0; i < numOfDays; ++i) {
    let day_text = (startDay + i) + '.' + ('' + startMonth).padStart(2, '0');
    days.push( day_text );
}


// Get chart data
data = [1, 2, 3, 4, 5];

function createChart() {

}
var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function () {
    if (this.readyState === 4) {  // When request is done

        if (this.status === 200) {  // Authorized

            let credits = JSON.parse(this.responseText);
            data = credits.data;


            // Chart options
            var options = {
                chart: {
                    height: '110%',
                    width: data.length * 40,
                    type: 'line',
                    zoom: {
                        enabled: false
                    },
                    toolbar: {
                        show: false
                    }
                },
                colors: ['#007ac5'],
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    curve: 'straight'
                },
                series: [{
                    name: "Credits",
                    data: data
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

            // Run and draw chart
            if(window.checkLoaded()) {
                var chart = new ApexCharts(document.querySelector("#credits__chart"), options);

                console.log(chart);
                chart.render();
            } else {
                window.addEventListener('load', function () {
                    var chart = new ApexCharts(document.querySelector("#credits__chart"), options);

                    console.log(chart);
                    chart.render();
                })
            }
        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/credits", true);
xhttp.withCredentials = true;  // To receive cookie
xhttp.send();




/** ===============  ANIMATIONS  =============== */



/**
 * Add code field animations
 * Hint Rise up when there is some text or cursor inside it
 */
var code = document.querySelector('#code');
code.addEventListener('focus', function () {
    code.closest('div').querySelector("label").classList.add('active');
});

code.addEventListener('blur', function () {
    if (code.value != "")
        return;

    code.closest('div').querySelector("label").classList.remove('active');
});