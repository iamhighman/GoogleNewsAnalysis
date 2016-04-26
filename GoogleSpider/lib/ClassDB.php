<?php

class DB{
   function DB(){
      $this->config();
   }
   function config(){
      $this->link = mysql_pconnect('localhost', 'root', 'imna1234tku*') or
      die("mysql_connect() failed.");
      mysql_select_db("Google", $this->link) or
      die("mysql_select_db() failed.");  	
      mysql_query("SET CHARACTER SET 'utf8'", $this->link);
   }

   function InsertKeyword($p){
      $title = mysql_real_escape_string($p['title']);
      $keyword = mysql_real_escape_string($p['keyword']);
      $tags = mysql_real_escape_string($p['tags']);
      $note = mysql_real_escape_string($p['note']);

      $sql = "  INSERT INTO `Google`.`KEYWORD` (`ID`,`TITLE`,`KEYWORD`,`TAGS`, `NOTE`) "; 
      $sql .= " VALUES('','$title','$keyword', '$tags', '$note');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo $sql;
         return false;
      }
   }

   function UpdateKeyword($p){
      $title = mysql_real_escape_string($p['title']);
      $keyword = mysql_real_escape_string($p['keyword']);
      $tags = mysql_real_escape_string($p['tags']);
      $note = mysql_real_escape_string($p['note']);
      $id = mysql_real_escape_string($p['id']);

      $sql = "  UPDATE `Google`.`KEYWORD` SET `TITLE` = '$title', `KEYWORD` = '$keyword' ";
      $sql .= " , `TAGS` = '$tags', `NOTE` = '$note'  WHERE  `KEYWORD`.`ID` = $id;";

      if(mysql_query($sql ,$this->link)){
         return true;
      }else{
         //echo $sql;
         return false;
      }
   }

   
   function InsertMonitor($p){
      $title = mysql_real_escape_string($p['title']);
      $attribute = mysql_real_escape_string($p['attribute']);
      $note = mysql_real_escape_string($p['note']);
      $frequency = mysql_real_escape_string($p['frequency']);
      $keywords = mysql_real_escape_string($p['keywords']);  
 
      $sql = "INSERT INTO `Google`.`MONITOR` (`ID`,`TITLE`,`KEYWORDS`,`ATTRIBUTE`,`NOTE`, `FREQUENCY`) ";
      $sql .= " VALUES('','$title', '$keywords','$attribute','$note', '$frequency');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo $sql;
         return false;
      }    
   }   

   function UpdateMonitor($p){
      $title = mysql_real_escape_string($p['title']);
      $attribute = mysql_real_escape_string($p['attribute']);
      $note = mysql_real_escape_string($p['note']);
      $id = mysql_real_escape_string($p['id']);
   
      $sql = "  UPDATE `Google`.`PROJECT` SET `TITLE` = '$title', `ATTRIBUTE` = '$attribute' ";
      $sql .= " , `NOTE` = '$note'  WHERE  `PROJECT`.`ID` = $id;";

      if(mysql_query($sql ,$this->link)){
         return true;
      }else{
         //echo $sql;
         return false;
      }
   }

  function InsertWebProject($p){
      $mid = mysql_real_escape_string($p['mid']);
      $note = mysql_real_escape_string($p['note']);

      $sql = "  INSERT INTO `Google`.`WEBPROJECT` (`ID`,`MID`,`COUNT`,`NOTE`) ";
      $sql .= " VALUES('', '$mid','0', '$note');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo $sql;
         return false;
      }
   }

   function UpdatWebProjectCount($count, $id){

      $sql = "  UPDATE `Google`.`WEBPROJECT` SET ";
      $sql .= " `COUNT` = '$count' WHERE  `WEBPROJECT`.`ID` = $id;";

      if(mysql_query($sql ,$this->link)){
         return true;
      }else{
         echo $sql;
         return false;
      }
   }

   function InsertWebContent($p, $pid, $keyword){
      $title = mysql_real_escape_string($p['title']);
      $url = mysql_real_escape_string($p['url']);
      $date = mysql_real_escape_string($p['date']);
      $quote = mysql_real_escape_string($p['quote']);
      $token = mysql_real_escape_string($keyword);

      $sql = "  INSERT INTO `Google`.`WEBCONTENT` (`ID`,`PID`,`TITLE`,`URL`,`DATE`,`QUOTE`,`TOKEN`) ";
      $sql .= " VALUES('', '$pid','$title', '$url', '$date', '$quote', '$token');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo $sql;
         return false;
      }

   }

   function selectKeyword($keyword, $option = false){
      $sql = "  SELECT * FROM `KEYWORD` WHERE TAGS like '%$keyword%';";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      echo "<table border=1><tr bgcolor=\"FFE7CD\">";
      if($option) echo "<td>Option</td>";
      echo "<td>Title</td><td>Keyword</td><td>Tags</td><td>Note</td></tr>";
      $i=0;
      while($row != null){
         list($V_ID,$V_TITLE, $V_KEYWORD,$V_TAGS,$V_NOTE) = $row;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         }
         if($option) echo "<td><input type=\"checkbox\" name=\"keywords[]\" value=\"$V_ID\"></td>";
         echo "<td>$V_TITLE</td><td>$V_KEYWORD</td><td>$V_TAGS</td>";
         echo "<td>$V_NOTE</td></tr>";
         $row = mysql_fetch_row($result);
      }
      echo "</table>";
   }

   function selectKeywordTags($filename){
      $sql = "  SELECT TAGS FROM `KEYWORD`;";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      $arr = array();
      while($row != null){
         list($V_TAGS) = $row;
         $tmp = explode(",", $V_TAGS); 
         $arr = array_merge($arr, $tmp);     
         $row = mysql_fetch_row($result);
      }
      $arr = array_unique($arr);
      foreach($arr as $id => $key){
         echo "<a href=\"$filename?keyword=$key\">$key</a>";
         echo "<br>";
      }
   }

   function selectMonitor(){
      $sql = "  SELECT * FROM `MONITOR`;";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      echo "<table border=1><tr bgcolor=\"FFE7CD\">";
      echo "<td>Title</td><td>Keywords</td><td>Attribute</td><td>Note</td><td>Frequency</td></tr>";
      $i=0;
      while($row != null){
         list($V_ID,$V_TITLE,$V_KEYWORDS,$V_ATTRIBUTE,$V_NOTE,$V_FREQUENCY) = $row;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         }
         $tmp = explode(",", $V_KEYWORDS);
         $kstring = "";
         foreach($tmp as $id => $kid){
            if(!is_numeric($kid)) continue;
            $sql1 = "SELECT title,keyword FROM `KEYWORD` WHERE ID = $kid;";
            $result1 = mysql_query($sql1);
            $row1 = mysql_fetch_row($result1);
            list($VV_TITLE, $VV_KEYWORD) = $row1;
            $c = count(explode(",", $VV_KEYWORD));
            $kstring .= $VV_TITLE."(".$c."), ";
         }

         echo "<td><a href=\"./Monitor.php?mid=$V_ID\">$V_TITLE</q></td>";
         echo "<td>$kstring</td><td>$V_ATTRIBUTE</td>";
         echo "<td>$V_NOTE</td><td>$V_FREQUENCY</td></tr>";
         $row = mysql_fetch_row($result);
      }
      echo "</table>";
   }

   function selectWebProject($mid){

      $sql = "SELECT * FROM `WEBPROJECT` WHERE MID = $mid;";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      echo "<table border=1><tr bgcolor=\"FFE7CD\">";
      echo "<td>ID</td><td>Entry</td><td>Count</td><td>Note</td></tr>";
      $i=0;
      while($row != null){
         list($V_ID,$V_MID,$V_COUNT,$V_NOTE,$V_TIMESTAMP) = $row;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         } 
         echo "<td>$V_ID</td>";
         echo "<td><a href=\"./Monitor.php?pid=$V_ID\">$V_TIMESTAMP</q></td>";
         echo "<td>$V_COUNT</td><td>$V_NOTE</td>";
         $row = mysql_fetch_row($result);
      }
      echo "</table>";
   }

   function selectWebContent($pid){

      $sql = "SELECT * FROM `WEBCONTENT` WHERE PID = '$pid';";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      echo "<table border=1 width=70%><tr bgcolor=\"FFE7CD\">";
      echo "<td>Id</td><td>Pid</td><td>Title</td><td>URL</td><td>Cache</td><td>Date</td><td>Quote</td><td>Tokens</td><td>Timestamp</td></tr>";
      $i=0;
      while($row != null){
         list($V_ID,$V_PID,$V_TITLE,$V_URL,$V_DATE,$V_QUOTE,$V_TOKENS,$V_TIMESTAMP) = $row;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         }
         echo "<td>$V_ID</td><td>$V_PID</td>";
         echo "<td>$V_TITLE</td><td><a href=\"$V_URL\">URL</a></td><td><a href=\"./html/$V_ID.html\">C</a></td>";
         echo "<td>$V_DATE</td><td>$V_QUOTE</td>";
         echo "<td>$V_TOKENS</td><td>$V_TIMESTAMP</td></tr>";
         $row = mysql_fetch_row($result);
      }
      echo "</table>";
   }


   function getMonitor(){
      $sql = "SELECT * FROM `MONITOR`;";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      $return = array();
      while($row != null){
         list($V_ID,$V_TITLE,$V_KEYWORDS,$V_ATTRIBUTE,$V_NOTE,$V_FREQUENCY) = $row;
         $tmp = array("id"=>$V_ID,"title"=>$V_TITLE,"keywords"=>$V_KEYWORDS,"attribute"=>$V_ATTRIBUTE,"note"=>$V_NOTE,"freqency"=>$V_FREQUENCY);
         array_push($return, $tmp);
         $row = mysql_fetch_row($result);
      }
      return $return;
   }

   function getKeyword($kids){
      if(substr($kids, -1) == ',') $kids = substr($kids, 0, -1);
      $sql = "SELECT KEYWORD FROM `KEYWORD` WHERE ID in ($kids);";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      $return = array();
      while($row != null){
         list($V_KEYWORD) = $row;
         $tmp = explode(",", $V_KEYWORD);
         $return = array_merge($return, $tmp);
         $row = mysql_fetch_row($result);
      }
      return $return;
   }


}   
?>
