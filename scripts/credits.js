/**
 * @fileoverview Credits page logic
 * File providing all functions which are used to control credits.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


/** ===============  TABLE REQUESTS  =============== */




var $table = $('#table');
var $popup = $('#popup')[0];


function foundCreditsId(user_id, event_id) {
    for (let credits_id in credits) {
        if (credits[credits_id].user_id == user_id && credits[credits_id].event_id == event_id) {
            return credits[credits_id].id;
        }
    }

    return '';
}


function creditsFormatter(value, row, index) {
    return '<div class="item" id="' + foundCreditsId(row.id, ) + '">' + '<p>' + value + '</p></div>'
}


function groupBy(arr, property) {
    return arr.reduce(function(memo, x) {
        if (!memo[x[property]]) {
            memo[x[property]] = [];
        }
        memo[x[property]].push(x);
        return memo;
    }, {});
}


function processCredits(credits_raw) {
    credits_raw.sort(function(first, second) {
        return first.user_id - second.user_id;
    });

    let credits_rawGroups = groupBy(credits_raw, 'user_id');

    let credits = {};

    for (let user_id in credits_rawGroups) {
        credits[user_id] = processUserCredits(credits_rawGroups[user_id]);
    }

    return credits;
}


function processUserCredits(userCredits_raw) {
    userCredits_raw.sort(function(first, second) {
        return first.date - second.date;
    });
    userCredits_rawGroups = groupBy(userCredits_raw, 'date');

    let userCredits = [];

    for (let date in userCredits_rawGroups) {
        userCredits[date] = [];

        for (let j in userCredits_rawGroups[date]) {
            userCredits[date].push({'id': userCredits_rawGroups[date][j].id, 'event_id': userCredits_rawGroups[date][j].event_id, 'value': userCredits_rawGroups[date][j].value});
        }
    }

    return userCredits;
}



function processUsers(users_raw) {
    let users = {};

    for (let i in users_raw) {
        users[users_raw[i].id] = users_raw[i];
    }

    return users;
}


function processEvents(events_raw) {
    let events = {};

    for (let i in events_raw) {
        events[events_raw[i].id] = events_raw[i];
    }

    return events;
}


function getDaysEvents(credits, days, events) {
    let processed_days = {};

    for (let day_id in days) {
        processed_days[day_id] = new Set();
    }

    for (let id in credits) {
        let event_id = credits[id]['event_id'];
        let day_id = events[event_id]['day_id'];

        processed_days[day_id].add(event_id);
    }

    return processed_days;
}






function getTableColumns(credits, days, events) {
    let columnsTop = [];
    let columnsBottom = [];

    let userColumns = ['id', 'name', 'group', 'total'];
    let fixedColumns = userColumns.length;


    let specialColumns = ['olymp', 'sport'];


    for (let i of userColumns) {
        columnsTop.push({
            field: i,
            title: i,
            sortable: true,
            rowspan: 2,
            valign: 'middle',
            filter: "input",
            // formatter: function (val) {
            //     return '<div class="title_cell">' + val + '</div>'
            // },
            class: 'title_cell'
        });
    }


    processed_days = getDaysEvents(credits, days, events);  // Dict of Sets {day_id: {event_id's, ....} , ..}


    for (let day_id in processed_days) {
        columnsTop.push({
            title: days[day_id].date,
            colspan: processed_days[day_id].size + 1,
            align: 'center'
        });

        for (let event_id of processed_days[day_id]) {
            columnsBottom.push({
                field: 'date' + days[day_id].date + 'id' + event_id,
                title: event_id,
                titleTooltip: 'Title: ' + events[event_id].title,
                sortable: true,
                align: 'center',
                valign: 'middle',
                // formatter: creditsFormatter,
                formatter: function (value, row, index) {
                    return '<div class="item" id="' + foundCreditsId(row.id, event_id) + '">' + '<p>' + value + '</p></div>'
                },
                events: {
                    'click .item': function (event) {
                        console.log('click ' + event.currentTarget)
                    }
                },
                class: 'cell'
            });
        }
        columnsBottom.push({
            field: 'date' + days[day_id].date + 'total',
            title: 'Total',
            sortable: true,
            align: 'center',
            valign: 'middle',
            // formatter: function (val) {
            //     return '<div class="total total_cell">' + val + '</div>'
            // },
            class: 'total_cell'
        });
    }

    for (let i of specialColumns) {
        columnsTop.push({
            field: i,
            title: i,
            sortable: true,
            rowspan: 2,
            valign: 'middle'
        });
    }

    return [columnsTop, columnsBottom];
}

