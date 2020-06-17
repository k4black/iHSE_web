// firebase_subscribe.js
const firebaseConfig = {
  apiKey: "AIzaSyCW292OF7R9J19a_QvCQXL4gfPp5KFY794",
  authDomain: "ihse-pushup.firebaseapp.com",
  databaseURL: "https://ihse-pushup.firebaseio.com",
  projectId: "ihse-pushup",
  storageBucket: "ihse-pushup.appspot.com",
  messagingSenderId: "464799760272",
  appId: "1:464799760272:web:27e62c8110ebe161aabd15",
  measurementId: "G-VC6JE5QJ46"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// consent-token.js
// messaging.requestPermission()
//     .then(function(){
//         return messaging.getToken();
//     })
//     .then(function(token){
//         console.log('token generated');
//         console.log(token);
//         console.log('token generated');
//     })
//     .catch(function(err){
//         console.log('NOOOONE', err);
//         alert('Вы можете включить уведомления о событиях, регистрациях и важных объявлениях в настройках браузера (рекомендуется).');
//     })


window.addEventListener('load', function () {

    // Check notifications are supported by web-browser
    if ('Notification' in window) {
        var messaging = firebase.messaging();

        // if (Notification.permission === 'granted') {
        //     console.log('granted subscribe');
        //     subscribe();
        // }

        if (Notification.permission === 'denied') {
            console.warn('No permissions for notifications.');
        }

        subscribe();
    }

});



function subscribe() {
    // запрашиваем разрешение на получение уведомлений
    messaging.requestPermission()
        .then(function () {
            // получаем ID устройства
            messaging.getToken()
                .then(function (currentToken) {
                    console.log(currentToken);

                    if (currentToken) {
                        sendTokenToServer(currentToken);
                    } else {
                        console.warn('Не удалось получить токен.');
                        setTokenSentToServer(false);
                    }
                })
                .catch(function (err) {
                    console.warn('При получении токена произошла ошибка.', err);
                    setTokenSentToServer(false);
                });
    })
    .catch(function (err) {
        console.warn('Не удалось получить разрешение на показ уведомлений.', err);
        console.warn('Вы можете включить уведомления о событиях, регистрациях и важных объявлениях в настройках браузера (рекомендуется).');
        // TODO: alert
    });
}


// отправка ID на сервер
function sendTokenToServer(currentToken) {
    if (!isTokenSentToServer(currentToken)) {
        console.log('Отправка токена на сервер...');

        let xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState === 4) {  // When request is done
                if (this.status === 200) {  // Got it
                    setTokenSentToServer(currentToken);
                    console.warn('Токен принят сервером');
                } else {
                    console.warn('Токен не принят сервером');
                }
            }
        };

        let data = JSON.stringify({'token': currentToken});
        xhttp.open("POST", "/notification", true);
        //xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('Content-Type', 'text/plain');
        xhttp.withCredentials = true;  // To receive cookie
        xhttp.send(data);
    } else {
        console.log('Токен уже отправлен на сервер.');
    }
}


// используем localStorage для отметки того,
// что пользователь уже подписался на уведомления
function isTokenSentToServer(currentToken) {
    return window.localStorage.getItem('sentFirebaseMessagingToken') == currentToken;
}

function setTokenSentToServer(currentToken) {
    window.localStorage.setItem('sentFirebaseMessagingToken', currentToken ? currentToken : '');
}

