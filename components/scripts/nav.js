/**
 * @fileoverview Logic for sidebar
 * File providing all functions which are used to control sidebar,
 * witch can by applied to eny page
 */



var openState = false;



function setupNav(active_tab) {
    // active_tab \in {'home', 'calendar', 'feedback', 'projects'}

    document.querySelector('#mi_' + active_tab).classList.add('mobile__item__active');

    if (user === undefined) {
        setUser();
    } else {
        loadUser(setUser);
    }

    document.querySelector('.mobile__item__logout').addEventListener('click', logout);
}






/**
 * Mobile sidebar state management
 * Open and close
 */
function showNav() {
    openState = true;
    document.querySelector('.mobile').classList.add('mobile__open');
    // console.log("Open menu");
}

function hideNav() {
    openState = false;
    document.querySelector('.mobile').classList.remove('mobile__open');
    // console.log("Close menu");
}




/**
 * Setup user account reference
 * OnClick try to open account.html
 */
function onAccountClicked() {
    console.log('onAccountClicked; status: ' + user !== undefined);

    if (user !== undefined) {
        window.location.href = "/account.html";
    } else {
        window.location.href = "/login.html";
    }
}


/**
 * Set user to account fields (sidebar)
 * (or guest bio if cookie does not exist)
 */
function setUser() {
    // Setup main bio (phone/name)
    let sidebar = document.querySelector('.mobile__sidebar');
    sidebar.querySelector('.mobile__sidebar__name').innerText = user.name;
    let phone = user.phone;
    phone = '+' + phone[0] + ' (' + phone.slice(1, 4) + ') ' + phone.slice(4, 7) + '-' + phone.slice(7);
    sidebar.querySelector('.mobile__sidebar__phone').innerText = phone;

    // Show hiden sidebar items
    let hidden = sidebar.querySelectorAll('.mobile__item__hidden');
    for (var i = 0; i < hidden.length; ++i) {
        hidden[i].classList.remove('mobile__item__hidden');
    }

    // Setup avatar
    if (user.avatar != null && user.avatar != '')
        sidebar.querySelector('.mobile__sidebar__avatar').style.backgroundImage = "url('" + user.avatar + "')";

    // Notification
    if (user.calendar)
        sidebar.querySelector('#nt__home').classList.add('active');
    if (user.feedback)
        sidebar.querySelector('#nt__feed').classList.add('active');
    // if (user.calendar)
    //     sidebar.querySelector('#nt__cal').classList.add('active');
    if (user.projects)
        sidebar.querySelector('#nt__prj').classList.add('active');
}


/**
 * Logout function
 * Send http POST request to clear session id
 */
function logout() {
    user = undefined;


    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                location = 'http://ihse.tk/index.html';  // Refer to start page
            }

            if (this.status === 302) {  // Ok - redir

            }
        }
    };

    xhttp.open("POST", "http://ihse.tk:50000/logout", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}







/**
 * Mobile sidebar swipe open
 */
//
// window.addEventListener('load', function(){
//
//     var touchsurface = document.getElementById('touchsurface'),
//         startX,
//         startY,
//         dist,
//         threshold = 150, // минимальное расстояние для swipe
//         allowedTime = 200, // максимальное время прохождения установленного расстояния
//         elapsedTime,
//         startTime
//
//     function handleswipe(isrightswipe){
//         if (isrightswipe)
//             touchsurface.innerHTML = 'Вы пролистнули <span style="color:red">в правую сторону!</span>'
//         else{
//             touchsurface.innerHTML = 'Пролистывания в правую сторону не обнаружено.'
//         }
//     }
//
//     touchsurface.addEventListener('touchstart', function(e){
//         console.log("Start!");
//         touchsurface.innerHTML = ''
//         var touchobj = e.changedTouches[0]
//         dist = 0
//         startX = touchobj.pageX
//         startY = touchobj.pageY
//         startTime = new Date().getTime() // время контакта с поверхностью сенсора
//         e.preventDefault()
//     }, false)
//
//     touchsurface.addEventListener('touchmove', function(e){
//         console.log("!");
//         e.preventDefault() // отключаем стандартную реакцию скроллинга
//     }, false)
//
//     touchsurface.addEventListener('touchend', function(e){
//         var touchobj = e.changedTouches[0]
//         dist = touchobj.pageX - startX // получаем пройденную дистанцию
//         elapsedTime = new Date().getTime() - startTime // узнаем пройденное время
//         // проверяем затраченное время,горизонтальное перемещение >= threshold, и вертикальное перемещение <= 100
//         var swiperightBol = (elapsedTime <= allowedTime && dist >= threshold && Math.abs(touchobj.pageY - startY) <= 100)
//         handleswipe(swiperightBol)
//         e.preventDefault()
//     }, false)
//
// }, false)