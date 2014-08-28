var chart = histogram().xlabel('NHit').margin({'left': 50}).bins(100);
var chart_log = histogram().xlabel('NHit').margin({'left': 50}).bins(100).log(true);

function update_chart(selector, seconds, update) {
    $.getJSON($SCRIPT_ROOT + '/query', {'name': 'nhit', 'seconds': seconds}, function(reply) {
        d3.select(selector).datum(reply.value).call(chart);
        d3.select(selector + '-log').datum(reply.value).call(chart_log);
    });
    setTimeout(function() { update_chart(selector, seconds, update); }, update*1000);
}
