// Initialize LightGallery

$(document).ready(function () {
    
    var media = $("#media")[0];
    
    lightGallery(media, {
        speed: 0,
        toogleThumb: false,
        backdropDuration: 0,
        slideEndAnimatoin: false,
        startClass: '',
        zoom: true,
        preload: 5,
        selector: '.lg-selector'
    });
    
    media.addEventListener('lgAfterAppendSubHtml', function(event) {
        var buttons = document.querySelectorAll(".toggle-btn");
        buttons.forEach(function(button) {
            // Add a click event listener to each button
            button.addEventListener("click", function() {
                var idx = this.getAttribute("data-idx");
                var infoContent = document.querySelector(".info-content-" + idx);
                var textContent = document.querySelector(".text-content-" + idx);
                var allButtons = document.querySelectorAll('.toggle-btn');
                allButtons.forEach(function(btn) {
                    btn.classList.remove("active");
                });
                
                if (this.firstChild.innerHTML === 'info') {
                    infoContent.style.display = "block";
                    textContent.style.display = "none";
                } else {
                    infoContent.style.display = "none";
                    textContent.style.display = "block";
                }
                this.classList.add("active");
            });
        });
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

