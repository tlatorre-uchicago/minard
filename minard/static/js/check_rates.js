function linspace(min, max, N) {
    var a = [];
    for (var i=0; i < N; i++) {
        a[i] = min + (max-min)*i/(N-1);
    }
    return a;
}

var color_scales = {};
for (var key in colorbrewer) {
    color_scales[key] = colorbrewer[key][5];
}

color_scales = d3.entries(color_scales);

var color_scale_cmos = d3.scale.linear()
    .domain(linspace(0,20000,10))
    .range(color_scales[12].value);

var color_scale_base = d3.scale.linear()
    .domain(linspace(0,120,3))
    .range(color_scales[12].value);

var crate = crate_view();
var crate_cmos = crate_view().scale(color_scale_cmos);
var crate_base = crate_view().scale(color_scale_base);

var card_cmos = card_view().scale(color_scale_cmos);
var card_base = card_view().scale(color_scale_base);


var element = $('#hero');
var width   = element.width();
var height  = width/2.0;

var svg = d3.select('#hero').append("svg")
    .attr("width", width)
    .attr("height", height);


function setup() {

    // set up crate view
    d3.select("#crate").datum([]).call(crate);

    // line break after crate 9 to get
    // XSNOED style
    $("#crate9").after("<br>"); 

}

function update(dtype) {
    $.getJSON($SCRIPT_ROOT + '/query_polling', { type: dtype }).done(function(result) {
        values = result.values;

        if(dtype == "cmos"){
            d3.select('#crate').datum(values).call(crate_cmos);
        }
        else if(dtype == "base"){
            d3.select('#crate').datum(values).call(crate_base);
        }

    });
}

function update_card(dtype, c) {
    $.getJSON($SCRIPT_ROOT + '/query_polling_card', { type: dtype, crate: c }).done(function(result) {
        values = result.values;

        if(dtype == "cmos"){
            d3.select('#card').datum(values).call(card_cmos);
        }
        if(dtype == "base"){
            d3.select('#card').datum(values).call(card_base);
        }

    });
}

