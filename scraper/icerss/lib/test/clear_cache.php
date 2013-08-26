<?php
header('Content-Type: text/plain');
require_once dirname(__FILE__) . '/../cache.php';

$cache = new Cache();
$cache->clear();
print "Cache cleared.";
?>
