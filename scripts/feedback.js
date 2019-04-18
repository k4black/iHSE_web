/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



/**
 * Add button event - press topbar
 * Set up day feedback form
 */
var days = document.querySelectorAll('.day');

for (var i = 0; i < days.length; i++) {

    days[i].addEventListener('click', function() {

        alert(this.querySelector('.day__name').innerText);

    });

}






// https://www.cssscript.com/animated-customizable-range-slider-pure-javascript-rslider-js/

var mySlider = new rSlider({
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

var slider2 = new rSlider({
    target: '#slider2',
    values: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    range: false,
    set: [5],
    tooltip: false,
    // onChange: function (vals) {
    //     console.log(vals);
    // }
});


/**
 * Add button event - press topbar
 * Set up day feedback form
 */
var button = document.querySelector('#btn');

button.addEventListener('click', function() {

    console.log("Overall: " + mySlider.getValue() );

    events = button.parentElement.querySelectorAll('.event');
    for (var i = 0; i < events.length; i++) {
        console.log("Event " + i + " " + events[i].firstChild.textContent + ": " + slider2.getValue() + " - " + events[i].lastChild.textContent );
    }

    users = button.parentElement.querySelectorAll('.day');
    for (var i = 0; i < users.length; i++) {
        console.log("User " + i + ": " + users[i].value );
    }




});



