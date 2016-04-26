<html>
<head>
<title>Google Monitor Project</title>
</head>
<body>

<h1>Google Monitor</h1>
<h2>Monitor Management</h2>

<?php                                                                                

   include("./lib/ClassDB.php");
   
   $db = new DB();
   if(isset($_GET['mid'])){
      $db->selectWebProject($_GET['mid']);
   }else{
      if(isset($_GET['pid'])){
         $db->selectWebContent($_GET['pid']);
      }else{
         $db->selectMonitor();
      }
   }
?>

</body>
</html>
