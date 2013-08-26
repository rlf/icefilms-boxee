<?php
require_once dirname(__FILE__) . '/init.php';

# Default values are taken from ini_get (set-up in init.php).
mysql_connect();
if ($GLOBALS['mysql.default_database']) {
    mysql_select_db($GLOBALS['mysql.default_database']);
} else die('mysql.default_database must be set');

/**
 * Returns the modified table name with the prefix configured.
 * @param <type> $table The "clean" table name
 */
function dbal_table($table) {
    return $GLOBALS['mysql.table_prefix'] . $table;
}
/**
 * Converts a php-timestamp to a db-timestamp
 **/
function dbal_date($time) {
    return date('Y-m-d H:i:s', $time);
}

/*
 * DataBase Abstraction Layer - currently only supports mysql
 */
function dbal_insert($table, $inserts) {
    $table = dbal_table($table);
    $values = array_map('mysql_real_escape_string', array_values($inserts));
    $keys = array_keys($inserts);
    $sql = 'INSERT INTO `'.$table.'` (`'.implode('`,`', $keys).'`) VALUES (\''.implode('\',\'', $values).'\')';
    return mysql_query($sql);
}

/**
 * queries the table using the clauses.
 * clauses is an array of 2-3 length tuples.
 * first and second place in tuple is key and value, optional 3rd is the comparison.
 **/
function dbal_query($table, $clauses, $order=false) {
    $table = dbal_table($table);
    $query = "SELECT * FROM `$table` WHERE 1=1";
    foreach ($clauses as $clause) {
        $comparison = '=';
        if (sizeof($clause) == 3) {
            if (array_search($clause[2], array('=', '<=', '>=', '<', '>'))) {
                $comparison = $clause[2];
            }
        } else if (sizeof($clause) != 2) {
            throw new Exception("Invalid argument: Clauses must be 2 or 3 tuples of key, value[, comparison]");
        }
        $key = $clause[0];
        $value = $clause[1];
        $query .= ' AND `' . mysql_real_escape_string($key) . "`$comparison'" . mysql_real_escape_string($value) . "'";
    }
    if ($order) {
        // Note: Vulnerable to injection.
        $query .= ' ORDER BY ' . implode(',', $order);
    }
    return dbal_query_sql($query);
}

function dbal_query_sql($sql, $failOnError=false) {
    $result = mysql_query($sql);
    $rows = array();
    if ($result) {
        while ($row=mysql_fetch_array($result, MYSQL_ASSOC)) {
            $rows[] = $row;
        }

        mysql_free_result($result);
    } else if ($failOnError) {
        die("Error executing sql: $sql\n" . mysql_error());
    }
    return $rows;
}

function dbal_delete($table, $clauses=array()) {
    $table = dbal_table($table);
    $query = "DELETE FROM `$table` WHERE 1";
    foreach ($clauses as $clause) {
        $comparison = '=';
        if (sizeof($clause) == 3) {
            if (array_search($clause[2], array('=', '<=', '>=', '<', '>'))) {
                $comparison = $clause[2];
            }
        } else if (sizeof($clause) != 2) {
            throw new Exception("Invalid argument: Clauses must be 2 or 3 tuples of key, value[, comparison]");
        }
        $key = $clause[0];
        $value = $clause[1];
        $query .= ' AND `' . mysql_real_escape_string($key) . "`$comparison'" . mysql_real_escape_string($value) . "'";
    }
    return mysql_query($query);
}


?>
