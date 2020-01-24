

function setupNav(active_tab) {
    // active_tab \in {'home', 'calendar', 'feedback', 'projects'}
    console.log('LOGlog');

    document.querySelector('#mi_' + active_tab).classList.add('mobile__item__active');
}


setupNav('home');


var open = false;

function showNav() {
    open = true;
    document.querySelector('.mobile').classList.add('mobile__open');
    // console.log("Open menu");
}

function hideNav() {
    open = false;
    document.querySelector('.mobile').classList.remove('mobile__open');
    // console.log("Close menu");
}