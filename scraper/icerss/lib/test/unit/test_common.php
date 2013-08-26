<?php
require_once dirname(__FILE__) . '/../simpletest/autorun.php';
require_once dirname(__FILE__) . '/../../common.php';

class TestCommon extends UnitTestCase {
    function setUp() {
        $_REQUEST['debug'] = 'true';
        ob_start();
    }

    function getOB() {
        $echo = ob_get_contents();
        ob_end_flush();
        return $echo;
    }

    function testDebugNoTrace() {
        // Act
        debug('Hello World');
        $debug = $this->getOB();

        // Assert
        $this->assertEqual($debug, "Hello World\n");
    }

    function testDebugWrongTrace() {
        // Arrange
        $_REQUEST['debug'] = '1';

        // Act
        debug('Hello World');
        $debug = $this->getOB();

        // Assert
        $this->assertEqual($debug, "");
    }

    function testDebugTrace() {
        // Arrange
        $_REQUEST['debug'] = 'TestCommon';

        // Act
        debug('My Trace');
        $debug = $this->getOB();

        // Assert
        $this->assertEqual($debug, "My Trace\n");
    }
}
?>
