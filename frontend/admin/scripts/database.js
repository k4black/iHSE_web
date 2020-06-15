/**
 * @fileoverview Admin page logic
 * File providing all functions which are used to control admin.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



var $table = $('#table');
var $popup = $('#popup');
var $popup_inputs = $('#popup .fields');
console.log($popup_inputs);



var current_table = 'users';




let users;
let events;
let projects;
let days;



let data = [
    {'id': 'NONE', 'title': 'NONE', 'type': 'NONE', 'def_type': 'NONE', 'direction': 'NONE', 'description': 'NONE'}
];

let fields = {
    'users': ['id', 'code', 'user_type', 'phone', 'name', 'sex', 'pass', 'team', 'project_id', 'avatar'],
    'sessions': ['id', 'user_id', 'user_type', 'user_agent', 'last_ip', 'time'],
    'credits': ['id', 'user_id', 'event_id', 'validator_id', 'time', 'value'],
    'codes': ['code', 'type', 'used'],
    'feedback': ['id', 'user_id', 'event_id', 'score', 'entertain', 'useful', 'understand', 'comment'],
    'top': ['id', 'user_id', 'day_id', 'chosen_1', 'chosen_2', 'chosen_3'],
    'projects': ['id', 'title', 'type', 'def_type', 'direction', 'description', 'annotation'],
    'events': ['id', 'type', 'title', 'description', 'host', 'place', 'time', 'day_id'],
    'classes': ['id', 'total', 'annotation'],
    'enrolls': ['id', 'class_id', 'user_id', 'time', 'attendance', 'bonus'],
    'days': ['id', 'date', 'title', 'feedback'],
    'notifications': ['id', 'user_id', 'token'],
    'vacations': ['id', 'user_id', 'date_from', 'date_to', 'time_from', 'time_to', 'accepted'],
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
        editRow(row);
        $popup.fadeIn(350);
    },
    'click .remove': function (e, value, row, index) {
        // alert('You click like action, row: ' + JSON.stringify(row));

        if (confirm("Are you sure? You wand to remove: \n" + JSON.stringify(row))) {
            // $table.bootstrapTable('remove', {
            //     field: 'id',
            //     values: [row.id]
            //     });
            removeRow(current_table, row.id);
        } else {
            // pass
        }
    }
};



function getTableColumns(tableName, fields) {
    let columns = [];

    for (let field of fields[tableName]) {
        if (field === 'user_id' || field === 'validator_id' || field === 'event_id' || field === 'class_id' || field === 'project_id' || field === 'day_id' || (tableName === 'classes' && field === 'id')) {
            columns.push({
                title: field,
                field: field,
                sortable: 'true',
                formatter: function (val) {
                    try {
                        if (field === 'user_id' || field === 'validator_id') {
                            return '<div class="replaced_cell" user_id=' + val + ' title="'+ field +': ' + val + '">' + users[val].name + '</div>'
                        }
                        if (field === 'event_id' || field === 'class_id') {
                            if (field === 'event_id') {
                                return '<div class="replaced_cell" event_id=' + val + ' title="event_id: ' + val + '">' + events[val].title + '</div>'
                            } else if (field === 'class_id') {
                                return '<div class="replaced_cell" class_id=' + val + ' title="class_id: ' + val + '">' + events[val].title + '</div>'
                            }
                        }
                        if (field === 'project_id') {
                            return '<div class="replaced_cell" project_id=' + val + ' title="project_id: ' + val + '">' + projects[val].title + '</div>'
                        }
                        if (field === 'day_id') {
                            return '<div class="replaced_cell" day_id=' + val + ' title="day_id: ' + val + '">' + days[val].date + '</div>'
                        }
                        if (tableName === 'classes' && field === 'id') {
                            return '<div class="replaced_cell" event_id=' + val + ' title="event_id: ' + val + '">' + events[val].title + '</div>'
                        }
                    } catch (err) {
                        console.log('Error', err)
                    }
                },
            });
        } else if (field === 'user_type' || (tableName === 'events' && field === 'type') || (tableName === 'enrolls' && field === 'attendance') || (tableName === 'days' && field === 'feedback') || (tableName === 'codes' && field === 'used') || (tableName === 'vacations' && field === 'accepted')) {
            columns.push({
                title: field,
                field: field,
                sortable: 'true',
                formatter: function (val) {
                    try {
                        // USER TYPE
                        if (field === 'user_type') {
                            if (val === 0 || val === '0') {
                                // Regualr user
                                return '<div class="user_type regular_user" user_type=' + val + ' title="user_type: ' + val + '">regular</div>'
                            } else if (val === 1 || val === '1') {
                                // Moderator
                                return '<div class="user_type moderator_user" user_type=' + val + ' title="user_type: ' + val + '">moderator</div>'
                            } else if (val === 2 || val === '2') {
                                // Admin
                                return '<div class="user_type admin_user" user_type=' + val + ' title="user_type: ' + val + '">admin</div>'
                            }
                        }

                        // EVENT TYPE
                        if (tableName === 'events' && field === 'type') {
                            if (val === 0 || val === '0') {
                                // Regualr event
                                return '<div class="event_type regular_event" event_type=' + val + ' title="event_type: ' + val + '">regular</div>'
                            } else if (val === 1 || val === '1' || val === 2 || val === '2') {
                                // Class
                                return '<div class="event_type class_event" event_type=' + val + ' title="event_type: ' + val + '">' + (val == 1 ? 'master' : 'lecture') + '</div>'
                            } else if (val === 3 || val === '3') {
                                // Regualr event
                                return '<div class="event_type fun_event" event_type=' + val + ' title="event_type: ' + val + '">fun</div>'
                            }
                        }

                        // TRUE/FALSE
                        if ((tableName === 'enrolls' && field === 'attendance') || (tableName === 'days' && field === 'feedback') || (tableName === 'codes' && field === 'used') || (tableName === 'vacations' && field === 'accepted')) {
                            if (val === true || val === 'true') {
                                // True value
                                return '<div class="bool_type true_bool" bool_type=' + val + ' title="bool_type: ' + val + '">true</div>'
                            } else if (val === false || val === 'false') {
                                // Falce value
                                return '<div class="bool_type false_bool" bool_type=' + val + ' title="bool_type: ' + val + '">false</div>'
                            }
                        }
                    } catch (err) {
                        console.log('Error', err)
                    }
                },
            });
        } else {
            columns.push({
                title: field,
                field: field,
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







// buildTable($table, current_table, fields, data);




/**
 * setup.sh table by current_table from global 'cache'
 */
