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
            // Grab wrapper element inside content.
            var wrap = this.getOverlay().find(".wrap");
            // Load the page specified in the trigger.
            wrap.load(this.getTrigger().attr("href"), initAssemblyTVSchedule);
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
            search: '@assemblyparty OR #asmparty',
            interval: 4000,
            title: "Assembly related tweets for <a href='http://twitter.com/#!/search/%23asmparty+OR"
                 + "+@assemblyparty'>#asmparty and @assemblyparty</a>",
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

function initAssemblyTVSchedule() {
    function pad(n, width, z) {
        z = z || '0';
        n = n + '';
        return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
    }

    var comingUp, updateDelay;
    // Create container element.
    if (!$('.coming-up').length) {
        comingUp = $('<ul>');
        var link = $('<a>').text('AssemblyTV')
            .attr('href', 'activities/assemblytv/schedule').attr('target', '_blank');
        $('<div>').attr('class', 'coming-up').appendTo('.overlay > .wrap')
            .append($('<h3>').append(link))
            .append('<span class="now"></span>')
            .append(comingUp);
    } else {
        comingUp = $('.coming-up ul').empty();
    }

    $.getJSON('activities/assemblytv/schedule/json', function (data, status) {
        if (!data || !data.events || !data.events.length) {
            console.log('Failed to retrieve schedule!', status, data);
            $('.coming-up').remove();
            return;
        }

        // Filter past events and grab current + 2 next events.
        var events = data.events.filter(function eventFilter(item, i) {
            return (new Date(item.time)).getTime() > Date.now() ||
                (new Date(item.end_time)).getTime() > Date.now();
        }).splice(0, 3);

        // The first event has not started yet, so we only show two next shows.
        if (new Date(events[0].time).getTime() > Date.now()) {
            events = events.splice(0, 2);
            updateDelay = new Date(events[0].time).getTime() - Date.now() + 5000;
        } else {
            updateDelay = new Date(events[1].time).getTime() - Date.now() + 5000;
        }

        events.forEach(function eventIterator(event, i) {
            var d = new Date(event.time),
                time = pad(d.getHours(), 2) + ':' + pad(d.getMinutes(), 2);
            // Append to HTML.
            if (!i && d.getTime() < Date.now()) {
                $('.coming-up .now').text(': ' + event.name);
            } else {
                $('<li>').text(time + ' – ' + event.name).appendTo(comingUp);
            }
        });

        setTimeout(initAssemblyTVSchedule, updateDelay);
    });
}