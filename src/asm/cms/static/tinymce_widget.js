tinyMCE.init({
    mode: 'specific_textareas',
    editor_selector: 'mceEditor',

    plugins : 'inlinepopups',

    theme: 'advanced',
    theme_advanced_toolbar_location : 'top',
    theme_advanced_toolbar_align : 'left',
    theme_advanced_buttons1: "bold,italic,strikethrough,justifyleft,justifycenter,justifyright,formatselect,bullist,numlist,link,unlink,image,table",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",

    dialog_type : 'modal',

    file_browser_callback: 'asmcmsFileBrowser',

    document_base_url: document.baseURI,

    width: 600,
    height: 800,

    gecko_spellcheck : true
});


function asmcmsFileBrowser(field_name, url, type, win) {

    tinyMCE.activeEditor.windowManager.open({
        url: window.location + '/@@tinymce-linkbrowser',
        inline: "yes",

    });
    return false;
}
