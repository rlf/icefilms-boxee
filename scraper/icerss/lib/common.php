<?php
function request_var($key, $default=FALSE) {
    if (isset($_REQUEST[$key])) {
        return $_REQUEST[$key];
    }
    return $default;
}

function debug($msg) {
    if (request_var('debug')) {
        // Check to see if trace is set, and if our back-trace is in it.
        $backtrace = debug_backtrace(FALSE);
        $backtrace = basename($backtrace[0]['file'], '.php');
        $trace = request_var('debug', '');
        if ($trace == 'true' || strpos($trace, $backtrace) !== false) {
            print($msg . "\n");
        }
    }
}
?>
