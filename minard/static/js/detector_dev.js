function linspace(min, max, N) {
    var a = [];
    for (var i=0; i < N; i++) {
        a[i] = min + (max-min)*i/(N-1);
    }
    return a;
}

var xsnoed1 = ["#4876ff","#32cd32","#ffff00","#ffa500","#ff0000"],
    xsnoed2 = ["#3a5fcd","#2e8b57","#cd9b1d","#ffa500","#ff0000"];

var color_scales = {};
color_scales.xsnoed1 = xsnoed1;
color_scales.xsnoed2 = xsnoed2;
for (var key in colorbrewer) {
    color_scales[key] = colorbrewer[key][5];
}

color_scales = d3.entries(color_scales);

var color_scale = d3.scale.linear()
    .domain(linspace(0,20000,10))
    .range(color_scales[12].value);

var color_scale_base = d3.scale.linear()
    .domain(linspace(0,150,3))
    .range(color_scales[12].value);

var chart = histogram()
    .on_scale_change(redraw)
    .color_scale(color_scale)
    .bins(50)
    .domain([0,0.01]);

var crate_cmos = crate_view().scale(color_scale)
                             .click(function(d,i) {
                                 switch_to_crate(i);
                             });

var card_cmos = card_view().scale(color_scale);

var crate_base = crate_view().scale(color_scale_base);

var element = $('#hero');
var width   = element.width();
var height  = width/2.0;

var svg = d3.select('#hero').append("svg")
    .attr("width", width)
    .attr("height", height);


function redraw() {
    d3.select("#crate").call(crate_cmos);
    //d3.select("#crate_test").call(crate_base); 
}

function setup() {

    // set up crate view
    d3.select("#crate").datum([]).call(crate_cmos);

    // line break after crate 9 to get
    // XSNOED style
    $("#crate9").after("<br>"); 
}

function update_cmos(result) {
    $.getJSON($SCRIPT_ROOT + '/query_polling', { type: 'cmos' }).done(function(result) {
        values_cmos = result.values;

        d3.select('#crate').datum(values_cmos).call(crate_cmos);
        //d3.select('#card').datum(values_cmos).call(card);

        redraw();
    });
}

function update_base(result) {
    $.getJSON($SCRIPT_ROOT + '/query_polling', { type: 'base' }).done(function(result) {
        values_base = result.values;

        d3.select('#crate_test').datum(values_base);

        redraw();
    });
}

function switch_to_crate(crate) {

    card.crate(crate)
    d3.select('#card').call(card_cmos);
    $('#card-7').after('<tr></tr>');
    $('#card-15').after('<tr></tr>');
    $('#card-23').after('<tr></tr>');
}

/*
click: function(d, i) {
    if ((i > 0) && (i <= 20))
        switch_to_crate(i-1);
};
*/
