$(document).ready(function(){
  // Showing/hiding navigation screen
  $(document).keydown(function(e) {
        if (e.which == 27) {
            toggle_navigation();
        }});

  $(".toggle-navigation").click(function() {toggle_navigation();});

  $("input.clear-first-focus").one('click', clear_input);

  $(".open-preview").click(show_preview);
  window.preview_location = $('link[rel="preview"]').attr('href');

  $("#navigation-tree").tree({
    ui: { theme_name: 'classic' },
    types: {
      htmlpage: { clickable: true, icon:  { image: '/winter10/@@/asm.cms/icons/page_white.png'}},
      homepage: { icon:  { image: '/winter10/@@/asm.cms/icons/house.png'}},
      news: { icon:  { image: '/winter10/@@/asm.cms/icons/newspaper.png'}},
      asset: { icon:  { image: '/winter10/@@/asm.cms/icons/page_white_picture.png'}}},
    data: { type: 'xml_nested',
            opts: {url: $('#navigation-tree').attr('href')}},
    callback: { onload: function() {
                    var tree = $.tree.reference('#navigation-tree');
                    $("#navigation-tree li").each(function() {
                        if ($('a', this).attr('href')+'/@@edit' == window.location) {
                            tree.select_branch($(this));
                        }});
                    tree.initialized = true; },
    });

    $('.expandable h3').click(toggle_extended_options);

    $('.url-action').click(trigger_url_action);
    $('#add-page').click(add_page);
});


function add_page() {
    var t = $.tree.reference('#navigation-tree');
    var add_page_url = t.selected.find('a').attr('href') + '/../@@addpage';
    $.post(add_page_url, $(this).parent().serialize(),
           function(data) { t.open_branch(t.selected); t.refresh(); });
    return false;
}

function trigger_url_action() {
    window.location = $(this).attr('href');
}

function toggle_extended_options() {
    $(this).parent().find('.expand').slideToggle();
    $(this).parent().find('.open').toggle();
    $(this).parent().find('.closed').toggle();
};

function clear_input() {
    $(this).val('');
};

function hide_navigation() {
    $("#navigation").hide();
    $("#navigation-actions").hide()
    $("#content").show()
    $("#actions").show()
    toggle_navigation = show_navigation;
    return false;
}

function show_navigation() {
    $("#navigation").show();
    $("#navigation-actions").show()
    $("#content").hide()
    $("#actions").hide()
    toggle_navigation = hide_navigation;
    return false;
}

toggle_navigation = show_navigation;

function show_preview() {
    w = window.open($('link[rel="root"]').attr('href')+'/@@preview-window');
    return false;
};
