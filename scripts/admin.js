/**
 * @fileoverview Admin page logic
 * File providing all functions which are used to control admin.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



var $table = $('#table');
var $popup = $('#popup');
var $popup_inputs = $('#popup .fields');
console.log($popup_inputs);



current_table = 'users';



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


users_raw = [
    {'id': 4, 'name': 'Boiko Tcar', 'team': 2, 'credits': 777},
    {'id': 3, 'name': 'Inav Petrovich', 'team': 0, 'credits': 666},
    {'id': 1, 'name': 'Max Pedroviv', 'team': 1, 'credits': 999},
];



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




let users;
let events;



let data = [
    {'id': 'NONE', 'title': 'NONE', 'type': 'NONE', 'def_type': 'NONE', 'direction': 'NONE', 'description': 'NONE'}
];
let fields = {
    'projects': ['id', 'title', 'type', 'def_type', 'direction', 'description'],
    'users': ['id', 'user_type', 'phone', 'name', 'pass', 'team', 'credits', 'avatar', 'project_id'],
    'sessions': ['id', 'user_id', 'user_type', 'user_agent', 'last_ip', 'time'],
    'events': ['id', 'type', 'title', 'description', 'host', 'place', 'time', 'date'],
    'classes': ['id', 'credits', 'count', 'total'],
    'credits': ['id', 'user_id', 'event_id', 'date', 'value'],
    'codes': ['code', 'type', 'used']
};





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



// Add buttons Edin and Remove
window.operateEvents = {
    'click .edit': function (e, value, row, index) {
        // alert('You click like action, row: ' + JSON.stringify(row));

        $popup.attr('row_index', index);
        $popup.attr('row_id', row["id"]);
        $popup.attr('row_edit', true);

        edit_row(row);

        console.log($popup.attr('row_index'));
        console.log($popup.attr('row_id'));

        $popup.fadeIn(350);
    },
    'click .remove': function (e, value, row, index) {
        // alert('You click like action, row: ' + JSON.stringify(row));

        if (confirm("Are you sure? You wand to remove: \n" + JSON.stringify(row))) {
            $table.bootstrapTable('remove', {
                field: 'id',
                values: [row.id]
                });
            remove_row(current_table, row.id);
        } else {
            // pass
        }
    }
};



function getTableColumns(tableName, fields) {
    let columns = [];

    for (let i = 0; i < fields[tableName].length; ++i) {
        if (fields[tableName][i] === 'user_id' || fields[tableName][i] === 'event_id' || (tableName === 'classes' && fields[tableName][i] === 'id')) {
            columns.push({
                title: fields[tableName][i],
                field: fields[tableName][i],
                sortable: 'true',
                formatter: function (val) {
                    try {
                        if (fields[tableName][i] === 'user_id') {
                            return '<div class="replaced_cell" user_id=' + val + ' title="user_id: ' + val + '">' + users[val].name + '</div>'
                        }
                        if (fields[tableName][i] === 'event_id') {
                            return '<div class="replaced_cell" event_id=' + val + ' title="event_id: ' + val + '">' + events[val].title + '</div>'
                        }
                        if (tableName === 'classes' && fields[tableName][i] === 'id') {
                            return '<div class="replaced_cell" event_id=' + val + ' title="event_id: ' + val + '">' + events[val].title + '</div>'
                        }
                    } catch (err) {
                        console.log('Error', err)
                    }
                },
            });
        } else {
            columns.push({
                title: fields[tableName][i],
                field: fields[tableName][i],
                sortable: 'true'
            });
        }
    }

    columns.push({
        title: 'Actions',
        field: 'operate',
        formatter: operateFormatter,
        events: 'operateEvents',
        width: '200'
    });

    return columns;
}



function buildTable($el, tableName, fields, data) {
    console.log('building - ' + tableName + ' from ', fields, data);
    // let columns = getTableColumns(tableName, fields);
    // let tableData = getTableData(tableName, data);

    $el.bootstrapTable('destroy').bootstrapTable({
        undefinedText: '-',
        columns: getTableColumns(tableName, fields),
        data: data,
        search: true
    });
}





let readyStatus = 0;  // loaded current table + users + events

function checkCreateTable(events_raw, users_raw) {
    if (readyStatus < 2) {
        return;
    }

    events = processEvents(events_raw);
    users = processUsers(users_raw);

    buildTable($table, current_table, fields, data);
}





// buildTable($table, current_table, fields, data);




/**
 * Get table information from server
 * Send http GET request and get table data (or send error if cookie does not exist)
 */
