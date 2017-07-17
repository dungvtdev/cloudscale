$(document).ready(function () {
    var isGettingData = false;

    var data = $("div#service-data div")

    var default_data = {
        period: data.data("period"),
        dataLength: data.data("data-length"),
        recentPoint: data.data("recent-point"),
        periodicNumber: data.data("periodic-number"),
        neuralSize: data.data("neural-size"),
        predictLength: data.data("predict-length"),
        updateInTime: data.data("update-in-time"),
    }

    var dataStates = $('.data-train')

    function camelCaseToDash(myStr) {
        return myStr.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
    }

    function filldata() {
        $.each(default_data, function (key, val) {
            $('form#settingForm input[name="' + key + '"]').val(val);
        })
    }

    function fillDataState(data) {
        console.log(data);
        dataStates.each(function (index) {

        })
    }

    function getData(url) {
        form = $('form#settingForm')
        arr = form.serializeArray()
        data = {}
        arr.forEach(function (elm) {
            data[camelCaseToDash(elm.name)] = elm.value;
        });

        isGettingData = true;

        $.ajax({
            url: url,
            type: 'GET',
            data: {
                dataLength: data['data-length'],
            },
            dataType: 'json',
            success: function (data) {
                fillDataState(data)
            },
            error: function () {
                isGettingData = false
            }
        })
    }

    function canGetData() {
        if (isGettingData)
            return false

        var hasData = true
        if (!dataStates) {
            return false;
        }
        dataStates.each(function (index) {
            if ($(this).text().trim() == "") {
                hasData = false
            }
        })
        return !hasData
    }

    var btn_refesh = $('form#settingForm button#refresh')
    btn_refesh.click(function () {
        filldata();
    });

    var dataTab = $('ul#settingTabs a[href="#data"]')
    dataTab.on('shown.bs.tab', function (e) {
        if (!canGetData())
            return;
        url = $('form#settingForm div#data').data('url')
        getData(url)
    });


    filldata()
});