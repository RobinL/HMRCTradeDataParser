var IMPORTAPP = {
    
}

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
        "#9edae5"
    ]);


$(function() {
$.when(p1, p2, p3).done(function(worlddata, countrydata, select_data) {

    IMPORTAPP.worlddata = worlddata[0]
    IMPORTAPP.countrydata = d3.csv.parse(countrydata[0])
    IMPORTAPP.select_box_data = select_data[0]["csv_like_data"]

    //Go from  ISO 3166-1 numeric code to alpha_2 code
    IMPORTAPP.country_numericid_lookup = {}
    _.each(IMPORTAPP.countrydata, function(d){
        IMPORTAPP.country_numericid_lookup[d["id"]] = {"alpha_2": d["alpha_2"], "name":d["name"]}
    })

    draw_map()
    draw_map_key()
    create_filters(8)
    

    get_new_imports_data()

    
    d3.select(window).on('resize', resize);


    $("#product").select2({data:[{id:"a", text:"aa"}]});


})

})

$(function() {
    //The following code deals with what happens when you click the 'level of detail' commodity codes
    $(".btn-group > .btn").click(function(){

        $(this).parent().parent().find(".btn-group > .btn").removeClass("active");
        
        $(this).addClass("active");

        //Change options in the product filter
        
    
    });

    $("#digitcode_btn").click(function(){


        create_filters($("#digitcode_btn > .btn.btn-default.active").attr("pval"))
        
    
    });




});


function activate_all_spinners() {
    $(".spinner").show()
}

function get_new_imports_data() {

    $("#spinnerdiv .spinner").show()
    $("#mapcontainer .spinner").show()
    $("#timeseriescontainer .spinner").show()
    $("#importerscontainer .spinner").show()


    dates = $("#date").val()
    countries = $("#country").val()
    products = $("#product").val()
    cn_code_length = $("#digitcode_btn > .btn.btn-default.active").attr("pval")
    ports = ["All"]

    stack_by = $("#stack_by_btn > .btn.btn-default.active").attr("pval")

    post_data = {
        dates: dates,
        countries: countries,
        products: products,
        stack_by: stack_by,
        ports: ports,
        cn_code_length: cn_code_length,
        importexport: IMPORTAPP.importexport

    }

    if (_.contains(dates,"All") & _.contains(countries,"All") & _.contains(products,"All") & _.contains(ports,"All")) {
        $(".all_results").hide()
        $("#too_many").show()
        return
    }

    p1 = $.getJSON("eu.json", post_data)
    p2 = $.getJSON("timeseries_eu.json", post_data)  

    $.when(p1, p2, p3).done(function(imports_data, timeseries_data) {

        IMPORTAPP.filtered_data = imports_data[0]["csv_like_data"]
        IMPORTAPP.timeseries_data = timeseries_data[0]["csv_like_data"]
        

        if (IMPORTAPP.filtered_data.length>999) {
            $(".all_results").hide()
            $("#no_results").hide()
            $("#too_many").show()
            $("#spinnerdiv .spinner").hide()
            return
        } else if (IMPORTAPP.filtered_data.length==0) {
            $(".all_results").hide()
            $("#too_many").hide()
            $("#no_results").show()
            $("#spinnerdiv .spinner").hide()
            return
        }
        else{
            $(".all_results").show()
            $("#too_many").hide()
            $("#no_results").hide()
        }

        $("#spinnerdiv .spinner").hide()


        get_consignments_by_country()
 
        

        map_colours()
        key_colours()
        $("#mapcontainer .spinner").hide()

        
        create_stacked_bar(IMPORTAPP.timeseries_data)
        $("#timeseriescontainer .spinner").hide()

      
        

    })

}


