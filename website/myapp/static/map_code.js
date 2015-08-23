

function draw_map(world, names) {

    d3.select("svg.map").remove()

    world = IMPORTAPP.worlddata
    names = IMPORTAPP.countrydata

    var margin = {
            top: 0,
            right: 0,
            bottom: 0,
            left: 0
        },
        width = 1000 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var svg = d3.select("#mapcontainer").append("svg")
        .attr("class", "map")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("viewBox", "0 0 " + width + " " + height)
        .attr("preserveAspectRatio", "xMinYMin")
        .append("g")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var countries = topojson.feature(world, world.objects.countries).features;

    countries = countries.filter(function(d) {
        return names.some(function(n) {
            if (d.id == n.id) return d.name = n.name;
        });
    }).sort(function(a, b) {
        return a.name.localeCompare(b.name);
    });

    var projection = d3.geo.mercator()
        .scale(IMPORTAPP.map_scale)
        .translate(IMPORTAPP.map_translate(width,height));

    var path = d3.geo.path()
        .projection(projection);

    svg.append("path")


    var shapes = svg.selectAll(".countrypath")
        .data(countries)


    var tooltip = d3.select(".tooltip")

    shapes.enter().append("path")
        .attr("class", function(d) {
            return "subunit " + d.id;
        })
        .attr("class", function(d) {
            return "countrypath";
        })
        .attr("d", path)
        .attr("id", function(d, i) {
            return d.id;
        })
        .attr("name", function(d, i) {
            return d.properties.name;
        })

    var shapes = svg.selectAll(".countrypath")
        .data(countries)

    shapes
        .on("mousemove", function(d) {

            alpha_2 = IMPORTAPP.country_numericid_lookup[d["id"]]["alpha_2"]
            d["alpha_2"] = alpha_2
       

            tooltip.transition()
                .duration(200)
                .style("opacity", function() {
                    return 0.9
                });


            tooltip
                .html(function() {
                    return map_tooltip_html(d)
                })
                .style("left", (d3.event.pageX + 15) + "px")
                .style("top", (d3.event.pageY - 60) + "px");
        
    })
        .on("mouseout", function(d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

}



function map_colours() {

    get_consignments_by_country()

    var world = IMPORTAPP.worlddata
    var names = IMPORTAPP.countrydata
    var svg = d3.select("#mapcontainer svg")

    var countries = topojson.feature(world, world.objects.countries).features;


    countries = countries.filter(function(d) {
        return names.some(function(n) {

            if (d.id == n.id) return d.name = n.name;
        });
    }).sort(function(a, b) {
        return a.name.localeCompare(b.name);
    });

    var shapes = svg.selectAll(".countrypath")
        .data(countries)


    shapes
        .attr('fill', function(d, i) {

            alpha_2 = IMPORTAPP.country_numericid_lookup[d["id"]]["alpha_2"]

            if (alpha_2 in IMPORTAPP.country_totals) {
                total = IMPORTAPP.country_totals[alpha_2]["proportion_of_max"]
            } else {
                total = 0
            }
            return map_colour_scale(total)
        })



}




function draw_map_key() {

    var num_steps = 50

    var map_colour_scale = d3.scale.log().domain([1, 1000]).range(["black", "#00CE0F"]);

    var max_key = 300
    var axis_scale = d3.scale.log().domain([1, 1000]).range([max_key, 0])

    var inverted_scale = axis_scale.invert

    svg = d3.select("#mapcontainer svg")    

    svg.append("g")
        .attr("transform", "translate(20,170)")
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 80)
        .attr("height", max_key + 70)
        .attr("fill", "white")


    steps = _.map(d3.range(num_steps), function(i) {
        return i * max_key / num_steps
    })

    svg = d3.select("#mapcontainer svg")

    svg.append("g")
        .attr("transform", "translate(70,170)")
        .selectAll(".keyrects")
        .data(steps)
        .enter()
        .append("rect")
        .attr("x", 0)
        .attr("y", function(d) {
            return d
        })
        .attr("width", 10)
        .attr("height", (max_key / num_steps) * 1.06)
        .attr("fill", function(d) {
            return map_colour_scale(inverted_scale(d))
        })

    var yAxis = d3.svg.axis()
        .scale(axis_scale)
        .orient("left")
        .ticks(10, ",0.2s")
        .tickSize(-10, 0)


    var svg = d3.select("#mapcontainer svg")

    svg.append("g")
        .attr("transform", "translate(70,170)")
        .attr("class", "y axis")
        .call(yAxis)

    svg.append("g")
        .attr("transform", "translate(90,170) rotate(90)")
        .append("text")
        .text("Value of imports (£)")
        .style("font-weight", "bold")
        .style("font-size", "12px")

    svg.append("g").attr("transform", "translate(27,160)")
        .append("text")
        .text("Key:")
        .style("font-weight", "bold")
        .style("font-size", "12px")
}



function key_colours() {

    //update numbers
    var my_max = _.max(IMPORTAPP.country_totals, function(d) {
        return d["quantity_exports"]
    })
    my_max = my_max["quantity_exports"]

    var axis_scale = d3.scale.log().domain([1000, my_max]).range([300, 0])

    var yAxis = d3.svg.axis()
        .scale(axis_scale)
        .orient("left")
        .ticks(10, ",0.2s")
        .tickSize(-10, 0)

    d3.selectAll(".y.axis")
        .transition()
        .duration(2000)
        .call(yAxis)
}

function map_colour_scale(this_value) {

    min_coloured = 0.01
    var map_colour_scale = d3.scale.log().domain([min_coloured, 1]).range(["black", "#00CE0F"]);

    if (this_value == 0) {
        return "#E7E5E5"
    } else if (this_value < min_coloured) {
        return "black"
    } else {
        return map_colour_scale(this_value)
    }
}

