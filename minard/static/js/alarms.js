setInterval(function() { $('#time').text(moment().tz('America/Toronto').format('HH:mm:ss')); }, 1000);

// checkboxes are checked by default
$('input[name="view"]').prop('checked',true);
// show/hide labels when checked/unchecked
$('input[name="view"]').click(function() {
    if ($(this).is(':checked')) {
        $('p span.label-' + $(this).val()).parent().show();
    } else {
        $('p span.label-' + $(this).val()).parent().hide();
    }
});

var level_labels = {
    'SUCCESS' : '<span class="label label-success label-block">Success</span>',
    'INFO'    : '<span class="label label-info label-block">Info</span>',
    'WARNING' : '<span class="label label-warning label-block">Warning</span>',
    'ERROR'   : '<span class="label label-danger label-block">Error</span>',
    'DEBUG'   : '<span class="label label-default label-debug label-block">Debug</span>',
    'UNKNOWN' : '<span class="label label-default label-unknown label-block">???</span>',
    21        : '<span class="label label-success label-block">Success</span>',
    20        : '<span class="label label-info label-block">Info</span>',
    30        : '<span class="label label-warning label-block">Warning</span>',
    40        : '<span class="label label-danger label-block">Error</span>',
    10        : '<span class="label label-default label-debug label-block">Debug</span>',
}

var _last_date = null;

function update_alarms(start)
{
    if (typeof(start) === 'undefined') start = -100;

    $.getJSON($SCRIPT_ROOT + '/get_alarm?start=' + start).done(function(obj) {
        var now = moment().tz('America/Toronto');

        for (var i=0; i < obj.alarms.length; i++)
        {
            var alarm = obj.alarms[i];

            var mom = moment(alarm.time);

            if (mom.isValid())
            {
                if (_last_date == null)
                {
                    _last_date = mom;
                } else
                {
                    if (!mom.isSame(_last_date, 'day'))
                    {
                        $('#log').prepend('<div class="border-bottom text-center">' + _last_date.format('MM/DD/YYYY') + '</div>');
                        _last_date = mom;
                    }
                }

                var label;
                var level = alarm.level;
                if (level in level_labels)
                {
                    label = level_labels[level];
                } else {
                    label = level_labels['UNKNOWN'];
                }

                var p = $('<p>')
                    .append(label)
                    .append(' ')
                    .append(mom.format('HH:mm:ss'))
                    .append(' ')
                    .append(alarm.message);

                $('#log').prepend(p);

                if ((i == obj.alarms.length-1) && !now.isSame(mom,'day'))
                {
                    $('#log').prepend('<div class="border-bottom text-center">' + mom.format('MM/DD/YYYY') + '</div>');
                    _last_date = now;
                }
            } else {
                // print whole message
                $('#log').prepend('<p>' + level_labels['UNKNOWN'] + ' ' + alarm.message);
            }
        }
        $("#log p").slice(1000).remove();
        setTimeout(function() { update_alarms(obj.latest+1) },1000); // 1 second
    });
};