function setTable() {
    console.log('setting Table: ', current_table);


    events = cache['events'];
    users = cache['users'];
    projects = cache['projects'];
    days = cache['days'];


    data = [];
    for (let id in cache[current_table]) {
        data.push(cache[current_table][id]);
    }

    buildTable($table, current_table, fields, data);
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
                let obj_raw;
                try {
                    obj_raw = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error', e);
                    obj_raw = [];
                }
                objs = groupByUnique(obj_raw, 'id');
                cache[tableName] = objs;

                func();
            } else if (this.status === 401) {
                alert('You have to be admin to use that page!\nThe incident will be reported.');
                window.location.href = document.location.origin;
            }
        }
    };

    xhttp.open("GET", "/admin_get_table?" + "table=" + tableName, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}







function loadAndCreateTable(table_name) {
    current_table = table_name;


    if (!(table_name in ['users', 'events', 'projects', 'days'])) {
        loadTable(table_name, function () {
            console.log('checkLoading', cache);
            checkLoading(setTable, ['users', 'events', 'projects', 'days', table_name]);
        });
    } else {
        loadTable(table_name, function () {
            console.log('checkLoading', cache);
            checkLoading(setTable, ['users', 'events', 'projects', 'days']);
        });
    }
}


$(function() {
    current_table = 'users';

    loadTable('users', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'projects', 'days']);});
    loadTable('events', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'projects', 'days']);});
    loadTable('projects', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'projects', 'days']);});
    loadTable('days', function () {console.log('checkLoading', cache); checkLoading(setTable, ['users', 'events', 'projects', 'days']);});

    // loadAndCreateTable(current_table);

    setupToolbar();
    setupTabs();
});








/**
 * Delete row by id
 * Send http POST request to delete row
 */
function removeRow(table_name, row_id) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                loadAndCreateTable(current_table);  // TODO: Check update
            }
        }
    };

    xhttp.open("POST", "/admin_remove_data?" + "table="+table_name + "&id=" + row_id, true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}



/**
 * Clear table on server
 * Send http POST request to clear table data (or send error if cookie does not exist)
 */
function clearTable(table_name) {
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

                loadAndCreateTable(current_table);  // TODO: Check update
            }

            else if (this.status === 401) {  // No account data
                alert('Требуется авторизация!');
            }
        }
    };

    xhttp.open("POST", "/admin_clearTable?" + "table=" + table_name, true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}



/**
 * Add or update row
 * Send http POST request to create/update row
 */