function getTableData(credits, users, days, events) {
    let data = [];

    for (let user_id in users) {
        let row = {};

        row['id'] = user_id;
        row['name'] = users[user_id].name;
        row['group'] = users[user_id].team;

        // To avoid undef
        row['total'] = 0;
        for (let day_id in days) {
            for (let event_id in events) {
                row['date' + days[day_id].date + 'id' + event_id] = 0;
            }
            row['date' + days[day_id].date + 'total'] = 0;
        }


        console.log('credits: ', credits);
        for (let credit_id in credits) {

            if (user_id == credits[credit_id]['user_id']) {  // Only for current user
                let event_id = credits[credit_id]['event_id'];
                let day_id = events[event_id]['day_id'];
                let value = credits[credit_id]['value'];

                row['date' + days[day_id].date + 'id' + event_id] = value;
                row['date' + days[day_id].date + 'total'] += value;
                row['total'] += value;
            }
        }

        data.push(row);
    }
    return data;
}



function buildTable($el, credits, users, days, events) {
    let [columnsTop, columnsBottom] = getTableColumns(credits, days, events);
    let data = getTableData(credits, users, days, events);

    console.log('data', data);
    console.log('columnsTop', columnsTop);
    console.log('columnsBottom', columnsBottom);

    $el.bootstrapTable('destroy').bootstrapTable({
        // responseHandler(res) {
        //   res.rows.forEach(row => {
        //     row.id = {
        //       'tableexport-msonumberformat': '\\@'
        //     }
        //   });
        //   return res
        // },
        // onAll: styleTable,
        undefinedText: '0',
        columns: [columnsTop, columnsBottom],
        data: data,
        search: true,
        fixedColumns: true,
        fixedNumber: 4,
    });
}


function setTable() {
    events = cache['events'];
    users = cache['users'];
    days = cache['days'];
    credits = cache['credits'];


    buildTable($table, credits, users, days, events);


    let userColumns = ['id', 'name', 'group', 'total'];


    $table.on('all.bs.table', function (e, name, args) {
        if (name !== "click-cell.bs.table") {
            return;
        }

        if (userColumns.includes(args[0])) {
            return;
        }

        console.log(name, args);
        let credit_id = args[3][0]['children'][0].id;
        let user_id = args[2].id;
        let value = args[1];
        let time = credits[credit_id]['time'];
        let event_id = args[0].slice(11);
        console.log(credit_id, user_id, event_id, time, event_id === 'tal');

        if (event_id === 'tal') {
            // Total
            return;
            addCredit(event_id, user_id, 0);
        } else {
            // edit some
            if (value === 0 || value === '0') {
                editCredit('', user_id, event_id, '', value);
            } else {
                editCredit(credit_id, user_id, event_id, time, value);
            }
        }
    })
}








/**
 * Get ALL obj information from server (ADMIN rights)
 * Save obj list to global 'cache'
 *
 * Run func on OK status
 */
function loadTable(tableName, func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                // loadingEventEnd();

                let obj_raw = JSON.parse(this.responseText);
                objs = groupByUnique(obj_raw, 'id');
                cache[tableName] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_get_table?" + "table=" + tableName, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}



function loadAndCreateTable() {
    cache['credits'] = undefined;

    loadTable('credits', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'credits', 'days']);});
}


$(function() {
    loadTable('users', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'credits', 'days']);});
    loadTable('events', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'credits', 'days']);});
    loadTable('days', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'credits', 'days']);});

    loadAndCreateTable();
});





function addCredit(user_id, value) {
    editCredit('', user_id,'', '', value)
}

function editCredit(id, user_id, event_id, time, value) {
    document.getElementById('id').value = id;
    document.getElementById('user_id').value = user_id;
    document.getElementById('event_id').value = event_id;
    document.getElementById('time').value = time;
    document.getElementById('value').value = value;

    $popup.style.display = 'block';
}



function saveCredit() {
    let id = document.getElementById('id').value;
    let user_id = document.getElementById('user_id').value;
    let event_id = document.getElementById('event_id').value;
    let time = document.getElementById('time').value;
    let value = document.getElementById('value').value;

    alert('Saving credit: ' + id + ' ' + user_id + ' ' + event_id + ' ' + time + ' ' + value);

    if (event_id === '' || value === '') {
        alert('Cannot save with empty EVENT_ID or VALUE');
        return;
    }

    $popup.style.display = 'none';

    let data = JSON.stringify({
                                "id": id,
                                "user_id": user_id,
                                "event_id": event_id,
                                "time": time,
                                "value": value,
                                });


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 1) {  // Opened
            // setLoading();
        }

        if (this.readyState === 4) {  // When request is done
            // setLoaded();

            if (this.status === 200) {  // Got it
                alert("ok!");
                // TODO: Optimize?
                loadAndCreateTable();

            }

            if (this.status === 405) {  //  Method Not Allowed or already got it
                alert("Cannot save event! NO PERMISSIONS");  // TODO: show Html error message
            }
        }
    };


    xhttp.open("POST", "http://ihse.tk:50000/admin_send_data?" + "table=credits", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}



/** ===============  LOGIC and REQUESTS  =============== */


