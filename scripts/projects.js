/**
 * @fileoverview Projects page logic
 * File providing all functions which are used to control projects.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */



/**
 * Get day information from server
 * Send http GET request and get list of projects
 * than parse of json data and create html
 */
var projects = document.querySelector('.wrapper');

var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up day field
            loadingEnd(); // TODO: Check

            var projects_data = JSON.parse( this.responseText );

            var projects_html = "";
            var project_html;

            for (var project of projects_data) {
                var names = project.name.split(',');
                var rez = '';
                for (var i of names) {
                    var tmp_name = i.split(' ').filter(word => word != '');
                    console.log(tmp_name);
                    if (rez != '') {
                        rez += ', '
                    }
                    rez += tmp_name[0] + ' ' + tmp_name[1][0] + '.';
                }


                project_html = '<div class="project">'+
                                   '<img src="images/rocket.jpeg">' +
                                   '<div class="description">' +

                                       '<div class="project__top_line">' +
                                           '<span>' + project.title + '</span>' +
                                           '<span style="text-align: right">' + project.type + '</span>' +
                                       '</div>' +

                                       '<p class="project__names">' + names + '</p>' +

                                       '<p class="project__desc">' + project.desc + '</p>' +

                                   '</div>' +
                               '</div>';



                projects_html += project_html + '<hr class="border_line">';
            }


            projects.innerHTML = projects_html;
        }
    }
};

xhttp.open("GET", "http://ihse.tk:50000/projects", true);
xhttp.send();
