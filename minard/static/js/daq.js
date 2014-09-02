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

if (threshold > 1000) {
    card = card.format(d3.format('.2s'));
}

$('#threshold').val(crate.threshold());

// Set threshold when <Enter> key is pressed
$('#threshold').keyup(function(event) {
  if (event.keyCode == 13) {
    crate.threshold($('#threshold').val());
    card.threshold($('#threshold').val());
    update();
  }
});
                    
function warn(jqxhr, text_status, error) {
    var err = text_status + ', ' + error;
    $('#status').text(err).attr('class', 'alert alert-warning');
}

function success() {
    $('#status').attr('class', 'alert alert-success').text('Connected');
}

var interval = 5000;

function update() {
    var name = $('#data-source').val();
    $.getJSON($SCRIPT_ROOT + '/query', {name: name, stats: $('#stats').val()})
        .done(function(result) {
            d3.select('#crate').datum(result.values).call(crate);
            d3.select('#card').datum(result.values).call(card);
            success()
        }).fail(warn);
}

d3.select('#crate').datum([]).call(crate);
d3.select('#card').datum([]).call(card);
// wrap first ten and last ten crates in a div
$('#crate' + [0,1,2,3,4,5,6,7,8,9].join(',#crate')).wrapAll('<div />');
$('#crate' + [10,11,12,13,14,15,16,17,18,19].join(',#crate')).wrapAll('<div />');
update();
setInterval(update,interval);
