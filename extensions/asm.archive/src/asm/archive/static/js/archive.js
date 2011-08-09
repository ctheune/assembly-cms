function supports_html5_storage() {
  try {
    return 'localStorage' in window && window['localStorage'] !== null;
  } catch (e) {
    return false;
  }
}
function onYouTubePlayerAPIReady() {
    var storage = window.localStorage;
    var playbackQuality = storage.getItem("youtube-playback-quality");
    var player = document.getElementById('ytplayerembed');
    if (playbackQuality != null) {
        player.setPlaybackQuality(playbackQuality);
    }
    /* Remember user's playback quality selection. */
    player.addEventListener(function(quality) {
        storage.setItem("youtube-playback-quality", quality);
    }, "onPlaybackQualityChange");
}

$(function() {
    $(':input[placeholder]').placeholder();
    $('.link-button').each(function() {
        $(this).attr('src', $(this).data('src'));
    });
});
