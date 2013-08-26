<?php
header('Content-Type: text/plain');
require_once dirname(__FILE__) . '/../common.php';
/*
 * Creates the relevant databases to be used by the icerss feed.
 */
$dbuser = $_REQUEST['u'] or die('Invalid db-user supplied!');
$dbpass = $_REQUEST['p'] or die('Invalid db-pass supplied!');
$dbname = isset($_REQUEST['db']) ? $_REQUEST['db'] : $dbuser;
$table_prefix = request_var('prefix', 'icerss_');

$db = mysql_connect('localhost', $dbuser, $dbpass) or die('Could not connect: ' . mysql_error());
mysql_select_db($dbname, $db) or die('Could not select db : ' . $dbname . ' : ' . mysql_error());
$base = "icerss_";

function sql($sql) {
    global $db;
    return mysql_query($sql, $db) or die('Error executing sql: ' . $sql . ' : ' . mysql_error());
}

function create_databases($base) {
    $tables = array($base . 'cache', $base . 'meta', $base . 'stats');
    sql('DROP TABLE IF EXISTS ' . implode(',', $tables));

    sql('CREATE TABLE ' . $base . 'cache (' .
            'id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,' .
            'url VARCHAR(255),' .
            'lastscanned DATETIME, ' .
            'jsondata TEXT, ' .
            'start INT UNSIGNED, ' .
            'end INT UNSIGNED' .
            ')');
    // TODO: Add UNIQUE key to url, start, end.
    sql('CREATE TABLE ' . $base . 'meta (' .
            'id VARCHAR(20) PRIMARY KEY,' .
            'lastscanned DATETIME, ' .
            'jsondata TEXT' .
            ')');
        
    sql('CREATE TABLE ' . $base . 'stats (' .
            'name VARCHAR(100), ' .
            'message VARCHAR(255), ' .
            'timestamp DATETIME, ' .
            'microtime INT UNSIGNED' .
            ')');
    
}

if ($_REQUEST['c'] == 'init' && isset($_REQUEST['u']) && isset($_REQUEST['p'])) {
    create_databases($base);
    echo("Databases has been created - data has been wiped - someone was hurt!\n");
} else {
    echo("Nothing was done to the databases!\n");
}
mysql_close($db);
$init_php = '../init.php';#realpath("../init.php");
if (is_writable($init_php)) {
    $fp = fopen($init_php, 'w');
    fwrite($fp, "<?php
/**
 * Contains constants needed for logging in to the mysql database etc.
 */
// Change these to sensible values!
ini_set('mysql.default_host', 'localhost');
ini_set('mysql.default_user', '$dbuser');
ini_set('mysql.default_password', '$dbpass');
# Change this, if it's not correct
\$GLOBALS['mysql.default_database'] = '$dbname';
\$GLOBALS['mysql.table_prefix'] = '$table_prefix';
?>");
    fclose($fp);
    echo("Setup information was saved to '$init_php'\n");
} else {
    echo("Could not create '$init_php'\n");
}
?>