/**
 * @fileoverview Admin page logic
 * File providing all functions which are used to control admin.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */

$('.openmodal').click(function (e) {
  e.preventDefault();
  $('.kadobagud').addClass('midsalod');
  });
$('.closemodal').click(function (e) {
  e.preventDefault();
  $('.kadobagud').removeClass('midsalod');
  });




 var $table = $('#table');

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

$(function () {
    $table.bootstrapTable({
        data: data,
        columns: [{
        title: 'ID',
        field: 'id',
        sortable: 'true'
      }, {
        title: 'Item Name',
        field: 'name',
        sortable: 'true'
      }, {
        title: 'Item Price',
        field: 'price'
      }, {
        title: 'Actions',
        field: 'operate',
        formatter: 'operateFormatter',
        events: 'operateEvents',
        width: '200'
      }]
    });
});

  function operateFormatter(value, row, index) {
    return [
      '<button class="pencil" href="javascript:void(0)" title="Edit">',
      '<i class="fa fa-wrench"></i> ',
        'Edit',
      '</button>',
      '<button class="remove danger_button" href="javascript:void(0)" title="Remove">',
      '<i class="fa fa-trash"></i> ',
        'Remove',
      '</button>'
    ].join('')
  }

  window.operateEvents = {
    'click .pencil': function (e, value, row, index) {
        // $table.SetEditable({ $addButton: $('#addNewRow')});

      alert('You click like action, row: ' + JSON.stringify(row));
      tmp_row = {
        "id": 123123,
        "name": "test1000",
        "price": "111$0"
        };

      $table.bootstrapTable('updateRow', {index: index, row: tmp_row});
      $('#popup').fadeIn(350);
      $('#popup').fadeOut(350);
    },
    'click .remove': function (e, value, row, index) {
      alert('You click like action, row: ' + JSON.stringify(row));
      $table.bootstrapTable('remove', {
        field: 'id',
        values: [row.id]
      })
    }
  };


    var $button = document.getElementsByName("refresh");
    // $button = $button.item(0);
        console.log($button);

  $(document).ready(function() {
        console.log('Ready');
        $button = $button.item(0);
        console.log($button);

    $button.onclick = (function () {
        console.log('refresh');

        data = [    {
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

    })
  });

$table.SetEditable({ $addButton: $('#addNewRow')});

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

