/**
 * @fileoverview Credits page logic
 * File providing all functions which are used to control credits.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


/** ===============  TABLE REQUESTS  =============== */




var $table = $('#table');
var $popup = $('#popup')[0];



function creditsFormatter(value, row, index) {
    return '<div class="item" id="' + row.id + '">' + '<p>' + value + '</p></div>'
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


function getDays(credits) {
    let days = {};

    for (let user_id in credits) {
        for (let date in credits[user_id]) {
            days[date] = new Set();
        }
    }

    for (let user_id in credits) {
        for (let date in credits[user_id]) {
            for (let i in credits[user_id][date]) {
                days[date].add(credits[user_id][date][i].event_id);
            }
        }
    }

    return days;
}


events_raw = [
    {'id': 0, 'type': 1, 'title': 'Some title 0', 'date': '06.10'},
    {'id': 1, 'type': 1, 'title': 'Some title 1', 'date': '06.10'},
    {'id': 2, 'type': 1, 'title': 'Some title 2', 'date': '07.10'},
    {'id': 3, 'type': 1, 'title': 'Some title 3', 'date': '07.10'},
    {'id': 4, 'type': 1, 'title': 'Some title 4', 'date': '07.10'},
    {'id': 5, 'type': 1, 'title': 'Some title 5', 'date': '07.10'},
    {'id': 6, 'type': 1, 'title': 'Some title 6', 'date': '08.10'},
    {'id': 7, 'type': 1, 'title': 'Some title 7', 'date': '09.10'},
    {'id': 8, 'type': 1, 'title': 'Some title 8', 'date': '09.10'},
    {'id': 9, 'type': 1, 'title': 'Some title 9', 'date': '06.10'},
];


credits_raw = [
    {'id': 0, 'user_id': 3, 'event_id': 0, 'date': '06.10', 'value': 100},
    {'id': 1, 'user_id': 3, 'event_id': 1, 'date': '06.10', 'value': 200},
    {'id': 2, 'user_id': 3, 'event_id': 3, 'date': '07.10', 'value': 300},
    {'id': 3, 'user_id': 3, 'event_id': 4, 'date': '07.10', 'value': 100},
    {'id': 4, 'user_id': 3, 'event_id': 5, 'date': '07.10', 'value': 50},
    {'id': 5, 'user_id': 3, 'event_id': 6, 'date': '08.10', 'value': 311},

    {'id': 6, 'user_id': 1, 'event_id': 0, 'date': '06.10', 'value': 311},
    {'id': 7, 'user_id': 1, 'event_id': 2, 'date': '07.10', 'value': 30},
    {'id': 8, 'user_id': 1, 'event_id': 5, 'date': '07.10', 'value': 50},
    {'id': 9, 'user_id': 1, 'event_id': 6, 'date': '08.10', 'value': 64},
    {'id': 10, 'user_id': 1, 'event_id': 7, 'date': '09.10', 'value': 45},

    {'id': 11, 'user_id': 4, 'event_id': 1, 'date': '06.10', 'value': 311},
    {'id': 12, 'user_id': 4, 'event_id': 2, 'date': '07.10', 'value': 30},
    {'id': 13, 'user_id': 4, 'event_id': 5, 'date': '07.10', 'value': 50},
    {'id': 14, 'user_id': 4, 'event_id': 7, 'date': '09.10', 'value': 64},
    {'id': 15, 'user_id': 4, 'event_id': 8, 'date': '09.10', 'value': 45},
];


users_raw = [
    {'id': 4, name: 'Boiko Tcar', 'group': 2, 'total': 777},
    {'id': 3, name: 'Inav Petrovich', 'group': 0, 'total': 666},
    {'id': 1, name: 'Max Pedroviv', 'group': 1, 'total': 999},
];




function getTableColumns(days, events) {
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
            filter: "input"
        });
    }


    for (let date in days) {
        columnsTop.push({
            title: date,
            colspan: days[date].size + 1,
            align: 'center'
        });

        for (let i of days[date]) {
            columnsBottom.push({
                field: 'date' + date + 'id' + i,
                title: i,
                titleTooltip: 'Title: ' + events[i].title,
                sortable: true,
                align: 'center',
                valign: 'middle',
                formatter: creditsFormatter,
                // formatter: function (val) {
                //     return '<div class="item">' + val + '</div>'
                // },
                events: {
                    'click .item': function (event) {
                        console.log('click ' + event.currentTarget)
                    }
                }
            });
        }
        columnsBottom.push({
            field: 'date' + date + 'total',
            title: 'Total',
            sortable: true,
            align: 'center',
            valign: 'middle',
            formatter: function (val) {
                return '<div class="total">' + val + '</div>'
            }
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

function getTableData(credits, users, days) {
    let data = [];

    for (let user_id in credits) {

        row = {};

        row['id'] = user_id;
        row['name'] = users[user_id].name;
        row['group'] = users[user_id].group;
        row['total'] = users[user_id].total;

        // To avoid undef
        for (let date in days) {
            for (let k of days[date]) {
                row['date' + date + 'id' + k] = 0;
            }
            row['date' + date + 'total'] = 0;
        }

        for (let date in credits[user_id]) {
            let sum = 0;
            for (let k in credits[user_id][date]) {
                row['date' + date + 'id' + credits[user_id][date][k].event_id] = credits[user_id][date][k].value;
                sum += credits[user_id][date][k].value;
            }

            row['date' + date + 'total'] = sum;
        }

        data.push(row);
    }

    return data;
}



function buildTable($el, credits, users, days, events) {
    let [columnsTop, columnsBottom] = getTableColumns(days, events);
    let data = getTableData(credits, users, days);

    // console.log('data', data);

    $el.bootstrapTable('destroy').bootstrapTable({
        // responseHandler(res) {
        //   res.rows.forEach(row => {
        //     row.id = {
        //       'tableexport-msonumberformat': '\\@'
        //     }
        //   });
        //   return res
        // },
        undefinedText: '0',
        columns: [columnsTop, columnsBottom],
        data: data,
        search: true,
        fixedColumns: true,
        fixedNumber: 4,
    });
}


var readyStatus = 0; // +1 For each loaded table (users, events, credits)

function checkCreateTable(events_raw, users_raw, credits_raw) {
    if (readyStatus < 3) {
        return;
    }


    let events = processEvents(events_raw);
    let users = processUsers(users_raw);
    let credits = processCredits(credits_raw);


    buildTable($table, credits, users, getDays(credits), events);

    let userColumns = ['id', 'name', 'group', 'total'];


    $table.on('all.bs.table', function (e, name, args) {
        if (name !== "click-cell.bs.table") {
            return;
        }

        if (userColumns.includes(args[0])) {
            return;
        }

        console.log(name, args);
        let id = args[2].id;
        let value = args[1];
        let date = args[0].slice(4, 9);
        let event_id = args[0].slice(11);
        console.log(id, date, event_id, event_id === 'tal');

        if (event_id === 'tal') {
            // Total
            return;
            addCredit(id, date, 0);
        } else {
            // edit some
            if (value === 0 || value === '0') {
                editCredit('', id, event_id, date, value);
            } else {
                let filtered = credits[id][date].filter(function(credit) {return credit.event_id == event_id});
                // console.log('credits', credits);
                // console.log('id/date', id, date, event_id);
                // console.log('filtered', filtered);
                let credit_id = '';
                if (filtered.length !== 0) {
                    credit_id = filtered[0].id;
                }

                editCredit(credit_id, id, event_id, date, value);
            }
        }
    })
}






function loadEvents() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                events_raw = JSON.parse(this.responseText);
                readyStatus++;
                checkCreateTable(events_raw, users_raw, credits_raw);
            }
            else if (this.status === 401) {  // No account data
                alert('Требуется авторизация!');
            } else {
                alert('Требуется авторизация!');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_get_table?" + "table=" + 'events', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}

function loadUsers() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                users_raw = JSON.parse(this.responseText);
                readyStatus++;
                checkCreateTable(events_raw, users_raw, credits_raw);
            }
            else if (this.status === 401) {  // No account data
                alert('Требуется авторизация!');
            } else {
                alert('Требуется авторизация!');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_get_table?" + "table=" + 'users', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}

function loadCredits() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                credits_raw = JSON.parse(this.responseText);
                readyStatus++;
                checkCreateTable(events_raw, users_raw, credits_raw);
            }
            else if (this.status === 401) {  // No account data
                alert('Требуется авторизация!');
            } else {
                alert('Требуется авторизация!');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_get_table?" + "table=" + 'credits', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


function loadAndCreateTable() {
    readyStatus = 0;

    // Loading of tables (users, events, credits)
    loadEvents();
    loadCredits();
    loadUsers();
}


$(function() {
    loadAndCreateTable();
});



function addCredit(user_id, date, value) {
    editCredit('', user_id,'', date,value)
}

function editCredit(id, user_id, event_id, date, value) {
    document.getElementById('id').value = id;
    document.getElementById('user_id').value = user_id;
    document.getElementById('event_id').value = event_id;
    document.getElementById('date').value = date;
    document.getElementById('value').value = value;

    $popup.style.display = 'block';
}



function saveCredit() {
    let id = document.getElementById('id').value;
    let user_id = document.getElementById('user_id').value;
    let event_id = document.getElementById('event_id').value;
    let date = document.getElementById('date').value;
    let value = document.getElementById('value').value;

    alert('Saving credit: ' + id + ' ' + user_id + ' ' + event_id + ' ' + date + ' ' + value);

    if (date === '' || event_id === '' || value === '') {
        alert('Cannot save with empty EVENT_ID or DATE or VALUE');
        return;
    }

    $popup.style.display = 'none';

    let data = JSON.stringify({
                                "id": id,
                                "user_id": user_id,
                                "event_id": event_id,
                                "date": date,
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





/**
 * Control progress circle
 * Send http POST request to get session id
 */
var progress = document.querySelector('.c100');
var procentage = progress.querySelector('span');
function setProgress(percent) {
    console.log(percent);

    percent = Math.min(100, percent);
    percent = Math.round(percent);

    console.log(percent);

    progress.className = "";
    progress.classList.add('c100');
    progress.classList.add("p" + percent);

    procentage.innerText = percent + "%";
}


setProgress(64.7);



startDay = 5;
numOfDays = 14;

topbar_html = "";

var days = [];
for (var i = 0; i < numOfDays; ++i) {
    days.push( (startDay + i) + "." + "06" );
}

// TODO: Graph

data = [30, 41, 35, 51, 49, 62, 69, 91, 26, 84, 90, 20, 20, 25];

// https://apexcharts.com/docs/installation/
var options = {
    chart: {
        height: 300,
        width: numOfDays * 40,
        type: 'line',
        zoom: {
            enabled: false
        },
        toolbar: {
            show: false
        }
    },
    dataLabels: {
        enabled: false
    },

    stroke: {
        curve: 'straight'
    },
    series: [{
        name: "Credits",
        data: data
    }],
    animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
        animateGradually: {
            enabled: true,
            delay: 150
        },
        dynamicAnimation: {
            enabled: true,
            speed: 350
        }
    },
    background: '#fff',
    grid: {
        // borderColor: '#111',
        row: {
            // colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
            opacity: 0.5
        },
    },
    // labels: series.monthDataSeries1.dates,
    xaxis: {
        categories: days,
    },
    yaxis: {
        ticks: {
            fixedStepSize: 10
        }
    },
};

window.addEventListener('load', function () {
    var chart = new ApexCharts(
        document.querySelector("#credits__chart"),
        options
    );


    chart.render();
});



// Chart



// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages':['corechart']});

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
function drawChart() {

    // Create the data table.
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Topping');
    data.addColumn('number', 'Slices');
    data.addRows([
        ['Mushrooms', 3],
        ['Onions', 1],
        ['Olives', 1],
        ['Zucchini', 1],
        ['Pepperoni', 2]
    ]);

    // Set chart options
    var options = {'title':'How Much Pizza I Ate Last Night',
        'width':400,
        'height':300};

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}