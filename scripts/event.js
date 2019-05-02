



const urlParams = new URLSearchParams(window.location.search);

var eventId = urlParams.get('id');
console.log(eventId);

var wrapper = document.querySelector('.wrapper');
var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function () {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up fields


            var event = JSON.parse( this.responseText );

            document.querySelector('.title').innerText = event.title;

            wrapper.querySelector('.time').firstElementChild.innerText = event.date;
            wrapper.querySelector('.time').lastElementChild.innerText = event.time;

            wrapper.querySelector('.location').firstElementChild.innerText = event.loc;

            wrapper.querySelector('.host').firstElementChild.innerText = event.host;

            wrapper.querySelector('.desc').firstElementChild.innerText = event.desc;

            // TODO: Hide when there is no enrollment
            wrapper.querySelector('.count').innerText = event.count + ' / ' + event.total;

            bar.animate( event.count / event.total );  // Number from 0.0 to 1.0

            if (event.count >= event.total) {
                wrapper.querySelector('#btn').classList.add('inactive');
            }
        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/event?id=" + eventId, true);
// xhttp.withCredentials = true; // To send Cookie;
xhttp.send();



// TODO: If admin get list of enrolled
// TODO: Add unenrollment





// https://kimmobrunfeldt.github.io/progressbar.js/
// var ProgressBar = require('scripts/progressbar.js');
var bar;
window.addEventListener('load', function () {
    console.log('Load');

    bar = new window.ProgressBar.Line('#container', {
        strokeWidth: 4,
        easing: 'easeInOut',
        duration: 1400,
        color: '#007ac5',
        trailColor: '#eee',
        trailWidth: 1,
        svgStyle: {width: '100%', height: '100%'},
        from: {color: '#007ac5'},
        to: {color: '#ed992f'},
        step: (state, bar) => {
            bar.path.setAttribute('stroke', state.color);
        }
    });
});
