/**
 * @fileoverview Projects page logic
 * File providing all functions which are used to control projects.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */




/** ===============  LOGIC and REQUESTS  =============== */


// TODO: Create wrapper in main.js
window.addEventListener('load', function () {
    console.log('Load');
    // loadProjects(setProjects);
    // Run 'setProjects' when both Projects and Names are loaded
    loadProjects(function () {checkLoading(setProjects, ['names', 'projects']);})
    loadNames(function () {checkLoading(setProjects, ['names', 'projects']);})
});





/**
 * Parse of cached projects data and create html
 */
function setProjects() { // If ok set up day field
    console.log('setProjects run with cache: ', cache);

    loadingEnd(); // TODO: Check
    let projects = document.querySelector('.wrapper');

    var projects_html = "";
    var project_html;

    for (let id in cache['projects']) {
        let project = cache['projects'][id];

        // var names = project.name.split(',');
        let names = '';

        for (let user_id in cache['names']) {  // TODO: optimize O notation? Now O(n^2)
            let name = cache['names'][user_id];
            // console.log('proj_id=', id, name, name['project_id']);
            if (id == name['project_id']) {  // Can be string
                // Current project has that user
                // console.log('ok');

                names += name.name.split(' ')[0] + ' ' + name.name.split(' ')[1][0] + '. ';
            }
        }


        project_html = '<div class="project" onclick="editProject(' + id + ')">' +
            '<img src="images/rocket.jpeg">' +
            '<div class="description">' +

            '<div class="project__top_line">' +
            '<span>' + project.title + '</span>' +
            '<span style="text-align:right">' + project.type + '</span>' +
            '</div>' +

            '<p class="project__names">' + names + '</p>' +

            '<p class="project__desc">' + project.description + '</p>' +

            '</div>' +
            '</div>';
        projects_html += project_html + '<hr class="border_line">';
    }

    projects.innerHTML = projects_html;
}
