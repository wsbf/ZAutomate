<?php
   require_once('../conn.php');
   require_once('../utils_ccl.php');
   $prior = -1; 
   if(!isset($_GET['showid']))
      $prior = -1;
   else
      $prior = $_GET['showid'];
   $qu = "SELECT showID FROM `show` WHERE show_typeID = 0 AND TIMESTAMPDIFF(MINUTE, start_time, end_time) > 60 ORDER BY end_time DESC LIMIT 100";
   $rows = mysql_query($qu) or die(mysql_error());
   while($row = mysql_fetch_array($rows, MYSQL_ASSOC))
      $shows[] = $row;
   do {
      $newShowID = $shows[rand(0, count($shows) - 1)]['showID'];
   } while($newShowID == $prior);
   echo $newShowID;
?> 
