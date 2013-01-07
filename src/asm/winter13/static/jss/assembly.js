// Gallery Navigation
// jquery.hotkeys module must be loaded before this file.
var galleryLinkEventsEnabled = false;

function galleryLinkNext(event) {
  if (!galleryLinkEventsEnabled) {
    return;
  }
  var address = $('#gallery-link-next').attr('href');
  if (address != null) {
    window.location = address;
    event.preventDefault();
  }
}

function galleryLinkPrevious(event) {
  if (!galleryLinkEventsEnabled) {
    return;
  }
  var address = $('#gallery-link-previous').attr('href');
  if (address != null) {
    window.location = address;
    event.preventDefault();
  }
}

function enableGalleryLinkEvents() {
  if (galleryLinkEventsEnabled === true) {
    return;
  }
  galleryLinkEventsEnabled = true;
  $(document).bind('keydown', {combi: 'right', disableInInput: true}, galleryLinkNext);
  $(document).bind('keydown', {combi: 'left' , disableInInput: true}, galleryLinkPrevious);
}

function disableGalleryLinkEvents() {
  if (galleryLinkEventsEnabled === false) {
    return;
  }
  galleryLinkEventsEnabled = false;
  $(document).unbind('keydown', {combi: 'right', disableInInput: true}, galleryLinkNext);
  $(document).unbind('keydown', {combi: 'left' , disableInInput: true}, galleryLinkPrevious);
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
    break;
  case YOUTUBE_BUFFERING:
    disableGalleryLinkEvents();
    break;
  case YOUTUBE_ENDED:
    enableGalleryLinkEvents();
    break;
  }
}

function onYouTubePlayerReady(playerId) {
  var ytplayer = document.getElementById(playerId);
  ytplayer.addEventListener("onStateChange", "galleryHandleYoutubeEvents");
}

// $(document).ready() shortcut:
$(function() {
  // Assembly Countdown!
  setInterval(function countDownTick() {
    $('#clock').load($('link[rel="site"]').attr('href') + '/@@countdown');
  }, 60000);

  // Rotate News
  var rotateDelay = 20000; // ms
  // Clicking a tab should cancel the rotate
  var tabItems = $('.tabs a').click(function () {
    clearTimeout(doRotateTabs);
  });
  if (tabItems.length > 0) {
    // Create the tabs and return the api
    var tabs = $('div.tabs').tabs('.newsitem', {api: true, current: 'active'});
    var doRotateTabs = setInterval(function () {
      if (tabs.getIndex() === tabItems.length - 1) {
        // Last tab, restart on first tab
        tabs.click(0);
      } else {
        tabs.next();
      }
    }, rotateDelay);
  }
  // Overlay Init for livestream
  // if the function argument is given to overlay,
  // it is assumed to be the onBeforeLoad event listener
  $("#livestream").overlay({
    mask: 'black',
    effect: 'apple',
    onBeforeLoad: function() {
      // grab wrapper element inside content
      var wrap = this.getOverlay().find(".wrap");
      // load the page specified in the trigger
      wrap.load(this.getTrigger().attr("href"));
    }
  });

  // Hotkey init
  enableGalleryLinkEvents();
});

// Twitter Follow button.
(function() {
    $.getScript('//platform.twitter.com/widgets.js');
})();

// Twitter latest tweets.
(function() {
    $.getScript("http://widgets.twimg.com/j/2/widget.js", function() {
        if (document.getElementById("twitter-latest-tweets") == undefined) {
            return;
        }
        new TWTR.Widget({
            id: "twitter-latest-tweets",
            version: 2,
            type: 'search',
            search: '@assemblyparty OR #asm',
            interval: 4000,
            title: "Assembly related tweets for #asm and @assemblyparty",
            width: 560,
            height: 115,
            theme: {
                shell: {
                    background: '#f5f5f5',
                    color: '#000000'
                },
                tweets: {
                    background: '#ffffff',
                    color: '#000000',
                    links: '#2D778E'
                }
            },
            features: {
                scrollbar: false,
                loop: true,
                live: true,
                behavior: 'default'
            }
        }).render().start();
    });
})();
