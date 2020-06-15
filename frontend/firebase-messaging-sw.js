
// firebase-messaging-sw.js
// importScripts('https://www.gstatic.com/firebasejs/3.6.8/firebase-app.js');
// importScripts('https://www.gstatic.com/firebasejs/3.6.8/firebase-messaging.js');

if( 'undefined' === typeof window){
    importScripts('https://www.gstatic.com/firebasejs/3.6.8/firebase-app.js');
    importScripts('https://www.gstatic.com/firebasejs/3.6.8/firebase-messaging.js');
}


const firebaseConfig = {
  apiKey: "AIzaSyCW292OF7R9J19a_QvCQXL4gfPp5KFY794",
  authDomain: "ihse-pushup.firebaseapp.com",
  databaseURL: "https://ihse-pushup.firebaseio.com",
  projectId: "ihse-pushup",
  storageBucket: "ihse-pushup.appspot.com",
  messagingSenderId: "464799760272",
  appId: "1:464799760272:web:27e62c8110ebe161aabd15",
  measurementId: "G-VC6JE5QJ46"
}

firebase.initializeApp(firebaseConfig);


// firebase.initializeApp({
//     messagingSenderId: '464799760272'
// });


const messaging = firebase.messaging();
