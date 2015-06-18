
var IMPORTAPP = {csv_loaded:false}

function resize() {

    var chart = d3.select("svg.map")
    aspect = chart.attr("width") / chart.attr("height")
    var targetWidth = window.innerWidth - 50
    targetWidth = Math.min(1200, targetWidth)
    chart.attr("width", targetWidth);
    chart.attr("height", targetWidth / aspect);

    var chart = d3.select("svg.sankey")
    aspect = chart.attr("width") / chart.attr("height") * 1
    var targetWidth = window.innerWidth - 50
    targetWidth = Math.min(1200, targetWidth)

    chart.attr("width", targetWidth);
    chart.attr("height", targetWidth / aspect);

}



queue()
    .defer(d3.json, "static/world-110m.json")
    .defer(d3.csv, "static/countries.csv")
    .defer(d3.json, "importsdata.json")
    .await(ready);

function ready(error, worlddata, countrydata,csvdata) {

    IMPORTAPP.worlddata = worlddata
    IMPORTAPP.countrydata = countrydata
    upload(csvdata["csv_like_data"])
    
    
   
}

function draw_sankey(sankey_data, max_height) {


    d3.select("svg.sankey").remove()

    var margin = {
            top: 10,
            right: 150,
            bottom: 9,
            left: 0
        },
        width = 800 - margin.left - margin.right,
        height = max_height - margin.top - margin.bottom;

    var formatNumber = d3.format(",.0f"),
        format = function(d) {
            return "£" + formatNumber(d) ;
        }



    var cat10scale = d3.scale.category10();

    var color = function(d) {

        var c = cat10scale(d);

        if (c == "#2ca02c") {
            return "#c7c7c7"
        } else {
            return c
        }
    }
 

    total_width = width + margin.left + margin.right
    total_height = height + margin.top + margin.bottom

    var svg = d3.select("#sankeycontainer").append("svg")
        .attr("class", "sankey")
        .attr("width", total_width)
        .attr("height", total_height)
        .attr("viewBox", "0 0 " + total_width + " " + total_height)
        .attr("preserveAspectRatio", "xMidYMid")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var sankey = d3.sankey()
        .nodeWidth(15)
        .nodePadding(18)
        .size([width, height]);


    var path = sankey.link();

    sankey
        .nodes(sankey_data.nodes)
        .links(sankey_data.links)
        .layout(10000);



    var link = svg.append("g").selectAll(".link")
        .data(sankey_data.links)
        .enter().append("path")
        .attr("class", "link")
        .attr("d", path)
        .style("stroke-width", function(d) {
            return Math.max(1, d.dy);
        })
        .sort(function(a, b) {
            return b.dy - a.dy;
        });

    link.append("title")
        .text(function(d) {
            return d.source.name + " → " + d.target.name + "\n" + format(d.value);
        });


    var link_text = svg.append("g").selectAll(".linktext")
        .data(sankey_data.links)
    link_text.enter().append("text")
        .attr("x", linkx)
        .attr("y", linky)
        .attr("dy", ".35em")
        .attr("text-anchor", "end")
        .attr("class", "linktext")
        .text(function(d) {
            if (linkx(d) < 500) {
                return format(d.value);
            }
        })


    var node = svg.append("g").selectAll(".node")
        .data(sankey_data.nodes)
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        })
        .call(d3.behavior.drag()
            .origin(function(d) {
                return d;
            })
            .on("dragstart", function() {
                this.parentNode.appendChild(this);
            })
            .on("drag", dragmove));

    node.append("rect")
        .attr("height", function(d) {
            return d.dy;
        })
        .attr("width", sankey.nodeWidth())
        .style("fill", function(d) {
            if (d.x < 300) {
                return colour_scale(d.value / IMPORTAPP.max_consignments)
            } else {
                return color(d.name.replace(/ .*/, ""));
            }
        })
        .style("stroke", function(d) {
            return d3.rgb(d.color).darker(2);
        })
        .append("title")
        .text(function(d) {
            return d.name + "\n" + format(d.value);
        });

    node.append("text")

    .attr("y", function(d) {
        return d.dy / 2;
    })
        .attr("dy", ".35em")
        .attr("transform", null)
        .text(function(d) {
            return d.name.substring(0, 65);
        })
        .attr("x", 6 + sankey.nodeWidth())
        .attr("text-anchor", "start");

    resize()

    function dragmove(d) {
        d3.select(this).attr("transform", "translate(" + d.x + "," + (d.y = Math.max(0, Math.min(height - d.dy, d3.event.y))) + ")");
        sankey.relayout();
        link.attr("d", path);
        link_text.attr("x", linkx)
        link_text.attr("y", linky)
    }
}


