<?php
require_once('automation_library.php');

$input = mysql_real_escape_string(trim(urldecode($_GET['query'])));
if(strlen($input) < 3)
	die();

$final_output = array();

//PHASE ZERO :: Search for carts
$now_ts = date("Y:m:d H:i:s", time());
$qx = sprintf("SELECT libcart.cartID, libcart.filename, libcart.start_date, libcart.end_date, 
			libcart.play_mask, libcart.title, 
			libcart.issuer, def_cart_type.type
		FROM `libcart`, `def_cart_type` 
		WHERE libcart.start_date <= '%s' 
		AND ( libcart.end_date >= '%s' OR libcart.end_date = '0000-00-00 00:00:00') 
		AND %s
		AND def_cart_type.cart_typeID = libcart.cart_typeID",
		$now_ts, $now_ts, allWordsIn($input, array("def_cart_type.type", "libcart.title", "libcart.issuer")));		

$rv = mysql_query($qx) or die(mysql_error());
while($cart = mysql_fetch_array($rv, MYSQL_ASSOC)) {
	$output = array($cart['cartID'], -1, $cart['type'], $cart['type'], $cart['type'], 
		$cart['title'], $cart['issuer'], $cart['type'], $cart['filename']);
	$final_output[] = $output;
}

// PHASE ONE :: Search by track name 
$qy = sprintf("SELECT * FROM `libtrack` 
		WHERE airabilityID <= 1 
		AND file_name != '' 
		AND %s", allWordsIn($input, "track_name"));
//echo $qy;
$rw = mysql_query($qy) or die("Line " . __LINE__ . ": " . mysql_error());
while ($track = mysql_fetch_array($rw, MYSQL_ASSOC)) {
	
	$cdid = $track['albumID'];
	$qz = sprintf("SELECT * FROM `libartist`, `libalbum`, `liblabel`, `def_rotations` 
			WHERE libalbum.albumID = '%s' 
			AND libalbum.artistID = libartist.artistID 
			AND libalbum.labelID = liblabel.labelID 
			AND def_rotations.rotationID = libalbum.rotationID
			LIMIT 1", $cdid);

	$rx = mysql_query($qz) or die("Line " . __LINE__ . ": " . mysql_error());
	$album = mysql_fetch_array($rx, MYSQL_ASSOC);
	
	$output = array($album['album_code'], $track['track_num'], $album['genre'], substr($album['rotation_bin'], 0, 1), 
		$album['artist_name'], $track['track_name'], $album['album_name'], 
		$album['label'], $track['file_name'] );
	$final_output[] = $output;	
}

// PHASE TWO :: Search by album name and artist name and albumNo
$qw = sprintf("SELECT * FROM `libartist`, `libalbum`, `liblabel`, `def_rotations` 
		WHERE libalbum.artistID = libartist.artistID 
		AND libalbum.labelID = liblabel.labelID 
		AND def_rotations.rotationID = libalbum.rotationID
		AND %s",
		allWordsIn($input, array("libalbum.album_name", "libartist.artist_name", "libalbum.album_code"))
		);
//echo $qw."\n";

$ru = mysql_query($qw) or die("Line " . __LINE__ . ": " . mysql_error());
while ($album = mysql_fetch_array($ru, MYSQL_ASSOC)) {
	$cdid = $album['albumID'];
	$qx = sprintf("SELECT track_name, track_num, file_name 
			FROM `libtrack` 
			WHERE airabilityID <= 1 
			AND file_name != '' 
			AND albumID='%s'",
			$cdid);
	$rv = mysql_query($qx) or die(mysql_error());
	while($track = mysql_fetch_array($rv, MYSQL_ASSOC)) {
		$output = array($album['album_code'], $track['track_num'], $album['genre'], substr($album['rotation_bin'], 0, 1), 
			$album['artist_name'], $track['track_name'], $album['album_name'], 
			$album['label'], $track['file_name'] );
		$final_output[] = $output;
	}
}



printOutput($final_output);

//



?>