function loadTable(table_name) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                data = JSON.parse(this.responseText);
                readyStatus++;
                checkCreateTable(events_raw, users_raw);
            }
            else if (this.status === 401) {  // No account data
                alert('Требуется авторизация!');
            } else {
                alert('Требуется авторизация!');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_get_table?" + "table=" + table_name, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}

function loadEvents() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                events_raw = JSON.parse(this.responseText);
                readyStatus++;
                checkCreateTable(events_raw, users_raw);
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
                checkCreateTable(events_raw, users_raw);
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






function loadAndCreateTable(table_name) {
    readyStatus = 0;

    // Loading of tables (users, events, and Main one)
    loadEvents();
    loadUsers();
    loadTable(table_name);  // TODO: Optimize
}


$(function() {
    current_table = 'users';
    loadAndCreateTable(current_table);

    setupToolbar();
    setupTabs();
});







/**
 * Add or update row
 * Send http POST request to create/update row
 */
function post_row(table_name, row) {
    var xhttp = new XMLHttpRequest();

    // xhttp.onreadystatechange = function() {
    //     if (this.readyState === 4) {
    //         if (this.status === 200) {
    //             // TODO ?
    //         }
    //     }
    // };
    console.log('Edited row', row);
    data = JSON.stringify(row);
    xhttp.open("POST", "http://ihse.tk:50000/admin_send_data?" + "table="+table_name, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}


/**
 * Delete row by id
 * Send http POST request to delete row
 */
function remove_row(table_name, row_id) {
    var xhttp = new XMLHttpRequest();

    // xhttp.onreadystatechange = function() {
    //     if (this.readyState === 4) {
    //         if (this.status === 200) {
    //             // TODO ?
    //         }
    //     }
    // };

    xhttp.open("POST", "http://ihse.tk:50000/admin_remove_data?" + "table="+table_name + "&id=" + row_id, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}



/**
 * Clear table on server
 * Send http POST request to clear table data (or send error if cookie does not exist)
 */
function clear_table(table_name) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                // TODO: Check Show table update
                $table.bootstrapTable('destroy');
                $table.bootstrapTable({
                    data: [],
                    columns: columns
                });
            }

            else if (this.status === 401) {  // No account data
                alert('Требуется авторизация!');
            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/admin_clear_table?" + "table=" + table_name, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}




function update_row(index, id) {
    tmp_row = {  // TODO: remove
        "id": id * id,
        "name": "test1000",
        "price": "111$0"
    };

    console.log($popup_inputs);

    for (let i = 0; i < fields.length; ++i) {
        console.log(fields[i], $popup_inputs.querySelector('input[name=' + fields[i] + ']'));
        tmp_row[fields[i]] = $popup_inputs.querySelector('input[name=' + fields[i] + ']').value;
    }


    $table.bootstrapTable('updateRow', {index: index, row: tmp_row});
    post_row(current_table, tmp_row);
    loadAndCreateTable(current_table);  // TODO: Check update
}

function create_row() {
    tmp_row = {  // TODO: remove
        "id": id * id,
        "name": "test1000",
        "price": "111$0"
    };

    console.log($popup_inputs);

    for (let i = 0; i < fields.length; ++i) {
        console.log(fields[i], $popup_inputs.querySelector('input[name=' + fields[i] + ']'));
        tmp_row[fields[i]] = $popup_inputs.querySelector('input[name=' + fields[i] + ']').value;
    }

    $table.bootstrapTable('append', tmp_row);
    post_row(current_table, tmp_row);
    loadAndCreateTable(current_table);  // TODO: Check update
}


function edit_row(row) {
    console.log(row);

    $popup_inputs.innerHTML = '';
    let inputs_html = '';
    for (let i = 0; i < columns.length; ++i) {
        if (columns[i]['field'] === 'operate') {
            break;
        }

        console.log(columns[i]['title'], columns[i]['field'], row[columns[i]['field']]);

        let current_inputs_html = '<label for=' + columns[i]['title'] + '>' + columns[i]['title'] + '</label>';
        if (Object.keys(row).length === 0) {
            if (columns[i]['title'] === 'id') {
                current_inputs_html += '<input name=' + columns[i]['title'] + ' value="" type="text" disabled>';
            } else {
                current_inputs_html += '<input name=' + columns[i]['title'] + ' value="" type="text">';
            }
        } else {
            if (columns[i]['title'] === 'id') {
                current_inputs_html += '<input name=' + columns[i]['title'] + ' value="' + row[columns[i]['field']] + '" type="text" disabled>';
            } else {
                current_inputs_html += '<input name=' + columns[i]['title'] + ' value="' + row[columns[i]['field']] + '" type="text">';
            }
        }

        inputs_html += '<div style="display: block">' + current_inputs_html + '</div>';
    }

    $popup_inputs.innerHTML = inputs_html;
}





function setupTabs() {
    console.log('setup-ing tabs');

    // TODO: Optimize
    $('#tab_users')[0].onclick = function () {
        current_table = 'users';
        loadAndCreateTable(current_table);
        $('.tabs button').removeClass('active_tab');
        $('#tab_users').addClass('active_tab');
    };
    $('#tab_sessions')[0].onclick = function () {
        current_table = 'sessions';
        $('.tabs button').removeClass('active_tab');
        $('#tab_sessions').addClass('active_tab');
        loadAndCreateTable(current_table);
    };
    $('#tab_credits')[0].onclick = function () {
        current_table = 'credits';
        $('.tabs button').removeClass('active_tab');
        $('#tab_credits').addClass('active_tab');
        loadAndCreateTable(current_table);
    };
    $('#tab_codes')[0].onclick = function () {
        current_table = 'codes';
        $('.tabs button').removeClass('active_tab');
        $('#tab_codes').addClass('active_tab');
        loadAndCreateTable(current_table);
    };
    $('#tab_feedback')[0].onclick = function () {
        current_table = 'feedback';
        loadAndCreateTable(current_table);
        $('.tabs button').removeClass('active_tab');
        $('#tab_feedback').addClass('active_tab');
    };
    $('#tab_projects')[0].onclick = function () {
        current_table = 'projects';
        loadAndCreateTable(current_table);
        $('.tabs button').removeClass('active_tab');
        $('#tab_projects').addClass('active_tab');
    };
    $('#tab_events')[0].onclick = function () {
        current_table = 'events';
        loadAndCreateTable(current_table);
        $('.tabs button').removeClass('active_tab');
        $('#tab_events').addClass('active_tab');
    };
    $('#tab_classes')[0].onclick = function () {
        current_table = 'classes';
        loadAndCreateTable(current_table);
        $('.tabs button').removeClass('active_tab');
        $('#tab_classes').addClass('active_tab');
    };
}

function setupToolbar() {
    $popup_inputs = $popup_inputs[0];
    console.log($popup_inputs);

    $('[name="refresh"]').click(function () {
        console.log('refresh');
        loadAndCreateTable(current_table);
    });

    $('#clear_table').click(function () {
        console.log('clear table');
        if (confirm("Are you sure? You wand to clear: \n" + current_table)) {
            clear_table(current_table);
        } else {
            // pass
        }
    });

    $('#addNewRow')[0].onclick = (function () {
        console.log('Adding new row');

        $popup.attr('row_edit', false);
        edit_row({});
        $popup.fadeIn(350);
    });
}



/** ===============  LOGIC and REQUESTS  =============== */


document.querySelector('.save').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('saved');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_save", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});


document.querySelector('.update').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('updated');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_update", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});


document.querySelector('.load').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('loaded');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_load", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});


document.querySelector('.codes').addEventListener('click', function () {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('created');
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/admin_codes", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});

