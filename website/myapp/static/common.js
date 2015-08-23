var IMPORTAPP = {
    
}

var port_colours = d3.scale.ordinal()
    .range(["#1f77b4",
        "#aec7e8",
        "#ff7f0e",
        "#ffbb78",
        "#d62728",
        "#ff9896",
        "#9467bd",
        "#c5b0d5",
        "#8c564b",
        "#c49c94",
        "#e377c2",
        "#f7b6d2",
        "#7f7f7f",
        "#c7c7c7",
        "#bcbd22",
        "#dbdb8d",
        "#17becf",
        "#9edae5"
    ]);








function map_tooltip_html(d) {

    var formatNumber = d3.format(",.0f"),
        format = function(d) {
            return "£" + formatNumber(d);
        }

    this_country = d["name"]
    var source = d3.select("#map-tooltip-template").html();

    var template = Handlebars.compile(source)

     if (d["alpha_2"] in IMPORTAPP.country_totals) {
    var quantity_exports = IMPORTAPP.country_totals[d["alpha_2"]]["quantity_exports"]
    quantity_exports = format(quantity_exports)
}
    else {quantity_exports="None"}

    var html = template({
        quantity_exports: quantity_exports,
        this_country: this_country
    })

    return html
}   