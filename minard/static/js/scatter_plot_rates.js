function history() {
    var params = {}
    params['crate'] = document.getElementById("crate-sel").value;
    params['slot'] = document.getElementById("slot-sel").value;
    params['channel'] = document.getElementById("channel-sel").value;
    window.location.replace($SCRIPT_ROOT + "/check_rates_history?" + $.param(params));
}

var data = window.data;
if( data != undefined && data != "" ){
    var data_length = data.length;
    var last_run = data[0][0];
    var first_run = data[data_length-1][0]
    var len = (last_run - first_run)/data.length;
    var run_offset = 0;
    var start_offset = 103214;
    var start = start_offset - run_offset;
    var end = d3.max(data, function(d) { return d[0]; }) + 1 - run_offset;
    
    var margin = {top: 20, right: 15, bottom: 60, left: 260}
        , width = 1600 - margin.left - margin.right
        , height = 760 - margin.top - margin.bottom;
    
     
    
    // Xrange starts when the we started storing cmos data    
    var x = d3.scale.linear()
        .domain([start, end])
        .range([ 0, width - 50 ]);
    
    var ymin = d3.max([0, d3.min(data, function(d) { return d[1]; })]);
    var ypad = ymin*0.1; 
    var ymax = d3.max(data, function(d) { return d[1]; });
    var yppad = ymax*0.1;
    
    var y = d3.scale.linear()
    	.domain([ymin-ypad, ymax+ypad])
    	.range([ height, 0 ]);
    
    var chart = d3.select('body')
        .append('svg:svg')
        .attr('width', width + margin.right + margin.left)
        .attr('height', height + margin.top + margin.bottom)
        .attr('class', 'chart');
    
    var valueline = d3.svg.line()
        .x(function(d) { return x(d[0]- run_offset); })
        .y(function(d) { return y(d[1]); });
    
    var main = chart.append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'main');
    
    // draw the x axis
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient('bottom')
        .ticks(len, "s");
    
    main.append('g')
        .attr('transform', 'translate(0,' + height + ')')
        .attr('class', 'main axis date')
        .call(xAxis);
    
    // draw the y axis
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient('left');
    
    main.append('g')
        .attr('transform', 'translate(0,0)')
        .attr('class', 'main axis date')
        .call(yAxis);
    
    d3.selectAll(".tick > text")
        .style("font-size", "18px");
    
    var g = main.append("svg:g"); 
    
    g.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);
    
    g.selectAll("scatter-dots")
        .data(data)
        .enter().append("svg:circle")
            .attr("cx", function (d,i) { return x(d[0] - run_offset); } )
            .attr("cy", function (d) { return y(d[1]); } )
            .attr("r", 8);
    
    
    chart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
    .append("text")
        .attr("class", "label")
        .attr("x", width+200 )
        .attr("y", 80)
        .style("text-anchor", "end")
        .text("Run Number")
        .style("font-size", "22px");
    
    chart.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "7.0em")
        .style("text-anchor", "end")
        .text("CMOS Rate (Hz)")
        .style("font-size", "22px");
}
 
