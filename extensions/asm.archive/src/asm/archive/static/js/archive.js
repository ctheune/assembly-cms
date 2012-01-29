$(function() {
    // This should show placeholders in IE.
    $(':input[placeholder]').placeholder();
    var screen_width = (window.innerWidth > 0) ? window.innerWidth : screen.width;

    // Load like buttons only on the desktop version:
    // Loading these buttons causes really long loading indicator display
    // and hides all navigation buttons (at least on Android 2.3 browser with
    // slow network connection).
    if (screen_width > 680) {
        // Load Facebook and Twitter buttons.
        $('.link-button').each(function() {
            $(this).attr('src', $(this).data('src'));
        });
        // Google +1 button.
        var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
        po.src = 'https://apis.google.com/js/plusone.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
    }
});