function stacked_bar_data(data) {


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
    dates = _.uniq(data, function(d) {
        return d.date;
    })



    //Get list of ports or countries (depending on which is selected)
    stack_by_units = _.uniq(data, function(d) {
        return d.stack_by;
    })

    final_data = []


    _.each(dates, function(date) {
        date = date.date
        var this_row = {}

        _.each(stack_by_units, function(stack_by_unit) {
            stack_by_unit = stack_by_unit.stack_by
            this_row[stack_by_unit] = 0

            _.each(data, function(d) {
                if ((d["stack_by"] == stack_by_unit) & (d["date"] == date)) {
                    this_row[stack_by_unit] += d["quantity"]
                }

            })

        })
        this_row["date"] = date
        this_row["formatted_date"] = d3.time.format("%b %Y")(d3.time.format("%Y-%m-%d").parse(date))
        final_data.push(this_row)
    })

    data = final_data

    data = data.sort(function(a, b) {

        return d3.time.format("%Y-%m-%d").parse(a.date) - d3.time.format("%Y-%m-%d").parse(b.date)
    });

    //Now we need to insert records where we have missing months
    dates_have = _.uniq(data, function(d) {
        return d.date;
    });
    dates_have = _.map(data, function(d) {
        return d.date
    });
    max_date = dates_have[0]
    min_date = dates_have.slice(-1)[0]

    //make list of all dates then filter

    var all_dates = []
    for (var year = 2005; year < 2020; year++) {

        for (var month = 1; month < 10; month++) {
            var this_date = year + "-0" + month + "-01"
            all_dates.push(this_date)
        };
        all_dates.push(year + "-10-01")
        all_dates.push(year + "-11-01")
        all_dates.push(year + "-12-01")
    };




    //Now filter down
    all_dates = _.filter(all_dates, function(d) {
        return d3.time.format("%Y-%m-%d").parse(d) >= d3.time.format("%Y-%m-%d").parse(max_date)
    })

    all_dates = _.filter(all_dates, function(d) {
        return d3.time.format("%Y-%m-%d").parse(d) <= d3.time.format("%Y-%m-%d").parse(min_date)
    })


    //Find dates that are not in data
    new_dates = _.difference(all_dates, dates_have)



    blank_record = data[0]

    _.each(new_dates, function(d) {

        new_record = {}

        _.each(_.keys(blank_record), function(k) {
            new_record[k] = 0
        })

        new_record["date"] = d
        new_record["formatted_date"] = d3.time.format("%b %Y")(d3.time.format("%Y-%m-%d").parse(d))

        data.push(new_record)

    })

    data = data.sort(function(a, b) {

        return d3.time.format("%Y-%m-%d").parse(a.date) - d3.time.format("%Y-%m-%d").parse(b.date)
    });

    return data


}