function get_sankey_height(data) {
    //We need to find the level with the most unique values and multiply by 30


    max_len = 0

    var keys =  ["country", "product", "port", "quantity"]
    for (var i = 0; i < 3; i++) {

        var filter_name = keys[i]

        var this_data = data.map(function(d) {
            return d[filter_name]
        })

        var unique_options = _.uniq(this_data)

        max_len = Math.max(unique_options.length, max_len)


    };

    return max_len * 40

}


function redraw() {
    filter_data()
    get_consignments_by_country()
    var sankey_data = csv_to_sankey_data(IMPORTAPP.filtered_data);
    var max_height = get_sankey_height(IMPORTAPP.filtered_data)
    draw_sankey(sankey_data, max_height);
    map_colours()
    key_colours()


}

function create_filters() {

    d3.select("#filters").html("")
    var data = IMPORTAPP.importdata
    filters = []

    var keys =  ["country", "product", "port", "quantity"]
    for (var i = 0; i < 3; i++) {

        var filter_name = keys[i]

        var this_data = data.map(function(d) {
            return d[filter_name]
        })

        var unique_options = _.uniq(this_data)
        unique_options.unshift("All")

        filters.push({
            "filter_name": filter_name,
            "unique_options": unique_options
        })

    };

    output_area = d3.select("#filters")

    select_divs = output_area
        .selectAll("div")
        .data(filters)

    select_divs.enter().append("div").classed("select_divs", true)

    select_boxes = select_divs.append("label").text(function(d) {
        my_str = d["filter_name"]
        my_str = my_str.charAt(0).toUpperCase() + my_str.slice(1);
        return my_str
    })

    select_boxes = select_divs.append("select")
        .attr("id", function(d) {
            return d["filter_name"]
        })
        .attr("key", function(d) {
            return d["filter_name"]
        })
        .attr("class", "select_boxes")
        .attr("multiple", "")




    options = select_boxes
        .selectAll(".select_boxes")
        .data(function(d) {
            return d["unique_options"]
        })

    options
        .enter()
        .append("option")
        .attr("value", function(d) {
            return d
        })
        .text(function(d) {
            return d.substr(0,60)
        })
        .filter(function(d) {
            return d == "All";
        })
        .attr("selected", "")

    d3.selectAll("select").on("change", function() {
            redraw()
        }

    )

}

function get_multi_select_array(selection_box_d3_selection) {

    var values = selection_box_d3_selection
        .selectAll("option")
        .filter(function(d, i) {
            return this.selected;
        });

    return_values = []
    _.forEach(values[0], function(d) {
        return_values.push(d.value);
    })

    return return_values
}

function filter_data() {

    var keys = _.keys(IMPORTAPP.importdata[0])
    var data = IMPORTAPP.importdata


    for (var i = 0; i < 3; i++) {
        var selection_box = d3.select("#" + keys[i])

        filter_values = get_multi_select_array(selection_box)


        if (!(_.contains(filter_values, "All"))) {
            data = _.filter(data, function(d) {
                return _.contains(filter_values, d[keys[i]])
            })
        }

    };


    IMPORTAPP.filtered_data = data
}

