$(document).ready(function() {
	$(chart_id).highcharts({
		chart: chart,
		title: title,
		xAxis: xAxis,
		yAxis: yAxis,
		credits: {
            enabled: false
        },
		tooltip: {
            shared: true,
            crosshairs: true,
            pointFormat: '{series.name}: <b>{point.y:,.2f}</b><br/>'
        },
        legend: {
        enabled: false
    },
		series: series
	});
	$(".button-collapse").sideNav();
});


Highcharts.setOptions({
    lang: {
        decimalPoint: ',',
        thousandsSeparator: '.'
    }
});

//$('#myTabs a').click(function (e) {
//  e.preventDefault()
//  $(this).tab('show')
//})
