<?php
require_once('../conn.php');

$q = "SELECT * FROM libtrack WHERE tFileName != ''";
$rs = mysql_query($q) or die(mysql_error());

echo "<pre>";

$ctr = 0;
while($row = mysql_fetch_array($rs)) {
	$tFileName = urldecode($row['tFileName']);
	$id = $row['tID'];
	
	
	$drop = "E:\\ZAutoLib\\";
	$tFileName = str_replace($drop, "", $tFileName);
	$tFileName = str_replace('\\', "", $tFileName);
	$tFileName = urlencode($tFileName);
	echo $id." | ".$tFileName."\n";
	
	$q = sprintf("UPDATE libtrack SET file_name='%s' WHERE tID='%s'", $tFileName, $id);
	if(mysql_query($q))
		$ctr++;
	else die(mysql_error());
}
echo "\nTOTAL ROWS AFFECTED: $ctr\n";


?>