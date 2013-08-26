<?php
require_once dirname(__FILE__) . '/../simpletest/autorun.php';
require_once dirname(__FILE__) . '/../../common.php';
require_once dirname(__FILE__) . '/../../icefilmscraper.php';
require_once dirname(__FILE__) . '/../../metahandler_imdbapi.php';
require_once dirname(__FILE__) . '/../cache_memory.php';
require_once dirname(__FILE__) . '/../statistics_echo.php';


class TestIcefilmScraper extends UnitTestCase {
    static $is_setup = FALSE;
    /**
     * jUnit4 BeforeClass annotation.
     **/
    function setUp() {
        $stats = new StatisticsEcho();
        $cache = new MemoryCache();
        $metahandler = new MetaHandlerIMDB($stats);
        $cachedmetahandler = new MetaHandlerCache($metahandler, $cache);

        if (!TestIcefilmScraper::$is_setup) {
            date_default_timezone_set("EST");
            $cache->clear();
            TestIcefilmScraper::$is_setup = TRUE;
        }

        $this->url = 'http://www.icefilms.info/movies/popular/1';
        $this->scraper = new IcefilmScraper($cachedmetahandler, $cache, $stats);
    }
    function doScrape($offset=0, $count=12, $expectedCount=-1) {
        if ($expectedCount < 0) {
            $expectedCount = $count;
        }
        $scraper = $this->scraper;
        $url = $this->url;
        $t1 = time();
        $jsonmovies = $scraper->__scrapeMovies($url, $offset, $count);
        $tdiff = (time() - $t1);
        $movies = $jsonmovies;
        $n = sizeof($movies['movies']);
        $this->assertTrue($tdiff <= 15, 'No requests should take more than 15 seconds');
        $this->assertEqual($n, $expectedCount, "number of movies $n != $expectedCount");
        print "Found $n movies in $tdiff seconds<br/>\n";
    }
    function doGetMovies($offset=0, $count=12, $expectedCount = -1) {
        if ($expectedCount < 0) {
            $expectedCount = $count;
        }
        $scraper = $this->scraper;
        $url = $this->url;
        $t1 = time();
        $jsonmovies = $scraper->getMovies($url, $offset, $count);
        $tdiff = (time() - $t1);
        $movies = $jsonmovies;
        $n = sizeof($movies['movies']);
        $this->assertEqual($tdiff, 0, 'we should hit the cache');
        $this->assertEqual($n, $expectedCount, 'number of movies');
        print "Found $n movies in $tdiff seconds<br/>\n";
    }

    function testScrapeMovies0_12() {
        $this->doScrape();
    }
    function testScrapeMovies240_10() {
        $this->doScrape(240, 10, 0);
    }
    function testScrapeMovies140_13() {
        $this->doScrape(140, 13, 10);
    }
    function testScrapeMovies0_25() {
        $this->doScrape(0, 25);
    }

    function testGetMoviesCacheHit0_12() {
        $this->doGetMovies();
    }
    function testGetMoviesCacheHit240_10() {
        $this->doGetMovies(240, 10, 0);
    }
    function testGetMoviesCacheHit140_13() {
        $this->doGetMovies(140, 13, 10);
    }
    function testGetMoviesCacheHit0_25() {
        $this->doGetMovies(0, 25);
    }

