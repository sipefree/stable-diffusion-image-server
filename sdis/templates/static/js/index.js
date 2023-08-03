class SDISToggleButtonGroup {
    constructor(groupName, sectionNames) {
        this.groupName = groupName;
        this.sectionNames = sectionNames;
        this.sectionEventHandlers = {};
        for (let sectionName of sectionNames) {
            this.sectionEventHandlers[sectionName] = () => {
                document.querySelectorAll(".sdis-toggle-content[data-group='" + groupName + "']").forEach((content) => {
                    content.classList.remove("sdis-toggle-content-active");
                    
                    if (content.getAttribute("data-section") === sectionName) {
                        content.classList.add("sdis-toggle-content-active");
                    }
                });
                
                document.querySelectorAll(".sdis-toggle-button[data-group='" + groupName + "']").forEach((btn) => {
                    btn.classList.remove("sdis-toggle-button-active");
    
                    if (btn.getAttribute("data-section") === sectionName) {
                        btn.classList.add("sdis-toggle-button-active");
                    }
                });
            }
        }
    }

    // Configures a button to toggle the section specified by the button's data-section attribute.
    // This button might already be set up with the correct event handler, or it might be cloned button
    // that needs to be configured.
    configureButton(button) {
        let sectionName = button.getAttribute("data-section");
        if (!this.sectionNames.has(sectionName)) {
            throw new Error("Section name " + sectionName + " is not a valid section name for this button group");
        }

        // remove any existing event handlers
        button.removeEventListener("click", this.sectionEventHandlers[sectionName]);

        // add the new event handler
        button.addEventListener("click", this.sectionEventHandlers[sectionName]);
    }

    configureAllButtons() {
        document.querySelectorAll(".sdis-toggle-button[data-group='" + this.groupName + "']").forEach((button) => {
            this.configureButton(button);
        });
    }
}

class SDISToggleSystem {
    constructor() {
        this.buttonGroups = {};
    }

    discoverButtonGroups() {
        var groupNames = new Set();
        document.querySelectorAll(".sdis-toggle-button").forEach(function(button) {
            let groupName = button.getAttribute("data-group");
            groupNames.add(groupName);
        });

        for (let groupName of groupNames) {
            let sectionNames = new Set();
            document.querySelectorAll(".sdis-toggle-button[data-group='" + groupName + "']").forEach(function(button) {
                let sectionName = button.getAttribute("data-section");
                sectionNames.add(sectionName);
            });

            this.buttonGroups[groupName] = new SDISToggleButtonGroup(groupName, sectionNames);
        }

        this.configureAllButtons();
    }

    configureAllButtons() {
        for (let groupName in this.buttonGroups) {
            this.buttonGroups[groupName].configureAllButtons();
        }
    }
}


var sdisToggleSystem = new SDISToggleSystem();

// Initialize LightGallery
$(document).ready(function () {
    
    var media = $("#media")[0];
    
    lightGallery(media, {
        speed: 0,
        toogleThumb: false,
        backdropDuration: 0,
        slideEndAnimation: false,
        startClass: '',
        zoom: true,
        preload: 5,
        selector: '.lg-selector'
    });
    
    sdisToggleSystem.discoverButtonGroups();

    media.addEventListener('lgAfterAppendSubHtml', function(event) {
        sdisToggleSystem.configureAllButtons();
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

