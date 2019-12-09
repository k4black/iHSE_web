/**
 * @fileoverview Admin page logic
 * File providing all functions which are used to control admin.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



var $table = $('#table');
var $popup = $('#popup');
var $popup_inputs = $('#popup .fields');
console.log($popup_inputs);
var $button = document.getElementsByName("refresh");




var data = [
    {
        "id": 0,
        "name": "test0",
        "price": "$0"
    },
    {
        "id": 1,
        "name": "test1",
        "price": "$1"
    },
    {
        "id": 2,
        "name": "test2",
        "price": "$2"
    },
    {
        "id": 3,
        "name": "test3",
        "price": "$3"
    },
    {
        "id": 4,
        "name": "test4",
        "price": "$4"
    },
    {
        "id": 5,
        "name": "test5",
        "price": "$5"
    },
    {
        "id": 6,
        "name": "test6",
        "price": "$6"
    },
    {
        "id": 7,
        "name": "test7",
        "price": "$7"
    },
    {
        "id": 8,
        "name": "test8",
        "price": "$8"
    },
    {
        "id": 9,
        "name": "test9",
        "price": "$9"
    },
    {
        "id": 10,
        "name": "test10",
        "price": "$10"
    },
    {
        "id": 11,
        "name": "test11",
        "price": "$11"
    },
    {
        "id": 12,
        "name": "test12",
        "price": "$12"
    },
    {
        "id": 13,
        "name": "test13",
        "price": "$13"
    },
    {
        "id": 14,
        "name": "test14",
        "price": "$14"
    },
    {
        "id": 15,
        "name": "test15",
        "price": "$15"
    },
    {
        "id": 16,
        "name": "test16",
        "price": "$16"
    },
    {
        "id": 17,
        "name": "test17",
        "price": "$17"
    },
    {
        "id": 18,
        "name": "test18",
        "price": "$18"
    },
    {
        "id": 19,
        "name": "test19",
        "price": "$19"
    },
    {
        "id": 20,
        "name": "test20",
        "price": "$20"
    }
];
var fields = ['id', 'name', 'price'];

var columns = [];  // TODO: columns name map
for (let i = 0; i < fields.length; ++i) {
    columns.push({
        title: fields[i],
        field: fields[i],
        sortable: 'true'
    });
}

columns.push({
    title: 'Actions',
    field: 'operate',
    formatter: 'operateFormatter',
    events: 'operateEvents',
    width: '200'
});

// var columns = [{
//         title: 'ID',
//         field: 'id',
//         sortable: 'true'
//         }, {
//         title: 'Item Name',
//         field: 'name',
//         sortable: 'true'
//       }, {
//         title: 'Item Price',
//         field: 'price'
//       }, {
//         title: 'Actions',
//         field: 'operate',
//         formatter: 'operateFormatter',
//         events: 'operateEvents',
//         width: '200'
//       }
// ];




function operateFormatter(value, row, index) {
    return [
        '<button class="edit" href="javascript:void(0)" title="Edit">',
        '<i class="fa fa-wrench"></i> ',
        'Edit',
        '</button>',
        '<button class="remove danger_button" href="javascript:void(0)" title="Remove">',
        '<i class="fa fa-trash"></i> ',
        'Remove',
        '</button>'
    ].join('')
}

function update_row(index, id) {
    tmp_row = {
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
}

function create_row() {
    tmp_row = {
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
            current_inputs_html += '<input name=' + columns[i]['title'] + ' value="" type="text">';
        } else {
            current_inputs_html += '<input name=' + columns[i]['title'] + ' value="' + row[columns[i]['field']] + '" type="text">';
        }
        inputs_html += '<div style="display: block">' + current_inputs_html + '</div>';
    }

    $popup_inputs.innerHTML = inputs_html;
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
                })
        } else {
            // pass
        }
    }
};

$(function () {

    // Creating table  - adding data and columns
    $table.bootstrapTable({
        data: data,
        columns: columns
    });

    $popup_inputs = $popup_inputs[0];
    console.log($popup_inputs);

    $button = $button.item(0);

    $button.onclick = (function () {
        console.log('refresh');

        data = [
        {
            "id": 19,
            "name": "test19",
            "price": "$19"
        },
        {
            "id": 20,
            "name": "test20",
            "price": "$20"
        }];

        $table.bootstrapTable('load',  data);
        // $table.bootstrapTable('refresh')

    });

    $('#addNewRow')[0].onclick = (function () {
        console.log('Adding new row');

        $popup.attr('row_edit', false);
        edit_row({});
        $popup.fadeIn(350);
    });

  });


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

