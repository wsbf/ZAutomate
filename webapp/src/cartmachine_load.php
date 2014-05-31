<?php
//updated 10aug11 to only get one cartType at a time

require_once('../conn.php');
require_once('../utils_ccl.php');
sanitizeInput();

if(!isset($_GET['type']))
	die("set the type, damn it.");
$type = $_GET['type'];

$now = time();
$now_ts = date("Y:m:d H:i:s", $now);
// new: cartID	start_date	end_date	play_mask	issuer	title	cart_typeID	filename
//old:	cartID	cartDateValid	cartDateInvalid	cartPlayMask	cartTitle	cartIssuer	cartType	cartFilename
$qu = sprintf("SELECT libcart.cartID, libcart.start_date, libcart.end_date, libcart.play_mask, libcart.title, libcart.issuer, def_cart_type.type, libcart.filename FROM `libcart`, `def_cart_type` WHERE libcart.start_date <= '%s' AND (libcart.end_date >= '%s' OR libcart.end_date = NULL OR libcart.end_date = '0000-00-00 00:00:00') AND def_cart_type.type LIKE '%s' AND def_cart_type.cart_typeID = libcart.cart_typeID order by libcart.cartID DESC", $now_ts, $now_ts, $type);
$rs = mysql_query($qu) or die(mysql_error());

$output = array();
while($row = mysql_fetch_array($rs, MYSQL_ASSOC)) {
	$row = str_replace(", "," ", $row);
	$imp = implode(", ", $row);
	$output[] = $imp;
}
echo implode("\n", $output);

?>
