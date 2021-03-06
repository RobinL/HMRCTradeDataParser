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


function draw_sankey(sankey_data) {

    //First of all calculate the height the diagram will be, the size of the padding, etc.
    var sankey_height_dict = get_sankey_height_dict(sankey_data)
    var max_height = sankey_height_dict["total_height"]

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
            return "£" + formatNumber(d);
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
        .nodePadding(sankey_height_dict["padding"])
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


            return d.source.name_text + " → " + d.target.name_text + "\n" + format(d.value);
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


            
           
         


            if (d.x < 300 & IMPORTAPP.importexport == "imports") {

                return colour_scale(d.value / IMPORTAPP.max_consignments)
            }

            else if (d.x > 600 & IMPORTAPP.importexport == "exports") {
                return colour_scale(d.value / IMPORTAPP.max_consignments)
            } else {
                return port_colours(d.name_text);
            }

           


        })
        .style("stroke", function(d) {
            return d3.rgb(d.color).darker(2);
        })
        .append("title")
        .text(function(d) {
            return d.name_text + "\n" + format(d.value);
        });

    node.append("text")

    .attr("y", function(d) {
        return d.dy / 2;
    })
        .attr("dy", ".35em")
        .attr("transform", null)
        .text(function(d) {
            return d.name_text.substring(0, 65);
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



function get_sankey_height_dict(sankey_data) {

    //var num_elements = get_sankey_num_elements()
    num_elements = IMPORTAPP.sankey_num_elements 


    var padding_target = 20
    var height_target = 40

    var total_per_element = padding_target + height_target
    var total_height_pre_normalisation = (total_per_element * num_elements) - padding_target


    if (total_height_pre_normalisation <= 1000) {
        return { 
            total_height:  total_height_pre_normalisation,
            padding: padding_target,
            height: height_target
            }
    }

    //If we exceed the max height of 1000, shrink everything

    var max_height_per_element_inc_padding = 1000/num_elements

    var constraint_factor = max_height_per_element_inc_padding/total_per_element

    var constraint_factor_padding = Math.pow(constraint_factor,0.5)

    var new_height_before_normalise = height_target* constraint_factor

    var new_padding_before_normalise = padding_target* constraint_factor_padding

    var normalise = ((new_height_before_normalise + new_padding_before_normalise)*num_elements - new_padding_before_normalise)/1000

    var final_height =new_height_before_normalise * normalise

    var final_padding = new_padding_before_normalise * normalise

    return { 
            total_height:  1000,
            padding: final_padding,
            height: final_height
            }






}

function get_sankey_num_elements() {
    //We need to find the level with the most unique values and multiply by 30

    var data = IMPORTAPP.filtered_data
    max_len = 0

    var keys = ["country", "product", "port", "quantity"]
    for (var i = 0; i < 4; i++) {

        var filter_name = keys[i]

        var this_data = data.map(function(d) {
            return d[filter_name]
        })

        var unique_options = _.uniq(this_data)

        max_len = Math.max(unique_options.length, max_len)


    };

    return max_len

}


function activate_all_spinners() {
    $(".spinner").show()
}

function get_new_imports_data() {

    $("#spinnerdiv .spinner").show()
    $("#sankeycontainer .spinner").show()
    $("#mapcontainer .spinner").show()
    $("#timeseriescontainer .spinner").show()
    $("#importerscontainer .spinner").show()


    dates = $("#date").val()
    countries = $("#country").val()
    products = $("#product").val()
    ports = $("#port").val()
    cn_code_length = $("#digitcode_btn > .btn.btn-default.active").attr("pval")

    stack_by = $("#stack_by_btn > .btn.btn-default.active").attr("pval")

    post_data = {
        dates: dates,
        countries: countries,
        products: products,
        ports: ports,
        stack_by: stack_by,
        cn_code_length: cn_code_length,
        importexport: IMPORTAPP.importexport

    }

    if (_.contains(dates,"All") & _.contains(countries,"All") & _.contains(products,"All") & _.contains(ports,"All")) {
        $(".all_results").hide()
        $("#too_many").show()
        return
    }

    p1 = $.getJSON("non_eu.json", post_data)
    p2 = $.getJSON("timeseries_non_eu.json", post_data)  

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
        var sankey_data = csv_to_sankey_data(IMPORTAPP.filtered_data);
        
        draw_sankey(sankey_data);
        $("#sankeycontainer .spinner").hide()
        

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

function create_filters(cn_code_length) {

    d3.select("#filters").html("")

    filters_dict = {}

    var keys = ["date", "country", "product", "port"]
    var sizes = [100, 200, 400, 100]

    //Use whatever digit codes chosen to convert select_box_data

  

    var filtered_select_box_data = []

    _.each(IMPORTAPP.select_box_data, function(d) {
        d = $.extend({}, d)

        if (d.s.indexOf("product") > -1){

            if (d.s.indexOf(cn_code_length) > -1){
                d.s = "product"
                filtered_select_box_data.push(d)
            }
        }
        else {
            filtered_select_box_data.push(d)    

        }
        
    })

    _.each(keys, function(d) {
        filters_dict[d] = []
    })

    _.each(filtered_select_box_data, function(d) {

        filters_dict[d.s].push(d)
    })



    filters = []

    _.each(filters_dict, function(d, k, i) {

        d.unshift({
            k: "All",
            v: "All"    
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
        my_str = "Non EU Country"
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
            return d["k"]
        })
        .text(function(d) {
            return d["v"].substr(0, 60)
        })

    $(".select_boxes").each(function(index) {
        $(this).select2({
            width: sizes[index]
        })

    })

    // Select some initial values
    $("#date").val("All").trigger("change");
    $("#country").val("All").trigger("change");
    $("#port").val("All").trigger("change");
    


    $(".select_boxes").on("change", function() {
            get_new_imports_data()
        }

    )

   $("#stack_by_btn").on("click", function() {
            get_new_imports_data()
        } 

    )

   
    $("#product").val(filters_dict.product[1].k).trigger("change");





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


    var data = $.extend([],IMPORTAPP.filtered_data)
    var keys = ["country_code", "product_code", "port_code", "quantity"]
    var keys_text = ["country", "product", "port"]

    if (IMPORTAPP.importexport == "exports") {
    var keys = ["port_code", "product_code", "country_code", "quantity"]
    var keys_text = ["port", "product", "country"]
}


    var total = _.reduce(data, function(memo, d){ return d["quantity"] + memo; }, 0);

    var one_percent_total = total/200



 
    replace_keys = {"port_code": {"key":"Other_port", "text":"All other ports", "text_key":"port"},
"product_code": {"key":"Other_product", "text":"All other products", "text_key":"product"},
"country_code": {"key":"Other_country", "text":"All other countries", "text_key": "country"},}


    var dict_of_totals = {}
    _.forEach(keys.slice(0,3), function(this_key){
        dict_of_totals[this_key] = {}
        _.forEach(data, function(d) {

            var this_value = d[this_key]
            dict_of_totals[this_key][this_value] = (dict_of_totals[this_key][this_value] || 0) + d["quantity"] 

        });
    });


    _.forEach(data, function(d) {
       _.forEach(keys.slice(0,3), function(this_key){
    
        //Look in this datapoint, and see whether 

   
        this_item = d[this_key]  //e.g. if this_key = "port code" this_item will be "ZLC" 
        if (dict_of_totals[this_key][this_item] < one_percent_total) {
       
            d[this_key] =replace_keys[this_key]["key"]
            d[replace_keys[this_key]["text_key"]] = replace_keys[this_key]["text"]

        }

        })
    })



    var dict_of_totals = {}
    _.forEach(keys.slice(0,3), function(this_key){
        dict_of_totals[this_key] = {}
        _.forEach(data, function(d) {

            var this_value = d[this_key]
            dict_of_totals[this_key][this_value] = (dict_of_totals[this_key][this_value] || 0) + d["quantity"] 

        });
    });

    var most_elems = 0
  


    _.forEach(_.keys(dict_of_totals), function(k) {
         
        most_elems = Math.max(_.size(dict_of_totals[k]),most_elems)
        
        
    })
      

    IMPORTAPP.sankey_num_elements = most_elems

    

    var nodes = []


    // Initial nodes
    _.forEach(data, function(d) {
            d["level1"] = d[keys[0]]
            d["level1text"] = d[keys_text[0]]
    })


    // Middle nodes
    _.forEach(data, function(d) {
            d["level2"] = d[keys[1]]
            d["level2text"] = d[keys_text[1]]
    })

    //Links between level 1 and level 2 
    _.forEach(data, function(d) {
        d["level2link"] = d[keys[0]] + d[keys[1]]
    })

    _.forEach(data, function(d) {
        d["level3"] = d[keys[2]]
        d["level3text"] = d[keys_text[2]]
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
                "name": d[level],
                "name_text": d[level+"text"]
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