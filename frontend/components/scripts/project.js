


loadNames(function () {});



function editOthersProject(project_id) {
    document.querySelector('body').classList.remove('edit_mode');
    loadProject(project_id, setPopupProject);
}

function editProject(project_id) {
    document.querySelector('body').classList.add('edit_mode');
    loadProject(project_id, setPopupProject);
}



/**
 * Class popup state management
 * Open and close
 */
function showProject() {
    openState = true;
    document.getElementById('project_popup').style.display = 'block';
    // console.log("Open menu");
}

function hideProject() {
    openState = false;
    document.getElementById('project_popup').style.display = 'none';
    // console.log("Close menu");
}






function setupData(elem, data) {
    elem.firstElementChild.innerHTML = data;
    elem.lastElementChild.value = data;
}


/**
 * Set class fields in the popup class info
 */
function setPopupProject() {
    let names = cache['names'];
    let project = cache['project'];
    let project_id = project.id;

    document.querySelector('#project_popup .project_popup__header__title').innerText = project.title;

    setupData(document.querySelector('#project_popup .desc'), project.description);
    setupData(document.querySelector('#project_popup .anno'), project.annotation);
    setupData(document.querySelector('#project_popup .dirs'), project.direction);
    setupData(document.querySelector('#project_popup .def_type'), project.def_type);
    setupData(document.querySelector('#project_popup .type'), project.type);

    let users_html = '';
    for (let id in names) {
        let user = names[id];

        if (user['project_id'] == project_id) {
            users_html += '<p class="user' + (user['id'] == cache['user']['id'] ? 'current_user' : '') + '">' + user.name + ' [' + user.team + ']</p>';
        }
    }


    document.querySelector('.names').innerHTML = users_html;



    // Setup buttons
    if (cache['user']['project_id'] == 0) {
        document.querySelector('#enroll').style.display = 'block';
        document.querySelector('#deenroll').style.display = 'none';
    } else if (project_id == cache['user']['project_id']) { // Current user enrolled
        document.querySelector('#enroll').style.display = 'none';
        document.querySelector('#deenroll').style.display = 'block';
    } else {
        document.querySelector('#enroll').style.display = 'none';
        document.querySelector('#deenroll').style.display = 'none';
    }


    document.querySelector('#enroll').onclick = function () {
        enrollProject();
    };
    document.querySelector('#deenroll').onclick = function () {
        deenrollProject();
    };


    showProject();
}









function enrollProject() {
    if (!confirm('Вы уверены, что хотите участвовать в проекте?')) {
        return;
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                location.reload();
                // cache['user']['project_id'] = cache['project']['id'];
                // loadProject(cache['project']['id'], setPopupProject);

            } else if (this.status === 409) {
                alert('Невозможно записаться. у вас уже есть проект.')
            }
        }
    };

    xhttp.open("POST", "/enroll_project?" + "project_id="+ cache['project']['id'], true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}


function deenrollProject() {
    if (!confirm('Вы уверены, что хотите покинуть проект?')) {
        return;
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                location.reload();
                // cache['user']['project_id'] = 0;
                // loadProject(cache['project']['id'], setPopupProject);
            } else if (this.status === 409) {
                alert('Невозможно отписаться. У вас нет проекта.');
            }
        }
    };

    xhttp.open("POST", "/deenroll_project?" + "project_id="+ cache['project']['id'], true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}





function saveProject() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                loadProject(cache['project']['id'], setPopupProject);
                // hideProject();
            } else if (this.status === 405) {
                alert('Вы не участник этого проекта. Нельзя его редактировать.')
            }
        }
    };

    let anno = document.querySelector('.anno').lastElementChild.value;
    let type = document.querySelector('.type').lastElementChild.value;
    let def_type = document.querySelector('.def_type').lastElementChild.value;
    let dirs = document.querySelector('.dirs').lastElementChild.value;
    let desc = document.querySelector('.desc').lastElementChild.value;

    if (desc == '' || type == '' || def_type == '' || dirs == '' || desc == '') {
        alert('Вы должны заполнить все поля!');
        return;
    }

    cache['project']['annotation'] = anno;
    cache['project']['type'] = type;
    cache['project']['def_type'] = def_type;
    cache['project']['direction'] = dirs;
    cache['project']['description'] = desc;

    let data = JSON.stringify(cache['project']);

    xhttp.open("POST", "/edit_project", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}

