<?php
require_once 'curl.php';

class IcefilmScraper {
    function __construct($metahandler, $cache, $stats=false) {
        $this->pagecache = $cache;
        $this->metahandler = $metahandler;
        $this->stats = $stats;
    }
    
    function getMovies($url, $offset, $count) {
        $data = $this->pagecache->getMovies($url, $offset, $count);
        if ($data) {
            return $data;
        }
        return $this->__scrapeMovies($url, $offset, $count);
    }

    function getTVShow($url) {
        $data = $this->pagecache->getMovies($url, 0, 0);
        if ($data) {
            return $data;
        }
        return $this->__scrapeTVShow($url);

    }
    
    /**
     * Scrapes the supplied URL for videos, and return a list of
     * MetaInfo objects.
     **/
    function __scrapeMovies($url, $offset=0, $count=12) {
        if ($this->stats) {
            $this->stats->start('icefilms.info:movies', "$url");
        }
        $curl = new Curl();
        $html = $curl->get($url);
        $dom = new DOMDocument();
        @$dom->loadHTML($html);
        $xpath = new DOMXPath($dom);
        $links = $xpath->query("//a[@name='i' and @id]|//a[starts-with(@href, '/ip.php?')]");
        //preg_match_all('|<a name=i id=(.+?)></a><img class=star><a href=/(.+?)>(.+?)<br>|', $html, $matches, PREG_SET_ORDER);
        $movies = array();
        $real_offset = min($links->length/2, $offset);
        $real_count = min($count, $links->length/2 - $real_offset);
        debug("offset=$offset, count=$count, real_offset=$real_offset, real_count=$real_count");
        if ($real_count > 0) {
            foreach (range($real_offset*2, ($real_offset + $real_count - 1)*2, 2) as $index) {
                // i: <a name=i id={id}></a>
                // i+1: <a href=/ip.php?{videoid}>{name}</a>
                $imdb_link = $links->item($index);
                $icefilm_link = $links->item($index + 1);

                $id = $imdb_link->attributes->getNamedItem('id')->nodeValue;
                $name = $icefilm_link->nodeValue;
                $url = substr($icefilm_link->attributes->getNamedItem('href')->nodeValue, 1);
                $metaInfo = $this->metahandler->getMetaInfo('tt' . $id);
                $metaInfo['name'] = $name;
                $metaInfo['url'] = $url;
                $movies[] = $metaInfo;
            }
        }
        $data = array('movies' =>$movies, 'count' => $links->length/2);
        $this->pagecache->cacheMovies($url, $offset, $offset + $count, $data);
        if ($this->stats) {
            $this->stats->end('icefilms.info:movies');
        }
        return $data;
    }

    function __scrapeTVShow($url, $offset=0, $count=12) {
        if ($this->stats) {
            $this->stats->start('icefilms.info:tv', "$url");
        }
        $curl = new Curl();
        $html = $curl->get($url);
        if (!$html) {
            return false;
        }
        $dom = new DOMDocument();
        @$dom->loadHTML($html); // Suppress warnings - odds are there are PLENTY!
        $xpath = new DOMXPath($dom);
        $nodes = $xpath->query("//h1");
        $seasons = array();
        foreach ($nodes as $header) {
            // Scrape IMDB info (name, id, metainfo)
            $name = $header->nodeValue;
            # and starts-with(@href, 'http://www.imdb.com/title/tt')", $header);
            $imdblinks = $xpath->query(".//a[@class='iframe' and starts-with(@href, 'http://www.imdb.com/title/tt')]", $header);
            $metaInfo = array();
            foreach ($imdblinks as $imdblink) {
                $imdblink = $imdblink->attributes->getNamedItem('href')->nodeValue;
                if (preg_match('|/title/(tt[0-9]+)|', $imdblink, $matches)) {
                    $id = $matches[1];
                    $metaInfo = $this->metahandler->getMetaInfo($id);
                    $metaInfo['id'] = $id;
                }
                break;
            }
            $metaInfo['name'] = $name;

            // Scrape seasons
            $nodes = $xpath->query("//span[@class='list']/h4|//span[@class='list']/a[@href and starts-with(@href, '/ip.php')]");
            $season = FALSE;
            foreach ($nodes as $node) {
                // Should be both h4 and a nodes.
                if ($node->nodeName == 'h4') {
                    if ($season) {
                        $seasons[] = $season;
                    }
                    $season = array('name' => $node->nodeValue, 'episodes' => array());
                } else if ($node->nodeName == 'a' && $season) {
                    $episode = array('name' => $node->nodeValue, 'url' => $node->attributes->getNamedItem('href')->nodeValue);
                    $season['episodes'][] = $episode;
                }
            }
            if ($season) {
                $seasons[] = $season;
            }
            break;
        }
        $data = array('show' => $metaInfo, 'seasons' => $seasons, 'count' => sizeof($nodes));
        $this->pagecache->cacheMovies($url, 0, 0, $data);
        if ($this->stats) {
            $this->stats->end('icefilms.info:tv');
        }
        return $data;
    }
}
?>
