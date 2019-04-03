var hamburgerButton = document.querySelector('.hamburger__button');
var mobileNav = document.querySelector('.mobile');
var mobileBg = document.querySelector('.mobile__background');



window.addEventListener('load', function(){

    var touchsurface = document.getElementById('touchsurface'),
        startX,
        startY,
        dist,
        threshold = 150, // минимальное расстояние для swipe
        allowedTime = 200, // максимальное время прохождения установленного расстояния
        elapsedTime,
        startTime

    function handleswipe(isrightswipe){
        if (isrightswipe)
            touchsurface.innerHTML = 'Вы пролистнули <span style="color:red">в правую сторону!</span>'
        else{
            touchsurface.innerHTML = 'Пролистывания в правую сторону не обнаружено.'
        }
    }

    touchsurface.addEventListener('touchstart', function(e){
        console.log("Start!");
        touchsurface.innerHTML = ''
        var touchobj = e.changedTouches[0]
        dist = 0
        startX = touchobj.pageX
        startY = touchobj.pageY
        startTime = new Date().getTime() // время контакта с поверхностью сенсора
        e.preventDefault()
    }, false)

    touchsurface.addEventListener('touchmove', function(e){
        console.log("!");
        e.preventDefault() // отключаем стандартную реакцию скроллинга
    }, false)

    touchsurface.addEventListener('touchend', function(e){
        var touchobj = e.changedTouches[0]
        dist = touchobj.pageX - startX // получаем пройденную дистанцию
        elapsedTime = new Date().getTime() - startTime // узнаем пройденное время
        // проверяем затраченное время,горизонтальное перемещение >= threshold, и вертикальное перемещение <= 100
        var swiperightBol = (elapsedTime <= allowedTime && dist >= threshold && Math.abs(touchobj.pageY - startY) <= 100)
        handleswipe(swiperightBol)
        e.preventDefault()
    }, false)

}, false)



var open = false;

function hamburgerOnClick() {
    if (!open) {
        openMobile();
    } else {
        closeMobile();
    }
}

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



hamburgerButton.addEventListener('click', hamburgerOnClick);
mobileNav.addEventListener('click', closeMobile);