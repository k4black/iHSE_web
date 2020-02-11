



$(function() {
    loadConfig();
});



function loadConfig() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4) {
            if (this.status === 200) {
                data = JSON.parse(this.responseText);

                $('#total')[0].value = data.total;
                $('#master')[0].value = data.master;
                $('#lecture')[0].value = data.lecture;
                $('#additional')[0].value = data.additional;
            }
        }
    };

    xhttp.open("GET", "//ihse.tk/admin_get_config", true);
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
        'additional': parseInt($('#additional')[0].value)
    };

    let data = JSON.stringify(config);

    xhttp.open("POST", "//ihse.tk/admin_post_config", true);
    //xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('Content-Type', 'text/plain');
    xhttp.withCredentials = true;  // To receive cookie
    xhttp.send(data);
}