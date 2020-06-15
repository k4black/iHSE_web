/**
 * @fileoverview Projects page logic
 * File providing all functions which are used to control projects.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */



{
    loadMainResources(
        [
            loadProjects,
            loadNames,
        ],
        ['names', 'projects'],
        [setProjects]
    );
}
runAfterLoading(function () {
    loadingStart();
});


/** ===============  LOGIC and REQUESTS  =============== */




/**
 * Parse of cached projects data and create html
 */
function setProjects() { // If ok set up day field
    // TODO: check user is loaded
    if ('user' in cache && cache['user'].project_id == 0) {
        document.getElementById('create_project').style.display = 'flex';
    }


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


        project_html =
            '<div class="project" project-id="' + project.id + '"' + (cache['user']['project_id'] == project.id ? 'onclick="editProject(' + project.id + ')"' : 'onclick="editOthersProject(' + project.id + ');"') + '>' +
                '<img src="images/' + (project.type === 'science' ? 'science.png' : (project.type === 'project' ? 'project.png': 'other.png')) + '">' +
                '<div class="description">' +

                    '<div class="project__top_line">' +
                        '<span>' + project.title + '</span>' +
                        '<div style="display: inline-flex; flex-direction: row">' +
                            // '<span style="text-align:right; width: fit-content; margin-left: 5px">' + project.type + '</span>' +
                            '<span style="text-align:right; width: fit-content; margin-left: 5px">' + (project.def_type === 'TED' ? 'TED' : 'Презентация') + '</span>' +
                        '</div>' +
                    '</div>' +

                    '<p class="project__names">' + names + '</p>' +

                    '<p class="project__anno">' + project.annotation + '</p>' +
                    // '<p class="project__desc">' + project.description + '</p>' +
                    (cache['user']['project_id'] == project.id ? '<button class="project__edit_button"><i class="mobile__item__icon large material-icons">edit</i></button>' : '') +
                '</div>' +
            '</div>';
        projects_html += project_html + '<hr class="border_line">';
    }

    projects.innerHTML = projects_html;
}
