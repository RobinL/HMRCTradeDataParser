
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

var p1 = $.getJSON("static/eu.json")
var p2 = $.ajax("static/countries.csv")
var p3 = $.getJSON("selectboxdata.json")



$(function() {


$.when(p1, p2, p3).done(function(worlddata, countrydata, select_data) {

    debugger;

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

})

})

$(function() {
    //The following code deals with what happens when you click the 'level of detail' commodity codes
    $(".btn-group > .btn").click(function(){
        $(this).parent().parent().find(".btn-group > .btn").removeClass("active");
        $(this).addClass("active");
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


function create_filters(cn_code_length) {

    d3.select("#filters").html("")

    filters_dict = {}

    var keys = ["date", "country", "product"]
    var sizes = [100, 200, 400]

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


    filtered_select_box_data = _.filter(filtered_select_box_data, function(d){
        return d.s != "port"
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




