$(document).ready(function(){
  $("#menu-navigation-handle").click(function () {
    $("#navigation-wrapper").show();
  });
  $("#navigation-wrapper .menu-head").click(function () {
    $("#navigation-wrapper").hide();
  });
  $("#sortable").sortable(
      {update: function(event, ui) { alert('asdf');}}
      );
});
