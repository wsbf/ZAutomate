<?php
$debug = FALSE;

if($debug)
	echo "<pre>";

require_once('../conn.php');
require_once('../utils_ccl.php');
// sanitizeInput();

/** get newest lbshow primary key **/
function maxShowID() {
	$rs = mysql_query("SELECT MAX(showID) FROM `show`") or die(mysql_error());
	$maxShow = mysql_fetch_array($rs);
	return $maxShow[0];
}

/** pull `show` for next newest rotation show; -1 if future **/
function nextShowID($prior) {
   $query = sprintf("select showID from `show` where wsbf.show.show_typeID = 0 and wsbf.show.showID != %d and TIMESTAMPDIFF(MINUTE, wsbf.show.start_time, wsbf.show.end_time) > 60 order by wsbf.show.end_time desc limit 100", $prior);
   $rows = mysql_query($query) or die("MySQL Error near line " . __LINE__ . ": " . mysql_error());
   while($row = mysql_fetch_array($rows, MYSQL_ASSOC))
      $shows[] = $row;
   return $shows[rand(0, count($shows) - 1)]['showID'];
}


/** prints output as created in genBestOfPlaylist() **/
function printOutput($output) {
	foreach($output as $line)
		echo implode("<|>", $line) . "\n";
		
}

/**
 * logs in automation
 * requires that no one is logged in already
 * @return int $showID the showID of the newly created show in the database
 */
function automationLogin(){
		$ifs = sprintf("INSERT INTO `show` (start_time, show_typeID, show_name, scheduleID) VALUES ('%s', 8, 'The Best of WSBF', NULL)", $time);
	$insert_fucking_show = mysql_query($ifs) or die("MySQL error [". __FILE__ ."] near line " . __LINE__ . ": " .mysql_error());

	$showID = mysql_insert_id($link);	// get showID of row just inserted

			$ifsh = sprintf("INSERT INTO `show_hosts` (showID, username, show_alias) VALUES (%d, 'Automation', NULL)", $showID);
	$insert_fucking_show_host = mysql_query($ifsh) or die("MySQL error [". __FILE__ ."] near line " . __LINE__ . ": " .mysql_error());	
	return($showID);
}

/** allWordsIn
 * David Cohen
 * Takes the search string and a the column name (or an array of column names)
 * Returns a string to insert into the WHERE clause of a MySQL query to 
 * return rows with that contain words in the following column.
 * 
 */

function allWordsIn($searchString, $columnNames){
	if(!is_array($columnNames))	// make into 1-element array if not already
		$columnNames = array($columnNames);
	$words = preg_split("/\s+/",$searchString, NULL, PREG_SPLIT_NO_EMPTY);
			// split into array alphanumeric characters and underscore
	$colWords = array();
	
	foreach($columnNames as $col){
		$thisColumnArray = array(); 
		foreach($words as $word)
			$thisColumnArray[] = "{$col} LIKE '%{$word}%'";
		$colWords[] = implode(" AND ", $thisColumnArray);
	}
	$result = "((" . implode(") OR (", $colWords) . "))";

	return($result);
}

?>
