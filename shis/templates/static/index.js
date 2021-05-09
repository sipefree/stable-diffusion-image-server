// Initialize LightGallery

$(document).ready(function () {

    $("#media").lightGallery({
        speed: 0,
        toogleThumb: false,
        backdropDuration: 0,
        slideEndAnimatoin: false,
        startClass: '',
        zoom: true,
        preload: 5,
        selector: 'li > div'
    });

});


$(document).keypress(function (e) {
    if (e.which === 61) {
        // zoom in on =
        $('#lg-zoom-in').click();
    } else if (e.which === 45) {
        // zoom out on -
        $('#lg-zoom-out').click();
    } else if (e.which === 48) {
        // reset on 0
        $('#lg-actual-size').click();
    }
});


// Initialize Selection JS

const selection = new SelectionArea({
    document: window.document,
    class: 'selection-area',
    container: 'body',
    selectables: ['#media > li'],
    boundaries: ['#media'],
})

// Selection Logic

selection.on('start', ({ event, store }) => {
    // console.log('start', capture(store));
    let target = event.target.parentNode;
    if (target.classList.contains('selected')) {
        target.classList.remove('selected');
        store.changed.removed.push(target);
    }
}).on('move', ({ store }) => {
    // console.log('move', capture(store));
    for (const el of store.changed.added) {
        el.classList.add('selected');
    }
    for (const el of store.changed.removed) {
        el.classList.remove('selected');
    }
}).on('stop', ({ store }) => {
    // console.log('stop', capture(store));
    selection.keepSelection();
    // console.log('end', capture(store));
});

// Capture object when it's logged

function clearEmpties(o) {
    for (var k in o) {
        if (!o[k] || typeof o[k] !== "object") {
            continue // If null or not an object, skip to the next iteration
        }

        // The property is an object
        clearEmpties(o[k]); // <-- Make a recursive call on the nested object
        if (Object.keys(o[k]).length === 0) {
            delete o[k]; // The object had no properties, so delete that property
        }
    }
}

function capture(object) {
    let whitelist = ['stored', 'selected', 'changed', 'added', 'removed', 'tagName', 'classList'];
    let parsed = JSON.parse(JSON.stringify(object, whitelist, 2));
    clearEmpties(parsed);
    return JSON.stringify(parsed, null, 2);
}

// Helper function to copy file list to clipboard.

function textToClipboard(text) {
    let dummy = document.createElement("textarea");
    document.body.appendChild(dummy);
    dummy.value = text;
    dummy.select();
    document.execCommand("copy");
    document.body.removeChild(dummy);
}

// Copy and Clear Selection buttons.

let notifTimer;

function showNotification(text) {
    clearTimeout(notifTimer);
    const notif = document.querySelector('.notification');
    notif.innerText = text;
    notifTimer = setTimeout(() => {notif.innerText = '';}, 3000);
}

function copySelection() {
    const elements = selection.getSelection();
    const paths = elements.map(function (element) {
        return element.querySelector('div.info').innerText
    })
    textToClipboard(paths.join("\r\n"));
    let notifText = 'Copied ' + paths.length + ' filenames to the clipboard!';
    showNotification(notifText);
}

function toggleSelection() {
    let elements = selection.getSelection();
    if (elements.length > 0) {
        for (const element of elements) {
            element.classList.remove('selected');
        }
        selection.clearSelection();
        showNotification('Deselected all elements!');            
    } else {
        elements = document.querySelectorAll('#media > li');
        for (const element of elements) {
            element.classList.add('selected');
            selection.select(element);
        }
        selection.keepSelection();
        showNotification('Selected all elements!');            
    }
}