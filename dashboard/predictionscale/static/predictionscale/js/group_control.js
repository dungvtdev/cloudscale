$(document).ready(function () {
    // processes = $('div.instance-process')

    function toFixed(value, precision) {
        var power = Math.pow(10, precision || 0);
        return String(Math.round(value * power) / power);
    }

    var data = [
        {
            instance_id: "{instance_id}",
            process: 0,
            message: '',
            status: 'running',
            next_secs: 'next seconds',
        }
    ]

    var predictData = [
        {
            'instance_id': "instance_id",
            'length': 10,
            'mean_val': 0,
            'max_val': 0,
        }
    ]


    var urlPredict = $('#group-control').data('url-predict')

    function predict() {
        $.ajax({
            url: urlPredict,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data && 'predict' in data) {
                    data = data['predict']
                    for (var i = 0; i < data.length; i++) {
                        var d = data[i];
                        var textPredict = $('.instance-process[data-id=' + d.instance_id + '] .instance-predict');
                        if(d.mean_val==null || d.max_val==null){
                            textPredict.text('Not Completed.')
                        }else{
                            t = 'Mean: ' + toFixed(d.mean_val*100, 2) + '%, Max: ' + toFixed(d.max_val*100, 2) + '% in ' + d.length + ' minute';
                            textPredict.text(t);
                        }

                    }
                }
                setTimeout(function () {
                    predict();
                }, 60 * 1000)
            },
            error: function (data) {
                setTimeout(function () {
                    predict();
                }, 20 * 1000)
            }
        })
    }

    function fillData(data) {
        if (!data)
            return 2
        if (!('process' in data))
            return 2
        data = data['process']
        next_secs = 30;
        for (var i = 0; i < data.length; i++) {
            var d = data[i]
            pbar = $('.instance-process[data-id=' + d.instance_id + '] .progress-bar')
            lstatus = $('.instance-process[data-id=' + d.instance_id + '] .instance-status')
            lmsg = $('.instance-process[data-id=' + d.instance_id + '] .instance-message')

            pbar.css('width', d.process + '%')
            pbar.text(d.process + " %")
            lstatus.text(d.status)
            lmsg.text(d.message)

            if (d.next_secs < next_secs) {
                next_secs = d.next_secs
            }
        }

        return next_secs
    }

    var url = $('#group-control').data('url')

    function pullData(url) {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                next_secs = fillData(data)
                if (next_secs == 0)
                    next_secs = 30
                setTimeout(function () {
                    pullData(url);
                }, next_secs * 1000)
            },
            error: function (data) {
                setTimeout(function () {
                    pullData(url);
                }, 2000)
            }
        })
    }

    pullData(url)
    predict()
});