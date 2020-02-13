/**
 * @fileoverview QR-codes scanning
 * File providing all functions which are used to control register.html page
 * Including animations and http requests if that are sending by NOT nav elements
 */


function getParameterByName(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

let currentEventId = getParameterByName('event');

window.addEventListener('load', function() {
    // alert("Ready!");

    currentEventId = getParameterByName('event');

    if (currentEventId == null) {
        currentEventId = 0;
    }

    loadEvent(currentEventId, setEvent);
    loadEnrollsByClassId(currentEventId, function () {});
    loadUsers(function () {});
});



/**
 * Get event information from server by user_id
 * Save list to global 'cache['users']'
 *
 * Run func on OK status
 */
function loadUsers(func) {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) { // If ok set up fields
                let users = JSON.parse(this.responseText);
                let objs = groupByUnique(users, 'code');

                cache['users'] = objs;

                func();
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_table?" + "table=" + 'users', true);
    xhttp.withCredentials = true; // To send Cookie;
    xhttp.send();
}


function setEvent() {
    let event = cache['event'];

    document.querySelector('.description .title').innerHTML = event['title'];
    document.querySelector('.description .desc').innerHTML = event['description'];

    let type_elem = "";
    if (event['type'] == 1) {
        type_elem = '<p class="event_type master_event">master</p>'
    } else if (event['type'] == 2) {
        type_elem = '<p class="event_type lecture_event">lecture</p>'
    }
    document.querySelector('.type').innerHTML = type_elem;
}


function setScannedClass() {
    document.querySelector('body').classList.add('scanned');
    setTimeout(removeScannedClass, 800);
}

function removeScannedClass() {
    document.querySelector('body').classList.remove('scanned');
}

function setWrongScannedClass() {
    document.querySelector('body').classList.add('wrong_scanned');
    setTimeout(removeWrongScannedClass, 800);
}

function removeWrongScannedClass() {
    document.querySelector('body').classList.remove('wrong_scanned');
}







let scannedSet = new Set();
let scanned = {};





function saveScanned() {
    let users_elems = document.querySelector('#scanned_list').children;

    let users_list = [];

    for (let i = 0; i < users_elems.length; ++i) {
        users_list.push({
            'id': users_elems[i].getAttribute('data-id'),
            'bonus': users_elems[i].querySelector('input').value,
            'name': users_elems[i].querySelector('p').innerText
        });
    }


    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                // TODO Redirect
            }
        }
    };


    let data = JSON.stringify(users_list);

    xhttp.open("POST", "//ihse.tk/checkin?" + "event="+currentEventId, true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}






function addScannedElem(scannedText) {
    let user = {'id': 0, 'name': 'Some Username'};

    try {
        user = cache['users'][scannedText];
    } catch (e) {
    }



    let scans_html = '<div class="user" data-id="' + user['id'] + '">' +
            '<p>' + user['name'] + '</p>' +
            '<input type="number" value="0">' +
            '<div class="remove_scanned" onclick="removeScannedElem(this.parentElement)"><i class="mobile__item__icon large material-icons">close</i></div>' +
        '</div>';

    document.querySelector('#scanned_list').innerHTML += scans_html;
}

function removeScannedElem(elem) {
    console.log('Removing: ', elem.getAttribute('data-id'));
    scannedSet.delete(elem.getAttribute('data-id'));
    elem.remove();
}


/** ===============  GR CODE SCANNING  =============== */




function onQRCodeScanned(scannedText) {
    if (scannedSet.has(scannedText)) {
        console.log('Already Scanned: ', scannedText);  // TODO: remove 
        return;  // Already scanned
    }


    console.log('Scanned: ', scannedText);


    if (cache['users'] == undefined || !Object.keys(cache['users']).includes(scannedText)) {
        console.log('No user with id: ', scannedText);
        setWrongScannedClass(); // Red blink animation
        document.getElementById("scannedTextMemo").innerText = scannedText + ' : ' + 'Wrong user!';
        return;
    }

    if (cache['event']['type'] === 1 || cache['event']['type'] === '1') {  // Master class, not lecture
        let user = cache['users'][scannedText];
        let enrolls = Object.values(cache['enrolls']).filter(function (i) {return i['user_id'] == user['id']});

        if (enrolls.length === 0) {
            alert('User are NOT enrolled!');
            return;
        }
    }

    alert('Ok. Add user with code ' + scannedText + ' to the list.');

    scannedSet.add(scannedText);


    setScannedClass(); // Green blink animation


    addScannedElem(scannedText);


    document.getElementById("scannedTextMemo").innerText = scannedText + ' : ' + 'Some Name';
    // TODO uncoment
    //document.getElementById("scannedTextMemo").value = scannedText + ' : ' + cache['users'][scannedText];
}

function provideVideo() {
    var n = navigator;

    if (n.mediaDevices && n.mediaDevices.getUserMedia) {
        return n.mediaDevices.getUserMedia({
            video: {
                facingMode: "environment"
            },
            audio: false
        });
    }

    return Promise.reject('Your browser does not support getUserMedia');
}

function provideVideoQQ() {
    return navigator.mediaDevices.enumerateDevices()
        .then(function (devices) {
            var exCameras = [];
            devices.forEach(function (device) {
                if (device.kind === 'videoinput') {
                    exCameras.push(device.deviceId)
                }
            });

            return Promise.resolve(exCameras);
        }).then(function (ids) {
            if (ids.length === 0) {
                return Promise.reject('Could not find a webcam');
            }

            return navigator.mediaDevices.getUserMedia({
                video: {
                    'optional': [{
                        'sourceId': ids.length === 1 ? ids[0] : ids[1]//this way QQ browser opens the rear camera
                    }]
                }
            });
        });
}

var jbScanner;
//this function will be called when JsQRScanner is ready to use
function JsQRScannerReady() {
    //create a new scanner passing to it a callback function that will be invoked when
    //the scanner succesfully scan a QR code
    jbScanner = new JsQRScanner(onQRCodeScanned);
    //var jbScanner = new JsQRScanner(onQRCodeScanned, provideVideo);
    //reduce the size of analyzed image to increase performance on mobile devices
    jbScanner.setSnapImageMaxSize(300);
    var scannerParentElement = document.getElementById("scanner");
    if (scannerParentElement) {
        //append the jbScanner to an existing DOM element
        jbScanner.appendTo(scannerParentElement);
    }
}





let scanningStatus = true;

function changeScanning() {
    if (scanningStatus) {
        scanningPause();
    } else {
        scanningResume();
    }

    scanningStatus = !scanningStatus;
}


function scanningPause() {
    document.querySelector('video').pause();
    jbScanner.stopScanning();

//    TODO: Add pause button
}


function scanningResume() {
    document.querySelector('video').load();
    jbScanner.resumeScanning();
}