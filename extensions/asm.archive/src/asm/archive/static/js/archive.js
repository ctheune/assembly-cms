$(function() {
    // This should show placeholders in IE.
    $(':input[placeholder]').placeholder();
    // Load Facebook and Twitter buttons.
    $('.link-button').each(function() {
        $(this).attr('src', $(this).data('src'));
    });

    // Google +1 button.
    var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
    po.src = 'https://apis.google.com/js/plusone.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
});
