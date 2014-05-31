<?php
require_once("../conn.php");
require_once("../utils_ccl.php");
//echo "<pre>";
$qu="SELECT libtrack.track_name, libtrack.track_num, libtrack.file_name,  libartist.artist_name, 
libalbum.album_name, libalbum.album_num, libalbum.genre 
FROM `libtrack`, `libartist`, `libalbum` 
WHERE libtrack.albumID = libalbum.albumID AND libartist.artistID = libalbum.artistID AND 
libalbum.rotationID <= 4  AND libtrack.file_name !='' AND libtrack.track_num = 1 
ORDER BY libalbum.albumID DESC";

$rs = mysql_query($qu) or die(mysql_error());

$genres = array();
echo "NUMBER OF ROWS: ".mysql_num_rows($rs)."\n\n";

while($row = mysql_fetch_array($rs, MYSQL_ASSOC)) {
	$content = preg_split("/[\s,\/]+/", $row['genre']);
	foreach ($content as $genre) {
		$genre = strtolower($genre);
		if(isset($genres[$genre])) {
			$genres[$genre]++;
		}
		else {
			$genres[$genre] = 1;
		}
	}
}
arsort($genres);

foreach($genres as $genre => $frequency) {
	echo $frequency."\t".$genre."\n";
}


?>