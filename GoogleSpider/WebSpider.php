<?php                                                                                

   include("/home/highman/public_html/GoogleMonitor/lib/ClassGoogleParser.php");
   include("/home/highman/public_html/GoogleMonitor/lib/ClassDB.php");

   $db = new DB();
   $parser = new GoogleParser(); //extend Parser class

   $monitors = $db->getMonitor(); //get all monitors task 
   foreach($monitors as $key => $values){
      $attribute = json_decode($values['attribute'], true); //the search attribute
      $keywordIDs = $db->getKeyword($values['keywords']); //get all keyword sets by kids
      
      $pid = $db->InsertWebProject(array("mid"=>$values['id'], "note"=>""));
      $subtotal = 0;
      foreach($keywordIDs as $key1 => $keyword){
        $k = urlencode($keyword);
        $url = "http://www.google.com/search?q=$k&num=100"; //only deal with the url here
        if(isset($attribute['as_eq'])) $url.="as_eq=".$attribute['as_eq'];
        if(isset($attribute['as_sitesearch'])) $url.="as_sitesearch=".$attribute['as_sitesearch'];

        $arrReturn = $parser->GoogleSearchParser($url, $attribute['limit']);//send url and limit only
  
        //print_r($arrReturn); 

        foreach($arrReturn as $key2 => $result){
           $serial = $db->InsertWebContent($result, $pid, $keyword);
           $html = $parser->fetchWebNoProxy($result['url']);
           $parser->saveContent("./html/".$serial.".html", $html);
        }
        $subtotal += count($arrReturn);
        echo "Google: ".date("F j, Y, g:i a").": Goo $keyword finished. SetNum:".$attribute['limit'].", Fetched:".count($arrReturn)."\n";
        sleep(rand(1,2));
      }
      $db->UpdatWebProjectCount($subtotal, $pid);
   }

?>
