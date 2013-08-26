<?php
/* 
 * Cache that doesn't need a DB (dummy cache.).
 */

class MemoryCache {
    static $cache = array();
    /**
     * Returns the cache as a json-string, or false.
     * @param type $url
     * @param type $offset
     * @param type $count
     * @return type
     */
    function getMovies($url, $offset, $count) {
        $key = "$url|$offset|" . ($offset+$count);
        if (array_key_exists($key, MemoryCache::$cache)) {
            return MemoryCache::$cache[$key];
        }
        return false;
    }

    function cacheMovies($url, $start, $end, $obj) {
        $key = "$url|$start|$end";
        MemoryCache::$cache[$key] = $obj;
        return true;
    }

    function getMetaInfo($id) {
        if (array_key_exists($id, MemoryCache::$cache)) {
            return MemoryCache::$cache[$id];
        }
        return false;
    }

    function cacheMetaInfo($id, $obj) {
        MemoryCache::$cache[$id] = $obj;
        return true;
    }

    /**
     * Clears the caches.
     */
    function clear() {
        MemoryCache::$cache = array();
    }
}
?>
