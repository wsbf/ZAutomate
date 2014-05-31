<?php 
define('DEBUG', false);
require_once('automation_library.php');
$min_tracks = 10;


if(!isset($_GET['showid']))
	$showid = nextShowID(-1);
else
	$showid = $_GET['showid'];


if($showid <= 0 || $showid >= maxShowID())
	$showid = nextShowID(-1);

function genBestOfPlaylist($showid) {
	$final_output = array();
	$cdcodes = array(); //don't play the same CD twice
	
	sanitizeInput($showid);
	/** get all the non-optional cdcodes/tracks from the current playlist **/

   //logbookID	showID	lb_album_code	lb_rotation	lb_track_num	lb_track_name	
   //lb_artist	lb_album	lb_label	time_played	played	deleted
	$qv = sprintf("SELECT lb_album_code, lb_track_num FROM `logbook` WHERE showID = %s AND lb_rotation != '0' ORDER BY logbookID ASC", $showid);
	
	$rt = mysql_query($qv) or 
      die("MySQL Error near line " . __LINE__ . " in automation_generate_showplist\n".$qv."\n: " . mysql_error());

	// echo "ROWS: ".mysql_num_rows($rt)."\n";
	while ($song = mysql_fetch_array($rt, MYSQL_ASSOC)) {
		
		$cdcode = $song['lb_album_code'];
		$trnum = $song['lb_track_num'];
		if($cdcode == "" || $trnum == "") {
			continue;
		}
		
	/** for this one song, pull artist, album, label info **/
   
   //albumID	album_name	num_discs	lbum_code	      artistID	
   //labelID	mediumID	   genre	      general_genreID	rotationID
	$qw = sprintf("SELECT * FROM `libartist`, `libalbum`, `liblabel`, `def_rotations` " . 
                 "WHERE libalbum.album_code = '%s' AND " . 
                 "libalbum.artistID = libartist.artistID AND " .
                 "libalbum.labelID = liblabel.labelID AND " .
                 "def_rotations.rotationID = libalbum.rotationID LIMIT 1", $cdcode);

		$ru = mysql_query($qw) or die("MySQL Error near line " . __LINE__ . ": " . mysql_error());
		$cd = mysql_fetch_array($ru, MYSQL_ASSOC);
		$cdid = $cd['albumID'];
		
	/** get the song and file names **/

	// libtrack: track_name 	disc_num	      track_num	
   //           artistID	   airabilityID	file_name	albumID
	$qx = sprintf("SELECT track_name, file_name 
			FROM `libtrack` 
			WHERE albumID = '%s' 
			AND track_num = '%s'
			AND airabilityID <= 1 
			LIMIT 1", $cdid, $trnum);
		
		$rv = mysql_query($qx) or die("MySQL Error near line " . __LINE__ . ": " . mysql_error());
		$track = mysql_fetch_array($rv, MYSQL_ASSOC);
		
		/** it's here, and it hasn't been played in *this* set before **/
		if($track['file_name'] != "" && !in_array($cdcode, $cdcodes)) {
			$cdcodes[] = $cdcode;
			
			$output = array();
			$output[] = $cdcode; //0
			$output[] = $trnum;
			$output[] = $cd['genre'];
			$output[] = substr($cd['rotation_bin'], 0, 1);
			$output[] = $cd['artist_name'];
			$output[] = $track['track_name'];
			$output[] = $cd['album_name'];
			$output[] = $cd['label'];
			$output[] = $track['file_name']; //8
		
			$final_output[] = $output;
		
		}
	}
	return $final_output;
}

/* require the plist to have 10 valid tracks - otherwise it's too short for cohesion */

	$list = genBestOfPlaylist($showid);
	while(count($list) < $min_tracks) {
	$list = genBestOfPlaylist($showid);
		$showid = nextShowID($showid);
		if($showid == -1)
			$showid = getNewShowID(-1);
		$list = genBestOfPlaylist($showid);
	}

	echo "SHOWID ".$showid."\n";
	printOutput($list);
?>
