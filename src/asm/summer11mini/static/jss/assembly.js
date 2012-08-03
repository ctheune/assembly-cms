// Rotate News 
$(function() { 
    var rotateDelay = 20000; //milliseconds 
    var rotateTabs=true;     
    var $tabItems = $('.tabs a').click(function(){ //clicking a tab should cancel the rotate 
        rotateTabs=false; 
    }); 
    var tabs = $("div.tabs").tabs('.newsitem', {api:true, current: 'active'}); //create the tabs and return the api 
    function doRotateTabs(){ //recursive function 
        if (rotateTabs) { 
            setTimeout(function(){ 
                if (!rotateTabs) return; 
                if(tabs.getIndex() == $tabItems.length-1){ //last tab. restart on first tab 
                    tabs.click(0); 
                } 
                else { 
                    tabs.next(); 
                } 
                doRotateTabs(); 
            }, rotateDelay); 
        } 
    } 
    doRotateTabs(); 
}); 
// Count-down
var target;
function startClock() {
    target = document.getElementById('clock').getAttribute('alt');
    setTimeout('updateClock()',3000);
}

function updateClock() {
  var now = new Date();
  var diff = Math.floor((target-now)/1000);
  if (diff < 0) { diff=0; }
  document.getElementById('clock_days').innerHTML=Math.floor(diff/86400);
  diff = diff % 86400;
  document.getElementById('clock_hours').innerHTML=Math.floor(diff/3600);
  diff = diff % 3600;
  document.getElementById('clock_minutes').innerHTML=Math.floor(diff/60);
  if (diff > 0) { setTimeout('updateClock()', 60000); }
}

// jquery.hotkeys module must be loaded before this file.
var galleryLinkEventsEnabled = false;

function galleryLinkNext(event) {
    if (!galleryLinkEventsEnabled) {
        return;
    }
    var newLocation = $('#gallery-link-next');
    var address = newLocation.attr('href');
    if (address != null) {
        window.location = address;
        event.preventDefault();
    }
}

function galleryLinkPrevious(event) {
    if (!galleryLinkEventsEnabled) {
        return;
    }
    var newLocation = $('#gallery-link-previous');
    var address = newLocation.attr('href');
    if (address != null) {
        window.location = address;
        event.preventDefault();
    }
}

function enableGalleryLinkEvents() {
    if (galleryLinkEventsEnabled == true) {
        return;
    }
    galleryLinkEventsEnabled = true;
    $(document).bind('keydown', {combi: 'right', disableInInput: true}, galleryLinkNext);
    $(document).bind('keydown', {combi: 'left', disableInInput: true}, galleryLinkPrevious);
}

enableGalleryLinkEvents();

function disableGalleryLinkEvents() {
    if (galleryLinkEventsEnabled == false) {
        return;
    }
    galleryLinkEventsEnabled = false;
    $(document).unbind('keydown', {combi: 'right', disableInInput: true}, galleryLinkNext);
    $(document).unbind('keydown', {combi: 'left', disableInInput: true}, galleryLinkPrevious);
}

var YOUTUBE_UNSTARTED = -1;
var YOUTUBE_ENDED = 0;
var YOUTUBE_PLAYING = 1;
var YOUTUBE_PAUSED = 2;
var YOUTUBE_BUFFERING = 3;
var YOUTUBE_VIDEO_CUED = 5;

function galleryHandleYoutubeEvents(state) {
    switch (state) {
    case YOUTUBE_PLAYING:
    case YOUTUBE_BUFFERING:
        disableGalleryLinkEvents();
        break;
    case YOUTUBE_ENDED:
        enableGalleryLinkEvents();
        break;
    default:
        // Do nothing.
    }
}

function onYouTubePlayerReady(playerId) {
    var ytplayer = document.getElementById(playerId);
    ytplayer.addEventListener("onStateChange", "galleryHandleYoutubeEvents");
}


$(document).ready(function(){

    $(function() {
     
       // if the function argument is given to overlay,
       // it is assumed to be the onBeforeLoad event listener
       $("a[rel]").overlay({
     
          mask: 'black',
          effect: 'apple',
     
          onBeforeLoad: function() {
     
             // grab wrapper element inside content
             var wrap = this.getOverlay().find(".wrap");
     
             // load the page specified in the trigger
             wrap.load(this.getTrigger().attr("href"));
          }
     
       });
    });
});
