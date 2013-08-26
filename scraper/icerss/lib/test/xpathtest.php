<?php
require_once dirname(__FILE__) . '/../common.php';
require_once dirname(__FILE__) . '/../curl.php';
$url = request_var('url', '');
$xpath = request_var('xpath', '');
$sub1 = request_var('sub1', '');
$sub2 = request_var('sub2', '');
function dumpNode($n, $indent = '') {
    $s = $indent . '[' . $n->nodeName;
    foreach ($n->attributes as $attr) {
        $s .= ' ' . $attr->nodeName . '=' . $attr->nodeValue;
    }
    $s .= '] = ' . $n->nodeValue;
    $s .= "\n";
    return $s;
}
if ($url && $xpath) {
    $curl = new Curl();
    $data = $curl->get($url);
    $output = htmlentities($data);
    $dom = new DOMDocument();
    @$dom->loadHTML($data);
    $xp = new DOMXPath($dom);
    $query = $xp->query($xpath);
    foreach ($query as $q) {
        $debug .= dumpNode($q);
        if ($sub1) {
            $q1 = $xp->query($sub1, $q);
            foreach ($q1 as $c1) {
                $debug .= dumpNode($c1, '  ');
                if ($sub2) {
                    $q2 = $xp->query($sub2, $c1);
                    foreach ($q2 as $c2) {
                        $debug .= dumpNode($c2, '    ');
                    }
                }
            }
        }
    }
}
?>
<html>
    <head><title>XPath Playground</title></head>
    <body>
        <form>
            <div>URL: <input type="text" name="url" id="url" size="80" value="<?=$url?>"/></div>
            <div>XPath: <input type="text" name="xpath" id="xpath" size="80" value="<?=$xpath?>"/></div>
            <div>Sub-1: <input type="text" name="sub1" id="sub1" size="80" value="<?=$sub1?>"/></div>
            <div>Sub-2: <input type="text" name="sub2" id="sub2" size="80" value="<?=$sub2?>"/></div>
            <div><input type="submit" value="Evaluate"/></div>
<h2>XPath:</h2>
<pre>
<?=$debug?>
</pre>
<h2>Content:</h2>
        <pre>
<?=$output?>
        </pre>
        </form>
    </body>
</html>
