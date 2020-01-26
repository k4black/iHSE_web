/**
 * @fileoverview Projects page logic
 * File providing all functions which are used to control projects.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */


// TODO: Create wrapper in main.js
window.addEventListener('load', function () {
    console.log('Load');
    loadProjects(setProjects);
});





/**
 * Parse of cached projects data and create html
 */
function setProjects() { // If ok set up day field
    loadingEnd(); // TODO: Check
    let projects = document.querySelector('.wrapper');

    var projects_html = "";
    var project_html;

    for (let id in cache['projects']) {
        let project = cache['projects'][id];

        // var names = project.name.split(',');
        var names = 'Names TODO remove';  // TODO: get names from names request
        // var rez = '';
        // for (var i of names) {
        //     if (i == [])
        //         continue;
        //
        //     var tmp_name = i.split(' ').filter(word => word != '');
        //     //console.log(tmp_name);
        //
        //     if (tmp_name == [] || tmp_name.length <= 0)
        //         continue;
        //
        //     if (rez != '') {
        //         rez += ', '
        //     }
        //
        //     rez += tmp_name[0] + ' ' + tmp_name[1][0] + '.';
        // }


        project_html = '<div class="project">' +
            '<img src="images/rocket.jpeg">' +
            '<div class="description">' +

            '<div class="project__top_line">' +
            '<span>' + project.title + '</span>' +
            '<span style="text-align:right">' + project.type + '</span>' +
            '</div>' +

            '<p class="project__names">' + names + '</p>' +

            '<p class="project__desc">' + project.desc + '</p>' +

            '</div>' +
            '</div>';
        projects_html += project_html + '<hr class="border_line">';
    }

    projects.innerHTML = projects_html;
}
