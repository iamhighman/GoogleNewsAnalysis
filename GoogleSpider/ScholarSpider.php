<?php                                                                                

   include("/home/Work2T/UPitts/GoogleMonitor/lib/ClassGoogleParser.php");
   include("/home/Work2T/UPitts/GoogleMonitor/lib/ClassDB_Scholar.php");

   $db = new DB_Scholar();
   $parser = new GoogleParser(); //extend Parser class
while(true){
   $monitors = $db->getMonitor(); //get all monitors task 
//print_r($monitors); die('');
   foreach($monitors as $key => $values){
      echo "\nGo : ".$values['name']." / ".$values['userid']."\n" ;
      $url= "http://scholar.google.com/citations?pagesize=100&view_op=list_works&user=".$values['userid']."AJ";
      $return = $parser->GoogleScholarParser($url, 2000);
      foreach($return[0] as $rid1 => $coauthor){
         $db->InsertCoauthors($coauthor, $values['id']);
      }
      foreach($return[1] as $rid2 => $paper){
         $db->InsertPapers($paper, $values['id']);
      }
      if(count($return[1]) == 0) $db->InsertNULLPapers($values['id']);
      $newauthors = $db->getNewAuthors();
      echo "\n1. Import ".count($return[0])." Coauthors and ".count($return[1])." Papers OK! \n";
      echo "2. Import ".count($newauthors)." new authors ... \n";
      foreach($newauthors as $rid3 => $author){
         $url= "http://scholar.google.com/citations?user=".$author['userid']."AJ";
         //echo $url."\n";
         $r = $parser->GoogleScholarParser($url, 10);
         $db->InsertNewAuthors($r[2][0], $author['userid']);
      }
      sleep(rand(1,5));
   }
   sleep(600);
}
?>
