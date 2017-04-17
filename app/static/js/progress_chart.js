var ctx = document.getElementById('xpChart').getContext('2d');

/*
 * Plugin to display tooltips without them needing to be hovered
 */
Chart.pluginService.register({
  beforeRender: function(chart) {
    if (chart.config.options.showAllTooltips) {
      // create an array of tooltips
      // we can't use the chart tooltip because there is only one tooltip per chart
      chart.pluginTooltips = [];
      chart.config.data.datasets.forEach(function(dataset, i) {
        last = chart.getDatasetMeta(i).data[6]
          chart.pluginTooltips.push(new Chart.Tooltip({
            _chart: chart.chart,
            _chartInstance: chart,
            _data: chart.data,
            _options: chart.options.tooltips,
            _active: [last]
          }, chart));
      });

      // turn off normal tooltips
      chart.options.tooltips.enabled = false;
    }
  },
  afterDraw: function(chart, easing) {
    if (chart.config.options.showAllTooltips) {
      // we don't want the permanent tooltips to animate, so don't do anything till the animation runs at least once
      if (!chart.allTooltipsOnce) {
        if (easing !== 1)
          return;
        chart.allTooltipsOnce = true;
      }

      // turn on tooltips
      chart.options.tooltips.enabled = true;
      Chart.helpers.each(chart.pluginTooltips, function(tooltip) {
        tooltip.initialize();
        tooltip.update();
        // we don't actually need this since we are not animating tooltips
        tooltip.pivot();
        tooltip.transition(easing).draw();
      });
      chart.options.tooltips.enabled = false;
    }
  }
});

Chart.defaults.global.defaultFontFamily = "'Raleway', sans-serif"

function xpChart() {
  var myChart = new Chart(ctx, {
    type: 'line',
    options: {
      legend: {
        display: false,
      },
      scales: {
        xAxes: [{
          gridLines: {
            display: false,
          },
          ticks: {
            fontSize: 15,
            fontColor: 'lightgrey'
          }
        }],
        yAxes: [{
          gridLines: {
            drawBorder: false,
          },
          ticks: {
            beginAtZero: true,
            fontSize: 15,
            fontColor: 'lightgrey',
            maxTicksLimit: 5,
            padding: 25,
          }
        }]
      },
      tooltips: {
        backgroundColor: 'rgba(30,144,255,0.8)',
        titleFontSize: 14,
        bodyFontSize: 14,
        xPadding: 12,
        yPadding: 10,
        displayColors: false,
        callbacks: {
          title: function(tooltip) { return 'Today' }
        }
      },
      showAllTooltips: true
    },
    data: {
      labels: labels,
      datasets: [{
        label: 'Aurei',
        data: data,
        tension: 0.0,
        borderColor: 'rgb(255,190,70)',
        backgroundColor: 'rgba(0,0,0,0.0)',
        pointBackgroundColor: ['white', 'white', 'white', 'white', 'white', 'white', 'rgb(255,190,70)'],
        pointRadius: 4,
        borderWidth: 2
      }]
    }
  });
}

