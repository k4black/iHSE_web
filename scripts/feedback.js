/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



// TODO: set today



/**
 * Add button event - press topbar
 * Set up day feedback form. GET request to get day data
 */
var days = document.querySelectorAll('.day');

for (var i = 0; i < days.length; i++) {

    form = document.querySelector('.feedback_form');

    days[i].addEventListener('click', function() {

        alert(this.querySelector('.day__name').innerText);




        var xhttp = new XMLHttpRequest();

        xhttp.onreadystatechange = function() {
            if (this.readyState === 4) {
                if (this.status === 200) { // If ok set up fields name and phone

                    // console.log(this.responseText);
                    var day = JSON.parse( this.responseText );

                    form.firstElementChild.innerText = day.title;

                    var events = form.querySelectorAll('.event');

                    for (var i = 0; i < events.length; i++) {
                        events[i].firstElementChild.innerText = day.events[i].title;
                    }

                }
            }
        };

        xhttp.open("GET", "http://ihse.tk:50000/feedback", true);
        xhttp.send();


        // TODO: set today
    });


}





// https://www.cssscript.com/animated-customizable-range-slider-pure-javascript-rslider-js/

var overallSlider = new rSlider({
    target: '#slider',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false, // range slider
    set:    [5], // an array of preselected values
    width:    null,
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
 * Add button event - 'feedback'
 * Send http POST request to set feedback message
 */
var button = document.querySelector('#btn');

button.addEventListener('click', function() {

    console.log("Overall: " + overallSlider.getValue() );

    events = button.parentElement.querySelectorAll('.event');
    for (var i = 0; i < events.length; i++) {
        console.log("Event " + i + " " + events[i].firstElementChild.textContent + ": " + eventSliders[i].getValue() + " - " + events[i].lastElementChild.textContent );
    }

    users = button.parentElement.querySelectorAll('.user');
    for (var i = 0; i < users.length; i++) {
        console.log("User " + i + ": " + users[i].value );
    }



    var query = "?day=" + document.querySelector('.today').lastElementChild.textContent;


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
        if (this.readyState === 4) {  // When request is done

            if (this.status === 200) {  // Got it
                alert("ok!");  // TODO: Redirection

            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("not!");  // TODO: show Html error message

            }
        }
    };


    xhttp.open("POST", "http://ihse.tk:50000/feedback" + query, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');

    xhttp.withCredentials = true;  // To receive cookie

    xhttp.send(data);

});





