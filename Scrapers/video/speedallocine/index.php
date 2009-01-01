<?php

include "allocine.php";

if($_GET['search']) {
		$in['FIND'] = $_GET['allocine'];
		$data = allocine($in);
}

if($_GET['id']) {
	if (file_exists("stock/".$_GET['id'].".xml")) {
		$handle = fopen("stock/".$_GET['id'].".xml",'r');
		$scraperxml = fread($handle, filesize("stock/".$_GET['id'].".xml"));
		fclose($handle);

	} else {
		$data = parser_allocine($_GET['id']);

		$scraperxml = "
		<details>
<title>".$data['TITLE']."</title>
<year>".$data['YEAR']."</year>
<director>".$data['DIRECTOR']."</director>
<tagline>".$data['TAGLINE']."</tagline>
<runtime>".$data['RUNTIME']."</runtime>
<studio>".$data['STUDIO']."</studio>
<credits>".$data['CREDITS']."</credits>
<rating>".$data['RATING']."</rating>
<votes>".$data['VOTES']."</votes>
<mpaa>".$data['MPAA']."</mpaa>
<genre>".$data['GENRE']."</genre>
		";

		if($data['INFOACTOR']) {
			foreach($data['INFOACTOR'] as $key => $value) {
		 		$scraperxml .="<actor>
				<thumb>".$data['INFOACTOR'][$key]['THUMB']."</thumb>
		 	       <name>".$data['INFOACTOR'][$key]['ACTOR']."</name>
		        	<role>".$data['INFOACTOR'][$key]['ROLE']."</role>
		    </actor>
			";
			}
		}

		if($data['ALLTHUMB']) {
			$scraperxml .= "<thumbs>
		";
			$count = 0;
			foreach($data['ALLTHUMB'] as $value) {
				$count++;
				if($count == 3)
					$fanart = "<fanart><thumb>$value</thumb></fanart>";
			 	$scraperxml .="<thumb>$value</thumb>
			";
			}
			$scraperxml .= "<thumb>".$data['PTHUMB']."</thumb>";
			$scraperxml .= "</thumbs>
				
$fanart
		";
		}

		$scraperxml .= "<outline>".$data['PLOT']."</outline>
		    <plot>".$data['PLOT']."</plot>
		</details>";

		if($data['TITLE'] AND $data['YEAR'] AND $data['DIRECTOR'] AND $data['TAGLINE'] AND $data['RUNTIME'] AND $data['STUDIO'] AND $data['CREDITS'] AND $data['RATING'] AND $data['VOTES'] AND $data['MPAA'] AND $data['GENRE'] AND $data['INFOACTOR'] AND $data['PTHUMB'] AND $data['ALLTHUMB']) {
			$fd = fopen('stock/'.$_GET['id'].".xml", "w"); // on ouvre le fichier cache 
			if ($fd) { 
				fwrite($fd,$scraperxml); // on ecrit le contenu du buffer dans le fichier cache 
				fclose($fd);
			}
		} 

	}
}


echo $scraperxml;
	
?>