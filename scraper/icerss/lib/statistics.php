<?php
require_once dirname(__FILE__) . '/dbal.php';

/**
 * Statistics allow for easy measuring statistics for certain operations.
 */
class Statistics {
    private $measurements = array();

    function start($name, $message) {
        $this->measurements[$name] = array('message' => $message, 'timestamp' => microtime(TRUE));
    }

    function end($name) {
        if (array_key_exists($name, $this->measurements)) {
            $inserts = $this->measurements[$name];
            $inserts['name'] = $name;
            $inserts['microtime'] = (microtime(TRUE) - $inserts['timestamp'])*1000;
            $inserts['timestamp'] = dbal_date($inserts['timestamp']);
            dbal_insert('stats', $inserts);
            unset($this->measurements[$name]);
        }
    }
}
?>
