



const urlParams = new URLSearchParams(window.location.search);

const myParam = urlParams.get('id');
console.log(myParam);




// https://kimmobrunfeldt.github.io/progressbar.js/
// var ProgressBar = require('scripts/progressbar.js');
window.addEventListener('load', function () {
    console.log('Load');

    var bar = new window.ProgressBar.Line('#container', {
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

    bar.animate(1.0);  // Number from 0.0 to 1.0

});
