function create_context(target) {
    var scale = tzscale().zone('America/Toronto');

    var size = $(target).width();
    var context = cubism.context(scale)
        .serverDelay(2e3)
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

    // delete old axes
    $(target + ' .axis').remove();

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

    // delete old rule
    $(target + ' .rule').remove();

    d3.select(target).append("div")
        .attr("class", "rule")
        .call(context.rule());

    return context;
}

function metric(context, name, crate, card, channel, method) {
    method = typeof method === 'undefined' ? 'avg' : method;

    var label;
    if (card === null)
        label = 'crate ' + crate;
    else if (channel == null)
        label = 'card ' + card;
    else
        label = 'channel ' + channel;

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
    }, label);
}

function create_horizons(target, context, metrics) {
    var horizon = context.horizon()
        .height(20)
        // horizon needs 2x the colors for positive and negative
        .colors(scale.range().concat(scale.range()))
        .extent(scale.domain())
        .format(function(n) {
            if (n == null)
                return '-';
            else
                return d3.format('.2s')(n);
            }
        );

    $(target + ' .horizon').remove();

    var horizons = d3.select(target).selectAll('.horizon')
        .data(metrics);
    // remove old divs
    //horizons.exit().remove();

    // add time series
    horizons.enter().insert('div','.bottom')
        .attr('class', 'horizon')
        .call(horizon);
}

var default_thresholds = {
    cmos: [100,2e3],
    base: [10, 80],
    occupancy: [0.001, 0.002]
}

function set_thresholds(lo, hi) {
    // set thresholds text area
    $('#threshold-lo').val(lo)
    $('#threshold-hi').val(hi)
}

var spam = {
target: '#timeseries',
source: $('#data-source').val(),
method: $('#data-method').val(),
context: null,
scale: null,
metrics:null,
update: function () {
    this.context.stop();
    this.context = create_context(this.target);
    this.metrics = [];
    for (var i=0; i < 20; i++) {
        this.metrics[i] = metric(this.context, this.source, i, null, null, this.method);
    }
    create_horizons(this.target, this.context, this.metrics);
}
}
    
var blah = {
target: '#timeseries-card',
source: $('#data-source').val(),
method: $('#data-method').val(),
context: null,
scale: null,
metrics:null,
crate: 0,
update: function () {
    if (this.context !== null)
        this.context.stop();
    this.context = create_context(this.target);
    this.metrics = [];
    for (var i=0; i < 16; i++) {
        this.metrics[i] = metric(this.context, this.source, this.crate, i, null, this.method);
    }
    create_horizons(this.target, this.context, this.metrics);
}
}
    
function setup() {
    source = $('#data-source').val();
    method = $('#data-method').val();

    var thresholds = default_thresholds[source];

    scale = d3.scale.threshold()
        .domain(thresholds)
        .range(colorbrewer['YlOrRd'][3]);

    spam.context = create_context('#timeseries');
    spam.scale = scale;

    spam.metrics = [];
    for (var i=0; i < 20; i++) {
        spam.metrics[i] = metric(spam.context, spam.source, i, null, null, spam.method);
    }

    create_horizons(spam.target, spam.context, spam.metrics);

    // set default thresholds in text area
    $('#threshold-lo').val(thresholds[0])
    $('#threshold-hi').val(thresholds[1])

    card = card_view()
        .scale(scale);

    crate = crate_view()
        .scale(scale)
        .click(function(d, i) {
            card.crate(i);
            d3.select('#card').call(card);
            $('#card-heading').text('Crate ' + i);
            $('#carousel').carousel('next');

            blah.crate = i;
            blah.update();
        });

    if (source == 'cmos') {
        card.format(d3.format('.2s'));
    } else if (source == "occupancy") {
        card.format(d3.format('.0e'));
    } else {
        card.format(d3.format());
    }
}

setup();

$('#data-method').change(function() {
    spam.method = this.value;
    spam.update();
    blah.method = this.value;
    blah.update();
});

$('#data-source').change(function() {
    if (this.value == 'cmos') {
        card.format(d3.format('.2s'));
    } else if (this.value == "occupancy") {
        card.format(d3.format('.0e'));
    } else {
        card.format(d3.format());
    }

    // update threshold values
    var thresholds = default_thresholds[this.value];
    set_thresholds.apply(this,thresholds);
    // update color scale
    scale.domain(thresholds);
    update();

    // update source, scale, and redraw
    spam.source = this.value;
    spam.scale.domain(thresholds);
    spam.update();
    blah.source = this.value;
    blah.scale.domain(thresholds);
    blah.update();
});

$('#threshold-lo').keypress(function(e) {
    if (e.which == 13) {
        spam.scale.domain([this.value,scale.domain()[1]]);
        spam.update();
        blah.scale.domain([this.value,scale.domain()[1]]);
        blah.update();

        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

$('#threshold-hi').keypress(function(e) {
    if (e.which == 13) {
        spam.scale.domain([scale.domain()[0],this.value]);
        spam.update();
        blah.scale.domain([scale.domain()[0],this.value]);
        blah.update();

        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
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
