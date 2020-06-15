/**
 * @fileoverview Common logic for all pages
 * File providing all functions which are used to control ANY page
 */




// Cashed sql tables ('users', 'events', ... etc)
// Each of table groupedUnique by Id value in that group
var cache = {};

// Current user or undefined if not login
var user;



// /**
//  * Run function after loading of the page
//  *
//  * @param func: function witch will be run only once after loading of the page
//  */
// function runAfterLoading(func) {
//     // TODO: Check if window already loaded
//     // (function(w) {
//     //     //private variable
//     //     var loaded = false;
//     //     w.onload = function() {
//     //         loaded = true;
//     //     };
//     //
//     //     w.checkLoaded = function() {
//     //         return loaded;
//     //     };
//     // })(window);
//
//     window.addEventListener('load', func);
// }



/**
 * Run function after loading of the page
 *
 * @param func: function witch will be run only once after loading of the page
 */
function runAfterLoading(func, timeout=15) {
    console.log('check');
    /in/.test(document.readyState) ? setTimeout(function () {runAfterLoading(func, timeout)}, timeout) : func()
}



/**
 * Load resources by function list
 * Activate loading start/end functions
 *
 * @param loaders_list: list of loader functions to run
 * @param waiting_list: list of strings with cache names
 * @param setup_funcs: function witch will be run only once after loading
 */
function loadMainResources(loaders_list, waiting_list, setup_funcs) {
    // runAfterLoading(loadingStart, 1);
    window.addEventListener('load', loadingStart);

    for (let res of waiting_list) {
        cache[res] = undefined;
    }

    // Run all functions after 1) page are loaded 2) resources are loaded
    let setup_func = function () {
        for (let func of setup_funcs) {
            func();
        }
        loadingEnd();
    }

    for (let func of loaders_list) {
        func(function () {checkLoading(function () {runAfterLoading(setup_func)}, waiting_list);});
    }
}




/**
 * Setup admin/moderator tag
 */
loadUser(function () {
    if (user['user_type'] >= 1) {
        document.querySelector('body').classList.add('moderator');

        if (user['user_type'] >= 2) {
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


/**
 * Get string of today date (dd.mm)
 */
function getToday() {
    let dd_mm = cache['today'];  // Debug??
    if (dd_mm == undefined) {
        dd_mm = cache['user'].today;
    }
    if (dd_mm == undefined) {
        let today_date = new Date();  //January is 0!
        dd_mm = String(today_date.getDate()).padStart(2, '0') + String(today_date.getMonth() + 1).padStart(2, '0');
    }
    return dd_mm;
}



/** ===============  AUXILIARY FUNCTIONS  =============== */


/**
 * Remove loading class on shadow-skeleton elements
 */
function loadingEnd() {
    console.log('LOADING END')
    document.querySelector('body').classList.add('loading_end');
}
function loadingStart() {
    console.log('LOADING START')
    document.querySelector('body').classList.remove('loading_end');
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





/**
 * Calculate hash from password
 * TODO: Check security
 * TODO: Add salt
 * @param {string} s - password with which the hash is calculated
 * @return {int}
 */
function hashCode(s, salt='') {
    s = salt + s;
    let h = 0;
    for(let i = 0; i < s.length; i++)
        h = Math.imul(31, h) + s.charCodeAt(i) | 0;

    return h;
}




/**
 * Update query params without refreshing a page
 *
 * @param {string} key - key param string
 * @param {string} value - value param string
 */
function setQueryParam(key, value) {
    if (history.pushState) {
        let urlParams = new URLSearchParams(window.location.search);
        urlParams.set(key, value);
        let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + (urlParams.toString() != '' ? '?' + urlParams.toString() : '');
        window.history.pushState({path: newurl}, '', newurl);
    }
}


/**
 * Read query params without refreshing a page
 *
 * @param {string} key - key param string
 * @return {string}
 */
function getQueryParam(key) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(key);
}


/**
 * Delete query params without refreshing a page
 *
 * @param {string} key - key param string
 */
function removeQueryParam(key) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.delete(key);
    let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + (urlParams.toString() != '' ? '?' + urlParams.toString() : '');
    window.history.pushState({path: newurl}, '', newurl);
}






/** ===============  SERVER REQUESTS  =============== */



/**
 * Get days list information from server
 * Send http GET request and get days list
 * Save user dict to global 'cache['days']'
 *
 * Run func on OK status
 */
function loadDays(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {  // Ok
                let days_raw;
                try {
                    days_raw = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error:', e);
                    days_raw = {};
                }

                let days = groupByUnique(days_raw['days'], 'id');
                cache['days'] = days;
                cache['today'] = days_raw['today'];

                func();
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
            }
        }
    };

    xhttp.open("GET", "/days", true);
    xhttp.send();
}



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
                try {
                    user = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error:', e);
                    user = {};
                }

                cache['user'] = user;

                func();
            } else if (this.status === 401) {  // Unauthorized

            }
        }
    };

    xhttp.open("GET", "/user", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


function loadOtherUser(user_id, func) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {  // Ok
                try {
                    user = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error:', e);
                    user = {};
                }

                cache['other'] = user;

                func();
            } else if (this.status === 401) {  // Unauthorized

            }
        }
    };

    xhttp.open("GET", "/user?id=" + user_id, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}



