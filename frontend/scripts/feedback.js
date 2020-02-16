/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



window.addEventListener('load', function () {
    loadDays(setDays);
});


function setDays() {
    let today = getToday();

    let days_list = Object.values(cache['days']).map(function (currentValue, index, array) {
        return currentValue['date'];
    });

    if (days_list.includes(today)) {
        today = today;
    } else {
        today = days_list[0];
    }

    let topbar_html = '';
    let i = 0;
    for (let day of cache['days']) {
        if (!day['feedback'] || day.id == 0) {
            ++i;
            continue;
        }

        if (day.date === today) {  // TODO: Today
            topbar_html += '<div class="day today selected">'
        } else {
            topbar_html += '<div class="day">'
        }

        topbar_html += '<div class="day__num">' + i + '</div>' +
            '<div class="day__name">' + day.date + '</div>' +
            '</div>';

        ++i;
    }


    document.querySelector('.topbar').innerHTML = topbar_html;


    // Set onclick loading other day
    var days = document.querySelectorAll('.day');
    for (let i = 0; i < days.length; i++) {
        days[i].addEventListener('click', function() {
            document.querySelector('.selected').classList.remove('selected');
            this.classList.add('selected');

            loadFeedback(this.lastElementChild.textContent, setFeedback);
        });
    }
}



/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Loading users in list
 * Send http GET request to get users
 */
var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function () {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up fields name and phone

            // console.log(this.responseText);
            var users = JSON.parse(this.responseText);

            var datalist_html = "";

            for (var i = 0; i < users.length; ++i) {
                datalist_html += '<option value="' + users[i] + '">';
            }


            document.querySelector('#users_list').innerHTML = datalist_html;
        }
    }
};

xhttp.open("GET", "//ihse.tk/names", true);
xhttp.withCredentials = true; // To send Cookie;
xhttp.send();




/**
 * Create topbar day buttons
 */
var today_date = new Date();
var dd = String(today_date.getDate()).padStart(2, '0');

var mm = String(today_date.getMonth() + 1).padStart(2, '0'); //January is 0!


var today = mm + '.' + dd;

startDay = 5;
startMonth = 6;
numOfDays = 14;
text_days = ['05.06', '08.06', '11.06', '14.06', '17.06', '18.06'];


topbar_html = "";

for (var i = 0; i < text_days.length; ++i) {
    let day_text = text_days[i];
    if ( day_text === today) {
        topbar_html += '<div class="day today selected">'
    } else {
        topbar_html += '<div class="day">'
    }

    topbar_html +=          '<div class="day__num">' + i + '</div>' +
        '<div class="day__name">' + day_text + '</div>' +
        '</div>';
}

console.log(topbar_html);
document.querySelector('.topbar').innerHTML = topbar_html;




setupDays();
function setupDays() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            days = JSON.parse( this.responseText );
            sortBy(days, 'date');

            let days_list = [];
            for (let day of days) {
                if (day.feedback) {
                    days_list.push(day.date);
                }
            }

            let today_date = new Date();  //January is 0!
            let dd_mm = String(today_date.getDate()).padStart(2, '0') + String(today_date.getMonth() + 1).padStart(2, '0');;

            if (days_list.includes(dd_mm)) {
                today = dd + '.' + mm;
            } else {
                today = days_list[0];
            }

            let topbar_html = '';
            for (var i = 0; i < days.length; ++i) {
                if (days[i].date === today) {  // TODO: Today
                    topbar_html += '<div class="day today selected">'
                } else {
                    topbar_html += '<div class="day">'
                }

                topbar_html += '<div class="day__num">' + i + '</div>' +
                    '<div class="day__name">' + days[i].date + '</div>' +
                    '</div>';
            }

            document.querySelector('.topbar').innerHTML = topbar_html;

            var days = document.querySelectorAll('.day');
            for (let i = 0; i < days.length; i++) {
                days[i].addEventListener('click', function() {
                    document.querySelector('.selected').classList.remove('selected');
                    this.classList.add('selected');

                    getDay(this.lastElementChild.textContent);
                });
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/days", true);
    xhttp.send();
}