function csv_to_sankey_data() {

    var data = IMPORTAPP.filtered_data
    var keys =  ["country", "product", "port", "quantity"]

    console.log(keys)

    var nodes = []

    _.forEach(data, function(d) {
        d["level1"] = d[keys[0]]
    })

    _.forEach(data, function(d) {
        d["level2"] = d[keys[1]]
    })

    _.forEach(data, function(d) {
        d["level2link"] = d[keys[0]] + d[keys[1]]
    })

    _.forEach(data, function(d) {
        d["level3"] = d[keys[2]]
    })

    _.forEach(data, function(d) {
        d["level3link"] = d[keys[1]] + d[keys[2]]
    })

    var levelList = ["level1", "level2", "level3"]

    //Get unique nodes
    //and a name index lookup
    _.forEach(levelList, function(level) {
        newnodes = _.uniq(data, function(d) {
            return d[level]

        })

        newnodes = newnodes.map(function(d) {
            return {
                "name": d[level]
            }
        })
        nodes = nodes.concat(newnodes)
    })



    var name_num_lookup = {};

    _.forEach(nodes, function(d, i) {
        name_num_lookup[d["name"]] = i;
    });

    //Get links

    var links = d3.nest()
        .key(function(d) {
            return d["level2link"];
        })
        .rollup(function(d) {

            quantity = d3.sum(d, function(g) {
                return g.quantity;
            });
            return {
                "source": name_num_lookup[d[0]["level1"]],
                "target": name_num_lookup[d[0]["level2"]],
                "value": quantity
            }
        }).entries(data);


    var links2 = d3.nest()
        .key(function(d) {
            return d["level3link"];
        })
        .rollup(function(d) {

            quantity = d3.sum(d, function(g) {
                return g.quantity;
            });
            return {
                "source": name_num_lookup[d[0]["level2"]],
                "target": name_num_lookup[d[0]["level3"]],
                "value": quantity
            }
        }).entries(data);

    links = links.concat(links2)



    var links = links.map(function(d) {
        return d["values"]
    })

    var sankey_data = {
        nodes: nodes,
        links: links
    }

    return sankey_data
}


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
        .scale(150)
        .translate([-10 + width / 2, 50 + height / 2]);

    var path = d3.geo.path()
        .projection(projection);

    svg.append("path")


    var shapes = svg.selectAll(".countrypath")
        .data(countries)


    tooltip = d3.select(".tooltip")

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
        .on("click", function(d, i) {

            country = d.name;
            // d3.select("#country").attr("value", country)

            //Get countries
            var this_data = IMPORTAPP.importdata.map(function(d) {
                return d["country"]
            })

            var unique_options = _.uniq(this_data)


            if (_.contains(unique_options, country)) {

                document.getElementById('country').value = country;
            } else {

                document.getElementById('country').value = "All";
            }

            redraw()


        })
        .on("mousemove", function(d) {

            if (d["name"] in IMPORTAPP.country_totals) {

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
            }
        })
        .on("mouseout", function(d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

}


function map_tooltip_html(d) {


    this_country = d["name"]
    var source = d3.select("#map-tooltip-template").html();

    var template = Handlebars.compile(source)


    var products = d3.select("#product");
    var products = get_multi_select_array(products);
    if (_.contains(products, "All")) {
        product = "All products"
    } else {
        product = products.join()
    }

    var port = d3.select("#port");
    ports = get_multi_select_array(port);
    if (_.contains(ports, "All")) {
        port = "All ports"
    } else {
        port = ports.join()
    }

    var num_consignments = IMPORTAPP.country_totals[this_country]["num_consignments"]

    var html = template({
        num_consignments: num_consignments,
        product: product,
        port: port,
        country: this_country
    })

    return html
}


function get_consignments_by_country() {

    data = IMPORTAPP.filtered_data

    var totals = d3.nest()
        .key(function(d) {
            return d["country"];
        })
        .rollup(function(d) {

            quantity = d3.sum(d, function(g) {
                return g.quantity;
            });
            return {

                "sum": quantity
            }
        }).entries(data);

    final_totals = {}
    _.forEach(totals, function(d) {
        final_totals[d["key"]] = {
            "num_consignments": d["values"]["sum"]
        }
    })

    most_consignments = _.max(final_totals, function(value, key) {
        return value["num_consignments"]
    })
    most_consignments = most_consignments["num_consignments"]

    _.forEach(final_totals, function(d) {
        d["proportion_of_max"] = d["num_consignments"] / most_consignments
    })



    IMPORTAPP.country_totals = final_totals
    IMPORTAPP.max_consignments = most_consignments


}


function colour_scale(this_value) {

    min_coloured = 0.01
    var colour_scale = d3.scale.log().domain([min_coloured, 1]).range(["black", "#00CE0F"]);

    if (this_value == 0) {
        return "#E7E5E5"
    } else if (this_value < min_coloured) {
        return "black"
    } else {
        return colour_scale(this_value)
    }
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
            if (d["name"] in IMPORTAPP.country_totals) {
                total = IMPORTAPP.country_totals[d["name"]]["proportion_of_max"]
            } else {
                total = 0
            }
            return colour_scale(total)
        })



}


