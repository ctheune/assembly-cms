tinyMCE.init({
    mode: 'specific_textareas',
    editor_selector: 'mceEditor',

    plugins : 'inlinepopups',

    theme: 'advanced',
    theme_advanced_toolbar_location : 'top',
    theme_advanced_toolbar_align : 'left',
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
