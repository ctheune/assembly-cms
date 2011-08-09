$(function() {
    $(':input[placeholder]').placeholder();
    $('.link-button').each(function() {
        $(this).attr('src', $(this).data('src'));
    });
});
