function timeSeries() {
    var margin = {top: 6, right: 0, bottom: 20, left: 40},
        width = 960 - margin.right,
        height = 120 - margin.top - margin.bottom;

    var title = '';

    var duration = 75000;

    function chart(selection) {
        selection.each(function(data) {
            now = new Date();

            var data_x = data.map(function(d) { return d.t; }),
                data_y = data.map(function(d) { return d.y; });

            var x = d3.time.scale()
                .domain([now - duration, +now])
                .range([0, width]);

            var y = d3.scale.linear()
                .domain([d3.min(data_y),d3.max(data_y)])
                .range([height, 0]);

            var line = d3.svg.line()
                .interpolate("basis")
                .x(function(d, i) {
                    return x(d.t); })
                .y(function(d, i) { return y(d.y); });

            var area = d3.svg.area()
                .interpolate("basis")
                .x(function(d, i) {
                    return x(d.t); })
                .y0(height)
                .y1(function(d, i) { return y(d.y); });

            var svg = d3.select(this).selectAll('svg').data([data]);
                
            var genter = svg.enter().append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .style("margin-left", -margin.left + "px")
              .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            genter.append('text').text(title).attr('x',10)
                .attr('y',height - margin.top).attr('class','title');

            genter.append("defs").append("clipPath")
                .attr("id", "clip")
              .append("rect")
                .attr("width", width)
                .attr("height", height);

            genter.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")");

            genter.append("g")
                .attr("clip-path", "url(#clip)")
              .append("path")
                .data([data])
                .attr("class", "line");

            genter.append("g")
                .attr("clip-path", "url(#clip)")
              .append("path")
                .data([data])
                .attr("class", "area");

            var g = svg.select('g');

            // redraw the line
            g.selectAll(".area").data([data])
                .attr("d", area)
                .attr("transform", null)
                .transition()
                .duration(1000)
                .ease('linear');

            g.select('.x.axis').transition().call(x.axis = d3.svg.axis().scale(x).orient("bottom"));

            // redraw the line
            g.selectAll(".line").data([data])
                .attr("d", line)
                .attr("transform", null)
                .transition()
                .duration(1000)
                .ease('linear');

            // slide the x-axis left
            //axis.transition()
            //    .duration(duration/2)
            //    .ease("linear")
            //    .call(x.axis);

            // slide the line left
            //svg.selectAll('.line, .area').transition()
            //    .duration(duration/2)
            //    .ease("linear")
            //    .attr("transform", "translate(" + x(now - (n - 1) * duration) + ")");

            // pop the old data point off the front
            //data.shift();
            //}
        });
    }
    chart.margin = function(_) {
        if (!arguments.length) return margin;
        margin = _;
        return chart;
    };

    chart.width = function(_) {
        if (!arguments.length) return width;
        width = _;
        return chart;
    };

    chart.height = function(_) {
        if (!arguments.length) return height;
        height = _;
        return chart;
    };

    chart.interval = function(_) {
        if (!arguments.length) return interval;
        interval = _;
        return chart;
    };

    chart.duration = function(_) {
        if (!arguments.length) return duration;
        duration = _;
        return chart;
    };

    chart.n = function(_) {
        if (!arguments.length) return n;
        n = _;
        return chart;
    };

    return chart;
}
