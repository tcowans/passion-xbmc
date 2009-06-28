<?php

//connection à la base de donnée 
require_once(dirname(__FILE__) . '/Settings.php');
global $db_server, $db_name, $db_user, $db_prefix, $db_passwd;
$link = mysql_connect($db_server, $db_user, $db_passwd) or die("Connexion impossible.");
$db = mysql_select_db($db_name, $link);


//on verfie qu'un parametre est present dans l'adresse
if(!isset($_GET['action'])) 
    die('Parametre necessaire');

//definition de la requete en fonction des parametres dans l'adresse
$action = $_GET['action'];

if (isset($_GET['param'])) 
{ 
    $lastvisit = intval($_GET['param']);
}                  
else
{
    $lastvisit = 99999999999;
}


if ($action ==  'getcat')
{
    $Query = "  SELECT 
                    id_cat, 
                    title, 
                    description, 
                    image, 
                    id_parent,
                    cat_type
                FROM 
                    smf_down_cat";
}
else
{
    $Query = "SELECT  id_file, 
                    date, 
                    title, 
                    description, 
                    totaldownloads, 
                    filesize, 
                    filename, 
                    fileurl, 
                    commenttotal, 
                    id_cat, 
                    totalratings, 
                    rating, 
                    type,
                    sendemail, 
                    id_topic, 
                    keywords, 
                    createdate, 
                    ssFilename,
                    version, 
                    author, 
                    description_en, 
                    script_language,
                    CASE
                        WHEN date > $lastvisit THEN 'true'
                        ELSE 'false'
                    END
            FROM smf_down_file 
            ";

/*
    if (isset($_GET['param'])) 
    { 
        $lastvisit = $_GET['param'];
        $Query .= "WHERE date > $lastvisit";
    }                    
*/
}


//Generation du fichier csv 
header("Content-Type: application/csv-tab-delimited-table"); 
header("Content-disposition: filename=result.csv"); 

$resQuery = mysql_query($Query);
if (mysql_num_rows($resQuery) != 0) { 
    // données de la table 
    while ($arrSelect = mysql_fetch_array($resQuery, MYSQL_ASSOC)) { 
        foreach($arrSelect as $elem) {
            $contenu=utf8_encode($elem);
            if ($contenu == '')
            {
                echo "None|";
            }
            else
            {
                $contenu = str_replace("<i>", "[I]",$contenu);
                $contenu = str_replace("</i>", "[/I]",$contenu);
                $contenu = str_replace("<strong>", "[B]",$contenu);
                $contenu = str_replace("</strong>", "[/B]",$contenu);
                $contenu = str_replace("&nbsp;", " ",$contenu);
                $textsansbalise = strip_tags($contenu);
                $text = str_replace("\r\n","</br>",$textsansbalise);
                echo "$text|"; 
            }
        } 
        echo "\n"; 
    } 
}

?> 
