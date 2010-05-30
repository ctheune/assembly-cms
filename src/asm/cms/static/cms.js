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
  window.root = $('link[rel="root"]').attr('href');

  $("#navigation-tree").tree({
    ui: { theme_name: 'classic' },
    types: {
      htmlpage: { clickable: true, icon:  { image: root+'/@@/asm.cms/icons/page_white.png'}},
      homepage: { icon:  { image: root+'/@@/asm.cms/icons/house.png'}},
      news: { icon:  { image: root+'/@@/asm.cms/icons/newspaper.png'}},
      sponsorsarea: { icon:  { image: root+'/@@/asm.cms/icons/page_white_medal.png'}},
      asset: { icon:  { image: root+'/@@/asm.cms/icons/page_white_picture.png'}}},
    data: { type: 'xml_nested',
            opts: {url: $('#navigation-tree').attr('href')}},
    callback: { onload: function(tree) {
                    $("#navigation-tree li").each(function() {
                        if ($('a', this).attr('href')+'/@@edit' == window.location) {
                            tree.toggle_branch($(this));
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

    $('.expandable .opener').click(toggle_extended_options);

    $('.url-action').click(trigger_url_action);
    $('#add-page').click(add_page);

    $('#delete-page').click(delete_page);

    $('.expandable .error').each(expand_section);
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

function expand_section() {
    $(this).parents('.section').each(function() {
        $(this).find('.expand').slideDown();
        $(this).find('.open').show();
        $(this).find('.closed').hide();
    });
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
    $(this).parents('.expandable').find('.expand').slideToggle();
    $(this).parent().find('.open').toggle();
    $(this).parent().find('.closed').toggle();
};

function clear_input() {
    $(this).val('');
};

function hide_navigation() {
    $("#navigation").hide();
    $("#navigation-actions").hide();
    $("#content").show();
    $("#actions").show();
    toggle_navigation = show_navigation;
    return false;
}

function show_navigation() {
    $("#navigation").show();
    $("#navigation-actions").show();
    $("#content").hide();
    $("#actions").hide();
    toggle_navigation = hide_navigation;
    return false;
}

toggle_navigation = show_navigation;

function show_preview() {
    w = window.open($('link[rel="root"]').attr('href')+'/@@preview-window');
    return false;
};
