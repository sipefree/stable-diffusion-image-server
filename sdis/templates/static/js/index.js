class SDISToggleButtonGroup {
    constructor(groupName, sectionNames) {
        this.groupName = groupName;
        this.sectionNames = sectionNames;
        this.sectionEventHandlers = {};
        for (let sectionName of sectionNames) {
            this.sectionEventHandlers[sectionName] = (event) => {
                let shouldEnable = !event.currentTarget.classList.contains("sdis-toggle-button-active");
                
                document.querySelectorAll(".sdis-toggle-content").forEach((content) => {
                    if (sectionNames.has(content.getAttribute("data-section"))) {
                        content.classList.remove("sdis-toggle-content-active");
                        
                        if (shouldEnable && content.getAttribute("data-section") === sectionName) {
                            content.classList.add("sdis-toggle-content-active");
                        }
                    }
                });
                
                document.querySelectorAll(".sdis-toggle-button[data-group='" + groupName + "']").forEach((btn) => {
                    btn.classList.remove("sdis-toggle-button-active");
                    
                    if (shouldEnable && btn.getAttribute("data-section") === sectionName) {
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
        for (let groupName of Object.keys(this.buttonGroups)) {
            this.buttonGroups[groupName].configureAllButtons();
        }
    }
}


class SDISCopyButtonSystem {
    
    constructor() {
        this.copyTextsByID = {};
        this.eventHandlersById = {};
    }
    
    discoverCopyTexts() {
        document.querySelectorAll(".sdis-copy-text").forEach((copyTextElement) => {
            let id = copyTextElement.getAttribute("data-id");
            if (id === null) {
                throw new Error("Copy text has no data-id attribute");
            }
            
            let copyText = copyTextElement.innerText
            
            this.copyTextsByID[id] = copyText;
            this.eventHandlersById[id] = (event) => {
                let copyButton = event.currentTarget;
                let copyText = this.copyTextsByID[id];
                navigator.clipboard.writeText(copyText);
                
                // Add the copied class immediately
                copyButton.classList.add('sdis-copy-button-copied');
                
                // After a small delay, add the fade class, remove the copied class
                setTimeout(() => {
                    copyButton.classList.add('sdis-copy-button-fade');
                    copyButton.classList.remove('sdis-copy-button-copied');
                }, 10);
                
                // After 1 second, remove the fade class
                setTimeout(() => {
                    copyButton.classList.remove('sdis-copy-button-fade');
                }, 1000);
            };
        });
        
        this.configureAllButtons();
    }
    
    
    configureAllButtons() {
        document.querySelectorAll(".sdis-copy-button").forEach((copyButton) => {
            let id = copyButton.getAttribute("data-id");
            if (id === null) {
                throw new Error("Copy button has no data-id attribute");
            }
            
            if (!(id in this.copyTextsByID)) {
                throw new Error("Copy button with data-id " + id + " has no corresponding copy text");
            }
            
            copyButton.removeEventListener("click", this.eventHandlersById[id]);
            copyButton.addEventListener("click", this.eventHandlersById[id]);
        });
    }
    
}

var sdisToggleSystem = new SDISToggleSystem();
var sdisCopySystem = new SDISCopyButtonSystem();

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
        selector: '.lg-selector',
        allowMediaOverlap: true,
        defaultCaptionHeight: 30,
        mobileSettings: {
            toogleThumb: false,
            backdropDuration: 0,
            slideEndAnimation: false,
            startClass: '',
            zoom: true,
            preload: 5,
            selector: '.lg-selector',
            allowMediaOverlap: true,
            defaultCaptionHeight: 30
        }
    });
    
    sdisToggleSystem.discoverButtonGroups();
    sdisCopySystem.discoverCopyTexts();
    
    media.addEventListener('lgAfterAppendSubHtml', function(event) {
        sdisToggleSystem.configureAllButtons();
        sdisCopySystem.configureAllButtons();
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

