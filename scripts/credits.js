/**
 * @fileoverview Credits page logic
 * File providing all functions which are used to control credits.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


/** ===============  TABLE REQUESTS  =============== */



var $table = $('#table');


  function buildTable($el, cells, rows) {
    var i
    var j
    var row
    var columns = []
    var data = [];

    for (i = 0; i < cells; i++) {
      columns.push({
        field: 'field' + i,
        title: 'Cell' + i,
        sortable: true,
        rowspan: 2,
        valign: 'middle',
        formatter: function (val) {
          return '<div class="item">' + val + '</div>'
        },
        events: {
          'click .item': function () {
            console.log('click')
          }
        }
      })
    }

    for (i = 0; i < rows; i++) {
      row = {}
      for (j = 0; j < cells + 3; j++) {
        row['field' + j] = 'Row-' + i + '-' + j
      }
      data.push(row)
    }

    columns.push({
      title: 'More Cells',
      colspan: 3,
      align: 'center'
    });

    columns.push({
      title: 'More Cells 2',
      colspan: 3,
      align: 'center'
    });


    //     columns.push({
    //     title: 'Actions',
    //     field: 'operate',
    //     formatter: 'operateFormatter',
    //     events: 'operateEvents',
    //     width: '200'
    // });


    $el.bootstrapTable('destroy').bootstrapTable({
      columns: [columns, [{
        field: 'field' + cells,
        title: 'Cells' + cells,
        sortable: true,
        align: 'center'
      }, {
        field: 'field' + (cells + 1),
        title: 'Cells' + (cells + 1),
        sortable: true,
        align: 'center'
      }, {
        field: 'field' + (cells + 2),
        title: 'Cells' + (cells + 2),
        align: 'center'
      }, {
        field: 'field' + cells,
        title: 'Cells' + cells,
        sortable: true,
        align: 'center'
      }, {
        field: 'field' + (cells + 1),
        title: 'Cells' + (cells + 1),
        sortable: true,
        align: 'center'
      }, {
        field: 'field' + (cells + 2),
        title: 'Cells' + (cells + 2),
        align: 'center'
      }]],


      data: data,
      search: true,
      fixedColumns: true,
      fixedNumber: 2
    })
  }


$(function() {
    buildTable($table, 10, 50)
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