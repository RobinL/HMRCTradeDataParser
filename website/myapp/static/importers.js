IMPORTERSAPP = {}



var spot_color = d3.scale.linear()
                    .domain([0, 1, 2, 3, 4, 5])
                    .range(["#BB0004", "#E83400", "#FF7611", "#FDC400", "#B4E800", "#63FE05"]);

$(function(){


	IMPORTERSAPP.map = L.map('map', {
	    center: [51.505, -0.09],
	    zoom: 13
	});

	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
	    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
	    maxZoom: 18,
	    id: 'mapbox.light',
	    accessToken: 'pk.eyJ1Ijoicm9iaW5saW5hY3JlIiwiYSI6IjAwYTg3MDAwNmFlZTk3MDlhNGIxY2VjNDk5Yjk4NWE1In0.DWAN8Om-9kOnwVTQIiDGaw'
	}).addTo(IMPORTERSAPP.map );





	//Now add points from importers API

	var p1 = $.getJSON("selectboxdata.json?type=product_8")


	$.when(p1).done(function(selectboxdata) {
		create_filters(selectboxdata["csv_like_data"])

		$("#importerscontainer .spinner").hide()
	})




})



function is_blank(data) {
    if (data != null && data !== undefined) {
        return false
    }
    else {
    	return true
    }
}




function create_filters(data) {



    target_div = d3.select("#filters")


    //Use whatever digit codes chosen to convert select_box_data

    target_div = target_div.append("div").classed("select_divs", true)

    target_div.append("label").text("Select product(s).  Results are limited to the 1000 most recent")

    target_div = target_div.append("select")
        .attr("id", "code_selection_box")
        .attr("class", "select_boxes")
        .attr("multiple", "")



    options = target_div.selectAll(".options")
        .data(data)
        .enter()
        .append("option")
        .attr("value", function(d) {
        
            return d["my_key"]
        })
        .text(function(d) {
     
            return d["value"].substr(0, 70)
        })

    $(".select_boxes").each(function(index) {
        $(this).select2({
            width: 500
        })

    })


    $(".select_boxes").on("change", function() {
            get_importers_data()
        }

    )



 }


	function get_importers_data() {

		try{			IMPORTERSAPP.layer.remove()
		}
		catch(err) {}
			
		

		post_data = {codes: $("#code_selection_box").val()}
		var p2 = $.getJSON("importers.json", post_data)

		$.when(p2).done(function(importersdata) {

			d3.select("#importerstable").remove()
			importersdata = importersdata["csv_like_data"]
			var markerArray = [];


		    var source   = $("#map-tooltip-template").html();

		    var template = Handlebars.compile(source)

			for (var i = 0; i < importersdata.length; i++) {

				d = importersdata[i]
		            
		        lat = d["lat"]
		        lng = d["lng"]

		        if (is_blank(lat)  ||  is_blank(lng)) {
		                       continue
		                   };
				style = {

				                "weight": 0,
				                "fillColor": spot_color(1),
				                "fillOpacity": 0.8,
				                "radius": 4*Math.pow(d["date_count"],0.5)

				            };

				var m = L.circleMarker([lat, lng], style)
				var html = template(d)


				m.bindPopup(html, {"offset":L.point(0,-10)})

				m.on("mouseover", function() {
				              this.openPopup();
				          });

				          m.on("mouseout", function() {
				    
				              this.closePopup()
				          });
				markerArray.push(m);

			};


			this_layer = L.featureGroup(markerArray).addTo(IMPORTERSAPP.map )
			IMPORTERSAPP.layer = this_layer
		    IMPORTERSAPP.map.fitBounds(this_layer.getBounds())

		    create_importers_table(importersdata)


		})



	}


function create_importers_table(table_data) {

	_.forEach(table_data, function(d) {

		delete d["lat"]
		delete d["lng"]
		delete d["date_count"]
	})

    

    svgContainer = d3.select("#importerscontainer")

    myTable = svgContainer.append("table")
        .attr("class", "table table-striped table-bordered table-condensed smalltabletext")
        .attr("id", "importerstable")
        .append("tbody");


    headers = _.keys(table_data[0])

    var th = myTable.append("tr")

    th.selectAll("th")
        .data(headers)
        .enter()
        .append("th")
        .html(function(d) {
            return d
        })


    var tr = myTable.selectAll("tr2").data(table_data).enter().append("tr")

    var td = tr.selectAll("td").data(function(d) {

            return_array = []

            _.each(d, function(j, k) {
                return_array.push({
                    value: j,
                    key: k
                })

            })


            return return_array

        })
        .enter()
        .append("td")
        .html(function(d, i) {


         
                return d["value"]
            
        })
}
