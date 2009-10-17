$(document).ready(function(){

  // Showing/hiding navigation screen
  $(document).keydown(function(e) {
        if (e.which == 27) {
            toggle_navigation();
        }});

  $("#menu-navigation-handle").click(show_navigation);
  $("#navigation-wrapper .menu-head").click(hide_navigation);

  $(".visit-site").click(show_preview);

  // Folder sorting
  $("#sortable").sortable({update: update_order});

  window.preview_location = $('link[rel="preview"]').attr('href');
  console.log('preview location', window.preview_location);

});

function update_order(event, ui) {
    var params = jQuery.param($("#subpages input"));
    jQuery.get($("#subpages").attr('action'), params, null, 'json');
}

function hide_navigation() {
    $("#navigation-wrapper").hide();
    $("body").css('overflow', 'scroll');
    toggle_navigation = show_navigation;
}

function show_navigation() {
    $("#navigation-wrapper").show();
    $("body").css('overflow', 'hidden');
    toggle_navigation = hide_navigation;
}

toggle_navigation = show_navigation;

function show_preview() {
    w = window.open($('link[rel="root"]').attr('href')+'/@@preview-window');
    return false;
};
