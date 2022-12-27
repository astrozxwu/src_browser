$(document).ready(function () {
    function dateToJulianNumber(d) {
        // convert a Gregorian Date to a Julian number.
        //    S.Boisseau / BubblingApp.com / 2014
        var x = Math.floor((14 - d.getMonth()) / 12);
        var y = d.getFullYear() + 4800 - x;
        var z = d.getMonth() - 3 + 12 * x;

        var n = d.getDate() + Math.floor(((153 * z) + 2) / 5) + (365 * y) + Math.floor(y / 4) + Math.floor(y / 400) - Math.floor(y / 100) - 32045;

        return n;
    }
    function julianIntToDate(n) {
        // convert a Julian number to a Gregorian Date.
        //    S.Boisseau / BubblingApp.com / 2014
//        var a = n + 32044;
//        var b = Math.floor(((4 * a) + 3) / 146097);
//        var c = a - Math.floor((146097 * b) / 4);
//        var d = Math.floor(((4 * c) + 3) / 1461);
//        var e = c - Math.floor((1461 * d) / 4);
//        var f = Math.floor(((5 * e) + 2) / 153);

//        var D = e + 1 - Math.floor(((153 * f) + 2) / 5);
//        var M = f + 3 - 12 - Math.round(f / 10);
//        var Y = (100 * b) + d - 4800 + Math.floor(f / 10);

//        return new Date(Y, M, D);
          return new Date((n-2440587.5)*864e5)
    }

//    console.log(julianIntToDate(2457000).toLocaleDateString("en-US"))
    Highcharts.setOptions({
        plotOptions: {
            line: {
                marker: {
                    enabled: false
                }
            },
            series: {
                animation: false,
                selected: false,
                states: {
                    inactive: {
                        opacity: 0.9
                    },

                },
                stickyTracking: false,
            },
            chart: {
                animation: false
            },

        }
    });
	var today = new Date();
	var julday = Math.floor((today.valueOf() / (1000 * 60 * 60 * 24)) - 0.5) + 2440588;
    let config = {
        chart: chart,
        title: title,
        xAxis: {
            title: {text: 'JD'},
            labels: {
                step: 2,
                formatter: function () {
                    return this.value + '<br />' + julianIntToDate(this.value).toLocaleDateString("en-US");
                }
            },
            max: julday + 180
        },
        yAxis: {title: {text: 'mag'}, reversed: true},
        series: series,
        animation: false,
        tooltip: {
            formatter: function() {
                return '<b>'+this.series.name +': </b>'+this.point.y+' '+this.point.err+'</br><b>JD: </b>' + this.point.x +'</br><b>UTC: </b>'+ julianIntToDate(this.point.x).toLocaleDateString("sv-SE") + '</br><b>FWHM: </b>'+ this.point.fwhm+'</br><b>site: </b>'+ this.point.code;}
        },
        plotOptions:{
            series:{
                turboThreshold:5000//larger threshold or set to 0 to disable
            }
        },
    }

    $(chart_id).highcharts(config);
});
