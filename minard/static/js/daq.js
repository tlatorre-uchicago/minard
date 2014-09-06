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

function metric(timeseries, crate, card, channel) {
    var label;
    if (card === null)
        label = 'crate ' + crate;
    else if (channel == null)
        label = 'card ' + card;
    else
        label = 'channel ' + channel;

    return timeseries.context.metric(function(start, stop, step, callback) {
        var params = {
            name: timeseries.source,
            start: start.toISOString(),
            stop: stop.toISOString(),
            now: new Date().toISOString(),
            step: 5,
            crate: crate,
            card: card,
            channel: channel,
            method: timeseries.method
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

function draw(timeseries) {
    // create a horizon from timeseries.context and draw horizons
    if (timeseries.horizon) {
        d3.select(timeseries.target).selectAll('.horizon')
        .call(timeseries.horizon.remove)
        .remove();
        }

    timeseries.horizon = timeseries.context.horizon()
        .height(20)
        .colors(timeseries.scale.range().concat(timeseries.scale.range()))
        .extent(timeseries.scale.domain())
        .format(timeseries.format);

    var horizons = d3.select(timeseries.target).selectAll('.horizon')
        .data(timeseries.metrics)
      .enter().insert('div','.bottom')
          .attr('class', 'horizon')
          .call(timeseries.horizon);

    if (timeseries.click)
        horizons.on('click', timeseries.click);
    }

function update_metrics(timeseries, crate, card) {
    if (timeseries.context != null)
        timeseries.context.stop();

        timeseries.context = create_context(timeseries.target);
    timeseries.metrics = [];

    if (typeof crate === 'undefined') {
        for (var i=0; i < 19; i++)
            timeseries.metrics[i] = metric(timeseries, i, null, null);
    } else if (typeof card === 'undefined') {
        for (var i=0; i < 16; i++)
            timeseries.metrics[i] = metric(timeseries, crate, i, null);
    } else {
        for (var i=0; i < 32; i++)
            timeseries.metrics[i] = metric(timeseries, crate, card, i);
    }
}

si_format = d3.format('.2s');

function format(d) {
    if (d == null)
        return '-';
    else
        return si_format(d);
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

function switch_to_crate(crate) {
    card.crate(crate);
    d3.select('#card').call(card);
    $('#card-heading').text('Crate ' + crate);
    $('.carousel').carousel('next');

    update_metrics(blah, crate);
    draw(blah);
    blah.crate = crate;
}

function switch_to_channel(crate, card) {
    $('#channel-heading').text('Crate ' + crate + ', Card ' + card);
    $('#carousel').carousel('next');
    update_metrics(channelts, crate, card);
    channelts.crate = crate;
    channelts.card = card;
    draw(channelts);
}

var spam = {
target: '#timeseries',
source: $('#data-source').val(),
method: $('#data-method').val(),
context: null,
horizon: null,
scale: null,
metrics:null,
format: format,
click: function(d, i) {
    switch_to_crate(i);
    }
}
    
var blah = {
target: '#timeseries-card',
source: $('#data-source').val(),
method: $('#data-method').val(),
context: null,
horizon: null,
scale: null,
metrics:null,
format: format,
click: function(d, i) {
    switch_to_channel(blah.crate, i);
    }
}
    
var channelts = {
target: '#timeseries-channel',
source: $('#data-source').val(),
method: $('#data-method').val(),
context: null,
horizon: null,
scale: null,
metrics:null,
format: format,
}

function setup() {
    source = $('#data-source').val();
    method = $('#data-method').val();

    var thresholds = default_thresholds[source];

    scale = d3.scale.threshold()
        .domain(thresholds)
        .range(colorbrewer['YlOrRd'][3]);

    spam.scale = scale;
    update_metrics(spam);
    draw(spam);

    blah.scale = scale;
    channelts.scale = scale;

    // set default thresholds in text area
    $('#threshold-lo').val(thresholds[0])
    $('#threshold-hi').val(thresholds[1])

    card = card_view()
        .scale(scale);

    crate = crate_view()
        .scale(scale)
        .click(function(d, i) {
            switch_to_crate(i);
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
    update_metrics(spam);
    draw(spam);
    blah.method = this.value;
    update_metrics(blah);
    if (blah.context)
        draw(blah);
    channelts.method = this.value;
    if (channelts.context)
        draw(channelts);
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
    update_metrics(spam);
    draw(spam);
    blah.source = this.value;
    blah.scale.domain(thresholds);
    update_metrics(blah, blah.crate);
    if (blah.context)
        draw(blah);
    channelts.source = this.value;
    channelts.scale.domain(thresholds);
    update_metrics(channelts, channelts.crate, channelts.card);
    if (channelts.context)
        draw(channelts);
});

$('#threshold-lo').keypress(function(e) {
    if (e.which == 13) {
        spam.scale.domain([this.value,scale.domain()[1]]);
        draw(spam);
        blah.scale.domain([this.value,scale.domain()[1]]);
        draw(blah);

        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

$('#threshold-hi').keypress(function(e) {
    if (e.which == 13) {
        spam.scale.domain([scale.domain()[0],this.value]);
        draw(spam);
        blah.scale.domain([scale.domain()[0],this.value]);
        draw(blah);

        d3.select("#crate").call(crate);
        d3.select("#card").call(card);
    }
});

$('.carousel').on('slide.bs.carousel', function(e) {
    var slide = $(e.relatedTarget).index();
    if (slide == 3) {
        spam.context.stop();
        blah.context.stop();
        if (baz.context)
            baz.context.start();
    } else if (slide == 1) {
        // card slide
        spam.context.stop();
        if (blah.context)
            blah.context.start();
        if (channelts.context)
            channelts.context.start();
    } else if (slide == 0) {
        // crate slide
        blah.context.stop();
        spam.context.start();
        channelts.context.stop();
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
