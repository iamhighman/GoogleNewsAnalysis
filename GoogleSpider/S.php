<?php


include("/home/Work2T/UPitts/GoogleMonitor/lib/ClassGoogleParser.php");
include("/home/Work2T/UPitts/GoogleMonitor/lib/ClassDB_Scholar.php");

$db = new DB_Scholar();
$parser = new GoogleParser(); //extend Parser class

$list = $db->getPaper(0, 1000000);
echo "Tasks: ".count($list)."\n";
foreach($list as $id => $c){
   $purl = $c['url'];
   $pid = $c['id'];
   $url = "http://scholar.google.com".$purl;
 
   if(!isset($c) || file_exists("./paper/".$pid)) continue; 

   $input = $parser->fetchWeb($url); //echo $input;
   if(strlen($input) == 0 ) $input = $parser->fetchWebNoProxy($url);
   $parser->saveContent("./paper/".$pid, $input);
   echo " ".$url." with ".strlen($input)." OK! \n";
   sleep(rand(0,0.11));
}

?>

