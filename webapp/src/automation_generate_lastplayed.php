<?php 
define('DEBUG', FALSE);

if(DEBUG) { 
	echo "<pre>";
	$time = microtime(true);
}
require_once('../conn.php');
require_once('../utils_ccl.php');
sanitizeInput();


// 6N, 3H, 2M, 1L

$progression = array('N','N','H','N','M','L','N','H','N','H','N','M');

// 9N, 3H
$progression = array('N','N','H','N','N','N','N','H','N','H','N','N');

$goodBins = array('N','H','M','L');
$binCounters = array('N'=>0, 'H'=>0, 'M'=>0, 'L'=>0);

$binLists = NULL; foreach($goodBins as $bin) $binLists[$bin] = array();


/** pull relevant info about each CD that has a track 1 filename
$cdQ = "SELECT libcd.cID, libcd.cAlbumNo, libartist.aPrettyArtistName, liblabel.lPrettyLabelName, 
libcd.cAlbumName, libcd.cGenre, libcd.cBin FROM libcd, libartist, liblabel, libtrack WHERE 
libcd.c_aID = libartist.aID AND libcd.c_lID = liblabel.lID AND libcd.cID = libtrack.t_cID 
AND libtrack.tFileName != '' AND libtrack.tTrackNo = '1'";
*/




//libalbum:: albumID	album_name	num_discs	album_code	artistID	labelID	mediumID	genre	general_genreID	rotationID
$cdQ = sprintf("SELECT libalbum.albumID, libalbum.album_code, libartist.artist_name, liblabel.label, libalbum.album_name, libalbum.genre, libalbum.rotationID, def_rotations.rotation_bin FROM `libalbum`, `libartist`, `liblabel`, `libtrack`, `def_rotations` WHERE libalbum.artistID = libartist.artistID AND libalbum.labelID = liblabel.labelID AND libalbum.albumID = libtrack.albumID AND def_rotations.rotationID = libalbum.rotationID AND libtrack.file_name != '' AND libtrack.track_num = '1'");




$cdR = mysql_query($cdQ) or die(mysql_error());

if(DEBUG) echo $cdQ."\n\n\n";


while($cd = mysql_fetch_array($cdR, MYSQL_ASSOC)) {
	// define ROTATION as first letter
	$cd['ROTATION'] = substr($cd['rotation_bin'], 0, 1);	// New => N, Heavy => H, etc.
	/** ignore optionals and yet-to-be-reviewds **/
	if(in_array($cd['ROTATION'], $goodBins)) {

		//echo $cd['cAlbumNo']."\n";
		
		/** find the most recent time this cd was played... allow for never **/
		$timeLastPlayed = 0;
		$plQ = "SELECT time_played FROM `logbook` WHERE lb_album_code='".$cd['album_code']."' ORDER BY logbookID DESC LIMIT 1";
		$plR = mysql_query($plQ) or die(mysql_error());
		if(mysql_num_rows($plR) == 1) {
			$pl = mysql_fetch_array($plR, MYSQL_ASSOC);
			$timeLastPlayed = strtotime($pl['time_played']);
		}
		$cd['TIMESTAMP'] = $timeLastPlayed;
		
		/** big 2-D array. by Bin, then by CDcode **/
		$binLists[$cd['ROTATION']][] = $cd;
	}
}

/** sort the bins by time last played. 0 is played least, n-1 most recently**/
function cdStructCompare($a, $b) {
	$alpha = (int)$a['TIMESTAMP'];
	$beta = (int)$b['TIMESTAMP'];
	
	if($alpha == $beta) return 0;
	return ($alpha < $beta) ? -1 : 1;
}
foreach($binLists as $key => &$binList) {	//pass by reference
	uasort($binList, 'cdStructCompare');
	if(DEBUG) echo $key." - ".count($binList)." \n";
}
	if(DEBUG) echo "\n\n";

/** now generate a playlist! **/
$counter = 0;
while($counter < count($progression)) {
	$bin = $progression[$counter];
	
	if($binCounters[$bin] >= count($binLists[$bin])) {
		$bin = 'N';
		//$binCounters[$bin] = (count($binLists['N']) - 1) - $binCounters[$bin];
	}
	
	$cd = $binLists[$bin][$binCounters[$bin]];
	$binCounters[$bin]++;
	$albumID = $cd['albumID'];
	
	//echo $cd['cAlbumNo'] . " " . $cd['cBin']." \n";
	
		/** pull all valid tracks, pick a random one **/
		$tracks = array();
		$qu = sprintf("SELECT * FROM `libtrack` 
			WHERE albumID='%s' AND airabilityID='1'", $albumID);
		$ru = mysql_query($qu) or die(mysql_error());
		if(mysql_num_rows($ru) == 0) {
			echo "continuing\n";
			continue;
		}
		while($track = mysql_fetch_array($ru, MYSQL_ASSOC))
			$tracks[] = $track;
		$track = $tracks[rand(0, count($tracks)-1 )];
		
	
	$output = array();
	$output[] = $cd['album_code'];
	$output[] = $track['track_num'];
	$output[] = $cd['genre'];
	$output[] = $cd['ROTATION'];
	$output[] = $cd['artist_name'];
	$output[] = $track['track_name'];
	$output[] = $cd['album_name'];
	$output[] = $cd['label'];
	$output[] = $track['file_name'];

	echo implode(" | ", $output) . "\n";
	
	
	$counter++;
}



//foreach($binLists['N'] as $key => $cd)
//	echo $key." | ".$cd['cAlbumNo']." | ".date('r', $cd['TIMESTAMP'])."\n";


if(DEBUG) echo "\n\nTime needed to execute: ".round(microtime(true)-$time,5)." seconds\n</pre>";
?>