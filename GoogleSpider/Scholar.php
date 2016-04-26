<html>
<head>
<title>Google Monitor Project</title>
</head>
<body>

<h1>Google Scholar Monitor</h1>

<?php                                                                                

   include("./lib/ClassDB_Scholar.php");
   
   $db = new DB_Scholar();
   if(isset($_GET['start'])){
      //$db->selectScholar($_GET['mid']);
      $db->selectScholar($_GET['start']);
   }else{
      if(isset($_GET['aid'])){
         $db->selectScholarContent($_GET['aid']);
      }else{
         $db->selectScholar(0);
      }
   }
?>

</body>
</html>
