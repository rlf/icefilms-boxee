<?php
require_once 'simpletest/autorun.php';

class AllTests extends TestSuite {
    function AllTests() {
        parent::__construct('IceRSS Test Suite');
        $this->collect(dirname(__FILE__) . '/unit', new SimplePatternCollector('/test.*php$/i'));
    }
}
?>