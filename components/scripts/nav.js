

function setupNav(active_tab) {
    // active_tab \in {'home', 'calendar', 'feedback', 'projects'}
    console.log('LOGlog');

    document.querySelector('#mi_' + active_tab).classList.add('mobile__item__active');
}


setupNav('home');