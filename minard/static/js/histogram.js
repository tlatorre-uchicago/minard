function histogram() {
    var margin = {top: 20, right: 25, bottom: 50, left: 50},
        width = null,
        height = null,
        xlabel = '',
        ylabel = '',
        nbins = 20,
        color = function(x) { return "steelblue" };

    function chart(selection) {
        selection.each(function(values) {
            if (width === null)
                width = $(this).width() - margin.left - margin.right;

            if (height === null)
                height = Math.round(width/1.6) - margin.top - margin.bottom;

            if (typeof this.x === "undefined")
            {
                var x = d3.scale.linear()
                    .domain([d3.min(values), d3.max(values)])
                    .range([0,width]);
                this.x = x;
            }

            x = this.x;

            var data = d3.layout.histogram()
                .bins(x.ticks(nbins))
                (values);

            var y = d3.scale.linear()
                .domain([0,d3.max(data, function(d) { return d.y; })])
                .range([height,0]);

            var x_axis = d3.svg.axis()
                .scale(x)
                .orient("bottom");

            var y_axis = d3.svg.axis()
                .scale(y)
                .orient("left");

            var svg = d3.select(this).selectAll("svg").data([1]);

            var genter = svg.enter().append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom)
                    .attr('pointer-events','all')
                  .append('g')
                    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            var element = this;

            genter.append('g').attr('class', 'x axis').attr('id','x-axis')
                .attr('transform', 'translate(0,' + height + ')')
                .call(x_axis);

            genter.append('g').attr('class', 'y axis').attr('id','y-axis')
                .call(y_axis);

            genter.append("rect")
                .attr("fill","white")
                .attr("width",width)
                .attr("height",height);

            genter.append('text')
                .attr('class', 'x label')
                .attr('text-anchor', 'middle')
                .attr('x', width/2)
                .attr('y', height + margin.bottom)
                .text(xlabel);

            genter.append('text')
                .attr('class', 'y label')
                .attr('text-anchor', 'end')
                .attr('y', 6)
                .attr('dy', '.75em')
                .attr('transform', 'rotate(-90)')
                .text(ylabel);

            draw();

            svg.selectAll('g').selectAll('rect,#x-axis,#y-axis')
                .on('mousedown', function(d) { 
                    mouse_down = d3.mouse(element);
                    var x_down = d3.scale.linear().domain(x.domain()).range([0,width]);

                    d3.event.preventDefault();

                    d3.select(window)
                        .on('mousemove', function(d) {
                            if (x_down !== null) {
                                var mouse = d3.mouse(element);
                                var scale = (x_down(mouse_down[0])/x_down(mouse[0]))
                                x.domain([0,x_down.domain()[1]*scale]);
                                draw();
                            }
                        d3.event.preventDefault();
                        })
                        .on('mouseup', function(d) {
                            if (x_down !== null) {
                                var mouse = d3.mouse(element);
                                var scale = (x_down(mouse_down[0])/x_down(mouse[0]))
                                x.domain([0,x_down.domain()[1]*scale]);
                                draw();
                            }
                            x_down = null;
                            d3.select(window).on('mouseup',null);
                            d3.select(window).on('mousemove',null);
                        });
                });

            function draw() {
                var data = d3.layout.histogram()
                    .bins(x.ticks(nbins))
                    (values);

                var y = d3.scale.linear()
                    .domain([0,d3.max(data, function(d) { return d.y; })])
                    .range([height,0]);

                var x_axis = d3.svg.axis()
                    .scale(x)
                    .orient("bottom");

                var y_axis = d3.svg.axis()
                    .scale(y)
                    .orient("left");

                var g = svg.select('g')

                g.select('.x.axis').transition().call(x_axis);
                g.select('.y.axis').transition().call(y_axis);

                g.select('.x.label').transition().text(xlabel);
                g.select('.y.label').transition().text(ylabel);

                var bar = g.selectAll('.hist-bar')
                    .data(data);

                bar.transition()
                    .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; })
                    .attr("fill", function(d) { return color(d.x); })
                    .attr('width', x(data[0].dx) - 1)
                    .attr('height', function(d) { return height - y(d.y); })
                    .style({opacity: 1});

                bar.enter().append("rect")
                    .attr("class", "hist-bar")
                    .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; })
                    .attr("fill", function(d) { return color(d.x); })
                    .attr("x", 1)
                    .attr('width', x(data[0].dx) - 1)
                    .attr('height', function(d) { return height - y(d.y); })
                    .style({opacity: 1});

                bar.exit().transition().style({opacity: 0}).remove();
            }
        });
    }

    chart.color = function(value) {
        if (!arguments.length) return color;
        color = value;
        return chart;
    }

    chart.height = function(value) {
        if (!arguments.length) return height;
        height = value;
        return chart;
    }

    chart.width = function(value) {
        if (!arguments.length) return width;
        width = value;
        return chart;
    }

    chart.margin = function(value) {
        if (!arguments.length) return margin;
        for (var k in value)
            margin[k] = value[k];
        return chart;
    }
         
    chart.xlabel = function(value) {
        if (!arguments.length) return xlabel;
        xlabel = value;
        return chart;
    }

    chart.ylabel = function(value) {
        if (!arguments.length) return ylabel;
        ylabel = value;
        return chart;
    }

    return chart;
}