function draw_map_key() {

    var num_steps = 50

    var colour_scale = d3.scale.log().domain([1, 1000]).range(["black", "#00CE0F"]);

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
        .attr("transform", "translate(55,170)")
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
            return colour_scale(inverted_scale(d))
        })

    var yAxis = d3.svg.axis()
        .scale(axis_scale)
        .orient("left")
        .ticks(10, ",0.2s")
        .tickSize(-10, 0)


    var svg = d3.select("#mapcontainer svg")

    svg.append("g")
        .attr("transform", "translate(55,170)")
        .attr("class", "y axis")
        .call(yAxis)

    svg.append("g")
        .attr("transform", "translate(70,170) rotate(90)")
        .append("text")
        .text("Number of consignments")
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
    my_max = _.max(IMPORTAPP.country_totals, function(d) {
        return d["num_consignments"]
    })
    my_max = my_max["num_consignments"]

    var axis_scale = d3.scale.log().domain([1, my_max]).range([300, 0])

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


function linkx(d) {
    var curvature = 0.5;
    var x0 = d.source.x + d.source.dx,
        x1 = d.target.x,
        xi = d3.interpolateNumber(x0, x1),
        x2 = xi(curvature),
        x3 = xi(1 - curvature),
        y0 = d.source.y + d.sy + d.dy / 2,
        y1 = d.target.y + d.ty + d.dy / 2;
    return (x0 + x1) / 2 + 50
}

function linky(d) {
    var curvature = 0.5;
    var x0 = d.source.x + d.source.dx,
        x1 = d.target.x,
        xi = d3.interpolateNumber(x0, x1),
        x2 = xi(curvature),
        x3 = xi(1 - curvature),
        y0 = d.source.y + d.sy + d.dy / 2,
        y1 = d.target.y + d.ty + d.dy / 2;
    return (y0 + y1) / 2
}



 function browserSupportFileUpload() {
        var isCompatible = false;
        if (window.File && window.FileReader && window.FileList && window.Blob) {
        isCompatible = true;
        }
        return isCompatible;
    }   

function upload(data) {



    if (data && data.length > 0) {

        if (IMPORTAPP.csv_loaded) {
            update_csv(data)
        }
        else 
        {first_csv(data)}
      
        

      
    } else {
        alert('No data to import!');
    }
      

   
}

function first_csv(data) {



    d3.selectAll(".hideonload").style("visibility","visible");
    d3.selectAll(".hideafterload").remove()

    IMPORTAPP.importdata = data
    IMPORTAPP.csv_loaded=true

    create_filters()
    draw_map()
    draw_map_key()
    redraw()
    
    d3.select(window).on('resize', resize);
    resize()
    
}

function update_csv(data) {

    IMPORTAPP.importdata = data
     create_filters()
     redraw()

}