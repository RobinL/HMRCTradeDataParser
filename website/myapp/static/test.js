$(function() {



	$("#test").html("hello")

	 post_data =  {dates: ["2015 01", "2015 04", "All"],
            countries: ["AF","US", "All"],
            products: ["01012100", "01012990", "01022110", "All"],
            ports: ["AOA", "FXT"]}


    p1 = $.getJSON("importsdata2.json", post_data)

})

