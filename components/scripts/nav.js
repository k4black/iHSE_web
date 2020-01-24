

var open_state = false;
var isLogin = false;


function setupNav(active_tab) {
    // active_tab \in {'home', 'calendar', 'feedback', 'projects'}
    console.log('LOGlog');

    document.querySelector('#mi_' + active_tab).classList.add('mobile__item__active');
}


setupNav('home');


/**
 * Mobile sidebar state management
 * Open and close
 */
function showNav() {
    open_state = true;
    document.querySelector('.mobile').classList.add('mobile__open');
    // console.log("Open menu");
}

function hideNav() {
    open_state = false;
    document.querySelector('.mobile').classList.remove('mobile__open');
    // console.log("Close menu");
}




/**
 * Setup user account reference
 * OnClick try to open account.html
 */
function onAccountClicked() {
    console.log('onAccountClicked; status: ' + isLogin);

    if (isLogin) {
        window.location.href = "account.html";
    } else {
        window.location.href = "login.html";
    }
}



/**
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 */
function loadUser() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                // console.log(this.responseText);
                user = JSON.parse(this.responseText);

                let sidebar = document.querySelector('.mobile__sidebar');
                sidebar.querySelector('.mobile__sidebar__name').innerText = user.name;
                sidebar.querySelector('.mobile__sidebar__phone').innerText = user.phone;

                isLogin = true;

                // Show menu items
                var hidden = sidebar.querySelectorAll('.mobile__item__hidden');
                for (var i = 0; i < hidden.length; ++i) {
                    hidden[i].classList.remove('mobile__item__hidden');
                }

                // Add admin tag
                if (user.type >= 2) {
                    document.querySelectorAll('body')[0].classList.add('admin');
                }

                // Show sidebar items
                var hidden = document.querySelectorAll('.header__item__hidden');
                for (var i = 0; i < hidden.length; ++i) {
                    hidden[i].classList.remove('header__item__hidden');
                    console.log('Show hidden items');
                }


                // Setup avatar
                if (user.avatar != null && user.avatar != undefined && user.avatar != '')
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
        }
    };

    xhttp.open("GET", "http://ihse.tk:50000/user", true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}




/**
 * Logout button
 * Send http POST request to clear session id
 */
var logout = document.querySelector('.mobile__item__logout');
if (logout != null)
logout.addEventListener('click', function () {

    var xhttp = new XMLHttpRequest();

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
});





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