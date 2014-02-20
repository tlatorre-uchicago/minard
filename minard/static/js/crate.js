function createArray(length) {
    var arr = new Array(length || 0),
        i = length;

    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while(i--) arr[length-1 - i] = createArray.apply(this, args);
    }

    return arr;
}

var crate_setup = createArray(19,32,16);

for (var i=0; i < 19; i++) {
    for (var j=0; j < 32; j++) {
        for (var k=0; k < 16; k++) {
            crate_setup[i][31-j][k] = (i << 16) | (k << 8) | j;
        }
    }
}

function card_view() {
    var svg;
    var crate = 12;
    var threshold = null;

    var format = d3.format('.0f');

    function chart(selection) {
        selection.each(function(data) {
            var root = d3.select(this).selectAll('table').data([crate], function(d) { return d; });
            root.exit().remove();
            var table = root.enter().append('div').attr('id','card-view').append('table')
                .attr('style','padding:2px;border-collapse:separate;border-spacing:1px');

            var setup = crate_setup[crate];

            var tr2 = table.selectAll('tr')
                .data(setup)
                .enter().append('tr');

            table.insert('tr',':first-child').selectAll('td').data(d3.range(17)).enter().append('td')
              .text(function(d, i) {
                if (i) {
                  return i-1;
                } else {
                  return '';
                }
              })
              .attr('class','card-label-col');

            var td = tr2.selectAll('td')
                .data(function(d) { return d; }, function(d) { return d; })
                .enter().append('td')
                .attr('id','channel')
                .attr('style','background-color:#e0e0e0')
                .attr('title', function(d) {
                    return 'Card ' + ((d >> 8) & 0xff) + ', Channel ' + (d & 0xff);});

            tr2.insert('td',':first-child').text(function(d, i) { return 31-i; })
              .attr('class','card-label-row');

            var k = [],
                v = [];

            for (var key in data) {
                k.push(key);
                v.push(data[key]);
            }

            var select = d3.select(this).selectAll('#channel')
                .data(k, function(d) { return d; });

            select.attr('style', function(d, i) {
                return (v[i] > threshold) ? 'background-color:#ca0020' : 'background-color:#bababa';
                })
                .text(function(d, i) { return format(v[i]); });

            select.exit().attr('style','background-color:#e0e0e0')
                .text(function() { return '';});
           });}

   chart.crate = function(value) {
       if (!arguments.length) return crate;
       crate = value;
       return chart;
   }
   
   chart.threshold = function(value) {
       if (!arguments.length) return threshold;
       threshold = value;
       return chart;
   }

   chart.format = function(value) {
       if (!arguments.length) return format;
       format = value;
       return chart;
   }
   return chart;
}

function crate_view() {
    var margin = {top: 20, right: 25, bottom: 50, left: 25},
        width = null,
        height = null;

    var threshold = null;

    var svg;

    var click = function(d, i) { return; };

    function chart(selection) {
        selection.each(function(data) {
        if (width === null)
            width = $(this).width() - margin.left - margin.right;

        if (height === null)
            height = Math.round(width/1.6) - margin.top - margin.bottom;

        var root = d3.select(this).selectAll('div').data([1]);

        var table = root.enter().append('div').attr('id','crate-view');

        var tr1 = table.selectAll('div')
            .data(crate_setup)
            .enter()
          .append('div')
            .on('click', click)
            .attr('style','float:left')
          .append('table')
            .attr('style','padding:2px;border-collapse:separate;border-spacing:1px')
            .attr('title', function(d, i) { return 'Crate ' + i; });

            tr1.insert('caption').text(function(d, i) { return i; })

        var tr2 = tr1.selectAll('tr')
            .data(function(d) { return d; })
            .enter().append('tr');

        var td = tr2.selectAll('td')
            .data(function(d) { return d; }, function(d) { return d; })
            .enter().append('td')
            .attr('style','background-color:#e0e0e0');

        var k = [],
            v = [];

        for (var key in data) {
            k.push(key);
            v.push(data[key]);
        }

        var select = d3.select(this).selectAll('#crate-view div table tr td')
            .data(k, function(d) { return d; });

        select.attr('style', function(d, i) {
            return (v[i] > threshold) ? 'background-color:#ca0020' : 'background-color:#bababa';
            });

        select.exit().attr('style','background-color:#e0e0e0');
       });}

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

       chart.click = function(value) {
           if (!arguments.length) return click;
           click = value;
           return chart;
       }

       chart.threshold = function(value) {
           if (!arguments.length) return threshold;
           threshold = value;
           return chart;
       }

    return chart;
}
