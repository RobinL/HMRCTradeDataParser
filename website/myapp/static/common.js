var IMPORTAPP = {
    
}


function stacked_bar_data(data) {

    // Need to munge the data into the format specified in https://github.com/mbostock/d3/wiki/Stack-Layout
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
    var dates = _.uniq(data, function(d) {
        return d.date;
    })

    //Get list of ports or countries (depending on which is selected)
    var stack_by_units = _.uniq(data, function(d) {
        return d.stack_by;
    })

    var final_data = []


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

    var data = final_data

    data = data.sort(function(a, b) {

        return d3.time.format("%Y-%m-%d").parse(a.date) - d3.time.format("%Y-%m-%d").parse(b.date)
    });

    //Now we need to insert records where we have missing months
    var dates_have = _.uniq(data, function(d) {
        return d.date;
    });

    var dates_have = _.map(data, function(d) {
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
    var new_dates = _.difference(all_dates, dates_have)

    var blank_record = data[0]

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
    var data = stacked_bar_data(data);
    }
    catch(err) {
        var data = []
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
                formatted_date: d["formatted_date"],
                y0: y0,
                y1: y0 += +d[name]
            };
        });
        d.total = d.stack_by[d.stack_by.length - 1].y1;

        //Make the total available for the popup box
        d.stack_by.forEach(function(dd) {
            dd.total = d.total
        })
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
        .text("Value of " + IMPORTAPP.importexport);

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
    var tooltip = d3.select(".tooltip")
    
    shapes
    .on("mousemove", function(d) {

            tooltip.transition()
                .duration(200)
                .style("opacity", function() {
                    return 0.9
                });


            tooltip
                .html(function() {
                    //return d["formatted_date"] + " " + d["name"] + ": £" + d3.format(".4s")(d["y1"] - d["y0"]);
                    return stacked_bar_tooltip_html(d)
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

function stacked_bar_tooltip_html(d) {
    var source = d3.select("#stacked-tooltip-template").html();

    var template = Handlebars.compile(source)

    var html = template({
        unit: d.quantity_exports,
        date: d.formatted_date,
        quantity:  "£" + d3.format(".4s")(d["y1"] - d["y0"]),
        total:  "£" + d3.format(".4s")(d.total)
    })

    return html
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