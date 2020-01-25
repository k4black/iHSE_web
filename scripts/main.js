/**
 * @fileoverview Common logic for all pages
 * File providing all functions which are used to control ANY page
 */



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




function processNames(names_raw) {
    names_raw.sort(function(first, second) {
        return first.id - second.id;
    });

    let names_rawGroups = groupBy(names_raw, 'id');

    let names = {};

    for (let user_id in names_rawGroups) {
        names[user_id] = names_rawGroups[user_id][0];
    }

    return names;
}


function processEnrolls(enrolls_raw) {
    enrolls_raw.sort(function(first, second) {
        return first.id - second.id;
    });

    let enrolls_rawGroups = groupBy(enrolls_raw, 'id');

    let enrolls = {};

    for (let user_id in enrolls_rawGroups) {
        enrolls[user_id] = enrolls_rawGroups[user_id][0];
    }

    return enrolls;
}
