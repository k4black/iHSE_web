/**
 * @fileoverview Credits page logic
 * File providing all functions which are used to control credits.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


/** ===============  TABLE REQUESTS  =============== */




var $table = $('#table');




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


users = processUsers(users_raw);
credits = processCredits(credits_raw);
days = getDays(credits);



function daysToTableColumns(days) {
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
                sortable: true,
                align: 'center',
                valign: 'middle',
                formatter: function (val) {
                    return '<div class="item">' + val + '</div>'
                },
                events: {
                    'click .item': function () {
                        console.log('click')
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

function creditsToTableData(credits, days) {
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




function testBuild($el, cells, subcells, rows) {
    var row;
    var columns = [];
    var data = [];

    let userColumns = ['id', 'name', 'group', 'total'];
    let fixedColumns = userColumns.length;

    let specialColumns = ['olymp', 'sport'];


    for (let i of userColumns) {
        columns.push({
            field: i,
            title: i,
            sortable: true,
            rowspan: 2,
            valign: 'middle'
        });
    }


    for (let i = 0; i < cells; ++i) {
        columns.push({
            title: 'More Cells ' + i ,
            colspan: subcells,
            align: 'center'
        });
    }

    for (let i of specialColumns) {
        columns.push({
            field: i,
            title: i,
            sortable: true,
            rowspan: 2,
            valign: 'middle'
        });
    }


    columnsBot = [];

    for (let i = 0; i < cells; ++i) {
        for (let k = 0; k < subcells - 1; ++k) {
            columnsBot.push({
                field: 'field' + (i*subcells + k),
                title: 'Cells' + (i*subcells + k),
                sortable: true,
                align: 'center',
                valign: 'middle',
                formatter: function (val) {
                    return '<div class="item">' + val + '</div>'
                },
                events: {
                    'click .item': function () {
                        console.log('click')
                    }
                }
            });
        }
        columnsBot.push({
            field: 'field' + (i*subcells + subcells - 1),
            title: 'Total' + (i*subcells + subcells - 1),
            sortable: true,
            align: 'center',
            valign: 'middle',
            formatter: function (val) {
                return '<div class="total">' + val + '</div>'
            }
        });
    }




    for (let i = 0; i < rows; i++) {
        row = {};
        for (let j of userColumns) {
            row[j] = j + i;
        }

        for (let j = 0; j < cells; j++) {
            for (let k = 0; k < subcells; ++k) {
                row['field' + (j*subcells + k)] = 'Row' + i + ' ' + j + ':' + k;
            }
        }

        for (let j of specialColumns) {
            row[j] = j + i;
        }

        data.push(row);
    }



    console.log(columns);
    console.log(columnsBot);
    console.log(data);


    $el.bootstrapTable('destroy').bootstrapTable({
        columns: [columns, columnsBot],
        data: data,
        search: true,
        fixedColumns: true,
        fixedNumber: fixedColumns
    })
}





function buildTable($el, credits, days) {
    let [columnsTop, columnsBottom] = daysToTableColumns(days);
    let data = creditsToTableData(credits, days);

    console.log('data', data);

    $el.bootstrapTable('destroy').bootstrapTable({
        undefinedText: '0',
        columns: [columnsTop, columnsBottom],
        data: data,
        search: true,
        fixedColumns: true,
        fixedNumber: 4,
    });
}


$(function() {
    buildTable($table, credits, getDays(credits));
    // testBuild($table, 3, 5, 3);
});



function operateFormatter(value, row, index) {
return [
    '<button class="edit" href="javascript:void(0)" title="Edit">',
        // '<i class="fa fa-wrench"></i> ',
        '<i class="material-icons" style="font-size:15px">build</i>',
        'Edit',
    '</button>',
    '<button class="remove danger_button" href="javascript:void(0)" title="Remove">',
        // '<i class="fa fa-trash"></i> ',
        '<i class="material-icons" style="font-size:18px">delete</i>',
        '<p>Remove</p>',
    '</button>'
].join('')
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