    function testGetTVShow() {
        // Arrange
        $json_expected = <<<EOT
{"show":{"id":"tt0092455","title":"Star Trek: The Next Generation","year":"1987","genres":["Action","Adventure","Sci-Fi"],"plot":{"en":"Set decades after Captain James T. Kirk's 5-year mission, a new generation of Starfleet officers in a new Enterprise set off on their own mission to go where no one has gone before."},"poster":"http:\/\/ia.media-imdb.com\/images\/M\/MV5BMTUwMDY5NDA4NV5BMl5BanBnXkFtZTYwMDEzNzA5._V1._SX320.jpg","runtime":"45 mins","rating":4.4,"director":"N\/A","writers":["Gene Roddenberry"],"actors":["Patrick Stewart","Brent Spiner","Jonathan Frakes","LeVar Burton"],"name":"Star Trek: The Next Generation (1987)"},"seasons":[
{"name":"Season 1 (1987)","episodes":[{"name":"1x01 Encounter at Farpoint","url":"\/ip.php?v=19523&"},
{"name":"1x02 The Naked Now","url":"\/ip.php?v=19525&"},
{"name":"1x03 Code of Honor","url":"\/ip.php?v=19526&"},
{"name":"1x04 The Last Outpost","url":"\/ip.php?v=19527&"},
{"name":"1x05 Where No One Has Gone Before","url":"\/ip.php?v=19529&"},
{"name":"1x06 Lonely Among Us","url":"\/ip.php?v=19528&"},
{"name":"1x07 Justice","url":"\/ip.php?v=19530&"},
{"name":"1x08 The Battle","url":"\/ip.php?v=19531&"},
{"name":"1x09 Hide and Q","url":"\/ip.php?v=19532&"},
{"name":"1x10 Haven","url":"\/ip.php?v=19533&"},
{"name":"1x11 The Big Goodbye","url":"\/ip.php?v=19534&"},
{"name":"1x12 Datalore","url":"\/ip.php?v=19535&"},
{"name":"1x13 Angel One","url":"\/ip.php?v=19536&"},
{"name":"1x14 11001001","url":"\/ip.php?v=19537&"},
{"name":"1x15 Too Short a Season","url":"\/ip.php?v=19539&"},
{"name":"1x16 When the Bough Breaks","url":"\/ip.php?v=19540&"},
{"name":"1x17 Home Soil","url":"\/ip.php?v=19541&"},
{"name":"1x18 Coming of Age","url":"\/ip.php?v=19542&"},
{"name":"1x19 Heart of Glory","url":"\/ip.php?v=19543&"},
{"name":"1x20 The Arsenal of Freedom","url":"\/ip.php?v=19544&"},
{"name":"1x21 Symbiosis","url":"\/ip.php?v=19545&"},
{"name":"1x22 Skin of Evil","url":"\/ip.php?v=19546&"},
{"name":"1x23 We'll Always Have Paris","url":"\/ip.php?v=19548&"},
{"name":"1x24 Conspiracy","url":"\/ip.php?v=19549&"},
{"name":"1x25 The Neutral Zone","url":"\/ip.php?v=19550&"}]
},
{"name":"Season 2 (1989)","episodes":[{"name":"2x07 Unnatural Selection","url":"\/ip.php?v=19621&"},
{"name":"2x09 The Measure of a Man","url":"\/ip.php?v=19623&"},
{"name":"2x13 Time Squared","url":"\/ip.php?v=19627&"},
{"name":"2x16 Q Who?","url":"\/ip.php?v=19630&"},
{"name":"2x17 Samaritan Snare","url":"\/ip.php?v=19631&"},
{"name":"2x18 Up the Long Ladder","url":"\/ip.php?v=19632&"},
{"name":"2x19 Manhunt","url":"\/ip.php?v=19633&"},
{"name":"2x22 Shades of Gray","url":"\/ip.php?v=19636&"}]},
{"name":"Season 3 (1990)","episodes":[{"name":"3x25 Transfigurations","url":"\/ip.php?v=68757&"},
{"name":"3x26 The Best of Both Worlds: Part 1","url":"\/ip.php?v=19661&"}]},
{"name":"Season 4 (1990)","episodes":[{"name":"4x01 The Best of Both Worlds: Part 2","url":"\/ip.php?v=19662&"},
{"name":"4x02 Family","url":"\/ip.php?v=19663&"},
{"name":"4x03 Brothers","url":"\/ip.php?v=19664&"},
{"name":"4x04 Suddenly Human","url":"\/ip.php?v=19665&"},
{"name":"4x05 Remember Me","url":"\/ip.php?v=19666&"},
{"name":"4x06 Legacy","url":"\/ip.php?v=19667&"},
{"name":"4x07 Reunion","url":"\/ip.php?v=19668&"},
{"name":"4x08 Future Imperfect","url":"\/ip.php?v=19669&"},
{"name":"4x09 Final Mission","url":"\/ip.php?v=19670&"},
{"name":"4x10 The Loss","url":"\/ip.php?v=19671&"},
{"name":"4x11 Data's Day","url":"\/ip.php?v=19672&"},
{"name":"4x12 The Wounded","url":"\/ip.php?v=19673&"},
{"name":"4x13 Devil's Due","url":"\/ip.php?v=19674&"},
{"name":"4x14 Clues","url":"\/ip.php?v=19675&"},
{"name":"4x15 First Contact","url":"\/ip.php?v=19676&"},
{"name":"4x16 Galaxy's Child","url":"\/ip.php?v=19677&"},
{"name":"4x17 Night Terrors","url":"\/ip.php?v=19678&"},
{"name":"4x18 Identity Crisis","url":"\/ip.php?v=19679&"},
{"name":"4x19 The Nth Degree","url":"\/ip.php?v=19680&"},
{"name":"4x20 Qpid","url":"\/ip.php?v=19681&"},
{"name":"4x21 The Drumhead","url":"\/ip.php?v=19682&"},
{"name":"4x22 Half a Life","url":"\/ip.php?v=19683&"},
{"name":"4x23 The Host","url":"\/ip.php?v=19684&"},
{"name":"4x24 The Mind's Eye","url":"\/ip.php?v=19685&"},
{"name":"4x25 In Theory","url":"\/ip.php?v=68615&"},
{"name":"4x26 Redemption: Part 1","url":"\/ip.php?v=68784&"}]},
{"name":"Season 5 (1991)","episodes":[{"name":"5x01 Redemption: Part 2","url":"\/ip.php?v=19686&"},
{"name":"5x02 Darmok","url":"\/ip.php?v=19687&"},
{"name":"5x03 Ensign Ro","url":"\/ip.php?v=19688&"},
{"name":"5x04 Silicon Avatar","url":"\/ip.php?v=19689&"},
{"name":"5x05 Disaster","url":"\/ip.php?v=19690&"},
{"name":"5x07 Unification: Part 1","url":"\/ip.php?v=19692&"},
{"name":"5x09 A Matter of Time","url":"\/ip.php?v=19694&"},
{"name":"5x10 New Ground","url":"\/ip.php?v=19695&"},
{"name":"5x11 Hero Worship","url":"\/ip.php?v=19696&"},
{"name":"5x12 Violations","url":"\/ip.php?v=19697&"},
{"name":"5x15 Power Play","url":"\/ip.php?v=19700&"},
{"name":"5x16 Ethics","url":"\/ip.php?v=19701&"},
{"name":"5x17 The Outcast","url":"\/ip.php?v=19702&"},
{"name":"5x18 Cause and Effect","url":"\/ip.php?v=19703&"},
{"name":"5x19 The First Duty","url":"\/ip.php?v=19704&"},
{"name":"5x20 Cost of Living","url":"\/ip.php?v=19705&"},
{"name":"5x21 The Perfect Mate","url":"\/ip.php?v=19706&"},
{"name":"5x22 Imaginary Friend","url":"\/ip.php?v=19707&"},
{"name":"5x23 I, Borg","url":"\/ip.php?v=19708&"},
{"name":"5x24 The Next Phase","url":"\/ip.php?v=19709&"},
{"name":"5x26 Time's Arrow: Part 1","url":"\/ip.php?v=19711&"}]},
{"name":"Season 6 (1992)","episodes":[{"name":"6x01 Time's Arrow: Part 2","url":"\/ip.php?v=19712&"},
{"name":"6x02 Realm of Fear","url":"\/ip.php?v=19713&"},
{"name":"6x03 Man of the People","url":"\/ip.php?v=19714&"},
{"name":"6x04 Relics","url":"\/ip.php?v=19715&"},
{"name":"6x05 Schisms","url":"\/ip.php?v=19716&"},
{"name":"6x06 True Q","url":"\/ip.php?v=19717&"},
{"name":"6x07 Rascals","url":"\/ip.php?v=19718&"},
{"name":"6x08 A Fistful of Datas","url":"\/ip.php?v=19719&"},
{"name":"6x09 The Quality of Life","url":"\/ip.php?v=19720&"},
{"name":"6x10 Chain of Command: Part 1","url":"\/ip.php?v=19721&"},
{"name":"6x11 Chain of Command: Part 2","url":"\/ip.php?v=19722&"},
{"name":"6x12 Ship in a Bottle","url":"\/ip.php?v=19723&"},
{"name":"6x13 Aquiel","url":"\/ip.php?v=19724&"},
{"name":"6x14 Face of the Enemy","url":"\/ip.php?v=19725&"},
{"name":"6x15 Tapestry","url":"\/ip.php?v=19726&"},
{"name":"6x16 Birthright: Part 1","url":"\/ip.php?v=19727&"},
{"name":"6x17 Birthright: Part 2","url":"\/ip.php?v=19728&"},
{"name":"6x18 Starship Mine","url":"\/ip.php?v=19729&"},
{"name":"6x19 Lessons","url":"\/ip.php?v=19730&"},
{"name":"6x20 The Chase","url":"\/ip.php?v=19731&"},
{"name":"6x21 Frame of Mind","url":"\/ip.php?v=19732&"},
{"name":"6x22 Suspicions","url":"\/ip.php?v=19733&"},
{"name":"6x23 Rightful Heir","url":"\/ip.php?v=19734&"},
{"name":"6x24 Second Chances","url":"\/ip.php?v=19735&"},
{"name":"6x25 Timescape","url":"\/ip.php?v=19736&"},
{"name":"6x26 Descent: Part 1","url":"\/ip.php?v=19737&"}]},
{"name":"Season 7 (1993)","episodes":[{"name":"7x01 Descent: Part 2","url":"\/ip.php?v=19738&"},
{"name":"7x02 Liaisons","url":"\/ip.php?v=19739&"},
{"name":"7x03 Interface","url":"\/ip.php?v=19740&"},
{"name":"7x04 Gambit: Part 1","url":"\/ip.php?v=19741&"},
{"name":"7x05 Gambit: Part 2","url":"\/ip.php?v=19742&"},
{"name":"7x06 Phantasms","url":"\/ip.php?v=19743&"},
{"name":"7x07 Dark Page","url":"\/ip.php?v=19744&"},
{"name":"7x08 Attached","url":"\/ip.php?v=19745&"},
{"name":"7x09 Force of Nature","url":"\/ip.php?v=19746&"},
{"name":"7x10 Inheritance","url":"\/ip.php?v=19747&"},
{"name":"7x11 Parallels","url":"\/ip.php?v=19748&"},
{"name":"7x12 The Pegasus","url":"\/ip.php?v=19749&"},
{"name":"7x13 Homeward","url":"\/ip.php?v=19750&"},
{"name":"7x14 Sub Rosa","url":"\/ip.php?v=19751&"},
{"name":"7x15 Lower Decks","url":"\/ip.php?v=19752&"},
{"name":"7x16 Thine Own Self","url":"\/ip.php?v=19753&"},
{"name":"7x17 Masks","url":"\/ip.php?v=19754&"},
{"name":"7x18 Eye of the Beholder","url":"\/ip.php?v=19755&"},
{"name":"7x19 Genesis","url":"\/ip.php?v=19756&"},
{"name":"7x20 Journey's End","url":"\/ip.php?v=19757&"},
{"name":"7x21 Firstborn","url":"\/ip.php?v=19758&"},
{"name":"7x22 Bloodlines","url":"\/ip.php?v=19759&"},
{"name":"7x23 Emergence","url":"\/ip.php?v=19760&"},
{"name":"7x24 Preemptive Strike","url":"\/ip.php?v=19761&"},
{"name":"7x25 All Good Things...","url":"\/ip.php?v=19762&"}]}],"count":1}
EOT;
        $expected = json_decode($json_expected, true);
        // Act
        $show = $this->scraper->__scrapeTVShow('http://www.icefilms.info/tv/series/1/426'); // Star Trek: Next Generation
        debug("SHOW: " . json_encode($show));
        // Assert
        $this->assertEqual($show, $expected);
    }
}
?>
