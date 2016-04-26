<html>
<head>
<title>Google Monitor Project</title>
</head>
<body>

<h1>Google Monitor</h1>
<h2>Keyword Management</h2>

<a href="Keyword.php?action=add">Add Keyword</a><p>

Or select the tags below: <p>

<?php                                                                                

   include("./lib/ClassDB.php");
   
   $db = new DB();

   if(isset($_GET['keyword'])){
      echo "<h3>".$_GET['keyword']."</h3>";
      $db->selectKeyword($_GET['keyword']);
   }else{
      if(isset($_GET['action'])){
?>
<form method="POST" action="./Action.php">
<input name="action" type="hidden" value="addKeyword">
<BR>Title:<input name="title" type="text" size="80" value=""><BR>
 Keyword: <input name="keyword" type="text" size="80" value=""> (Split by ,)<BR>
 Tags: <input name="tags" type="text" size="80" value=""> (Split by ,)<BR>
 Note: <input name="note" type="text" size="80" value=""><BR>
 <input type="submit" name="s" value="Go">
</form>

<?php         
      }else{    
         $db->selectKeywordTags("Keyword.php");
      }
   }
?>

</body>
</html>
