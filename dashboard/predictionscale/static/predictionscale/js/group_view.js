/**
 * Created by dungvt on 14/08/2017.
 */

$(document).ready(function () {
    var url = $('#group-view').data('url')
    function getLog(){
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                fillLog(data.log);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    function fillLog(data){
        var logs = data.split('\n');
        for(var i=0;i<logs.length;i++){
            if(logs[i] != "") {
                logs[i] = logs[i].slice(0, 19) + " =>   " + logs[i].slice(30);
            }
        }
        logs = logs.join('<br/>');
        $("#content").html(logs);
    }

    getLog();
});
