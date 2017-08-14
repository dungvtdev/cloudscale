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
                $("#content").text(data.log);
            },
            error: function (data) {
                console.log(data);
            }
        });
    }

    getLog();
});
