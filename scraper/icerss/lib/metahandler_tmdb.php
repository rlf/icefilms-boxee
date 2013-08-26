<?php
require_once dirname(__FILE__) . '/metahandler.php';
require_once dirname(__FILE__) . '/curl.php';

define("COMMA", "|, ?|");
/**
 * Real implementation of the MetaHandler API using the IMDBApi.
 */
 
class MetaHandlerTMDB extends MetaHandler {
    function __construct($stats = false, $api_key='e45a323100c8daf9b792599c1f08049a') {
        $this->stats = $stats;
		$this->api_key = $api_key;
    }
    /**
     * Returns a MetaInfo object.
     **/
    function getMetaInfo($id)
    {
        if ($this->stats) {
            $this->stats->start('tmdb', "getMetaInfo, $id");
        }
        $curl = new Curl();
        // TODSELECT s1.name, ROUND(s1.microtime/1000) 'sec', COUNT(*), MIN(s2.microtime), AVG(s2.microtime), MAX(s2.microtime) FROM `icerss_stats` s1, `icerss_stats` s2 WHERE s1.name = s2.name GROUP BY s1.name, secO: protect against injections?
        $jsonData = $curl->get('http://api.themoviedb.org/2.1/Movie.imdbLookup/en/json/' . $this->api_key . '/' . $id);
        $data = json_decode($jsonData, true);
        if (!$data) {
            return False;
        }
		$data = $data[0];
        $genres = array();
		if (array_key_exists('genres', $data)) {
	        foreach ($data['genres'] as $genre) {
	        	$genres[] = $genre['name'];
	        }
		}
        // [0.0 - 10.0] -> 0-5
        $rating = floatval($data['rating']) / 2;
        $writers = preg_split(COMMA, $data->Writer);
        $actors = preg_split(COMMA, $data->Actors);
        $plot = array('en' => $data['overview']);
		$poster = 'N/A';
		if (array_key_exists('posters', $data)) {
			foreach ($data['posters'] as $img) {
				if ($img['image']['size'] == 'cover') {
					$poster = $img['image']['url'];
					break;
				}
			}
		}
		$runtime = intval($data['runtime']); // Minutes
		$runtime = intval(floor($runtime / 60)) . ' hr ' . ($runtime % 60) . ' mins';
		$year = $data['released'];
		if (strlen($year) > 4) {
			$year = substr($year, 0, 4);
		}
		$tmdb = $data['id'];
		// TODO: Fetch director, writers + actors
        if ($this->stats) {
            $this->stats->end('tmdb');
        }
        return array(
            'id' => $id,
            'title' => $data['name'],
            'year' => $year,
            'genres' => $genres,
            'plot' => $plot,
            'poster' => $poster,
            'runtime' => $runtime,
            'rating' => $rating,
            'director' => '',
            'writers' => array(),
            'actors' => array()
        );
    }
}
?>