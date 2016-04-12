<?php

/**
 * Logs whatever is in $_GET['cartid'].
 * $_GET['cartid'] is only the cartID when it's logging a cart.
 * 
 */

require_once('../conn.php');
require_once('../utils_ccl.php');
require_once('../logbook/logging_functions.php');
require_once('automation_library.php');
sanitizeInput();

$tablename = "logbook"; //lbplaylist_test
$nowPlaying = 1; /** change to 1 if you want carts to show up to listeners **/
$showid = -1; //automation has no show id
$numinshow = 0; //this is irrelevant for automation: sort by pDTS instead
$time = date("Y-m-d H:i:s", strtotime('now'));


if(!isset($_GET['cartid']))
	die("No valid data");

// Figure out if someone is on air (whether to attach it to their show playlist)
$qu = "SELECT end_time, showID FROM `show` ORDER BY start_time DESC LIMIT 1";
$rs = mysql_query($qu) or die("MySQL error near line " . __LINE__ . ": " . mysql_error());
$rowShow = mysql_fetch_array($rs, MYSQL_ASSOC);
if(!$rowShow['end_time'] || $rowShow['end_time'] == '0000-00-00 00:00:00') {
	$showid = $rowShow['showID'];
}
else
	$showID = automationLogin();


// A numeric cart id pulls from libcart. Non-numeric (H199-4) pulls from libtrack, libcd, etc.
// CART
if(is_numeric($_GET['cartid'])) {
	$cartid = $_GET['cartid'];
	$qu = sprintf("SELECT libcart.title, libcart.issuer, def_cart_type.type FROM `libcart`, `def_cart_type` WHERE cartID='%s' AND libcart.cart_typeID = def_cart_type.cart_typeID", $cartid);;
	$rs = mysql_query($qu) or die("MySQL error near line " . __LINE__ . ": " . mysql_error());
	$rowCart = mysql_fetch_array($rs, MYSQL_ASSOC);
	/** the sanitize function is in ../utils_ccl.php **/
	sanitize($rowCart);
	
	$title = $rowCart['title'];
	$issuer = $rowCart['issuer'];
	$type = $rowCart['type'];
	// logbookID	showID	lb_album_code	lb_rotation	lb_track_num	lb_track_name	lb_artist	lb_album	lb_label	time_played	played	deleted
	$query = sprintf("INSERT INTO `%s` 
		(showID, lb_album_code, lb_track_num, lb_rotation, lb_artist, lb_track_name, lb_album, lb_label, time_played, played) VALUES 
		('%s', '%d', 0, '%s', '%s', '%s', '', '', '%s', 1)", 
		$tablename, $showid, $cartid, $type, $issuer, $title, $time);
	
	// don't update now_playing.
}
// SONG
else {
	$albumNo = substr($_GET['cartid'], 0, strpos($_GET['cartid'], '-') );
	$trackNo = substr($_GET['cartid'], strpos($_GET['cartid'], '-')+1);
	$qu = sprintf("SELECT * FROM `libalbum`, `libtrack`, `liblabel`, `libartist`, `def_rotations` WHERE libalbum.artistID = libartist.artistID AND libalbum.labelID = liblabel.labelID AND libalbum.albumID = libtrack.albumID AND libtrack.track_num = '%s' AND libalbum.album_code = '%s' AND def_rotations.rotationID = libalbum.rotationID LIMIT 1", $trackNo, $albumNo);
	
	$rs = mysql_query($qu) or die("MySQL error near line " . __LINE__ . ": " . mysql_error());
	
	if(mysql_num_rows($rs) != 1) {
		echo "\n\n\n" . "ERROR: Not 1 row returned!\n";
		die();
	}
	$row = mysql_fetch_array($rs, MYSQL_ASSOC);
	/** the sanitize function is in ../utils_ccl.php **/
	sanitize($row);
	$genre = $row['genre'];
	$rotation = substr($row['rotation_bin'], 0, 1);
	$artist = $row['artist_name'];
	$track = $row['track_name'];
	$album = $row['album_name'];
	$label = $row['label'];
	
	$query = sprintf("INSERT INTO `%s` 
		(showID, lb_album_code, lb_track_num, lb_rotation, lb_artist, lb_track_name, lb_album, lb_label, time_played, played) VALUES 
		('%d', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s', 1)", 
		$tablename, $showid, $albumNo, $trackNo, $rotation, $artist, $track, $album, $label, $time);
	
	$update_now_playing = sprintf("UPDATE now_playing SET logbookID = LAST_INSERT_ID(), lb_track_name = '%s', lb_artist_name = '%s'", $track, $artist);	
	sendRDS($artist, $track);
}



//echo "Hello! You are logging number $cartid\n";
//echo "Show ID is $showid\n";

if(mysql_query($query)){
	if(!empty($update_now_playing))
		mysql_query($update_now_playing) or die("MySQL error near line " . __LINE__ . ": " . mysql_error());

	echo "Logged ". $_GET['cartid'] ." successfully.";
}
else 
	echo "MySQL error near line " . __LINE__ . ": " . mysql_error();

//lbplaylist: p_sID, pNumInShow, pAlbumNo, pTrackNo, pGenre, pRotation, 
//pArtistName, pSongTitle, pAlbumTitle, pRecordLabel, pCurrentlyPlaying
?>