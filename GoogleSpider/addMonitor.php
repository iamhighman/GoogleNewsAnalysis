<html>
<head>
<title>Google Monitor Project</title>

<script language="JavaScript">
function toggle(source) {
  checkboxes = document.getElementsByName('keywords[]');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = source.checked;
  }
}
</script> 

</head>
<body>

<h1>Google Monitor</h1>
<h2>Add Monitor Page</h2>

<form method="POST" action="./Action.php">

<?php                                                                                

   include("./lib/ClassDB.php");
   
   $db = new DB();

   if(isset($_GET['keyword'])){
       echo "<h3>".$_GET['keyword']."</h3>";
       $db->selectKeyword($_GET['keyword'], true);
?>
<input type="checkbox" id="checkAll8" ONCLICK="toggle(this)"/>CheckAllKeywords<p>
<input name="action" type="hidden" value="addMonitor">
<BR>Title:<input name="title" type="text" size="80" value=""><BR>
 Attribute: <textarea rows="4" cols="50" name="attribute"></textarea><BR>
 Note: <input name="note" type="text" size="80" value=""><BR>
 Frequency: <input name="frequency" type="text" size="80" value=""><BR>
 <input type="submit" name="s" value="Go">
</form>

<?php         
   }else{    
      $db->selectKeywordTags("addMonitor.php");
   }
?>

</body>
</html>
