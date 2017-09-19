/**
 * @brief drawColumnChart
 * @description function takes a dictionary of chart context info and generates a column chart
 * @param chart_context: the dictionary containing chart generation info
 */
function drawColumnChart(chart_context) {
    var data = new google.visualization.DataTable(chart_context['data']);
    var options = {
        alignment: 'center',
        fontName: 'Roboto',
        colors: chart_context['colors'],
        backgroundColor: 'none',
        title: chart_context['title'],
        width: chart_context['width'],
        height: chart_context['height'],
        titleTextStyle: {
            fontSize: 16,
            fontWeight: 100,
            bold: false
        },
        chartArea: {
            left: 100,
            top: 64,
            width: '55%',
            height: '50%'
        },
        hAxis: {
            title: chart_context['x-axis'],
            textStyle: {
                fontSize: 12
            },
            slantedText: true,
            slantedTextAngle: 60
        },
        vAxis: {
            title: chart_context['y-axis'],
            textStyle: {
                fontSize: 12
            }
        },
        legend: {
            position: 'right',
        },
        orientation: 'horizontal'
    };
    var chart = new google.visualization.ColumnChart(
        document.getElementById(chart_context['tag']));
    chart.draw(data, options);
}

/**
 * @brief drawColumnChartConditional
 * @description function takes in a more robust context dictionary and generates a more customized column chart
 * @param chart_context: the dictionary containing the chart context data
 */
function drawColumnChartConditional(chart_context) {
    var data = new google.visualization.DataTable(chart_context['data']);
    var yticks = chart_context['y-ticks'];
    var xticks = chart_context['x-ticks'];
    var options = {
        alignment: 'center',
        fontName: 'Roboto',
        backgroundColor: 'none',
        title: chart_context['title'],
        width: chart_context['width'],
        height: chart_context['height'],
        titleTextStyle: {
            fontSize: 16,
            fontWeight: 100,
            bold: false
        },
        chartArea: {
            left: 100,
            top: 64,
            width: '70%',
            height: '80%'
        },
        hAxis: {
            title: chart_context['x-axis'],
            textStyle: {
                fontSize: 12
            },
            slantedText: true,
            slantedTextAngle: 60
        },
        vAxis: {
            title: chart_context['y-axis'],
            ticks: [{v: -100, f: yticks[0]},
                    {v: -50, f: yticks[1]},
                    {v: 0, f: yticks[2]},
                    {v: 10, f: yticks[3]},
                    {v: 20, f: yticks[4]}],
            textStyle: {
                fontSize: 12
            }
        },
        legend: 'none',
        orientation: 'horizontal'
    };
    var chart = new google.visualization.ColumnChart(
        document.getElementById(chart_context['tag']));
    chart.draw(data, options);
}