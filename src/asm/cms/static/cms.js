$(document).ready(function(){
  // Showing/hiding navigation screen
  $(document).keydown(function(e) {
        if (e.which == 27) {
            toggle_navigation();
        }});

  $("#menu-navigation-handle").click(function() {toggle_navigation(); return false;});
  $("#toggle-extended-menu").click(function() {
    $('#global-navigation2').toggle();
     return false;});

  $("#navigation-tree a").click(show_subpages);
  $("#search input").one('click', init_search);

  // Folder sorting
  $("#sortable").sortable({update: update_order});

  $("#preview-handle").click(show_preview);
  window.preview_location = $('link[rel="preview"]').attr('href');

  $("#navigation-tree").tree({
    ui: { theme_name: 'classic' },
    types: {
     htmlpage: { icon:  { image: '/winter10/@@/asm.cms/icons/page_white.png'}},
     homepage: { icon:  { image: '/winter10/@@/asm.cms/icons/house.png'}},
     news: { icon:  { image: '/winter10/@@/asm.cms/icons/newspaper.png'}},
     asset: { icon:  { image: '/winter10/@@/asm.cms/icons/page_white_picture.png'}}},
    data: { type: 'xml_nested',
            opts: {url: $('#navigation-tree').attr('href')}},
    callback: { onselect: function(node, tree) { if (!tree.initialized) { return; }
                                                 window.location = $('a', node).attr('href'); },
                onload: function() { 
                    var tree = $.tree.reference('#navigation-tree');
                    $("#navigation-tree li").each(function() {
                        if ($('a', this).attr('href') == window.location) {
                            tree.select_branch($(this));
                        }});
                    tree.initialized = true; }},
    });

  $('.toggle-additional-widgets').click(function() {
        $('.additional-widgets').slideToggle();
        return false; });
});

function init_search() {
    $(this).val('');
};

function update_order(event, ui) {
    var params = jQuery.param($("#subpages input"));
    jQuery.get($("#subpages").attr('action'), params, null, 'json');
}

function hide_navigation() {
    $("#navigation").hide();
    $("#content").show()
    toggle_navigation = show_navigation;
    return false;
}

function show_navigation() {
    $("#navigation").show();
    $("#content").hide()
    toggle_navigation = hide_navigation;
    return false;
}

toggle_navigation = show_navigation;

function show_preview() {
    w = window.open($('link[rel="root"]').attr('href')+'/@@preview-window');
    return false;
};

function show_subpages(e) {
    if ($(this).hasClass('selected')) {
        window.location = $(this).attr('href');
    };
    $.get($(this).attr('href')+'/@@navdetails',
          function(data) {
              $('#navigation-details').html(data); 
          });
    $('#navigation-tree .selected').removeClass('selected');
    $(this).addClass('selected');
    return false;
};
