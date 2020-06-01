



$(function() {
    loadConfig();
    loadPlaces();
});



function loadConfig() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                let data = JSON.parse(this.responseText);

                $('#total')[0].value = data.total;
                $('#master')[0].value = data.master;
                $('#lecture')[0].value = data.lecture;
                $('#additional')[0].value = data.additional;

                $('#groups')[0].value = data.groups;
            }
        }
    };

    xhttp.open("GET", "/admin_get_config", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}


function saveConfig() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('ok');
            }
        }
    };

    let config = {
        'total': parseInt($('#total')[0].value),
        'master': parseInt($('#master')[0].value),
        'lecture': parseInt($('#lecture')[0].value),
        'additional': parseInt($('#additional')[0].value),

        'groups': parseInt($('#groups')[0].value),
    };

    let data = JSON.stringify(config);

    xhttp.open("POST", "/admin_post_config", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}




function loadPlaces() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                let places;
                try {
                    places = JSON.parse(this.responseText);
                } catch (e) {
                    console.log('error', e)
                    places = []
                }

                $('#places')[0].value = places.join('\n');
            }
        }
    };

    xhttp.open("GET", "/admin_get_places", true);
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send();
}


function savePlaces() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                alert('ok');
            }
        }
    };

    let places = $('#places')[0].value.split('\n');
    let data = JSON.stringify(places);

    xhttp.open("POST", "/admin_post_places", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}