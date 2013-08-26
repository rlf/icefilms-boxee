<?php
require_once dirname(__FILE__) . '/../common.php';
/**
 * StatisticsEcho
 */
class StatisticsEcho {
    private $table = 'stats';
    private $measurements = array();

    function start($name, $message) {
        $this->measurements[$name] = array('message' => $message, 'timestamp' => microtime(TRUE));
    }

    function end($name) {
        if (array_key_exists($name, $this->measurements)) {
            $inserts = $this->measurements[$name];
            $inserts['name'] = $name;
            $inserts['microtime'] = (microtime(TRUE) - $inserts['timestamp'])*1000;
            $inserts['timestamp'] = date('Y-m-d H:i:s', $inserts['timestamp']);
            debug(json_encode($inserts));
            unset($this->measurements[$name]);
        }
    }
}
?>
