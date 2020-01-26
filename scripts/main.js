/**
 * @fileoverview Common logic for all pages
 * File providing all functions which are used to control ANY page
 */




// Cashed sql tables ('users', 'events', ... etc)
// Each of table groupedUnique by Id value in that group
var cache = {};

// Current user or undefined if not login
var user;


/**
 * Setup admin/moderator tag
 */
loadUser(function () {
    if (user.type >= 1) {
        document.querySelector('body').classList.add('moderator');

        if (user.type >= 2) {
            document.querySelector('body').classList.add('admin');
        }
    }
});


/**
 * Check if all necessary resources are loaded
 * If true then run function
 */
function checkLoading(foo, waiting_list) {
    let loaded = true;
    for (let res of waiting_list) {
        if (!(res in cache) || cache[res] === undefined) {
            loaded = false;
        }
    }

    if (loaded) {
        foo();
    }
}



/** ===============  AUXILIARY FUNCTIONS  =============== */


/**
 * Remove loading class on shadow-skeleton elements
 */
function loadingEnd() {
    let ls = document.querySelectorAll('.data__loading');
    for (let i = 0; i < ls.length; i++) {
        ls[i].classList.remove('data__loading');
    }
}


/**
 * Sort array of dicts by some field
 * return: array of objs
 */
function sortBy(arr, property) {
    arr.sort(function (first, second) {
        return first[property] - second[property];
    });
}

/**
 * Group array of dicts by some field
 * return: dict of arrays {id1: [], id2: [], ...}
 */
function groupBy(arr, property) {
    sortBy(arr, property);

    return arr.reduce(function (memo, x) {
        if (!memo[x[property]]) {
            memo[x[property]] = [];
        }
        memo[x[property]].push(x);
        return memo;
    }, {});
}

/**
 * Group array of dicts by some unique field
 * return: dict of elements {id1: obj, id2: obj, ...}
 */
function groupByUnique(arr, property) {
    sortBy(arr, property);

    return arr.reduce(function(memo, x) {
        if (!memo[x[property]]) {
            memo[x[property]] = x;
        }
        return memo;
    }, {});
}



/** ===============  SERVER REQUESTS  =============== */



/**
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 * Save user dict to global 'var user'
 *
 * Run func on OK status
 */
function loadUser(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {  // Ok
                user = JSON.parse(this.responseText);

                func();
            } else if (this.status === 401) {  // Unauthorized

            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/user", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


/**
 * Get enrolls information from server according to event_id
 * Send http GET request and loist of enrolls by event_id  TODO: rename in class_id
 * Save enrolls list to global 'cache'
 *
 * Run func on OK status
 */
function loadEnrollsByClassId(class_id, func) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {
                let enrolls_raw = JSON.parse(this.responseText);
                let enrolls = groupByUnique(enrolls_raw, 'id');
                cache['enrolls'] = enrolls;

                func();
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/enrolls?event_id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}



/**
 * Get names information from server
 * Save enrolls list to global 'cache'
 *
 * Run func on OK status
 */
function loadNames(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                let names_raw = JSON.parse(this.responseText);
                names = groupByUnique(names_raw, 'id');
                cache['names'] = names;

                func();
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/names", true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}



/**
 * Get class information from server by class_id (event_id)
 * Save enrolls list to global 'cache['class']'
 *
 * Run func on OK status
 */
function loadClass(class_id, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                let event_class = JSON.parse(this.responseText);

                cache['class'] = event_class;

                func();
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/class?id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


/**
 * Get day information from server
 * Send http GET request and get today json schedule
 * Save enrolls list to global 'cache['events']'
 *
 * Run func on OK status
 */
function loadDay(day, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let day_data = JSON.parse(this.responseText);

            let current_events = {};
            for (let time of day_data) {
                for (let event of time.events) {
                    current_events[event.id] = event;
                }
            }
            cache['events'] = current_events;

            func();
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/day?day=" + day, true);
    xhttp.send();
}

/**
 * Get projects information from server
 * Send http GET request and get projects json schedule
 * Save enrolls list to global 'cache['projects']'
 *
 * Run func on OK status
 */
function loadProjects(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let projects_data = JSON.parse(this.responseText);
            let projects = groupByUnique(projects_data, 'id');

            cache['projects'] = projects;

            func();
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/projects", true);
    xhttp.send();
}

/**
 * Get credits information from server by user cookies
 * Send http GET request and get projects json schedule
 * Save enrolls list to global 'cache['projects']'
 *
 * Run func on OK status
 */
function loadCredits(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let credits_raw = JSON.parse(this.responseText);
            let credits = groupBy(credits_raw, 'id');

            cache['credits'] = credits;

            func();
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/credits", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}
