


/**
 * Class popup state management
 * Open and close
 */
function showClass() {
    open_state = true;
    document.getElementById('class_popup').style.display = 'block';
    // console.log("Open menu");
}

function hideClass() {
    open_state = false;
    document.getElementById('class_popup').style.display = 'none';
    // console.log("Close menu");
}



