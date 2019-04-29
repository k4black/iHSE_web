/**
 * @fileoverview Index page logic
 * File providing all functions which are used to control index.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */





/** ===============  LOGIC and REQUESTS  =============== */


// TODO: Loading icon


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
