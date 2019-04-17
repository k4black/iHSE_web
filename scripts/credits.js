/**
 * @fileoverview Credits page logic
 * File providing all functions which are used to control credits.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


// TODO: Loading indicator





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



// TODO: Graph


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