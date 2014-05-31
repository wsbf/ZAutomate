<?php

define('DEBUG', FALSE);

if(DEBUG) { 
	echo "<pre>";
	$time = microtime(true);
}
require_once('../conn.php');
require_once('../utils_ccl.php');
sanitizeInput();
$now = time();
$now_ts = date("Y:m:d H:i:s", $now);



$q = sprintf("SELECT * FROM `libcart`, `def_cart_type` WHERE def_cart_type.cart_typeID = libcart.cart_typeID AND start_date < '%s' 
		AND (end_date >= '%s' OR end_date='0000-00-00 00:00:00' OR end_date = NULL) AND def_cart_type.type = '%s'", $now_ts, $now_ts, $_GET['type']);
$rs = mysql_query($q) or die(mysql_error());
$rows = array();
while($row = mysql_fetch_array($rs, MYSQL_ASSOC))
	$rows[] = $row;
if(count($rows) == 0) {
	; 
} else {
	$key = array_rand($rows, 1);
	$row = str_replace(", "," ", $rows[$key]);
	$imp = implode(", ", $row);
	echo $imp;
}	
?>