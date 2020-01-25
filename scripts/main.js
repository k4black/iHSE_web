/**
 * @fileoverview Common logic for all pages
 * File providing all functions which are used to control ANY page
 */



/**
 * Remove loading class on shadow-skeleton elements
 */
function loadingEnd() {
    let ls = document.querySelectorAll('.data__loading');
    for (let i = 0; i < ls.length; i++) {
        ls[i].classList.remove('data__loading');
    }
}