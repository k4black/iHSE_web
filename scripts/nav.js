/**
 * @fileoverview Navigation control
 * File providing all functions can be used to control any navigation panel
 * Including animations and http requests if that are sending by nav elements
 */


// TODO: Compile site - optimize





/** ===============  LOGIC and REQUESTS  =============== */


// TODO: Nav panel notification
// TODO: Push notification
// TODO: Cookies notification? =) (Just say it during correspond sending)



/**
 * Account open management
 * OnClick rty to open account.html
 */
var isLogin = false;
var sidebarAccount = document.querySelector('.mobile__sidebar__account');

if (sidebarAccount != null)
sidebarAccount.addEventListener('click',
function () {

    if (isLogin)
        window.location.href = "account.html";

    else
        window.location.href = "login.html";
});



/**
 * Get account information from server
 * Send http GET request and get user bio (or guest bio if cookie does not exist)
 * TODO: optimize selection
 */
var sidebar = document.querySelector('.mobile__sidebar');
if (sidebar != null) {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields name and phone

                // console.log(this.responseText);
                var user = JSON.parse(this.responseText);
                sidebar.querySelector('.mobile__sidebar__name').innerText = user.name;
                sidebar.querySelector('.mobile__sidebar__phone').innerText = user.phone;

                isLogin = true;

                // Show menu items
                hidden = sidebar.querySelectorAll('.mobile__item__hidden');
                for (var i = 0; i < hidden.length; ++i) {
                    hidden[i].classList.remove('mobile__item__hidden');
                }


                // Setup avatar
                sidebar.querySelector('.mobile__sidebar__avatar').style.backgroundImage = "url(" + useer.avatar + ")";


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




/** ===============  ANIMATIONS  =============== */



/**
 * Add navigation button event - 'back'
 */
var mobileNav = document.querySelector('.arrow');
if (mobileNav != null)
mobileNav.addEventListener('click', function () {

    //alert(document.referrer);

    switch (document.referrer) {
        case "http://ihse.tk/login.html":
            window.location.href = "http://ihse.tk/";
            break;

        case "http://ihse.tk/register.html":
            window.location.href = "http://ihse.tk/login.html";
            break;

        case "http://ihse.tk/account.html":
            window.location.href = "http://ihse.tk/";
            break;

        case "http://ihse.tk/create.html":
            window.location.href = "http://ihse.tk/projects.html";
            break;

        default:
            window.location.href = document.referrer;
            break;
    }


    // window.location.href = document.referrer;
});





/**
 * Mobile Floating button management
 * OnScroll hide and appear
 * TODO: Position error
 */
var floatingButton = document.querySelector('.mobile__floating__button');

var hide = false;

function showFloating() {
    hide = false;
    floatingButton.classList.remove('hide');
    // console.log("Show floating button");
}

function hideFloating() {
    hide = true;
    floatingButton.classList.add('hide');
    // console.log("Hide floating button");
}

var lastScrollTop = 0;
function floatingButtonOnScroll() {
    if (open) {  // if sidebar is open
        return
    }

    // Credits: "https://github.com/qeremy/so/blob/master/so.dom.js#L426"
    var st = window.pageYOffset || document.documentElement.scrollTop;
    if (st > lastScrollTop){
        // downscroll code
        if (!hide)
            hideFloating();
    } else {
        // upscroll code
        if (hide)
            showFloating();
    }
    lastScrollTop = st <= 0 ? 0 : st; // For Mobile or negative scrolling
}

if (floatingButton != null)
window.addEventListener('scroll', floatingButtonOnScroll);




/**
 * Mobile sidebar management
 * OnClick on hamburger button
 * TODO: optimize selection
 */
var hamburgerButton = document.querySelector('.hamburger__button');
var mobileNav = document.querySelector('.mobile');

var open = false;

function openMobile() {
    open = true;
    mobileNav.classList.add('open');
    // console.log("Open menu");
}

function closeMobile() {
    open = false;
    mobileNav.classList.remove('open');
    // console.log("Close menu");
}

function hamburgerOnClick() {
    if (!open) {
        openMobile();
    } else {
        closeMobile();
    }
}
if (hamburgerButton != null)
hamburgerButton.addEventListener('click', hamburgerOnClick);

if (mobileNav != null)
mobileNav.addEventListener('click', closeMobile);





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