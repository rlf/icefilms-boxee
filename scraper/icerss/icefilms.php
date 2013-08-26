<?php
header('Content-Type: application/json');
// authentication needed on the request
// The icefilmsrss script simply forwards the url parameter to icefilms.info, scrapes
// the response, and extracts movie-ids, then it lookup the meta-data from tvdb.com and
// finally return a RSS feed to be used in Boxee.
// 
// Backlog:
// * Scrape icefilms
// * Generate RSS
// * Add meta-data
// * Enable caching (TTL on RSS + store RSS in database and use it for requests on the same url)
//
require_once dirname(__FILE__) . '/lib/common.php';
require_once dirname(__FILE__) . '/lib/cache.php';
require_once dirname(__FILE__) . '/lib/statistics.php';
require_once dirname(__FILE__) . '/lib/metahandler.php';
#require_once dirname(__FILE__) . '/lib/metahandler_imdbapi.php';
require_once dirname(__FILE__) . '/lib/metahandler_tmdb.php';
require_once dirname(__FILE__) . '/lib/icefilmscraper.php';

$uri = request_var('url');
$count = request_var('count', '50');
$offset = request_var('offset', '0');
if (($uri && strpos('http', $uri) != FALSE) || !is_numeric($count) || !is_numeric($offset)) {
    print json_encode(array('success' => FALSE, 'message' => 'Invalid url supplied', 'data' => array()));
    return;
}
$url = 'http://www.icefilms.info/' . $uri;
$t1 = time();
$cache = new Cache();
$stats = new Statistics();
//$metahandler_imdb = new MetaHandlerIMDB($stats);
$metahandler_imdb = new MetaHandlerTMDB($stats);
$metahandler = new MetaHandlerCache($metahandler_imdb, $cache);
$scraper = new IcefilmScraper($metahandler, $cache, $stats);
if (preg_match('|^tv/series/.*|', $uri)) {
    $movies = $scraper->getTVShow($url);
} else if (is_numeric($count) && is_numeric($offset)) {
    $count = intval($count);
    $offset = intval($offset);
    $movies = $scraper->getMovies($url, $offset, $count);
} else {
    print json_encode(array('success' => FALSE, 'message' => 'Invalid count or offset supplied', 'data' => array()));
    return;
}
$t2 = time();
print json_encode(array('success' => $movies != false, 'message' => ($t2-$t1) . " seconds", 'data' => $movies));
?>
