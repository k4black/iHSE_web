
/* Floating button hide */
var floatingButton = document.querySelector('.mobile__floating__button');

var hide = false;

function showFloating() {
    hide = false;
    floatingButton.classList.remove('hide');
    console.log("Show floating button");
}

function hideFloating() {
    hide = true;
    floatingButton.classList.add('hide');
    console.log("Hide floating button");
}

var lastScrollTop = 0;
function floatingButtonOnScroll() {
    if (open) {
        return
    }

    var st = window.pageYOffset || document.documentElement.scrollTop; // Credits: "https://github.com/qeremy/so/blob/master/so.dom.js#L426"
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

window.addEventListener('scroll', floatingButtonOnScroll);



/* Open/close mobile menu */
var hamburgerButton = document.querySelector('.hamburger__button');
var mobileNav = document.querySelector('.mobile');

var open = false;


function openMobile() {
    open = true;
    mobileNav.classList.add('open');
    console.log("Open menu");
}

function closeMobile() {
    open = false;
    mobileNav.classList.remove('open');
    console.log("Close menu");
}


function hamburgerOnClick() {
    if (!open) {
        openMobile();
    } else {
        closeMobile();
    }
}


hamburgerButton.addEventListener('click', hamburgerOnClick);
mobileNav.addEventListener('click', closeMobile);

/* Swipe open*/

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