function create_stacked_bar(data) {


    try {
    data = stacked_bar_data(data);
    }
    catch(err) {
        data = []
    }



    var margin = {
            top: 20,
            right: 50,
            bottom: 60,
            left: 40
        },
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




    var total_width = width + margin.left + margin.right
    var total_height = height + margin.top + margin.bottom


    var svg = d3.select("#timeseriescontainer").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("viewBox", "0 0 " + total_width + " " + total_height)
        .attr("class", "timeseries")
        .attr("preserveAspectRatio", "xMidYMid")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var distinct_stack_by_units = d3.keys(data[0]).filter(function(key) {
        return key !== "date" & key !== "formatted_date";
    })




    data.forEach(function(d) {
        var y0 = 0;
        d.stack_by = distinct_stack_by_units.map(function(name) {
            return {
                name: name,
                y0: y0,
                y1: y0 += +d[name]
            };
        });
        d.total = d.stack_by[d.stack_by.length - 1].y1;
    });


    x.domain(data.map(function(d) {
        return d["formatted_date"]
    }));



    if (data.length > 50) {
    xAxis.tickValues(data.map( function(d,i) { if (i % 3 == 0 ) {return d["formatted_date"]; } else {return ""}} ))
    }



    y.domain([0, d3.max(data, function(d) {
        return d.total;
    })]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", function(d) {
            return "rotate(-45)"
        });

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Value of imports into UK");

    var stack_by = svg.selectAll(".stack_by")
        .data(data)
        .enter().append("g")
        .attr("class", "g")
        .attr("transform", function(d) {
            return "translate(" + x(d.formatted_date) + ",0)";
        });

    stack_by.selectAll("rect")
        .data(function(d) {
            return d.stack_by;
        })
        .enter().append("rect")
        .attr("width", x.rangeBand())
        .attr("y", function(d) {
            return y(d.y1);
        })
        .attr("height", function(d) {
            return y(d.y0) - y(d.y1);
        })
        .style("fill", function(d) {
            return port_colours(d.name.replace(/  .*/, ""));
        });

    var legend = svg.selectAll(".legend")
        .data(distinct_stack_by_units.slice().reverse())
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) {
            return "translate(0," + i * 20 + ")";
        });

    legend.append("rect")
        .attr("x", width + 8)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", port_colours);

    legend.append("text")
        .attr("x", width + 2)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) {
            return d;
        });


        var shapes = svg.selectAll("rect")
     

        shapes
        .on("mousemove", function(d) {



                tooltip.transition()
                    .duration(200)
                    .style("opacity", function() {
                        return 0.9
                    });


                tooltip
                    .html(function() {
                        return d["name"] + ": £" + d3.format(".4s")(d["y1"] - d["y0"]);
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






function create_filters(cn_code_length) {

    d3.select("#filters").html("")

    filters_dict = {}

    var keys = ["date", "country", "product"]
    var sizes = [100, 200, 400]

    //Use whatever digit codes chosen to convert select_box_data

  

    var filtered_select_box_data = []

    _.each(IMPORTAPP.select_box_data, function(d) {
        d = $.extend({}, d)

        if (d.select_box.indexOf("product") > -1){

            if (d.select_box.indexOf(cn_code_length) > -1){
                d.select_box = "product"
                filtered_select_box_data.push(d)
            }
        }
        else {
            filtered_select_box_data.push(d)    

        }
        
    })


    filtered_select_box_data = _.filter(filtered_select_box_data, function(d){
        return d.select_box != "port"
    })



    _.each(keys, function(d) {
        filters_dict[d] = []
    })

    _.each(filtered_select_box_data, function(d) {

        filters_dict[d.select_box].push(d)
    })



    filters = []

    _.each(filters_dict, function(d, k, i) {

        d.unshift({
            my_key: "All",
            value: "All"
        })


        filters.push({
            filter_name: k,
            filter_options: d
        })

    })



    output_area = d3.select("#filters")

    select_divs = output_area
        .selectAll("div")
        .data(filters)

    select_divs.enter().append("div").classed("select_divs", true)

    select_boxes = select_divs.append("label").text(function(d) {
        my_str = d["filter_name"]
        if (my_str == "country") {
        my_str = "EU Country"
    }
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
            return d["my_key"]
        })
        .text(function(d) {
            return d["value"].substr(0, 60)
        })

    $(".select_boxes").each(function(index) {
        $(this).select2({
            width: sizes[index]
        })

    })

    // Select some initial values
    $("#date").val("All").trigger("change");
    $("#country").val("All").trigger("change");
    


    $(".select_boxes").on("change", function() {
            get_new_imports_data()
        }

    )

    $("#stack_by_btn").on("click", function() {
            get_new_imports_data()
        }

    )

    $("#product").val(filters_dict.product[1].my_key).trigger("change");





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
        .scale(430)
        .translate([-100 + width / 2, 500 + height / 2]);

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


function get_consignments_by_country() {

    data = IMPORTAPP.filtered_data

    var totals = d3.nest()
        .key(function(d) {
            return d["country_code"];
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

            alpha_2 = IMPORTAPP.country_numericid_lookup[d["id"]]["alpha_2"]

            if (alpha_2 in IMPORTAPP.country_totals) {
                total = IMPORTAPP.country_totals[alpha_2]["proportion_of_max"]
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