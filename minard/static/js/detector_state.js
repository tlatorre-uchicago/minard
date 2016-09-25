function flattenArray(arr) {
    return [].concat.apply([],arr);
}
function display_binary_crate_view(key,crates_data,sizeinfo,node)
{
    var coloringFunc = function(data) {
        return function(k,i) {
        var v = data[k];
        if (v === null || typeof v === 'undefined')
            return 'background-color:#e0e0e0';
        else if (v===0) {
            return 'background-color:grey';
        }
        else
            return 'background-color:green';
    };}

    display_crate_view(key,crates_data,sizeinfo,node,coloringFunc);
}
function display_continuous_crate_view(key,crates_data,sizeinfo,node)
{
    // For now this just assumes a linear scale from 0-255.
    // May have to generalize at some point.
    var scale = d3.scale.linear().domain([0,255]).range(['#6666ff','#ff0000']);
    var coloringFunc = function(data) {
        return function(k, i) {
            var v = data[k];
            if (v === null || typeof v === 'undefined') {
                return 'background-color:#e0e0e0';
            }
            else {

                return 'background-color:' + scale(+v);
    }};}
    display_crate_view(key,crates_data,sizeinfo,node,coloringFunc);
}
function display_crate_view(key,crates_data,sizeinfo,node,coloringFunc)
{
    var d = crates_data.map(function(crate,i) {
    if(crate) {
            MBs =  crate.map(function(mb,i) {
                if(mb) {
                    return mb[key];
                }
                else {
                   return Array.apply(null,Array(32)).map(function(x,i){return null;})
                }
            });
            return  flattenArray(MBs)
        }
        else {
            return Array.apply(null,Array(512)).map(function(x,i){return null;})
        }
    });
    d = flattenArray(d)
    var crate = crate_view()
        .caption(true)
        .height(height)
        .width(width);
    if(coloringFunc){
        crate.coloringFunction(coloringFunc)
    }
    var g = node.append('div')
            .attr('id','crate')
            .attr('width',width)
            .attr('height',height)
            .attr('class',"col-md-10 col-md-offset-1");
    g.datum(d).call(crate);
}
function display_detector_control(detector_control_info) {
    var det_cont = d3.select("#detector_control");
    var bounds = det_cont.node().parentElement.parentElement.clientWidth
    var height = 100;
    var width = bounds;
    var step_size = width/15;
    radius = step_size/4.0;
    var xpos_func = function(d,i) { return step_size+i*step_size; }
    var ypos_func = function(d,i) { return height/2.0; }
    var svg = det_cont.append("svg")
        .attr("width",width)
        .attr("height",height)
        .attr("viewBox","0 0 "+width.toString()+" "+height.toString())
        .attr("class","rack_mask");
    var arr = [];
    arr.push(["T",detector_control_info["timing_rack"]]);
    for(var i=1;i<12;i++) {
        arr.push([i.toString(),detector_control_info["rack"+i.toString()]]);
    }
    svg.selectAll('circle')
        .data(arr)
        .enter()
        .append('circle')
        .attr("cx",xpos_func)
        .attr("cy",ypos_func)
        .attr("r",radius)
        .attr("fill",function(d) { return d[1]==1 ? 'green' : 'red'; })
        .attr("class",function(d) { return d[1]==1 ? 'on' : 'off'; });
    svg.selectAll('text')
        .data(arr)
        .enter()
        .append('text')
        .text(function(d){return d[0];})
        .attr("text-anchor","middle")
        .attr("font-size","16px")
        .attr("fill","white")
        .attr("x",xpos_func)
        .attr("y",function(d,i) { return ypos_func(d,i)+5;});
}
function display_triggers(wordlist) {
    var mtc = d3.select('#mtc');
    display_array_as_list(mtc,wordlist,'Enabled Triggers');
};
function display_ped_delay(delay) {
    var mtc = d3.select('#mtc')
    mtc.append("h3").text("Pedestal Delay = "+ delay.toString() +"ns");

};
function display_lockout_width(lockout) {
    var mtc = d3.select('#mtc')
    mtc.append("h3").text("Lockout Width = "+ lockout.toString()+"ns");
};
function display_control_reg(wordlist) {
    var mtc = d3.select('#mtc')
    display_array_as_list(mtc,wordlist,'Control Register Values');
};
function display_crates(title,crates) {
    var mtc = d3.select('#mtc');
    mtc.append('h3').text(title);
    var crate_list = mtc.append('ul');
    crate_list.selectAll('li')
        .data(crates)
        .enter()
        .append('li')
        .text(function(d) { return d;});
};
function display_prescale(prescale) {
    var mtc = d3.select('#mtc');
    mtc.append('h3').text('Prescale = '+prescale.toString());
};
function display_caen(caen_info) {
    var caen = d3.select("#CAEN");
    caen.append('h4').text("Acquisition Mode = "+caen_info.acquisition_mode);
};
function display_tubii(tubii_info) {
    var tubii = d3.select("#tubii");
    var bounds = tubii.node().parentElement.parentElement.clientWidth
	var height = 50;
    var width = bounds;
    var step_size = width/30;
    radius = step_size;
    var xpos_func = function(d,i) { return step_size+i*step_size; }
    var ypos_func = function(d,i) { return height/4.0; }

    tubii.append('h4').text("Trigger Mask");
    var svg = tubii.append("svg")
        .attr("width",width)
        .attr("height",height)
        .attr("viewBox","0 0 "+width.toString()+" "+height.toString())
        .attr("class","rack_mask");
    var arr = [];
    for(var i=0;i<16;i++) {
        arr.push([i.toString(),(tubii_data["trigger_mask"]&(1<<i))/(1<<i),"External Trigger " + i.toString()]);
    }
    arr.push(["M1",(tubii_data["trigger_mask"]&(1<<16))/(1<<16),"MTCA Mimic 1"]);
    arr.push(["M2",(tubii_data["trigger_mask"]&(1<<17))/(1<<17),"MTCA Mimic 2"]);
    arr.push(["B",(tubii_data["trigger_mask"]&(1<<18))/(1<<18), "Burst Trigger"]);
    arr.push(["C",(tubii_data["trigger_mask"]&(1<<19))/(1<<19), "Combo Trigger"]);
    arr.push(["P",(tubii_data["trigger_mask"]&(1<<20))/(1<<20), "Prescale Trigger"]);
    arr.push(["U",(tubii_data["trigger_mask"]&(1<<21))/(1<<21), "Unused Trigger"]);
    arr.push(["T",(tubii_data["trigger_mask"]&(1<<22))/(1<<22), "TELLIE"]);
    arr.push(["S",(tubii_data["trigger_mask"]&(1<<23))/(1<<23), "SMELLIE"]);
    svg.selectAll('rect')
        .data(arr)
        .enter()
        .append('rect')
        .attr("x",xpos_func)
        .attr("y",ypos_func)
        .attr("width",radius)
	.attr("height",radius)
        .attr("fill",function(d) { return d[1]==1 ? 'green' : 'red'; })
        .attr("class",function(d) { return d[1]==1 ? 'on' : 'off'; })
	.append("svg:title")
	.text(function(d){return d[2];});
    svg.selectAll('text')
        .data(arr)
        .enter()
        .append('text')
        .text(function(d){return d[0];})
        .attr("text-anchor","middle")
        .attr("font-size","16px")
        .attr("fill","white")
        .attr("x",function(d,i) { return xpos_func(d,i)+0.5*radius;})
        .attr("y",function(d,i) { return ypos_func(d,i)+0.5*radius+5;});

    tubii.append('h4').text("Speaker Mask");
    var svg = tubii.append("svg")
        .attr("width",width)
        .attr("height",height)
        .attr("viewBox","0 0 "+width.toString()+" "+height.toString())
        .attr("class","rack_mask");
    var arr = [];
    for(var i=0;i<16;i++) {
        arr.push([i.toString(),(tubii_data["speaker_mask"]&(1<<i))/(1<<i),"External Trigger " + i.toString()]);
    }
    arr.push(["M1",(tubii_data["speaker_mask"]&(1<<16))/(1<<16),"MTCA Mimic 1"]);
    arr.push(["M2",(tubii_data["speaker_mask"]&(1<<17))/(1<<17),"MTCA Mimic 2"]);
    arr.push(["B",(tubii_data["speaker_mask"]&(1<<18))/(1<<18),"Burst Trigger"]);
    arr.push(["C",(tubii_data["speaker_mask"]&(1<<19))/(1<<19),"Combo Trigger"]);
    arr.push(["P",(tubii_data["speaker_mask"]&(1<<20))/(1<<20),"Prescale Trigger"]);
    arr.push(["U",(tubii_data["speaker_mask"]&(1<<21))/(1<<21),"Unused Trigger"]);
    arr.push(["T",(tubii_data["speaker_mask"]&(1<<22))/(1<<22),"TELLIE"]);
    arr.push(["S",(tubii_data["speaker_mask"]&(1<<23))/(1<<23),"SMELLIE"]);
    arr.push(["GT",(tubii_data["speaker_mask"]&(1<<24))/(1<<24),"Global Trigger"]);
    svg.selectAll('rect')
        .data(arr)
        .enter()
        .append('rect')
        .attr("x",xpos_func)
        .attr("y",ypos_func)
        .attr("width",radius)
        .attr("height",radius)
        .attr("fill",function(d) { return d[1]==1 ? 'green' : 'red'; })
        .attr("class",function(d) { return d[1]==1 ? 'on' : 'off'; })
	.append("svg:title")
	.text(function(d){return d[2];});
    svg.selectAll('text')
        .data(arr)
        .enter()
        .append('text')
        .text(function(d){return d[0];})
        .attr("text-anchor","middle")
        .attr("font-size","16px")
        .attr("fill","white")
        .attr("x",function(d,i) { return xpos_func(d,i)+0.5*radius;})
        .attr("y",function(d,i) { return ypos_func(d,i)+0.5*radius+5;});

    tubii.append('h4').text("Counter Mask");
    var svg = tubii.append("svg")
        .attr("width",width)
        .attr("height",height)
        .attr("viewBox","0 0 "+width.toString()+" "+height.toString())
        .attr("class","rack_mask");
    var arr = [];
    for(var i=0;i<16;i++) {
        arr.push([i.toString(),(tubii_data["counter_mask"]&(1<<i))/(1<<i),"External Trigger " + i.toString()]);
    }
    arr.push(["M1",(tubii_data["counter_mask"]&(1<<16))/(1<<16),"MTCA Mimic 1"]);
    arr.push(["M2",(tubii_data["counter_mask"]&(1<<17))/(1<<17),"MTCA Mimic 2"]);
    arr.push(["B",(tubii_data["counter_mask"]&(1<<18))/(1<<18),"Burst Trigger"]);
    arr.push(["C",(tubii_data["counter_mask"]&(1<<19))/(1<<19),"Combo Trigger"]);
    arr.push(["P",(tubii_data["counter_mask"]&(1<<20))/(1<<20),"Prescale Trigger"]);
    arr.push(["U",(tubii_data["counter_mask"]&(1<<21))/(1<<21),"Unused Trigger"]);
    arr.push(["T",(tubii_data["counter_mask"]&(1<<22))/(1<<22),"TELLIE"]);
    arr.push(["S",(tubii_data["counter_mask"]&(1<<23))/(1<<23),"SMELLIE"]);
    arr.push(["GT",(tubii_data["counter_mask"]&(1<<24))/(1<<24),"Global Trigger"]);
    svg.selectAll('rect')
        .data(arr)
        .enter()
        .append('rect')
        .attr("x",xpos_func)
        .attr("y",ypos_func)
        .attr("width",radius)
        .attr("height",radius)
        .attr("fill",function(d) { return d[1]==1 ? 'green' : 'red'; })
        .attr("class",function(d) { return d[1]==1 ? 'on' : 'off'; })
        .append("svg:title")
        .text(function(d){return d[2];});
    svg.selectAll('text')
        .data(arr)
        .enter()
        .append('text')
        .text(function(d){return d[0];})
        .attr("text-anchor","middle")
        .attr("font-size","16px")
        .attr("fill","white")
        .attr("x",function(d,i) { return xpos_func(d,i)+0.5*radius;})
        .attr("y",function(d,i) { return ypos_func(d,i)+0.5*radius+5;});
    var cmode;
    if(tubii_data["counter_mode"]==1) cmode="Rate";
    else cmode="Totaliser";
    tubii.append('h5').text("Counter mode: " + cmode);
    tubii.append('h5').text("Meta-Trigger settings go here...");

    var csource, losource, cbackup, ecal;
    if(tubii_data["clock_source"]==1) csource="TUBii";
    else csource="TUB";
    tubii.append('h5').text("Clock Source: " + csource);
    if(tubii_data["clock_status"]==1) cbackup="BAD";
    else cbackup="GOOD";
    tubii.append('h5').text("Clock Status: " + cbackup);
    if(tubii_data["lo_source"]==1) losource="TUBii";
    else losource="TUB";
    tubii.append('h5').text("Lockout Source: " + losource);
    if(tubii_data["ecal"]==1) ecal="ON";
    else ecal="OFF";
    tubii.append('h5').text("ECAL Mode: " + ecal);

    tubii.append('h5').text("CAEN Gain Path: " + tubii_data["caen_gain_path"]); // 1-8, high is attenuating
    tubii.append('h5').text("CAEN Channel Selected: " + tubii_data["caen_channel_select"]);
    // 1 means A9 goes to Scope/Caen Ch 1 instead of A1
    // 2 means A10 goes to Scope/Caen Ch2 instead of A2
    // 4 means A11 goes to Scope/Caen Ch3 instead of A3
    // 8 means A8 to Scope/Caen Ch 0 instead of A0

    tubii.append('h5').text("DGT: " + tubii_data["dgt_reg"] + " ns");
    tubii.append('h5').text("LO: " + tubii_data["lockout_reg"] + " ns");
    tubii.append('h5').text("DAC Thresh: " + tubii_data["dac_reg"] + " V");
};
function display_array_as_list(node,arr,title) {
    node.append('h3').text(title);
    var display_node = node.append('ul');
    display_node.selectAll('li')
        .data(arr)
        .enter()
        .append('li')
        .text(function(d) { return d.toString();});

}
function display_dictionary_as_list(node,dict,title) {
    keys =Object.keys(dict)
    node.append('h3').text(title);
    var display_node = node.append('ul');
    display_node.selectAll('li')
        .data(keys)
        .enter()
        .append('li')
        .text(function(d) { return d+' = '+dict[d].toString();});

}
function display_mtca_thresholds(dacs){
    var mtc = d3.select('#mtc');

    function dac_to_volts(value) { return (10.0/4096)*value - 5.0; }
    volt_dict = {}
    for(var key in dacs)
    { volt_dict[key] = dac_to_volts(dacs[key]).toFixed(2)+"V"; }

    //Maybe someday tie this into the trigger scan
    display_dictionary_as_list(mtc,volt_dict,'MTCA Thresholds');
}
function display_crate_mask(mask,dom_node,title,size_info) {
    var width = size_info.width;
    var height =size_info.height;
    dv = dom_node.append("div");
    dv.append("h4").text(title).attr("float","left");
    var svg = dv.append("svg")
        .attr("width",width)
        .attr("height",height)
        .attr("viewBox","0 0 "+width.toString()+" "+height.toString())
        .attr("class","crate_mask");
    var title_percent = 0.10;
    var title_width = title_percent*width;
    width=(1- title_percent)*width;
    var step_size = width/21;
    var xpos_func = function(d,i) { return title_width+i*step_size; }
    var ypos_func = function(d,i) { return height/2.0; }
    svg.selectAll("circle")
        .data(mask)
        .enter()
        .append("circle")
        .attr("cx",xpos_func)
        .attr("cy",ypos_func)
        .attr("r",height/2.0)
        .attr("class",function(d) { return d ? 'on' : 'off'; })
    svg.selectAll('text')
        .data(mask)
        .enter()
        .append('text')
        .text(function(d,i){return i.toString();})
        .attr("text-anchor","middle")
        .attr("font-size","10px")
        .attr("fill","white")
        .attr("x",xpos_func)
        .attr("y",function(d,i) { return ypos_func(d,i)+3;});
};
function display_run_type(run_type,time_stamp) {
    var run_type_translation = {
    0:"Maintenance",
    1:"Transition",
    2:"Physics",
    3:"Deployed Source",
    4:"External Source",
    5:"ECA",
    6:"Diagnostic",
    7:"Experimental",
    };
    var calib_translation = {
    11:"TELLIE",
    12:"SMELLIE",
    13:"AMELLIE",
    14:"PCA",
    15:"ECA Pedestal",
    16:"ECA Time Slope"
    };
    var detector_state_translation = {
    21:"DCR Activity",
    22:"Compensation Coils Off",
    23:"PMTS Off",
    24:"Bubblers On",
    25:"Recirculation",
    26:"SL Assay",
    27:"Unusual Activity"
    };
    var flag = false;
    var translator = function(low_bit,high_bit,trans_map){
        ret = []
        for(i=low_bit;i<=high_bit;i++)
        {
            if(run_type & (1<<i)) {
                if(i-low_bit >= Object.keys(trans_map).length) {
                   ret.push("SPARE (???)");
                }
                else {
                    ret.push(trans_map[i]);
                }
            }
        }
        return ret;
    };
    var run_desc = translator(0,10,run_type_translation);
    var calib_desc = translator(11,20,calib_translation);
    var det_state_desc = translator(21,31,detector_state_translation);
    if(run_desc.length == 0) {
        run_desc.push("None");
    }
    var title = document.getElementById("run_title");
    var appendToTitle = function(type,desc){
        var thisSubTitle = document.createElement('h2');
        thisSubTitle.appendChild(document.createTextNode(desc.toString()));
        title.appendChild(thisSubTitle);
    }
    appendToTitle('h2',run_desc);
    if(calib_desc.length > 0){
        appendToTitle('h3',calib_desc);
    }
    if(det_state_desc.length > 0){
        appendToTitle('h3',det_state_desc);
    }
    date = new Date(Date.parse(time_stamp))
    str= date.toString()
    // This will probably break during when changing to/from DST
    // JS doesn't seem to contain a good way for displaying a date with a tz
    str = str.replace('GMT-0400 ','').replace('GMT-0500 ','')
    str = str.replace('(EDT)','EDT').replace('(EST)','EST')
    appendToTitle('p',str);
};
function crate() {
    var width = 780;
    var height = 80;

    function my(){

    }
    my.width = function(value) {
        if(!arguments.length) {
            return width;
        }
        width = value;
        return my;
    }
    my.height = function(value) {
        if(!arguments.length) {
            return height;
        }
        height = value;
        return my;
    }

    return my;
}
