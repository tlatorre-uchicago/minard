function create_context(target) {
    var scale = tzscale().zone('America/Toronto');

    var size = $(target).width();
    var context = cubism.context(scale)
        .serverDelay(1e3)
        .clientDelay(1e3)
        .step(5e3)
        .size(size);

    function format_seconds(date) {
        return moment.tz(date, 'America/Toronto').format('hh:mm:ss');
    }

    function format_minutes(date) {
        return moment.tz(date, 'America/Toronto').format('hh:mm');
    }

    function format_day(date) {
        return moment.tz(date, 'America/Toronto').format('MMMM DD');
    }

    if (context.step() < 6e4) {
        focus_format = format_seconds;
    } else if (context.step() < 864e5) {
        focus_format = format_minutes;
    } else {
        focus_format = format_day;
    }

    // add time axes
    d3.select(target).selectAll(".axis")
        .data(["top", "bottom"])
      .enter().append("div")
        .attr("class", function(d) { return d + " axis"; })
        .each(function(d) {
            var axis = context.axis()
                .ticks(12)
                .orient(d)
                .focusFormat(focus_format)
            d3.select(this).call(axis);
        });

    d3.select(target).append("div")
        .attr("class", "rule")
        .call(context.rule());

    return context;
}

function metric(context, name, crate, card, channel, method) {
    method = typeof method === 'undefined' ? 'avg' : method;

    return context.metric(function(start, stop, step, callback) {
        var params = {
            name: name,
            start: start.toISOString(),
            stop: stop.toISOString(),
            now: new Date().toISOString(),
            step: 5,
            crate: crate,
            card: card,
            channel: channel,
            method: method
        }

        d3.json($SCRIPT_ROOT + '/metric_hash?' + $.param(params),
            function(data) {
                if (!data)
                    return callback(new Error('unable to load data'));

                return callback(null,data.values);
            }
        );
    }, name);
}

var source = $('#data-source').val();
var method = $('#data-method').val();
var context = create_context('#tscrate');

// crate metrics
crate_metrics = [];
for (var i=0; i < 20; i++) {
    crate_metrics[i] = metric(context, source, i, null, null, method);
}

var horizon = context.horizon().height(20);

// add time series
d3.select('#tscrate').selectAll('.horizon')
    .data(crate_metrics)
  .enter().insert('div','.bottom')
    .attr('class', 'horizon')
    .call(horizon);

var threshold=1000;

var colors = colorbrewer['YlOrRd'][3];
var scale = d3.scale.threshold().domain([0.001,0.002]).range(colors);

$('#data-source').change(function() {
    var source = $('#data-source').val();
    if (source == 'cmos') {
        card.format(d3.format('.2s'));
    } else if (source == "occupancy") {
        card.format(d3.format('.0e'));
    } else {
        card.format(d3.format());
    }
    update();
});

$('#threshold-lo').keypress(function(e) {
    if (e.which == 13) {
        scale.domain([$('#threshold-lo').val(),scale.domain()[1]]);
        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

$('#threshold-hi').keypress(function(e) {
    if (e.which == 13) {
        scale.domain([scale.domain()[0],$('#threshold-hi').val()]);
        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

var card = card_view()
    .threshold(threshold)
    .scale(scale);

var crate = crate_view()
    .threshold(threshold)
    .scale(scale)
    .click(function(d, i) {
        card.crate(i);
        d3.select('#card').call(card);
        $('#card h4 small').text('Crate ' + i);
        $('#carousel').carousel('next');
    });

var interval = 5000;

function update() {
    var name = $('#data-source').val();
    $.getJSON($SCRIPT_ROOT + '/query', {name: name, stats: $('#stats').val()})
        .done(function(result) {
            d3.select('#crate').datum(result.values).call(crate);
            d3.select('#card').datum(result.values).call(card);
        });
}

d3.select('#crate').datum([]).call(crate);
d3.select('#card').datum([]).call(card);
// wrap first ten and last ten crates in a div
$('#crate' + [0,1,2,3,4,5,6,7,8,9].join(',#crate')).wrapAll('<div />');
$('#crate' + [10,11,12,13,14,15,16,17,18,19].join(',#crate')).wrapAll('<div />');
update();
setInterval(update,interval);
