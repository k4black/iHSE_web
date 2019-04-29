/**
 * @fileoverview Calendar page logic
 * File providing all functions which are used to control calendar.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */




var today_date = new Date();
var dd = String(today_date.getDate()).padStart(2, '0');
var mm = String(today_date.getMonth() + 1).padStart(2, '0'); //January is 0!


var today = mm + '.' + dd;



startDay = 5;
numOfDays = 14;

topbar_html = "";

for (var i = 0; i < numOfDays; ++i) {
    if ( (startDay + i) == 15) {
        topbar_html += '<div class="day today selected">'
    } else {
        topbar_html += '<div class="day">'
    }

    topbar_html +=          '<div class="day__num">' + i + '</div>' +
        '<div class="day__name">' + (startDay + i) + '.' + '06' + '</div>' +
        '</div>';
}

console.log(topbar_html);
document.querySelector('.topbar').innerHTML = topbar_html;








/**
 * Get day information from server
 * Send http GET request and get today json schedule
 * than parse of json data and create html
 * TODO: optimize selection
 * TODO: optimize html generation
 */
var day = document.querySelector('.calendar__day');

var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up day field

            var day_data = JSON.parse( this.responseText );



            var day_html = "";
            var time_html;
            var event_html;

            for (var time of day_data) {

                time_html = '<div class="time">' +
                    '<div class="bar">' +
                    '<div>' + time.time + '</div>' +
                    '</div>' +
                    '<div class="events">';

                for (var event of time.events) {
                    event_html =    '<div class="event">' +
                        '<p class="event__title">' + event.title + '</p>' +

                        (event.desc == undefined ? "" : '<p class="event__desc">' + event.desc + '</p>') +

                        (event.host == undefined && event.loc == undefined ? "" :
                            '<div class="event__last_line">' +
                            '<span class="event__names">' + (event.host == undefined ? "" : event.host) + '</span>' +
                            '<span class="event__loc">' + (event.loc == undefined ? "" : event.loc) + '</span>' +
                            '</div>') +
                        '</div>';

                    time_html += event_html;

                }

                time_html += '</div>' + '</div>' + '<hr class="border_line">';

                day_html += time_html;
            }


            day.innerHTML = day_html;
        }
    }
};


// Get today date
var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!

today = mm + '.' + dd;

xhttp.open("GET", "http://ihse.tk:50000/day?day=" + today, true);
xhttp.send();




// TODO: Optimize html creation




/**
 * Add button event - press topbar
 * Set up day feedback form. GET request to get day data
 */
var days = document.querySelectorAll('.day');

for (var i = 0; i < days.length; i++) {

    form = document.querySelector('.calendar__day');

    days[i].addEventListener('click', function() {

        alert(this.querySelector('.day__name').innerText);

        document.querySelector('.selected').classList.remove('selected');
        this.classList.add('selected');

        var query = "day=" + this.lastElementChild.textContent;


        var xhttp = new XMLHttpRequest();

        xhttp.onreadystatechange = function() {
            if (this.readyState === 1) { // Opened
                form.innerHTML = '<img class="loading" alt="Loading" src="images/loading.gif">'
            }
            if (this.readyState === 4) {
                if (this.status === 200) { // If ok set up day field

                    var day_data = JSON.parse( this.responseText );



                    var day_html = "";
                    var time_html;
                    var event_html;


                    for (var time of day_data) {

                        time_html = '<div class="time">' +
                            '<div class="bar">' +
                            '<div>' + time.time + '</div>' +
                            '</div>' +
                            '<div class="events">';

                        for (var event of time.events) {
                            event_html =    '<div class="event">' +
                                '<p class="event__title">' + event.title + '</p>' +

                                (event.desc == undefined ? "" : '<p class="event__desc">' + event.desc + '</p>') +

                                (event.host == undefined && event.loc == undefined ? "" :
                                    '<div class="event__last_line">' +
                                    '<span class="event__names">' + (event.host == undefined ? "" : event.host) + '</span>' +
                                    '<span class="event__loc">' + (event.loc == undefined ? "" : event.loc) + '</span>' +
                                    '</div>') +
                                '</div>';

                            time_html += event_html;

                        }

                        time_html += '</div>' + '</div>' + '<hr class="border_line">';

                        day_html += time_html;
                    }


                    form.innerHTML = day_html;
                }
            }
        };

        xhttp.open("GET", "http://ihse.tk:50000/day?" + query, true);
        xhttp.send();


        // TODO: set today
    });


}