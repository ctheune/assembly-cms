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
    types: {                                    // XXX the winter10 reference is *bad*
      htmlpage: { clickable: true, icon:  { image: '/winter10/@@/asm.cms/icons/page_white.png'}},
      homepage: { icon:  { image: '/winter10/@@/asm.cms/icons/house.png'}},
      news: { icon:  { image: '/winter10/@@/asm.cms/icons/newspaper.png'}},
      sponsorsarea: { icon:  { image: '/winter10/@@/asm.cms/icons/page_white_medal.png'}},
      asset: { icon:  { image: '/winter10/@@/asm.cms/icons/page_white_picture.png'}}},
    data: { type: 'xml_nested',
            opts: {url: $('#navigation-tree').attr('href')}},
    callback: { onload: function(tree) {
                    $("#navigation-tree li").each(function() {
                        if ($('a', this).attr('href')+'/@@edit' == window.location) {
                            tree.select_branch($(this));
                        }});},
                ondblclk: function(node, tree) {
                    window.location = $('a', node).attr('href')+'/@@edit';
                },
                onmove: function(node, ref, type, tree, rb) {
                    $.post($('a', ref).attr('href')+'/../@@arrange',
                           {id: $(node).attr('id'),
                            type: type},
                            function() { tree.refresh(); });},
                },
    rules: {drag_copy: false,
            max_children: 1},
    });

    $('.expandable h3').click(toggle_extended_options);

    $('.url-action').click(trigger_url_action);
    $('#add-page').click(add_page);

    $('#delete-page').click(delete_page);
});


function delete_page() {
    var t = $.tree.reference('#navigation-tree');
    var target = $(t.selected.find('a')[0]);
    if (!confirm('Delete page "' + target.text() +'"?')) {
        return false;
    }
    $.post(target.attr('href') + '/../@@delete', {}, 
            function (data) { window.location = data; });
    return false;
}

function add_page() {
    var t = $.tree.reference('#navigation-tree');
    var add_page_url = t.selected.find('a').attr('href') + '/../@@addpage';
    $.post(add_page_url, $(this).parent().serialize(),
           function(data) { window.location = data; });
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
