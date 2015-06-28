
var IMPORTAPP = {csv_loaded:false}

function resize() {


    var chart = d3.select("svg.map")
    aspect = chart.attr("width") / chart.attr("height")
    var targetWidth = $("#mapcontainer").width()
    targetWidth = Math.min(1200, targetWidth)
    chart.attr("width", targetWidth);
    chart.attr("height", targetWidth / aspect);

    var chart = d3.select("svg.sankey")

    if (!chart.empty()) {
        aspect = chart.attr("width") / chart.attr("height") * 1
        var targetWidth = $("#sankeycontainer").width()
        targetWidth = Math.min(1200, targetWidth)

        chart.attr("width", targetWidth);
        chart.attr("height", targetWidth / aspect);

}

 var chart = d3.select("svg.timeseries")

    if (!chart.empty()) {
        aspect = chart.attr("width") / chart.attr("height") * 1
        var targetWidth = $("#timeseriescontainer").width()
        targetWidth = Math.min(1200, targetWidth)

        chart.attr("width", targetWidth);
        chart.attr("height", targetWidth / aspect);

}


}




var p1 = $.getJSON("static/world-110m.json")
var p2 = $.ajax("static/countries.csv")
var p3 = $.getJSON("selectboxdata.json")

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
"#9edae5"]);

$.when(p1,p2,p3).done(function(worlddata,countrydata, select_data) {

    IMPORTAPP.worlddata = worlddata[0]
    IMPORTAPP.countrydata = d3.csv.parse(countrydata[0])
    IMPORTAPP.select_box_data = select_data[0]["csv_like_data"]

    draw_map()
    draw_map_key()
    create_filters()
    get_new_imports_data()



    $("#date").val("All").trigger("change") ;
    $("#country").val("All").trigger("change") ;
    $("#port").val("All").trigger("change") ;
    $("#product").val("01012100").trigger("change") ;

    resize()
    d3.select(window).on('resize', resize);



})




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
                return port_colours(d.name.replace(/  .*/, ""));
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


function get_new_imports_data() {


    dates = $("#date").val()
    countries = $("#country").val()
    products = $("#product").val()
    ports = $("#port").val()

    post_data =  {dates: dates,
            countries: countries,
            products: products,
            ports: ports}


    p1 = $.getJSON("importsdata2.json", post_data)
    p2 = $.getJSON("timeseries.json", post_data)
    p3 = $.getJSON("importers.json", post_data)
    
    
    $.when(p1,p2,p3).done(function(imports_data, timeseries_data, importers_data) {




        IMPORTAPP.filtered_data = imports_data[0]["csv_like_data"]
        IMPORTAPP.timeseries_data = timeseries_data[0]["csv_like_data"]
        IMPORTAPP.importers_data = importers_data[0]["csv_like_data"]

        if (IMPORTAPP.filtered_data.length>=0) {

            get_consignments_by_country()
            var sankey_data = csv_to_sankey_data(IMPORTAPP.filtered_data);
            var max_height = get_sankey_height(IMPORTAPP.filtered_data)
            draw_sankey(sankey_data, max_height);
            map_colours()
            key_colours()

        }

         if (IMPORTAPP.importers_data.length>=0) {

          
            create_importers_table(IMPORTAPP.importers_data);
            create_stacked_bar(IMPORTAPP.timeseries_data)
         

        }


    })

}




