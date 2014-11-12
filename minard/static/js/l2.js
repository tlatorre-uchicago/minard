function update_files(name, interval) {
    // update the list of files in the l2 state `name`

    $.getJSON($SCRIPT_ROOT + '/get_l2?name=' + name).done(function(obj) {
        $('#' + name + ' tbody tr').remove();
        for (var i=0; i < obj.files.length; i++) {
            var tr = $('<tr>')
                .append($('<td>').text(obj.files[i]))
                .append($('<td>').text(obj.times[i]));
            $('#' + name).find('tbody').append(tr);
        }
        setTimeout(function() {update_files(name, interval); }, interval*1000);
    });
}
