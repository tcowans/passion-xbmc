<?php

// TRAITEMENT ALLOCINE
function allocine($data, $id = false) {
	
	//echo "ALLOCINE: ".$data['FIND']." -> ".$data['RELEASE']." [".$data['SECTION']."]\n";
	$opq = @file_get_contents('http://www.allocine.fr/recherche/?rub=1&page=1&motcle='.eregi_replace ( " ", "%20", $data['FIND']));
	preg_match_all('#<td valign=\"top\"><h4><a href=\"/film/fichefilm_gen_cfilm=(\d+)\.html\"#SUmis',$opq,$matches,PREG_SET_ORDER);
	foreach ($matches as $resultat) {
		$parserid = $resultat[1];
		break;
	}
	$data = parser_allocine($parserid);
	$data['LINK'] = "http://www.allocine.fr/film/fichefilm_gen_cfilm=$parserid.html";
	return $data;
}

function parser_allocine($id) {
	$data['LINK'] = "http://www.allocine.fr/film/fichefilm_gen_cfilm=$id.html";

	$opq = @file_get_contents('http://www.allocine.fr/film/fichefilm_gen_cfilm='.$id.'.html');
	$data['IDALLO'] = $id;
	//TITLE
	preg_match_all('#<title>(.+)</title>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['TITLE'] = strip_tags($info[1]);
		break;
	}
	//ORIGINALTITLE
	preg_match_all('#<h4>Titre original : <i>(.+)</i>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['ORIGINALTITLE'] = strip_tags($info[1]);
		break;
	}
	//REALISATEUR
	preg_match_all('#Réalisé par <[^>]*>(.+)</h4>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['DIRECTOR'] = strip_tags($info[1]);
		break;
	}
	//YEAR
	preg_match_all('#Année de production : (\d+)</h4>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['YEAR'] = strip_tags($info[1]);
		break;
	}
	//GENRE
	preg_match_all('#Genre : <[^<]*>(.+)</h4>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['GENRE'] = strip_tags($info[1]);
		$data['GENRE'] = ereg_replace(",", " / ", $data['GENRE']);
		break;
	}
	//DUREE	
	preg_match_all('#Durée : (.+).&nbsp;<#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['RUNTIME'] = strip_tags($info[1]);
		break;
	}
	//STUDIO
	preg_match_all('#Distribué par (.*)</h4>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['STUDIO'] = strip_tags($info[1]);
		break;
	}
	//RATING	
	preg_match_all('#Note moyenne : <img src="[^"]*" width="52" height="13" class="etoile_(\d+)" border="0" />&nbsp;pour (\d+) critique#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['RATING'] = strip_tags($info[1]);
		$data['VOTES'] = strip_tags($info[2]);
		break;
	}
	//TAGLINE
	preg_match_all('#<div align="justify" style="padding: 5 0 5 0"><h4>(.*)</h4>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		if($data['TAGLINE'])
			$data['TAGLINE'] .= " / ";
		$data['TAGLINE'] = strip_tags($info[1]);
	}
	//MPAA
	preg_match_all('#Fiche Technique(.*)</table>#SUmis',$opq,$mpaa,PREG_SET_ORDER);
	//print_r($mpaa);
	preg_match_all('#<h4>(.*)</h4>#SUmis',$mpaa[0][1],$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		if($data['MPAA'])
			$data['MPAA'] .= " / ";
		$data['MPAA'] .= strip_tags($info[1]);
	}

	//Bande Annonce 
	preg_match_all('#video/player_gen_cmedia=(\d+)&#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['IDBA'] = strip_tags($info[1]);
		break;
	}
	//PLOT
	preg_match_all('#<td valign="top" style="padding:10 0 0 0"><div align="justify"><h4>([^&]*)</h4></div>#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['PLOT'] = strip_tags($info[1]);
		break;
	}

	//THUMB
	preg_match_all('#<img src="([^"]*)" border="0" alt="" class="affichette" />#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['PTHUMB'] = strip_tags($info[1]);
		break;
	}

	//ACTOR
	preg_match_all('#<a href="([^"]*)" class="link5"><h5 style="line-height: 100%"><b>Casting#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['LINKACTOR'] = 'http://www.allocine.fr'.$info[1];
		break;
	}

	//CREDITS
	$opq = @file_get_contents($data['LINKACTOR']);
	preg_match_all('#Scénariste(.*)Equipe technique#SUmis',$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$list = explode("\n",trim(strip_tags($info[1])));
		foreach($list as $value) {
			if(trim($value)) {
				if($data['CREDITS'])
					$data['CREDITS'] .= " / ";
				$data['CREDITS'] .= trim($value);
			}
		} 

		break;
	}





	//GETACTOR
	preg_match_all("#<b>Acteurs</b></h4>(.*)</table>#SUmis",$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$output = $info[1];
		break;
	}

	preg_match_all('#<h5>([^<]*)</h5></td>[^<]*<td width="50%" valign="center" style="padding:2 0 2 0"><h5><a href="([^"]*)" class="link1">([^<]*)</a></h5></td>#SUmis',$output,$infos,PREG_SET_ORDER);
	$count = 0;
	foreach ($infos as $info) {
		$data['INFOACTOR'][$count]['ROLE'] = $info[1];
		$data['INFOACTOR'][$count]['LINKACTOR'] = 'http://www.allocine.fr'.$info[2];
		$data['INFOACTOR'][$count]['ACTOR'] = $info[3];
		$count++;
	}

	$count = 0;
	foreach ($data['INFOACTOR'] as $key => $value) {
		$opq = @file_get_contents($data['INFOACTOR'][$key]['LINKACTOR']);
		preg_match_all('#<img src="([^"]*)" width="120" height="160" border="0">(.*)<td valign="top" style="padding:0 0 10 0">(.*)</td></tr></table>#SUmis',$opq,$infos,PREG_SET_ORDER);
		foreach ($infos as $info) {
			$data['INFOACTOR'][$key]['THUMB'] = $info[1];
			$data['INFOACTOR'][$key]['INFOS'] = strip_tags($info[3]);
			break;

		}
		$count++;
		if($count > 7) 
			break;
	}

	//THUMB HAUTE DEFINITION
	$opq = @file_get_contents('http://www.allocine.fr/film/galerievignette_gen_cFilm='.$id.'.html');
	preg_match_all("#<img id='imgNormal' class='photo' src='([^']*)'#SUmis",$opq,$infos,PREG_SET_ORDER);
	foreach ($infos as $info) {
		$data['THUMB'] .= $info[1];
		break;
	}

	if($data['THUMB']) {
		if(eregi("nmedia",$data['THUMB']))
			$link = ereg_replace("/nmedia(.*).jpg", "idthumb.jpg", $data['THUMB']);
		if(eregi("medias",$data['THUMB']))
			$link = ereg_replace("/medias(.*).jpg", "/mediasidthumb.jpg", $data['THUMB']);
		//ALLTHUMB HAUTE DEFINITION
		preg_match_all('#"fichier":"(.*).jpg",#SUmis',$opq,$infos,PREG_SET_ORDER);
		$count = 0;
		foreach ($infos as $info) {
			$data['ALLTHUMB'][$count] = ereg_replace("idthumb", $info[1], $link);
			$count++;
		}
	}

	if(!$data['THUMB']) $data['THUMB'] = $data['PTHUMB'];
		
	//print_r($data);
	return $data;
}

?>