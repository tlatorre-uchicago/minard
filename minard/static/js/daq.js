var threshold = Number(url_params['threshold']);
var name = url_params['name'];

var card = card_view().threshold(threshold);

if (threshold > 1000) {
    card = card.format(d3.format('.2s'));
}

var crate = crate_view().threshold(threshold);
crate.click(function(d, i) {
    card.crate(i);
    d3.select('#card').call(card);
    $('#card h4 small').text('Crate ' + i);
})

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
    $.getJSON($SCRIPT_ROOT + '/query', {name: name, stats: $('#stats').val()})
        .done(function(result) {
            d3.select('#crate').datum(result.value).call(crate);
            d3.select('#card').datum(result.value).call(card);
            success()
        }).fail(warn);
}

d3.select('#crate').datum([]).call(crate);
d3.select('#card').datum([]).call(card);
update();
setInterval(update,interval);
