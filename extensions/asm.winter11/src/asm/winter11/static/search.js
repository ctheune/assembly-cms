function asmcms_search_normalize_name(name)
{
    var normalized = name.toLowerCase();
    normalized = normalized.replace(/[^a-z0-9]/, "-");
    normalized = normalized.replace(/-+/, "-");
    normalized = normalized.replace(/^-/, "");
    normalized = normalized.replace(/-$/, "");
    return normalized;
}

function asmcms_search_site_name_to_anchor(name)
{
    return "search-site-" + asmcms_search_normalize_name(name);
}

$(document).ready(function() {
    var out = "<div>Results from: ";
    $("#search-results").append();
    $("#search-sites a").each(function(site_index, site) {
        var site_name = $(site).text();
        out += "<span class='search-site-name'><a href='#" +
            asmcms_search_site_name_to_anchor(site_name) + "'>" + site_name + "</a></span> ";
    });
    out += "</div>";
    $("#search-results dl").prepend(out);

    $("#search-sites a").each(function(site_index, site) {
        $.getJSON(
            $(site).attr("href") + "?" + $("#searchform").serialize(),
            function(search_results) {
                // console.log(search_results);
                var site_name = $(site).text();
                var site_anchor = asmcms_search_site_name_to_anchor(site_name);
                $("#search-results dl").append(
                    "<h3><a href='#" + site_anchor + "' name='" + site_anchor + "'>" +
                        site_name + "</a></h3>");
                $(search_results).each(function(index, element) {
                    $("#search-results dl").append(
                        "<dt><a href='" + element['url'] + "'>" + element["title"] + "</a></dt>\n" +
                            "<dd><div class='preview'>" + element["content"] + "</div></dd>"
                    );
                });
            });
    });
});
