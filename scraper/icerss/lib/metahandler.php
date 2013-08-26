<?php
#
# MetaHandler defines classes to interface with meta-information-providers (i.e. IMDB, www.imdbapi.com, tvdb, tmdb.com)
#
abstract class MetaHandler {
    abstract function getMetaInfo($id);
}

class MetaHandlerCache {
    function __construct($handler, $cache=None) {
        $this->handler = $handler;
        $this->cache = $cache;
    }
    /**
     * Returns a MetaInfo object.
     **/
    function getMetaInfo($id) {
        $meta = $this->cache->getMetaInfo($id);
        if ($meta) {
            return $meta;
        }
        $meta = $this->handler->getMetaInfo($id);
        if ($meta) {
            $this->cache->cacheMetaInfo($id, $meta);
        } else {
        	$meta = array('id' => $id);
        }
        return $meta;
    }
}
?>
