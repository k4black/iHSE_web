/**
 * @fileoverview Feedback page logic
 * File providing all functions which are used to control feedback.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



/**
 * Add button event - press topbar
 * Send http POST request to get session id
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
    values: [2008, 2009, 2010, 2011, 2014],
    range: true, // range slider
    set:    null, // an array of preselected values
    width:    null,
    scale:    true,
    labels:   true,
    tooltip:  true,
    step:     null, // step size
    disabled: false, // is disabled?
    onChange: null // callback

});





