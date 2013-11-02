function bar_chart() {
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 960 - margin.left - margin.right,
        height = 220 - margin.top - margin.bottom;

    var svg;

    var click = function(d, i) { return; };
    var click_bg = function() { return; };

    var layout = function(data) {
        var bins = [];
        for (var key in data) {
            var i = bins.push(Object());
            bins[i-1].x = key;
            bins[i-1].y = data[key];
        }
        return bins;
    }

    function chart(selection) {
        selection.each(function(data) {
        data = layout(data);

        var data_x = data.map(function(d) { return d.x; }),
            data_y = data.map(function(d) { return d.y; });

        var x = d3.scale.ordinal()
            .rangeRoundBands([0,width],0.1)
            .domain(data_x);

        var y = d3.scale.linear()
            .range([height,0])
            .domain([0,d3.max(data_y)]);

        var x_axis = d3.svg.axis().scale(x).orient('bottom');
        var y_axis = d3.svg.axis().scale(y).orient('left');

        if (data[0].hasOwnProperty('dx')) {
            // histogram
            //x = d3.scale.linear()
            //    .range([0,width])
            //    .domain([d3.min(data_x), d3.max(data_x)]);
            //var bin_edges = data_x.slice(0);
            //bin_edges.push(data[data.length-1].x + data[data.length-1].dx);
            //x_axis.tickValues(bin_edges);
        }

        if (!svg) {
            svg = d3.select(this).append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
              .append('g')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            svg.append('g').attr('class', 'x axis')
                .attr('transform', 'translate(0,' + height + ')')
                .call(x_axis);

            svg.append('g').attr('class', 'y axis').call(y_axis);

            svg.append('rect')
                .attr('fill', 'white')
                .attr('width', width)
                .attr('height', height)
                .on('click', click_bg);
        }

        svg.select('.x.axis').transition().call(x_axis);
        svg.select('.y.axis').transition().call(y_axis);

        var bars = svg.selectAll('.bar')
            .data(data_x);

        bars.enter().append('rect')
            .attr('class', 'bar')
            .attr('x', width)
            .attr('width', x.rangeBand())
            .attr('y', function(d, i) { return y(data_y[i]); })
	    .attr('height', function(d, i) { return height - y(data_y[i]); })
	    .on('click', click);

        bars.transition()
            .attr('x', function(d, i) { return x(data_x[i]); })
            .attr('width', x.rangeBand())
            .attr('y', function(d, i) { return y(data_y[i]); })
            .attr('height', function(d, i) { return height - y(data_y[i]); });

        bars.exit().transition().style({opacity: 0}).remove();

       });}

       chart.click = function(value) {
           if (!arguments.length) return click;
           click = value;
           return chart;
       }

       chart.click_bg = function(value) {
           if (!arguments.length) return click_bg;
           click_bg = value;
           return chart;
       }

       chart.layout = function(value) {
           if (!arguments.length) return layout;
           layout = value;
           return chart;
       }

    return chart;
}

function histogram_chart() {
    var chart = bar_chart().layout(d3.layout.histogram());
    return chart;
}
