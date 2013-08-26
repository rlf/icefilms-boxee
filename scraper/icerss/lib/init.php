<?php
/**
 * Contains constants needed for logging in to the mysql database etc.
 */
// Change these to sensible values!
ini_set('mysql.default_host', 'localhost');
ini_set('mysql.default_user', 'homer');
ini_set('mysql.default_password', 'simpson');
# Change this, if it's not correct
$GLOBALS['mysql.default_database'] = ini_get('mysql.default_user');
$GLOBALS['mysql.table_prefix'] = 'icerss_';
?>
