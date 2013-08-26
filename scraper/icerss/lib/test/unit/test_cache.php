<?php
require_once dirname(__FILE__) . '/../simpletest/autorun.php';
require_once dirname(__FILE__) . '/../../cache.php';

class TestCache extends UnitTestCase {
    function testCacheMiss() {
        $cache = new Cache();
        $cache->clear();

        $id = 'myid';

        //
        // Test Meta cache
        //

        // MISS
        $this->assertTrue($cache->getMetaInfo($id) == false);
        $meta = array('mymeta' => 'mydata');

        // POPULATE
        $this->assertTrue($cache->cacheMetaInfo($id, $meta));

        // HIT
        $this->assertTrue($cache->getMetaInfo($id) == $meta);

        // HIT - different object
        $cache = new Cache();
        $this->assertTrue($cache->getMetaInfo($id) == $meta);

        // TWEAK - timeout
        $staledate = time() - CACHE_TIMEOUT - 1;
        mysql_query("UPDATE icerss_meta SET `lastscanned`='$staledate' WHERE `id`='$id'");

        // MISS
        $this->assertTrue($cache->getMetaInfo($id) == false);
        // Even though we miss, the db is not up-to-date (we live with this!!)
        $this->assertTrue($cache->cacheMetaInfo($id, $meta) == false);

        // MISS - new object = cleanup
        $cache = new Cache();
        $this->assertTrue($cache->getMetaInfo($id) == false);

        //
        // Test Movies Cache
        //
        $url = 'myurl';
        $offset = 10;
        $count = 10;
        $start = 10;
        $end = 20;
        $this->assertTrue($cache->getMovies($url, $offset, $count) == false);

        $movies = array('movies' => array('mymoooovie'), 'count' => 1);
        $this->assertTrue($cache->cacheMovies($url, $start, $end, $movies));
        $movies2 = $cache->getMovies($url, $start, $count);
        #print json_encode($movies) . "|" . json_encode($movies2) . "\n";
        $this->assertTrue($movies2 == $movies);

        // TWEAK - timeout
        $staledate = time() - CACHE_TIMEOUT - 1;
        mysql_query("UPDATE icerss_cache SET `lastscanned`='$staledate' WHERE `url`='$url'");
        $this->assertTrue($cache->getMovies($url, $start, $count) == false);
        $this->assertTrue($cache->cacheMovies($url, $start, $end, $movies) == true);
    }
}

?>
