<?php
include("/home/highman/public_html/GoogleMonitor/lib/ClassParser.php");

class GoogleParser extends Parser {

   function GoogleScholarParser($base_url, $limit){
      $arr_coauthor= array(); $arr_papers = array(); $arr_infos = array();
      $matches; $resultStats=0;

      for($j=0;$j < $limit;$j+=100){
         $input = $this->fetchWeb($base_url."&cstart=".$j);  //echo strlen($input)."\n";
         if(strlen($input) < 10000) {
           sleep(rand(1,5)); $input = $this->fetchWebNoProxy($base_url."&cstart=".$j);
         }
         if($j==0){ //handle the coauthor only in the first page
            $results = explode("/citations?user", $input);
            array_shift($results); array_shift($results); array_pop($results); //one more for the select all option
            foreach($results as $rid => $chunk){
               $uid = $this->find2find($chunk, "=", "&");
               array_push($arr_coauthor, array("userid"=>$uid));
            }

            $name = $this->find2find($input, "<span id=\"cit-name-display\" class=\"cit-in-place-nohover\">", "</span>");
            $affiliation = $this->find2find($input, "<span id=\"cit-affiliation-display\" class=\"cit-in-place-nohover\">", "</span>");
            $fields = str_replace("&nbsp;", "", strip_tags($this->find2find($input, "<span id=\"cit-int-read\">", "</span></form>")));
            array_push($arr_infos, array("name"=>$name, "aff"=>$affiliation, "fields"=>$fields));
         }
         $results = explode("<td id=\"col-title\">", $input);
         array_shift($results);array_shift($results);
         $resut_counter = 0;
         foreach($results as $rid => $chunk){
            $url = str_replace("&amp;", "&", $this->find2find($chunk, "href=\"", "\""));
            $title = $this->find2find($chunk, "cit-dark-large-link\">", "<");
            $authors = strip_tags($this->find2find($chunk, "</a><br><span class=\"cit-gray\">", "</span>"));
            $source = $this->find2find($chunk, "</span><br><span class=\"cit-gray\">", "</span>");
            $citation = str_replace("&nbsp;", "", strip_tags($this->find2find($chunk, "<td id=\"col-citedby\">", "</td>")));
            $year = $this->find2find($chunk, "col-year\">", "</td>");
            array_push($arr_papers, array("url"=>$url, "title"=>$title,"authors"=>$authors,"source"=>$source,"citation"=>$citation,"year"=>$year));
            $resut_counter++; //for the last page escape
         }
         if($resut_counter < 50) break;
      }
      return array($arr_coauthor, $arr_papers, $arr_infos); 
   }

   function GoogleSearchParser($base_url, $limit){
      $regexp = "/<a\s[^>]*href=(\"??).*(http[^\" >]*?)\\1[^>]*>(.*)<\/a>/siU";
      $arr= array(); $matches; $resultStats=0;

      for($j=0;$j < $limit;$j+=100){
         $input = $this->fetchWeb($base_url."&start=".$j);  //echo $base_url."&start=".$j;
         $results = explode("<h3 class=\"r\">", $input);
         array_shift($results);  
         $resut_counter = 0; 
         foreach($results as $rid => $chunk){
            $url = $this->find2find($chunk, "/url?q=", "&amp;");
            $title = $this->find2find($chunk, "\">", "</a>");
            $sub = $this->find2find($chunk, "class=\"st", "/span>");
            $date = date("Y-m-d", strtotime($this->find2find($sub, "\">", "<b>")));
            $quote = $this->find2find($sub, "</b>", "<b>.");
            array_push($arr, array("title"=>$title, "url"=>$url, "date"=>$date, "quote"=>$quote));
            $resut_counter++; //for the last page escape
         }
         if($resut_counter < 50) break;
      }

/*
      for($j=0;$j < $limit;$j+=100){
         $input = $this->fetchWeb($url."&start=".$j);
         $input = str_replace("/url?q=", "", $input); //Goolge Result re-version 20120218
         preg_match_all($regexp, $input, $matches, PREG_SET_ORDER);
         $arr = array_merge($arr, $matches);
         if(count($arr) < 50) break;
      }

      $i = 1;
      $arrReturn = array();
      foreach($arr as $match) {
         # $match[2] = link address
         # $match[3] = link text
         $filter = "ct=clnk|sa=X|google.com|72.14.235.104|googleusercontent";
         $filter .= "|.pdf|.doc|.ppt|.xls|youtube.com|blogger.com";
         if(!ereg($filter, $match[2])){
            $title = $match[3];
            $arrtmp = explode("&amp;sa=U", $match[2]); //Trim Google inner re-direct code
            $arrReturn[$title] = $arrtmp[0];
            $i++;
         }
      }
*/
      return $arr;
   }


}

?>