/**
 * Get project information from server by id
 * Send http GET request and get project description
 * Save user dict to global 'cache['project']'
 *
 * Run func on OK status
 */
function loadProject(project_id, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {  // Ok
            let project;
            try {
                project = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                project = {};
            }

            cache['project'] = project;

            func();
        }
    };

    xhttp.open("GET", "/project" + '?id=' + project_id, true);
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
        if (this.readyState === 4 && this.status === 200) {
            let enrolls_raw;
            try {
               enrolls_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                enrolls_raw = [];
            }
            let enrolls = groupByUnique(enrolls_raw, 'id');
            cache['enrolls'] = enrolls;

            func();
        }
    };

    xhttp.open("GET", "/enrolls?event_id=" + class_id, true);
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
        if (this.readyState === 4 && this.status === 200) { // If ok set up fields
            let names_raw;
            try {
               names_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                names_raw = [];
            }

            names = groupByUnique(names_raw, 'id');
            cache['names'] = names;

            func();

        }
    };

    xhttp.open("GET", "/names", true);
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
        if (this.readyState === 4 && this.status === 200) { // If ok set up fields
            let event_class;
            try {
               event_class = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                event_class = {};
            }

            cache['class'] = event_class;
            func();
        }
    };

    xhttp.open("GET", "/class?id=" + class_id, true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}




/**
 * Get event information from server by event_id
 * Save to global 'cache['event']'
 *
 * Run func on OK status
 */
function loadEvent(event_id, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) { // If ok set up fields
            let event;
            try {
               event = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                event = {};
            }

            cache['event'] = event;

            func();
        }
    };

    xhttp.open("GET", "/event?id=" + event_id, true);
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
            let day_data;
            try {
               day_data = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                day_data = [];
            }

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

    let query = '';
    if (day != '') {
        query = '?day=' + day;
    }

    xhttp.open("GET", "/day" + query, true);
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
            let projects_data;
            try {
               projects_data = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                projects_data = [];
            }

            let projects = groupByUnique(projects_data, 'id');

            cache['projects'] = projects;

            func();
        }
    };

    xhttp.open("GET", "/projects", true);
    xhttp.send();
}




/**
 * Get feedback information from server by date
 * Send http GET request and get projects json schedule
 * Save feedback list to global 'cache['feedback']'
 *
 * Run func on OK status
 */
function loadFeedback(date, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up day field
                let feedback;
                try {
                    feedback = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error:', e);
                    feedback = {};
                }

                cache['feedback'] = feedback;

                func();
            }
        }
    };

    xhttp.open("GET", "/feedback?date=" + date , true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}












/**
 * Get credits information from server by user cookies
 * Send http GET request and get projects json schedule
 * Save enrolls list to global 'cache['credits']'
 *
 * Run func on OK status
 */ 
function loadCredits(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) { // If ok set up day field
            let credits_raw;
            try {
               credits_raw = JSON.parse(this.responseText);
            } catch (e) {
                console.log('error:', e);
                credits_raw = [];
            }

            let credits = groupByUnique(credits_raw, 'id');

            cache['credits'] = credits;

            func();
        }
    };

    xhttp.open("GET", "/credits", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}


