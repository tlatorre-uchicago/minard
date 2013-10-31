function bar_chart() {
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 960 - margin.left - margin.right,
        height = 120 - margin.top - margin.bottom;

    var svg;

    function chart(selection) {
        selection.each(function(data) {
        var x = d3.scale.ordinal().rangeRoundBands([0,width],0.1)
            .domain(data.x);
        var y = d3.scale.linear().range([height,0])
            .domain([0,d3.max(data.y)]);

        var x_axis = d3.svg.axis().scale(x).orient('bottom');
        var y_axis = d3.svg.axis().scale(y).orient('left');

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
        }

        var bars = svg.selectAll('.bar')
            .data(data.y);

        bars.enter().append('rect')
            .attr('class', 'bar')
            .attr('x', function(d, i) { return x(data.x[i]); })
            .attr('width', x.rangeBand())
            .attr('y', function(d) { return y(d); })
            .attr('height', function(d) { return height - y(d); });

        bars.transition()
            .attr('x', function(d, i) { return x(data.x[i]); })
            .attr('width', x.rangeBand())
            .attr('y', function(d) { return y(d); })
            .attr('height', function(d) { return height - y(d); });

        bars.exit().transition().remove();

       });}

    return chart;
}
