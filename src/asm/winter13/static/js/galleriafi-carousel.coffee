addImage = (image) ->
        image_root = "http://assembly.galleria.fi#{escape image}"
        $("<div class='item carousel-image'>" +
          "<a href='#{image_root}'>" +
          "<img class='carousel-image' src='#{image_root}?img=smaller' alt='#{escape image}'/>" +
          "</a>" +
          "</div>").appendTo $("#galleriafiCarousel .carousel-inner")

$(document).ready ->
        $.getJSON "#{document.baseURI}/wasm-13-galleriafi.json", (data) ->
                images = _.shuffle _.keys data
                index = 3
                console.log images.length
                for image in images[0...index]
                        addImage image
                $("#galleriafiCarousel").carousel {interval: 3000}
                $("#galleriafiCarousel").on "slid", ->
                        if index < images.length
                                addImage images[index]
                                index += 1
