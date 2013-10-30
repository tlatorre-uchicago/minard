function bar_chart() {
    var margin = {top: 6, right: 0, bottom: 20, left: 40},
        width = 960 - margin.right,
        height = 120 - margin.top - margin.bottom;

    function chart(selection) {
        selection.each(function(data) {
        var x = d3.scale.ordinal().rangeRoundBands([0,width]);
        var y = d3.scale.linear().range([height,0]);

        var x_axis = d3.svg.axis().scale(x).orient('bottom');
        var y_axis = d3.svg.axis().scale(y).orient('left');

        var svg = d3.select(this).append('svg')
            .attr('width', width)
            .attr('height', height)

        svg.append('g').attr('class', 'x axis')
            .attr('transform', 'translate(0,' + height + ')')
            .call(x_axis);

        svg.append('g').attr('class', 'y axis').call(y_axis)

        svg.selectAll('.bar')
            .data(data.y)
          .enter().append('rect')
            .attr('class', 'bar')
            .attr('x', function(d) { return x(d.x); })
            .attr('width', x.rangeBand())
            .attr('y', function(d) { return y(d.y); })
            .attr('height', function(d) { return height - y(d.y); });

        });}

    return chart;
}
