function timeSeries(url) {

    var margin = {top: 6, right: 0, bottom: 20, left: 40},
        width = 960 - margin.right,
        height = 120 - margin.top - margin.bottom;

    var n = 243,
        duration = 750;

    function chart(selection) {
        selection.each(function(name) {

            var now = new Date(Date.now() - duration);

            var element = this;

            $.getJSON(url, {'name': name + 'hello',
                            'first': now - (n - 2) * duration,
                            'last': now - duration,
                            'npoints': n})
                .done(plot)
                .fail(function(_, __, err) {alert(err);});

            function plot(response) {

                var data = response.data;

                var x = d3.time.scale()
                        .domain([now - (n - 2) * duration, now - duration])
                        .range([0, width]);

                var y = d3.scale.linear()
                    .domain([d3.min(data),d3.max(data)])
                    .range([height, 0]);

                var line = d3.svg.line()
                    .interpolate("basis")
                    .x(function(d, i) {
                        return x(now - (n - 1 - i) * duration); })
                    .y(function(d, i) { return y(d); });

                var svg = d3.select(element).append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .style("margin-left", -margin.left + "px")
                  .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                svg.append("defs").append("clipPath")
                    .attr("id", "clip")
                  .append("rect")
                    .attr("width", width)
                    .attr("height", height);

                var axis = svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(x.axis = d3.svg.axis().scale(x).orient("bottom"));

                var path = svg.append("g")
                    .attr("clip-path", "url(#clip)")
                  .append("path")
                    .data([data])
                    .text(String(data))
                    .attr("class", "line");

                var update = function(){
                    return $.getJSON(url,{'name': name + 'world',
                                          'last': null});
                }

                setInterval(function(){
                        update()
                            .done(tick)
                            .fail(function(_, __, err) { alert(err);});
                },duration);

                function tick(response) {
                    var value = response.value;

                    // update the domains
                    now = new Date();
                    x.domain([now - (n - 2) * duration, now - duration]);
                    y.domain([d3.min(data), d3.max(data)]);

                    // push the accumulated count onto the back, and reset the count
                    data.push(value);

                      // redraw the line
                      svg.selectAll(".line")
                          .attr("d", line)
                          .attr("transform", null);

                      // slide the x-axis left
                      axis.transition()
                          .duration(duration)
                          .ease("linear")
                          .call(x.axis);

                      // slide the line left
                      path.transition()
                          .duration(duration)
                          .ease("linear")
                          .attr("transform", "translate(" + x(now - (n - 1) * duration) + ")")
                            //.each("end", tick);

                      // pop the old data point off the front
                      data.shift();
                }
            }
        });
    }
    return chart;
}