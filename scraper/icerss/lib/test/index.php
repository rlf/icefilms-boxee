<html>
    <head><title>Installation and Test of IceRSS</title></head>
    <body>
<pre>
Installation and Test of IceRSS
-------------------------------
TODO: Add some funky fancy CSS to this... perhaps...
        
Test
====
<a href="alltests.php">Run complete test-suite</a> - And have patience! Young padowan
  - <a href="unit/test_common.php">TestCommon</a>
  - <a href="unit/test_cache.php">TestCache</a>
  - <a href="unit/test_metahandlerimdb.php">TestMetaHandlerIMDB</a>
  - <a href="unit/test_metahandlertmdb.php">TestMetaHandlerTMDB</a>
  - <a href="unit/test_icefilmscraper.php">TestIcefilmScraper</a>


Information
===========
<a href="xpathtest.php">XPath Test</a> - A sandbox for testing XPath expressions against URLs
<a href="info.php">See phpinfo() for this server</a>

Installation
============
<a href="clear_cache.php">Clear the caches</a>

<form name="create_db" action="create_db.php?c=init" method="POST"><table>
<tr><td>username</td><td><input type="text" name="u" id="u" value="" size="20"/></td></tr>
<tr><td>password</td><td><input type="password" name="p" id="p" value="" size="20"/></td></tr>
<tr><td>database</td><td><input type="text" name="db" id="db" value="" size="20"/></td></tr>
<tr><td>table-prefix</td><td><input type="text" name="prefix" id="prefix" value="icerss_" size="20"/></td></tr>
<tr><td>&nbsp;</td><td><input type="submit" value="Install"/></td></tr>
</table></form>
TODO: Add some fancy warning (perhaps 2-5 levels of javascript popups?) to warn
about the above button being a bit... violent... to the database and all...
... naaa... people will eventually learn.

Statistics
==========
Usage <a href="stats.php">statistics</a> of providers.
</pre></body>
</html>