$(document).ready(function(){
  $(document).keydown(function(e) {
        if (e.which == 27) {
            hide_navigation();
        }});

  $("#menu-navigation-handle").click(function () {
    $("#navigation-wrapper").show();
    $("body").css('overflow', 'hidden');
  });
  $("#navigation-wrapper .menu-head").click(hide_navigation);
  $("#sortable").sortable({update: update_order});
});


function update_order(event, ui) {
    //alert($("#subpages").attr('action'));
    //alert($("#subpages").elements);
}

function hide_navigation(){
    $("#navigation-wrapper").hide();
    $("body").css('overflow', 'scroll');
}
