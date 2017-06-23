$(document).ready(function() {
	$(chart_id).highcharts({
		chart: chart,
		title: title,
		xAxis: xAxis,
		yAxis: yAxis,
		tooltip: {
            shared: true,
            crosshairs: true,
            pointFormat: '{series.name}: <b>{point.y:,.2f}</b><br/>'
        },
		series: series
	});
});

//$('#myTabs a').click(function (e) {
//  e.preventDefault()
//  $(this).tab('show')
//})
