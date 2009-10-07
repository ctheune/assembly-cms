$(document).ready(function(){

  // Showing/hiding navigation screen
  $(document).keydown(function(e) {
        if (e.which == 27) {
            toggle_navigation();
        }});

  $("#menu-navigation-handle").click(show_navigation);
  $("#navigation-wrapper .menu-head").click(hide_navigation);

  // Folder sorting
  $("#sortable").sortable({update: update_order});
});


function update_order(event, ui) {
    //alert($("#subpages").attr('action'));
    //alert($("#subpages").elements);
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
