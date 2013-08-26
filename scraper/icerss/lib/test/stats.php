<?php
require_once dirname(__FILE__) . '/../dbal.php';
$table = dbal_table('stats');
$sql = "SELECT name, ROUND(microtime/1000) sec, COUNT(*) cnt FROM `$table` GROUP BY name, sec ORDER BY name, sec ASC";
$rows = dbal_query_sql($sql, true);
$charts = array();
foreach ($rows as $row) {
    if (!array_key_exists($row['name'], $charts)) {
        $charts[$row['name']] = array();
    }
    $charts[$row['name']][] = array('hit' => $row['cnt'], 'sec' => $row['sec']);
}
$sql = "SELECT name, STDDEV(microtime/1000) dev, AVG(microtime/1000) avg FROM `$table` GROUP BY name ORDER BY name";
$rows = dbal_query_sql($sql, true);
$stddev = array();
foreach ($rows as $row) {
    $dev = floatval($row['dev']);
    $avg = floatval($row['avg']);
    $stddev[$row['name']] = array("avg" => $avg, "min" => $avg-$dev, "max" => $avg+$dev);
}
?>
<html>
    <head><title>Statistics of IceRSS</title>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
function drawChart() { <? $i = 1;foreach ($charts as $name => $chart) { ?>
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'seconds');
    data.addColumn('number', 'hits');
    data.addRows(<?=sizeof($chart)?>);
<? foreach ($chart as $j => $data) { ?>
    data.setValue(<?=$j?>, 0, '<?=$data['sec']?>');
    data.setValue(<?=$j?>, 1, <?=$data['hit']?>);
<? } ?>
    var chart = new google.visualization.ColumnChart(document.getElementById('chart<?=$i?>_div'));
    chart.draw(data, {width: 400, height: 240, title: 'Hits over response-times',
    hAxis: {title: 'response time (secs)', titleTextStyle: {color: 'red'}}
});<? $i++; } ?>
}
    </script>
    </head>
    <body>
        <h1>Statistics</h1>
<? $i = 1; foreach ($charts as $name => $chart) { ?>
        <h2><?=$name?></h2>
        <div id="chart<?=$i?>_div"></div>
        <pre>
<? foreach ($stddev[$name] as $key => $value) { ?>
<?=$key?> : <?=$value?>

<? } ?>
        </pre>
<? $i++; } ?>
    </body>
</html>
