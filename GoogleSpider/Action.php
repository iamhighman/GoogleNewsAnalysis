<html>
<head>
<title>GNews Monitor Project</title>
</head>
<body>
<?php                                                                                

   include("./lib/ClassDB.php");
   include("./lib/ClassParser.php");
   
   $db = new DB();
   $parser = new Parser();

   switch($_REQUEST['action']){
      
     case 'addKeyword':
       $db->insertKeyword($_POST);
       echo "<meta http-equiv=\"refresh\" content=\"0;url=./Keyword.php\">";
     break;

     case 'addMonitor':
       $keywrods="";
       foreach($_POST['keywords'] as $id => $k){
          $keywords.=$k.",";
       }
       $_POST['keywords'] = substr($keywords, 0, -1);
       $db->insertMonitor($_POST);
       echo "<meta http-equiv=\"refresh\" content=\"0;url=./Monitor.php\">";
     break;

     default: echo "Assign a action first...";
     break;

   }
?>

</body>
</html>
