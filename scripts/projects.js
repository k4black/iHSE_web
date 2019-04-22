/**
 * @fileoverview Projects page logic
 * File providing all functions which are used to control projects.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


/**
 * Get day information from server
 * Send http GET request and get list of projects
 * than parse of json data and create html
 * TODO: optimize selection
 * TODO: optimize html generation
 */
var projects = document.querySelector('.wrapper');

var xhttp = new XMLHttpRequest();

xhttp.onreadystatechange = function() {
    if (this.readyState === 4) {
        if (this.status === 200) { // If ok set up day field

            var projects_data = JSON.parse( this.responseText );

            console.log(projects_data);


            var projects_html = "";
            var project_html;

            for (var project of projects_data) {

                project_html = '<div class="project">'+
                                   '<img src="images/avatar.png">' +
                                   '<div class="description">' +

                                       '<div class="project__top_line">' +
                                           '<span>' + project.title + '</span>' +
                                           '<span style="text-align: right">' + project.type + '</span>' +
                                       '</div>' +

                                       '<p class="project__names">' + project.name + '</p>' +

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