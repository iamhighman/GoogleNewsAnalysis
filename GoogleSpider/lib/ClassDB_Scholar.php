<?php

class DB_Scholar{
   function DB_Scholar(){
      $this->config();
   }
   function config(){
      $this->link = mysql_pconnect('localhost', '', '') or
      die("mysql_connect() failed.");
      mysql_select_db("Scholar", $this->link) or
      die("mysql_select_db() failed.");  	
      mysql_query("SET CHARACTER SET 'utf8'", $this->link);
   }

   function InsertCoauthors($p, $aid){
      $userid = mysql_real_escape_string($p['userid']);

      $sql = "  INSERT INTO `Scholar`.`Coauthors` (`Id`,`Aid`,`Userid`) ";
      $sql .= " VALUES('', '$aid', '$userid');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo "DBF!";
         return false;
      }

   }

   function InsertPapers($p, $aid){
      $title = mysql_real_escape_string($p['title']);
      $authors = mysql_real_escape_string($p['authors']);
      $url = mysql_real_escape_string($p['url']);
      $source = mysql_real_escape_string($p['source']);
      $citation = mysql_real_escape_string($p['citation']);
      $year = mysql_real_escape_string($p['year']);

      $sql = "  INSERT INTO `Scholar`.`Papers` (`Id`, `Aid`,`Title`, `Authors`, `Source`, `Year`, `Citation`, `URL`)";
      $sql .= " VALUES (NULL, '$aid', '$title', '$authors', '$source', '$year', '$citation', '$url');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo "DBF!";
         return false;
      }

   }

   function InsertNULLPapers($aid){

      $sql = "  INSERT INTO `Scholar`.`Papers` (`Id`, `Aid`,`Title`, `Authors`, `Source`, `Year`, `Citation`, `URL`)";
      $sql .= " VALUES (NULL, '$aid', '', '', '', '', '', '$aid');";
      if(mysql_query($sql ,$this->link)){
         echo "NULL";
         return mysql_insert_id();
      }else{
         echo "DBF!";
         return false;
      }

   }

   function InsertNewAuthors($p, $uid){
      $name = mysql_real_escape_string($p['name']);
      $aff = mysql_real_escape_string($p['aff']);
      $fields = mysql_real_escape_string($p['fields']);

      $sql = "  INSERT INTO `Scholar`.`Authors` (`Id`, `Name`,`Affiliation`, `Fields`, `Userid`, `Note`)";
      $sql .= " VALUES (NULL, '$name', '$aff', '$fields', '$uid', '');";
      if(mysql_query($sql ,$this->link)){
         return mysql_insert_id();
      }else{
         echo "DBF!";
         return false;
      }

   }


   function selectScholar($start){
      $sql0 = "SELECT count(id) FROM `Authors`;";
      $result0 = mysql_query($sql0);
      $row0 = mysql_fetch_row($result0);
      list($ACOUNT) = $row0;

      $sql0 = "SELECT count(id) FROM `Papers`;";
      $result0 = mysql_query($sql0);
      $row0 = mysql_fetch_row($result0);
      list($PCOUNT) = $row0;

      $sql0 = "SELECT count(distinct(aid)) FROM `Papers`;";
      $result0 = mysql_query($sql0);
      $row0 = mysql_fetch_row($result0);
      list($ACOUNT_OK) = $row0;
      
      echo "Start from: ";
      for($j=0;$j<$ACOUNT;$j+=1000){
         echo "<a href=\"./Scholar.php?start=$j\">$j</a> | ";
      }

      $sql = "  SELECT * FROM `Authors` limit ".$start.", 1000;";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);

      echo "<h3>Unique Authors: $ACOUNT</h3>";
      echo "<h3>Downloaded Authors: $ACOUNT_OK</h3>";
      echo "<h3>Unique Papers: $PCOUNT</h3>";  

      echo "<table border=1><tr bgcolor=\"FFE7CD\">";
      echo "<td>No</td><td>Name</td><td>Affiliation</td><td>Fields</td><td>URL</td><td>Note</td></tr>";
      $i=0;
      while($row != null){
         list($V_ID,$V_NAME,$V_AFF,$V_FIELDS,$V_USERID,$V_NOTE) = $row;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         }
         echo "<td>$i</td><td><a href=\"./Scholar.php?aid=$V_ID\">$V_NAME</a></td>";
         echo "<td>$V_AFF</td><td>$V_FIELDS</td>";
         echo "<td><a href=\"http://scholar.google.com/citations?user=".$V_USERID."AJ\">$V_USERID</a></td>";
         echo "<td>$V_NOTE</td></tr>";
         $row = mysql_fetch_row($result);
      }
      echo "</table>";
   }

   function selectScholarContent($aid){

      $sql = "SELECT * FROM `Authors` WHERE ID = '$aid';";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      list($A_ID,$A_NAME,$A_AFF,$A_FIELDS,$A_USERID,$A_NOTE) = $row;
      echo "<h3>Name: $A_NAME</h3>";
      echo "<h3>Affiliation: $A_AFF</h3><h3>Fields: $A_FIELDS</h3>";

      echo "<h2>Coauthors</h2>";
      echo "<table border=1 width=100%><tr bgcolor=\"FFE7CD\">";
      echo "<td>No</td><td>Coauthor</td><td>Affiliation</td><td>Fields</td></tr>";
      $sql2 = "SELECT b.id, a.Userid, b.name, b.Affiliation, b.Fields FROM `Coauthors` as a, `Authors` as b WHERE a.aid = '$aid' and a.Userid = b.Userid";
      $result2 = mysql_query($sql2);
      $row2 = mysql_fetch_row($result2);
      $i=0;
      while($row2 != null){
         list($V_ID, $V_USERID,$V_NAME,$V_AFF,$V_FIELDS) = $row2;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         }
         echo "<td>$i</td><td><a href=\"./Scholar.php?aid=$V_ID\">$V_NAME</td>";
         echo "<td>$V_AFF</td><td>$V_FIELDS</td>";
         echo "</tr>";
         $row2 = mysql_fetch_row($result2);
      }
      echo "</table><p>";

      echo "<h2>Papers</h2>";
      echo "<table border=1 width=100%><tr bgcolor=\"FFE7CD\">";
      echo "<td>No</td><td>Id</td><td>Aid</td><td>Title</td><td>Authors</td><td>Source</td><td>Year</td><td>Citation</td><td>URL</td></tr>";
 
      $sql1 = "SELECT * FROM `Papers` WHERE Aid = '$aid';";
      $result1 = mysql_query($sql1);
      $row1 = mysql_fetch_row($result1);
      $i=0;   
      while($row1 != null){
         list($V_ID,$V_AID,$V_TITLE,$V_AUTHORS,$V_SOURCE,$V_YEAR,$V_CITATION,$V_URL) = $row1;
         if(++$i % 2 == 0) {
            echo "<tr bgcolor=CDE5FF>";
         }else{
            echo "<tr>";
         }
         echo "<td>$i</td><td>$V_ID</td><td>$V_AID</td>";
         echo "<td>$V_TITLE</td><td>$V_AUTHORS</td>";
         echo "<td>$V_SOURCE</td><td>$V_YEAR</td>";
         echo "<td>$V_CITATION</td>";
         echo "<td><a href=\"http://scholar.google.com/$V_URL\">Link</td></tr>";
         $row1 = mysql_fetch_row($result1);
      }
      echo "</table>";
   }


   function getMonitor(){
      $sql = "SELECT * FROM `Authors` WHERE `Id` not in (SELECT `Aid` FROM `Papers`)";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      $return = array();
      while($row != null){
         list($V_ID,$V_NAME,$V_AFF,$V_FIELDS,$V_USERID,$V_NOTE) = $row;
         $tmp = array("id"=>$V_ID,"name"=>$V_NAME,"aff"=>$V_AFF,"fields"=>$V_FIELDS,"userid"=>$V_USERID,"note"=>$V_NOTE);
         array_push($return, $tmp);
         $row = mysql_fetch_row($result);
      }
      return $return;
   }

   function getNewAuthors(){
      $sql = "SELECT * FROM `Coauthors` WHERE `Coauthors`.`Userid` not in (SELECT `Userid` FROM `Authors`)";
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      $return = array();
      while($row != null){
         list($V_ID,$V_AID,$V_USERID) = $row;
         $tmp = array("id"=>$V_ID,"aid"=>$V_AID,"userid"=>$V_USERID);
         array_push($return, $tmp);
         $row = mysql_fetch_row($result);
      }
      return $return;
   }

   function getPaper($start, $num){
      $sql = "SELECT * FROM `Papers` limit $start, $num;"; echo $sql;
      $result = mysql_query($sql);
      $row = mysql_fetch_row($result);
      $return = array();
      while($row != null){
         list($V_ID, $V_AID, $V_TITLE, $V_AUTHORS, $V_SOURCE, $V_YEAR, $V_CITATION, $V_URL) = $row;
         $tmp = array("id"=>$V_ID,"url"=>$V_URL);
         array_push($return, $tmp);
         $row = mysql_fetch_row($result);
      }
      return $return;
   }

}   
?>
