function histogramChart(update) {
    var margin = {top: 10, right: 30, bottom: 30, left: 30},
        width = 960,
        height = 500;

    var histogram = d3.layout.histogram(),
        x = d3.scale.linear(),
        y = d3.scale.linear(),
        xAxis = d3.svg.axis().scale(x).orient("bottom"),
        yAxis = d3.svg.axis().scale(y).orient("left");

    var interval = 1000;

    function chart(selection) {
        selection.each(function(values) {

            // Compute the histogram.
            data = histogram(values);

            function attrgetter(a){
                return function(x) { return x[a]; };
            }

            var bin_edges = data.map(attrgetter('x'));
            bin_edges.push(bin_edges[bin_edges.length-1] + data[0].dx);

            xAxis.tickValues(bin_edges);

            // Update the x-scale.
            x.domain([d3.min(bin_edges), d3.max(bin_edges)])
                .range([0, width - margin.left - margin.right]);

            // Update the y-scale.
            y.domain([0, d3.max(data, function(d) { return d.y; })])
                .range([height - margin.top - margin.bottom, 0]);

            // Select the svg element, if it exists.
            var svg = d3.select(this).selectAll("svg").data([data]);

            // Otherwise, create the skeletal chart.
            var gEnter = svg.enter().append("svg").append("g");
            gEnter.append("g").attr("class", "bars");
            gEnter.append("g").attr("class", "x axis");
            gEnter.append("g").attr("class", "y axis");

            // Update the outer dimensions.
            svg.attr("width", width)
                .attr("height", height);

            // Update the inner dimensions.
            var g = svg.select("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Update the bars.
            var bar = svg.select(".bars").selectAll(".bar").data(data);
            bar.enter().append("rect");
            bar.exit().remove();
            bar.attr("width", function(d) { return x(d.dx) - x(0) - 1; })
                .attr("x", function(d) { return x(d.x); })
                .attr("y", function(d) { return y(d.y); })
                .attr("height", function(d) { return y.range()[0] - y(d.y); })
                .order();

            // Update the x-axis.
            g.select(".x.axis")
                .attr("transform", "translate(0," + y.range()[0] + ")")
                .call(xAxis);

            var labels = g.select('.x.axis').selectAll('text');
            while (labels[0].length > 10){
                labels.filter(function(d, i) { return i % 2; }).remove();
                labels = g.select('.x.axis').selectAll('text');
            }

            g.select(".y.axis")
                .call(yAxis);

            setInterval(function() {
                update().done(redraw);
            },interval);

            function redraw(result) {
                // Update the bars.
                data = histogram(result.values);
                bar.data(data)
                    .transition()
                    .duration(1000)
                    .attr("y", function(d) { return y(d.y); })
                    .attr("height", function(d) { return y.range()[0] - y(d.y); });
            }

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

    // Expose the histogram's value, range and bins method.
    d3.rebind(chart, histogram, "value", "range", "bins");

    // Expose the x-axis' tickFormat method.
    d3.rebind(chart, xAxis, "tickFormat", "ticks");

    return chart;
}
