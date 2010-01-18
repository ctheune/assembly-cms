tinyMCE.init({
    mode: 'specific_textareas',
    editor_selector: 'mceEditor',

    plugins : 'advlink,inlinepopups,fullscreen,table,contextmenu',

    theme: 'advanced',
    theme_advanced_toolbar_location : 'top',
    theme_advanced_toolbar_align : 'left',
    theme_advanced_buttons1: "formatselect,|,bold,italic,strikethrough,|,justifyleft,justifycenter,justifyright,|,bullist,numlist,table,|,link,anchor,unlink,image,|,code,fullscreen",
    theme_advanced_buttons2: "",
    theme_advanced_buttons3: "",

    theme_advanced_blockformats: "p,h2,h3,blockquote,code",

    dialog_type : 'modal',

    file_browser_callback: 'asmcmsFileBrowser',

    document_base_url: document.baseURI,

    width: "100%",
    height: 400,

    gecko_spellcheck : true
});


function asmcmsFileBrowser(field_name, url, type, win) {

    tinyMCE.activeEditor.windowManager.open({
        // XXX The ../ means we know that /edition is the current base
        url: window.location + '/../../@@tinymce-linkbrowser',
        width:400,
        height:400,
        inline: "yes",
    }, {window: win,
        input: field_name}
    );
    return false;
}
