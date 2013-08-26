<?php
/*
 * The PageCache allows for a locally stored cache of urls in json form.
 */
require_once 'common.php';
require_once 'dbal.php';

define('CACHE_TIMEOUT', 21600); // 6 hrs
class Cache {
    function __construct() {
        $this->page_table = 'cache';
        $this->meta_table = 'meta';
        $this->__cleanUp();
    }

    /**
     * Returns the cache as a json-string, or false.
     * @param type $url
     * @param type $offset
     * @param type $count
     * @return type 
     */
    function getMovies($url, $offset, $count) {
        // TODO: Support cache-hits within start-end range
        $clauses = array(array('url', $url), 
            array('start', $offset), 
            array('end', $offset+$count),
            array('lastscanned', dbal_date(time() - CACHE_TIMEOUT), '>=')
            );
        $rows = dbal_query($this->page_table, $clauses, array('lastscanned DESC'));
        if (sizeof($rows) > 0) {
            debug("++ PAGE CACHE HIT ++ $url");
            return json_decode($rows[0]['jsondata'], true);
        }
        debug("-- PAGE CACHE MISS -- $url");
        return false;
    }
    
    function cacheMovies($url, $start, $end, $obj) {
        // TODO: Do some cleanup first... i.e. delete all thats older than lastscanned
        $inserts = array(
            'url'           => $url, 
            'start'         => $start, 
            'end'           => $end, 
            'lastscanned'   => dbal_date(time()), 
            'jsondata'      => is_string($obj) ? $obj : json_encode($obj)
        );
        return dbal_insert($this->page_table, $inserts);
    }
    
    function getMetaInfo($id) {
        $clauses = array(
            array('id', $id),
            array('lastscanned', dbal_date(time() - CACHE_TIMEOUT), '>=')
            );
        $rows = dbal_query($this->meta_table, $clauses);
        if ($rows && sizeof($rows) == 1) {
            debug("++ META CACHE HIT ++ $id : " . json_encode($rows));
            return json_decode($rows[0]['jsondata'], true);
        }
        debug("-- META CACHE MISS -- $id");
        return false;
    }
    
    function cacheMetaInfo($id, $obj) {
        $inserts = array(
            'id'           => $id, 
            'lastscanned'   => dbal_date(time()), 
            'jsondata'      => is_string($obj) ? $obj : json_encode($obj)
        );
        return dbal_insert($this->meta_table, $inserts);
    }
    
    /**
     * Clears the caches.
     */
    function clear() {
        dbal_delete($this->page_table) or die("Error deleting table: " . mysql_error());
        dbal_delete($this->meta_table) or die("Error deleting table: " . mysql_error());
    }
    
    /**
     * Cleans stale cache-data
     **/
    function __cleanUp() {
        $staledate = dbal_date(time() - CACHE_TIMEOUT);
        $clauses = array(
            array('lastscanned', $staledate, '<')
        );
        dbal_delete($this->page_table, $clauses);
        dbal_delete($this->meta_table, $clauses);
    }
}
?>
