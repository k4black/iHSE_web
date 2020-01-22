



var tabs = [];
var current_timeline = 'vacations';



$(function() {
    current_timeline = 'vacations';
    // loadAndCreateTable(current_table);

    // setupToolbar();
    // setupTabs();
    loadDays();
});


function loadDays() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone
                days = JSON.parse(this.responseText);

                tabs = ['vacations'];
                for (let day of days) {
                    tabs.push(day.date);
                }

                setupTabs();
            }
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/days", true);
    // xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


function setupTabs() {
    tabs_html = '';
    for (let tab_name of tabs) {
        tabs_html += '<button ' + (tab_name === 'vacations' ? 'class="active_tab"' : '') + ' id="tab_' + tab_name + '">' + tab_name + '</button>';
    }
    $('.tabs')[0].innerHTML = tabs_html;

    for (let tab_name of tabs) {
        $('#tab_' + tab_name)[0].onclick = function () {
            current_timeline = tab_name;
            loadAndCreateTimeline(current_timeline);
            $('.tabs button').removeClass('active_tab');
            $('#tab_' + tab_name).addClass('active_tab');
        };
    }
}




function loadAndCreateTimeline(timeline) {

}