function saveRow() {
    let row = {};

    console.log($popup_inputs);

    for (let field of fields[current_table]) {
        console.log(field, $popup_inputs.querySelector('input[name=' + field + ']'));
        if (current_table === 'events' && field === 'time') {
            row[field] = $popup_inputs.querySelector('input[name=' + field + ']').value.replace('-', '\n');
        } else {
            row[field] = $popup_inputs.querySelector('input[name=' + field + ']').value;
            // row[field] = time.replace(' ', '\n').replace('-', '\n');
        }
    }

    // $table.bootstrapTable('updateRow', {index: index, row: row});
    
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                loadAndCreateTable(current_table);  // TODO: Check update
            }
        }
    };
    
    console.log('Edited row', row);
    let  data = JSON.stringify(row);

    xhttp.open("POST", "/admin_send_data?" + "table="+current_table, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}

function createRow() {
    let row = {};

    for (let field of fields[current_table]) {
        row[field] = '';
    }

    editRow(row);
}


function editRow(row) {
    console.log(row);

    $popup_inputs.innerHTML = '';
    let inputs_html = '';
    for (let field of fields[current_table]) {
        if (current_table === 'events' && field === 'time') {
            row[field] = row[field].replace('\n', '-');
        }
        console.log(field, row[field]);


        let current_inputs_html = '<label for=' + field + '>' + field + '</label>';

        let disabled = (field === 'id' ? 'disabled' : '');
        let list = (field === 'user_id' || field === 'validator_id' || field === 'event_id' || field === 'class_id' || field === 'project_id' || field === 'day_id' ? 'list=' + field + '_list' : '');
        let placeholder = (field.slice(0, 4) === 'date' ? 'placeholder="dd.mm"' : '');
        placeholder = (field.slice(0, 4) === 'time' ? 'placeholder="hh.mm"' : '');
        placeholder = (current_table === 'events' && field === 'time' ? 'placeholder="hh.mm-hh.mm"' : '');
        if (Object.keys(row).length === 0) {
            current_inputs_html += '<input name="' + field + '" value="" type="text" ' + disabled + ' ' + list + ' ' + placeholder + '>';
        } else {
            current_inputs_html += '<input name="' + field + '" value="' + row[field] + '" type="text" ' + disabled + ' ' + list + ' ' + placeholder + '>';
        }

        if (field === 'user_id' || field === 'validator_id' || field === 'event_id' || field === 'class_id' || field === 'project_id' || field === 'day_id') {
            current_inputs_html += '<datalist id="' + field + '_list" name="' + field + '_list">';

            if (field === 'user_id') {
                for (let id in users) {
                    current_inputs_html += '<option value="' + id + '">' + users[id].name + '</option>';
                }
            } else if (field === 'validator_id') {
                for (let id in users) {
                    if (users[id].user_type !== 0 && users[id].user_type !== '0') {
                        current_inputs_html += '<option value="' + id + '">' + users[id].name + '</option>';
                    }
                }
            } else if (field === 'event_id' || field === 'class_id' ) {
                for (let id in events) {
                    current_inputs_html += '<option value="' + id + '">' + events[id].title + '</option>';
                }
            } else if (field === 'project_id') {
                for (let id in projects) {
                    current_inputs_html += '<option value="' + id + '">' + projects[id].title + '</option>';
                }
            } else if (field === 'day_id') {
                for (let id in days) {
                    current_inputs_html += '<option value="' + id + '">' + days[id].date + '</option>';
                }
            }

            current_inputs_html += '</datalist>';
        }

        inputs_html += '<div style="display:block">' + current_inputs_html + '</div>';
    }

    $popup_inputs.innerHTML = inputs_html;
}





function setupTabs() {
    console.log('setup.sh-ing tabs');



    for (let tab_name in fields) {
        $('#tab_' + tab_name)[0].onclick = function () {
            current_table = tab_name;
            loadAndCreateTable(current_table);
            $('.tabs button').removeClass('active_tab');
            $('#tab_' + tab_name).addClass('active_tab');
        };
    }
}

function setupToolbar() {
    $popup_inputs = $popup_inputs[0];
    console.log($popup_inputs);

    $('[name="refresh"]').click(function () {
        console.log('refresh');
        loadAndCreateTable(current_table);
    });

    $('#clearTable').click(function () {
        console.log('clear table');
        if (confirm("Are you sure? You wand to clear: \n" + current_table)) {
            clearTable(current_table);
        } else {
            // pass
        }
    });

    $('#addNewRow').click(function () {
        console.log('Adding new row');

        createRow();
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

    xhttp.open("GET", "/admin_save", true);
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

    xhttp.open("GET", "/admin_update", true);
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

    xhttp.open("GET", "/admin_load", true);
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

    xhttp.open("GET", "/admin_codes", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
});

