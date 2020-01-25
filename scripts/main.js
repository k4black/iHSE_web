/**
 * @fileoverview Common logic for all pages
 * File providing all functions which are used to control ANY page
 */




/**
 * Cashed sql tables
 * ('users', 'events', ... etc)
 * Each of table groupedUnique by Id value in that group
 */
var cache = {};

/**
 * Current user or undefined if not login
 */
var user;



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