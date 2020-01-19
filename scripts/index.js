/**
 * @fileoverview Index page logic
 * File providing all functions which are used to control index.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


// TODO: Hide .html
// ihse.tk/login.html -> ihse.tk/login





/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Get day information from server
 * Send http GET request and get today json schedule
 * than parse of json data and create html
 */
 var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) { // If ok set up day field
        loadingEnd(); // TODO: Check

        var day_data = JSON.parse( this.responseText );


        var day_html = "";
        var time_html;
        var event_html;

            for (let time of day_data) {

                time_html = '<div class="time">' +
                                '<div class="bar">' + time.time + '</div>' +
                                    '<div class="events">';

                for (let event of time.events) {
                    event_html =
                        '<div class="event" data-id="' + event.id + '" ' + (event.type === 'regular' ? '' : 'active-event') + '>' +
                            (event.type === 0 || event.type === '0' ? '' : '<a href="event.html?id=' + event.id + '">') +
                                '<p class="event__title">' + event.title + '</p>' +

                                (event.desc === undefined ? "" : '<p class="event__desc">' + event.desc + '</p>') +

                                ((event.host === undefined || event.host === '') && (event.loc === undefined || event.loc === '') ? "" : '<div class="event__last_line">' +
                                    '<span class="event__names">' + (event.host === undefined ? "" : event.host) + '</span>' +
                                    '<span class="event__loc">' + (event.loc === undefined ? "" : event.loc) + '</span>' +
                                '</div>') +
                            (event.type === 0 || event.type === '0' ? '' : '</a>') +
                        '</div>';


                    time_html += event_html;
                }

                time_html += '</div>' + '</div>';

                time_html += '<hr class="border_line">';

                day_html += time_html;
            }


        document.querySelector('.calendar__day').innerHTML = day_html;  // Set day html
    }
};


// Get today date
var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!

if (today.getDate() < 5 || today.getMonth() + 1 < 6)
    today = '05.06';
else
    today = dd + '.' + mm;


xhttp.open("GET", "http://ihse.tk:50000/day?day=" + today, true);
xhttp.send();
