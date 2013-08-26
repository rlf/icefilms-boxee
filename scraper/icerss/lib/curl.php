<?php
require_once dirname(__FILE__) . '/common.php';
#
# Snagged from http://stackoverflow.com/questions/26947/how-to-implement-a-web-scraper-in-php
# 
class Curl {       

    public $cookieJar = "";

    public function __construct($cookieJarFile = FALSE) {
        if (!$cookieJarFile) {
            $cookieJarFile = ini_get('upload_tmp_dir') . "/cookies.txt";
        }
        $this->cookieJar = $cookieJarFile;
    }

    function setup() { 
        $header = array();
        $header[0] = "Accept: text/xml,application/xml,application/xhtml+xml,";
        $header[0] .= "text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5";
        $header[] =  "Cache-Control: max-age=0";
        $header[] =  "Connection: keep-alive";
        $header[] = "Keep-Alive: 300";
        $header[] = "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7";
        $header[] = "Accept-Language: en-us,en;q=0.5";
        $header[] = "Pragma: "; // browsers keep this blank.


        curl_setopt($this->curl, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7');
        curl_setopt($this->curl, CURLOPT_HTTPHEADER, $header);
        curl_setopt($this->curl,CURLOPT_COOKIEJAR, $this->cookieJar); 
        curl_setopt($this->curl,CURLOPT_COOKIEFILE, $this->cookieJar);
        curl_setopt($this->curl,CURLOPT_AUTOREFERER, true);
        # Warning: curl_setopt(): CURLOPT_FOLLOWLOCATION cannot be activated when safe_mode is enabled
        #curl_setopt($this->curl,CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($this->curl,CURLOPT_RETURNTRANSFER, true);  
    }


    function get($url) {
        debug('URL: ' . $url);
        $this->curl = curl_init($url);
        $this->setup();

        $response = $this->request();
        debug('DATA: ' . $response);
        return $response;
    }

    function postForm($url, $fields, $referer='') {
        $this->curl = curl_init($url);
        $this->setup();
        curl_setopt($this->curl, CURLOPT_URL, $url);
        curl_setopt($this->curl, CURLOPT_POST, 1);
        curl_setopt($this->curl, CURLOPT_REFERER, $referer);
        curl_setopt($this->curl, CURLOPT_POSTFIELDS, $fields);
        return $this->request();
    }

    function getInfo($info) {
        $info = ($info == 'lasturl') ? curl_getinfo($this->curl, CURLINFO_EFFECTIVE_URL) : curl_getinfo($this->curl, $info);
        return $info;
    }

    function request() {
        return curl_exec($this->curl);
    }
}

?>
