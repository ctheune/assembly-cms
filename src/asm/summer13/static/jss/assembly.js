// On document ready.
$(function documentReady() {
    initStreamOverlay();
    initNewsRotation();
    initCountDown();
    initTwitter();
});

function initNewsRotation() {
    var tabItems = $('.tabs a').click(function () { clearTimeout(doRotateTabs); });
    if (tabItems.length) {
        // Create the tabs and return the api.
        var tabs = $('div.tabs').tabs('.newsitem', {api: true, current: 'active'});
        var doRotateTabs = setInterval(function rotateTabs() {
            if (tabs.getIndex() == tabItems.length - 1) {
                tabs.click(0); // Last tab, restart on first tab.
            } else {
                tabs.next();
            }
        }, 20000);
    }
}

function initStreamOverlay() {
   // If the function argument is given to overlay,
   // it is assumed to be the onBeforeLoad event listener.
   $('a[rel="#overlay"]').overlay({
      mask: 'black',
      effect: 'apple',
      onBeforeLoad: function wrapOverlay() {

         // grab wrapper element inside content
         var wrap = this.getOverlay().find(".wrap");

         // load the page specified in the trigger
         wrap.load(this.getTrigger().attr("href"));
      }
   });
}

function initCountDown() {
    function countDownTick() {
        $('#clockWrapper').load('@@countdown');
    }
    setInterval(countDownTick, 60000);
}

function initTwitter() {
    // Load Twitter Follow button.
    $.getScript('//platform.twitter.com/widgets.js');

    // Load latest tweets ticker.
    $.getScript("//widgets.twimg.com/j/2/widget.js", function tweetScriptLoaded() {
      if ($('#twitter-latest-tweets').length > 0) 
        new TWTR.Widget({
            id: "twitter-latest-tweets",
            version: 2,
            type: 'search',
            search: '@assemblyparty OR #asms12',
            interval: 4000,
            title: "Assembly related tweets for <a href='http://twitter.com/#!/search/%23asms12+OR"
                 + "+@assemblyparty'>#asms12 and @assemblyparty</a>",
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

      if ($('#twitter-latest-tweets-asmtv').length > 0) 
        new TWTR.Widget({
            id: "twitter-latest-tweets-asmtv",
            version: 2,
            type: 'search',
            search: '@assemblytv',
            interval: 4000,
            title: "Assembly related tweets for <a href='http://twitter.com/#!/search/"
                 + "@assemblytv'>@assemblytv</a>",
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
}