/**
 * Get and set feedback day description
 * GET request to get day data
 */
function getDay(dayNum) {

    form = document.querySelector('.feedback_form');

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                var day = JSON.parse( this.responseText );

                form.firstElementChild.innerText = day.title;

                var events = form.querySelectorAll('.event');

                for (var i = 0; i < events.length; i++) {
                    events[i].firstElementChild.innerText = day.events[i].title;
                }

            }
        }
    };

    xhttp.open("GET", "//ihse.tk/feedback?day=" + dayNum, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


/**
 * Add button event - press topbar
 * Set up day feedback form. GET request to get day data
 */
var days = document.querySelectorAll('.day');
for (let i = 0; i < days.length; i++) {

    days[i].addEventListener('click', function() {

        document.querySelector('.selected').classList.remove('selected');
        this.classList.add('selected');


        getDay(this.lastElementChild.textContent)
    });

}




/**
 * First time Set up day feedback form.
 * GET request to get day data
 */
var today_date = new Date();
var dd = String(today_date.getDate()).padStart(2, '0');
var mm = String(today_date.getMonth() + 1).padStart(2, '0'); //January is 0!


var today = mm + '.' + dd;

getDay(today);





/**
 * Setup sliders
 * https://www.cssscript.com/animated-customizable-range-slider-pure-javascript-rslider-js/
 */
var overallSlider = new rSlider({
    target: '#slider',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false, // range slider
    set:    [5], // an array of preselected values
    scale:    true,
    labels:   true,
    tooltip:  false,
    step:     1, // step size
    disabled: false, // is disabled?
    onChange: null // callback
});


var eventSliders = [];

eventSliders[0] = new rSlider({
    target: '#event1',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});

eventSliders[1] = new rSlider({
    target: '#event2',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});

eventSliders[2] = new rSlider({
    target: '#event3',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
});




/**
 * Add button event - 'send feedback'
 * Send http POST request to set feedback message
 */
document.querySelector('#btn').addEventListener('click', function() {

    events = document.querySelectorAll('.event');
    users = document.querySelectorAll('.user');

    // Checking full fields
    var flag = false;
    for (let i = 0; !flag && i < events.length; ++i) {
        flag = (events[i].lastElementChild.textContent === '');
    }
    for (let i = 0; !flag && i < users.length; ++i) {
        flag = (users[i].value === '');
    }
    if (flag){ // If some field are empty - do nothing
        alert('You have to fill all fields!');  // TODO: show Html error message
        return;
    }

    var data = JSON.stringify({"overall": overallSlider.getValue(),
                                     "user1": users[0].value,
                                     "user2": users[1].value,
                                     "user3": users[2].value,
                                     "event1": eventSliders[0].getValue(),
                                     "event2": eventSliders[1].getValue(),
                                     "event3": eventSliders[2].getValue(),
                                     "event1_text": events[0].lastElementChild.textContent,
                                     "event2_text": events[1].lastElementChild.textContent,
                                     "event3_text": events[2].lastElementChild.textContent
                              });


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            setLoaded();

            if (this.status === 200) {  // Got it
                location = "../index.html"
            }

            if (this.status === 302) {  // Ok - redir

            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("not!");  // TODO: show Html error message
            }
        }
    };


    var query = "?day=" + document.querySelector('.today').lastElementChild.textContent;
    xhttp.open("POST", "//ihse.tk/feedback" + query, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);

});




/** ===============  ANIMATIONS  =============== */



/**
 * Show and hide loading button
 */
var button = document.querySelector('#btn');
var button2 = document.querySelector('#btn2');
function setLoading() {
    button.style.display = 'none';
    button2.style.display = 'block';
}

function setLoaded() {
    button.style.display = 'block';
    button2.style.display = 'none';
}



