$(document).ready(function () {
    var data = {
        'real': [['time', 'value']],
        'predict': [['time', 'value']],
        'scale': ['time', 0], // 0 down, 1 up
    }

    var getting = false;
    var submit_btn = $('form#report_datetime button');
    console.log(submit_btn)
    submit_btn.click(function(){
        if(getting) return;
        getData();
    })

    // function min(arr){
    //     if(!arr)
    //         return 0;
    //     m = arr[0]
    //     for(var i=1;i<arr.length;i++){
    //         if(m>arr[i]) m = arr[i];
    //     }
    //     return m
    // }
    //
    // function max(arr){
    //     if(!arr)
    //         return 0;
    //     m = arr[0]
    //     for(var i=1;i<arr.length;i++){
    //         if(m<arr[i]) m = arr[i];
    //     }
    //     return m
    // }

    function getData(){
        getting = true;
        var url = $('form#report_datetime button').data('url')

        var input_vals = $('form#report_datetime input')

        input_data = {
            'from': input_vals[0].value,
            'to': input_vals[1].value
        }

        $.ajax({
            url: url,
            type: 'GET',
            data: {
                'range': input_data
            },
            dataType: 'json',
            success: function (data) {
                getting = false;
                console.log(data)
            },
            error: function () {
                getting = false
            }
        })
    }

    // var svg = d3.select("svg#report"),
    //     margin = {top: 20, right: 80, bottom: 30, left: 50},
    //     width = svg.attr("width") - margin.left - margin.right,
    //     height = svg.attr("height") - margin.top - margin.bottom,
    //     g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    //
    // var parseTime = d3.timeParse("%Y%m%d");
    //
    // var x = d3.scaleTime().range([0, width]),
    //     y = d3.scaleLinear().range([height, 0]),
    //     z = d3.scaleOrdinal(d3.schemeCategory10);
    //
    // var line = d3.line()
    //     .curve(d3.curveBasis)
    //     .x(function (d) {
    //         return x(d[0]);
    //     })
    //     .y(function (d) {
    //         return y(d[1]);
    //     });
    //
    //
    // function draw(data) {
    //     var real_data = data.real
    //     var predict_data = data.predict
    //     var scale_data = data.scale
    //
    //     var minx = 0,
    //         maxx = 10000000000000000;
    //     ls = [real_data, predict_data, scale_data]
    //     lines = [{
    //             id: 'Real point',
    //             values: real_data,
    //         },
    //         {
    //             id: 'Predict point',
    //             values: predict_data
    //         }]
    //     for (var i = 0; i < ls.length; i++) {
    //         d = ls[i]
    //         if (d && d.length > 0) {
    //             if (minx > d[0]) minx = d[0]
    //             if (maxx < d[d.length - 1]) maxx = d[d.length - 1]
    //         }
    //     }
    //     x.domain(minx, maxx);
    //     y.domain([
    //         d3.min(ls, function (c) {
    //             return d3.min(c, function (d) {
    //                 return d[1];
    //             });
    //         }),
    //         d3.max(ls, function (c) {
    //             return d3.max(c, function (d) {
    //                 return d[1];
    //             });
    //         })
    //     ]);
    //     z.domain(lines.map(function(l){return l.id}));
    //
    //     g.append("g")
    //         .attr("class", "axis axis--x")
    //         .attr("transform", "translate(0," + height + ")")
    //         .call(d3.axisBottom(x));
    //
    //     g.append("g")
    //         .attr("class", "axis axis--y")
    //         .call(d3.axisLeft(y))
    //         .append("text")
    //         .attr("transform", "rotate(-90)")
    //         .attr("y", 6)
    //         .attr("dy", "0.71em")
    //         .attr("fill", "#000")
    //         .text("Usage, %");
    //
    //     var series = g.selectAll(".series")
    //         .data(lines)
    //         .enter().append("g")
    //         .attr("class", "series");
    //
    //     series.append("path")
    //         .attr("class", "line")
    //         .attr("d", function (d) {
    //             return line(d.values);
    //         })
    //         .style("stroke", function (d) {
    //             return z(d.id);
    //         });
    //
    //     series.append("text")
    //         .datum(function (d) {
    //             return {id: d.id, value: d.values[d.values.length - 1]};
    //         })
    //         .attr("transform", function (d) {
    //             return "translate(" + x(d.value[0]) + "," + y(d.value[1]) + ")";
    //         })
    //         .attr("x", 3)
    //         .attr("dy", "0.35em")
    //         .style("font", "10px sans-serif")
    //         .text(function (d) {
    //             return d.id;
    //         });
    // }
});
