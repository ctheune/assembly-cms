var KEY_ESCAPE = 27;

$(document).ready(function(){
    // Showing/hiding navigation screen
    $(document).keydown(function(e) {
        if (e.which == KEY_ESCAPE) {
            toggle_navigation();
        }});

    $(".toggle-navigation").click(function() {toggle_navigation();});

    $("input.clear-first-focus").one('click', clear_input);

    $(".open-preview").click(show_preview);
    window.preview_location = $('link[rel="preview"]').attr('href');
    window.root = $('link[rel="root"]').attr('href');

    $("#navigation-tree").bind("loaded.jstree", function(event, data) {
        // Show currently open page and its sub pages in navigation tree.
        var tree = data.inst;
        var opened_page_id = $('link[rel="pageid"]').attr('href');
        var node = tree._get_node("#" + opened_page_id)[0];

        tree.open_node(node);
        tree.select_node(node);
        // We don't know why we have to call save_selected here, but if we
        // don't then the selection disappears again. :/
        tree.save_selected();
    }).bind("dblclick.jstree", function(event) {
        var node = event.target;
        // This check is here as if we double click iconed items, we'll get a
        // target that points to the actual icon. It does not have have any
        // URL information, but the parent node that holds the icon has.
        if (node.href == undefined) {
            node = node.parentNode;
        }
        if (node.href != undefined) {
            window.location = node.href + '/@@edit';
        }
    }).bind("move_node.jstree", function(event, data) {
        var tree = data.inst;
        var type = data.rslt.p;
        var moved_node = data.rslt.o;
        var target_node = data.rslt.r;

        $.post($('a', target_node).attr('href')+'/../@@arrange',
               {id: $(moved_node).attr('id'),
                type: type},
               function() { tree.refresh(); }
              );
    }).jstree({
        plugins: [ "themes", "xml_data", "ui", "types", "dnd"],
        xml_data: {
            ajax: {
                url: $('#navigation-tree a').attr('href'),
                data: function(node) {
                    if (node.attr) {
                        return {parent_id: node.attr("id")};
                    }
                    // We are opening navigation for the first time on current
                    // page => there is no parent as we want to get the root
                    // of the navigation tree. We also want to get all the
                    // branches from current page to the root.
                    return {page_id: $('link[rel="pageid"]').attr('href')};
                }
            }
        },
        core: { animation: 0 },
        ui: {
            theme_name: 'classic'
        },
        types: {
            types: {
                htmlpage: { icon:  { image: root+'/@@/asm.cmsui/icons/page_white.png'}},
                homepage: { icon:  { image: root+'/@@/asm.cmsui/icons/house.png'}},
                news: { icon:  { image: root+'/@@/asm.cmsui/icons/newspaper.png'}},
                sponsorsarea: { icon:  { image: root+'/@@/asm.cmsui/icons/page_white_medal.png'}},
                asset: { icon:  { image: root+'/@@/asm.cmsui/icons/page_white_picture.png'}}
            },
        },
    });

    $('.expandable .opener').click(toggle_extended_options);

    $('.url-action').click(trigger_url_action);
    $('form[id="addpage"]').submit(add_page);

    $('#delete-page').click(delete_page);

    $('.expandable .error').each(expand_section);
});

function delete_page() {
    var t = $.jstree._reference('#navigation-tree');
    var target = t.get_selected();
    // TODO if branch is closed, then deletion does not show its children.
    // but if it's open, then chidren's names are show in target.text().
    if (!confirm('Delete page "' + $.trim(target.text()) +'"?')) {
        return false;
    }
    $.post(target.find("a").attr("href") + '/../@@delete', {},
            function (data) { window.location = data; });
    return false;
}

function expand_section() {
    $(this).parents('.section').each(function() {
        $(this).find('.expand').slideDown();
        $(this).find('.open').show();
        $(this).find('.closed').hide();
    });
}

function add_page() {
    var title = $(this).find("input[name=title]");
    if ($.trim(title.attr('value')).length == 0) {
        // XXX For some reason title.addClass() does not work.
        title.css("background-color", "#FBE3E4");
        title.css("color", "#8a1f11");
        title.css("border-color", "#FBC2C4");
        return false;
    }
    var t = $.jstree._reference('#navigation-tree');
    var add_page_url = t.get_selected().find("a").attr("href") + '/../@@addpage';

    $(this).ajaxError(
        function() {
            // XXX For some reason title.addClass() does not work.
            title.css("background-color", "#FBE3E4");
            title.css("color", "#8a1f11");
            title.css("border-color", "#FBC2C4");
        });

    $.post(add_page_url, $(this).serialize(),
           function(data) { window.location = data; });
    return false;
}

function trigger_url_action() {
    window.location = $(this).attr('href');
}

function toggle_extended_options() {
    $(this).parents('.expandable').find('.expand').slideToggle();
    $(this).parent().find('.open').toggle();
    $(this).parent().find('.closed').toggle();
};

function clear_input() {
    $(this).val('');
};

function hide_navigation() {
    $("#navigation").hide();
    $("#navigation-actions").hide();
    $("#content").show();
    $("#actions").show();
    toggle_navigation = show_navigation;
    return false;
}

function show_navigation() {
    $("#navigation").show();
    $("#navigation-actions").show();
    $("#content").hide();
    $("#actions").hide();
    toggle_navigation = hide_navigation;
    return false;
}

toggle_navigation = show_navigation;

function show_preview() {
    w = window.open($('link[rel="root"]').attr('href')+'/@@preview-window');
    return false;
};