function create_stacked_bar(data) {


    // First we need to munge the data into the format specified in https://github.com/mbostock/d3/wiki/Stack-Layout


 // {
 //      "month": "01", 
 //      "port": "London Heathrow Airport", 
 //      "quantity": 284699, 
 //      "year": "2015"
 //    }, 
 //    {
 //      "month": "02", 
 //      "port": "London Heathrow Airport", 
 //      "quantity": 22119, 
 //      "year": "2015"
 //    }, 


    //date  Felixstow  Stanstead  
    //11-Oct-13   41.62   22.36


    //Get list of dates
    dates = _.uniq(data, function(d) { return d.date; })
    //Get list of ports
    ports = _.uniq(data, function(d) { return d.port; })

    final_data = []

      
    _.each(dates, function(date) {
        date = date.date
        var this_row = {}
        
        _.each(ports, function(port) {
            port = port.port
            this_row[port] = 0

            _.each(data, function(d) {
                if ((d["port"] == port) & (d["date"] == date)) {
                    this_row[port] += d["quantity"]
                } 

            })

        })
        this_row["date"] = date
        this_row["formatted_date"] = d3.time.format("%b %Y")(d3.time.format("%Y-%m-%d").parse(date))
        final_data.push(this_row)
    })

    data = final_data



    var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
    .rangeRound([height, 0]);


var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(function(d) {
        return "£" + d3.format(".2s")(d)
    });

d3.selectAll("svg.timeseries").remove()


var total_width =  width + margin.left + margin.right
var total_height =  height + margin.top + margin.bottom


var svg = d3.select("#timeseriescontainer").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .attr("viewBox", "0 0 " + total_width + " " + total_height)
    .attr("class", "timeseries")
        .attr("preserveAspectRatio", "xMidYMid")
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var distinct_ports = d3.keys(data[0]).filter(function(key) { return key !== "date" & key !== "formatted_date"; })



  data.forEach(function(d) {
    var y0 = 0;
    d.ports = distinct_ports.map(function(name) { return {name: name, y0: y0, y1: y0 += +d[name]}; });
    d.total = d.ports[d.ports.length - 1].y1;
  });

  data.sort(function(a, b) { return b.date - a.date; });

  x.domain(data.map(function(d) { return d["formatted_date"]}));
  y.domain([0, d3.max(data, function(d) { return d.total; })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Value of exports to UK");

  var state = svg.selectAll(".state")
      .data(data)
    .enter().append("g")
      .attr("class", "g")
      .attr("transform", function(d) { return "translate(" + x(d.formatted_date) + ",0)"; });

  state.selectAll("rect")
      .data(function(d) { return d.ports; })
    .enter().append("rect")
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.y1); })
      .attr("height", function(d) { return y(d.y0) - y(d.y1); })
      .style("fill", function(d) { return port_colours(d.name.replace(/  .*/, "")); });

  var legend = svg.selectAll(".legend")
      .data(distinct_ports.slice().reverse())
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
      .attr("x", width - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", port_colours);

  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { return d; });

resize()

}


function create_importers_table(table_data) {

    d3.select("#importerstable").remove()

    svgContainer = d3.select("#importerscontainer")

        myTable = svgContainer.append("table")
                    .attr("class","table table-striped table-bordered table-condensed smalltabletext")
                    .attr("id", "importerstable")
                    .append("tbody");

     
        


        headers = _.keys(table_data[0])

        var th =myTable.append("tr")

        th.selectAll("th")
            .data(headers)
            .enter()
            .append("th")
            .html(function(d){return d})


        var tr = myTable.selectAll("tr2").data(table_data).enter().append("tr")

        var td = tr.selectAll("td").data(function(d) {

                return_array = []

                _.each(d, function(j,k) {
                    return_array.push({value: j, key:k})
                    
                })

              
                return return_array

                })
                .enter()
                .append("td")
                .html(function(d,i) {
                    
                   
                    if (d["key"]=="date") {

                        return d3.time.format("%b %Y")(d3.time.format("%Y-%m-%d").parse(d["value"]))
                    
                    }
                    else {
                        return d["value"]
                    }
                })
}


function update_filters() {

    d3.select("#filters").html("")
    var data = IMPORTAPP.filtered_data
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
            return d.substr(0,30)
        })


    $(".select_boxes").each(function(index) {

        $(this).select2()

    })

    $(".select_boxes").on("change", function() {
            //Post data to form



            get_new_imports_data()
        }

    )

}

function create_filters() {

    d3.select("#filters").html("")
   
    filters_dict = {}

    var keys =  ["date", "country", "product", "port"]
    var sizes = [100,200,400,100]
    

    _.each(keys, function(d) {
        filters_dict[d]=  []
    })

    _.each(IMPORTAPP.select_box_data, function(d) {

        filters_dict[d.select_box].push(d )
    })



    filters = []

    _.each(filters_dict, function(d,k,i){ 

        
            d.unshift({key: "All", value: "All"})
        

        filters.push({filter_name: k, filter_options: d})
        


    })




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
            return d["filter_options"]
        })

    options
        .enter()
        .append("option")
        .attr("value", function(d) {
            return d["key"]
        })
        .text(function(d) {
            return d["value"].substr(0,60)
        })

    $(".select_boxes").each(function(index) {
        $(this).select2({width:sizes[index]})

    })

    $(".select_boxes").on("change", function() {
            get_new_imports_data()
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

    var formatNumber = d3.format(",.0f"),
        format = function(d) {
            return "£" + formatNumber(d) ;
        }

    this_country = d["name"]
    var source = d3.select("#map-tooltip-template").html();

    var template = Handlebars.compile(source)


    var quantity_exports = IMPORTAPP.country_totals[this_country]["quantity_exports"]

    var html = template({
        quantity_exports: format(quantity_exports),
        this_country: this_country
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
            "quantity_exports": d["values"]["sum"]
        }
    })

    most_consignments = _.max(final_totals, function(value, key) {
        return value["quantity_exports"]
    })
    most_consignments = most_consignments["quantity_exports"]

    _.forEach(final_totals, function(d) {
        d["proportion_of_max"] = d["quantity_exports"] / most_consignments
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
        .text("Value of exports (£)")
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
        return d["quantity_exports"]
    })
    my_max = my_max["quantity_exports"]

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




