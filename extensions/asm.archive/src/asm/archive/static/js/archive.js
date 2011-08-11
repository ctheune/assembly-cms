(function() {
    // This should show placeholders in IE.
    $(':input[placeholder]').placeholder();
    // Load Facebook and Twitter buttons.
    $('.link-button').each(function() {
        $(this).attr('src', $(this).data('src'));
    });
})();
