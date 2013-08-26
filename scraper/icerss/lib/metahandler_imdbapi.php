<?php
require_once dirname(__FILE__) . '/metahandler.php';
require_once dirname(__FILE__) . '/curl.php';

define("COMMA", "|, ?|");
/**
 * Real implementation of the MetaHandler API using the IMDBApi.
 */
 
class MetaHandlerIMDB extends MetaHandler {
    function __construct($stats = false) {
        $this->stats = $stats;
    }
    /**
     * Returns a MetaInfo object.
     **/
    function getMetaInfo($id)
    {
        if ($this->stats) {
            $this->stats->start('imdbapi', "getMetaInfo, $id");
        }
        $curl = new Curl();
        // TODSELECT s1.name, ROUND(s1.microtime/1000) 'sec', COUNT(*), MIN(s2.microtime), AVG(s2.microtime), MAX(s2.microtime) FROM `icerss_stats` s1, `icerss_stats` s2 WHERE s1.name = s2.name GROUP BY s1.name, secO: protect against injections?
        $jsonData = $curl->get('http://www.imdbapi.com/?i=' . $id );
        $data = json_decode($jsonData);
        if (!$data) {
            print "No movie for id=" . $id . " found in imdapi.com";
            return False;
        }
        $genres = preg_split(COMMA, $data->Genre);
        // [0.0 - 10.0] -> 0-5
        $rating = floatval($data->Rating) / 2;
        $writers = preg_split(COMMA, $data->Writer);
        $actors = preg_split(COMMA, $data->Actors);
        $plot = array('en' => $data->Plot);
        if ($this->stats) {
            $this->stats->end('imdbapi');
        }
        return array(
            'id' => $id,
            'title' => $data->Title,
            'year' => $data->Year,
            'genres' => $genres,
            'plot' => $plot,
            'poster' => $data->Poster,
            'runtime' => $data->Runtime,
            'rating' => $rating,
            'director' => $data->Director,
            'writers' => $writers,
            'actors' => $actors
        );
    }
}
?>