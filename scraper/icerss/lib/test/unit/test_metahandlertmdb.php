<?php
require_once dirname(__FILE__) . '/../simpletest/autorun.php';
require_once dirname(__FILE__) . '/../../metahandler_tmdb.php';

class TestMetaHandlerTMDB extends UnitTestCase {
    function testGetMetaInfo() {
        $handler = new MetaHandlerTMDB();
        $metainfo = $handler->getMetaInfo('tt1119646');
		debug('TMDB: ' . json_encode($metainfo));
        $expected = json_decode('{"id":"tt1119646","title":"The Hangover","year":"2009","genres":["Comedy","Crime"],"plot":{"en" : "A Las Vegas-set comedy centered around three groomsmen who lose their about-to-be-wed buddy during their drunken misadventures, then must retrace their steps in order to find him."},"poster":"http://cf1.imgobject.com/posters/87b/4e91c4e15e73d64c3800087b/the-hangover-cover.jpg","runtime":"1 hr 40 mins","rating":4.3,"director":"","writers":[],"actors":[]}', TRUE);
        $this->assertEqual($metainfo, $expected);
    }
}
?>
