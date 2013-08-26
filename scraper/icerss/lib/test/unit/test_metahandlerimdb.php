posters<?php
require_once dirname(__FILE__) . '/../simpletest/autorun.php';
require_once dirname(__FILE__) . '/../../metahandler_imdbapi.php';

class TestMetaHandlerIMDB extends UnitTestCase {
    function testGetMetaInfo() {
        $handler = new MetaHandlerIMDB();
        $metainfo = $handler->getMetaInfo('tt1119646');
        $expected = json_decode('{"id":"tt1119646","title":"The Hangover","year":"2009","genres":["Comedy","Crime"],"plot":{"en" : "A Las Vegas-set comedy centered around three groomsmen who lose their about-to-be-wed buddy during their drunken misadventures, then must retrace their steps in order to find him."},"poster":"http:\/\/ia.media-imdb.com\/images\/M\/MV5BMTU1MDA1MTYwMF5BMl5BanBnXkFtZTcwMDcxMzA1Mg@@._V1._SX320.jpg","runtime":"1 hr 40 mins","rating":3.95,"director":"Todd Phillips","writers":["Jon Lucas","Scott Moore"],"actors":["Zach Galifianakis","Bradley Cooper","Justin Bartha","Ed Helms"]}', TRUE);
        $this->assertEqual($metainfo, $expected);
    }
}
?>
