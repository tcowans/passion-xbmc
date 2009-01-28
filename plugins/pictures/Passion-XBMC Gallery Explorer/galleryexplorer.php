<?php

//Get the database and board information
require_once(dirname(__FILE__) . '/Settings.php');
global $db_server, $db_name, $db_user, $db_prefix, $db_passwd;

if(isset($_GET['cat']))
{
    $idcat = (int)$_GET['cat'];
    if ($idcat == 0) {$start = 'True';}
    else {$start = 'False';}
}
else
{
    $start = 'True';
}

//connection à la base de donnée 
 
$link = mysql_connect($db_server, $db_user, $db_passwd) or die("Connexion impossible.");
$db = mysql_select_db($db_name, $link);
  
header("Content-Type: application/csv-tab-delimited-table"); 
header("Content-disposition: filename=table.csv"); 

      

if ($start == 'False')
{
    $resQuery = mysql_query("   SELECT `ID_CAT` , `TITLE` , `DESCRIPTION` , `IMAGE` , `ID_PARENT`
                            FROM `smf_gallery_cat`
                            WHERE `ID_PARENT` = $idcat"); 

    if (mysql_num_rows($resQuery) != 0) { 
        // données de la table 
        while ($arrSelect = mysql_fetch_array($resQuery, MYSQL_ASSOC)) { 
            $i = 0;
            foreach($arrSelect as $elem) {
                $contenu=utf8_encode($elem);
                if ($contenu == ''){$contenu = "None";}
                
                switch(mysql_field_name($resQuery,$i))
                {
                    case "ID_CAT":
                        echo "$contenu|CAT|";
                    break;
    
                    case "DESCRIPTION":
                        $contenu = strip_tags($contenu);
                        $contenu = str_replace("\r\n","</br>",$contenu);
                        echo "$contenu|";                     
                    break;
                    
                    case "IMAGE":
                        echo "$contenu|None|";
                    break;
                    
                    default:
                        echo "$contenu|";
                }
                $i++;
            } 
            echo "\n"; 
        } 
    } 

    $resQuery = mysql_query("   SELECT `ID_PICTURE` , `TITLE` , `DESCRIPTION` , `THUMBFILENAME`, `FILENAME`, `ID_CAT`
                                FROM `smf_gallery_pic` 
                                WHERE `ID_CAT` = $idcat"); 



    if (mysql_num_rows($resQuery) != 0) { 
        // données de la table 
        while ($arrSelect = mysql_fetch_array($resQuery, MYSQL_ASSOC)) { 
            $i = 0;
            foreach($arrSelect as $elem) {
                $contenu=utf8_encode($elem);
                if ($contenu == ''){$contenu = "None";}

                switch(mysql_field_name($resQuery,$i))
                {
                    case "ID_PICTURE":
                        echo "$contenu|PIC|";
                    break;
    
                    case "DESCRIPTION":
                        $contenu = strip_tags($contenu);
                        $contenu = str_replace("\r\n","</br>",$contenu);
                        echo "$contenu|";                     
                    break;
                    
                    case "FILENAME":
                    case "THUMBFILENAME":
                        $contenu = "http://passion-xbmc.org/gallery/".$contenu;
                        echo "$contenu|";
                    break;
                    
                    default:
                        echo "$contenu|";
                }
            
                $i++;
            } 
            echo "\n"; 
        } 
    } 
}
else
{
    $authorizedcat = '(30,43,61,98,105)';
    $resQuery = mysql_query("   SELECT `ID_CAT` , `TITLE` , `DESCRIPTION` , `IMAGE` , `ID_PARENT`
                                FROM `smf_gallery_cat`
                                WHERE `ID_CAT` IN $authorizedcat "); 

    if (mysql_num_rows($resQuery) != 0) { 
        // données de la table 
        while ($arrSelect = mysql_fetch_array($resQuery, MYSQL_ASSOC)) { 
            $i = 0;
            foreach($arrSelect as $elem) {
                $contenu=utf8_encode($elem);
                if ($contenu == ''){$contenu = "None";}
                
                switch(mysql_field_name($resQuery,$i))
                {
                    case "ID_CAT":
                        echo "$contenu|CAT|";
                    break;
    
                    case "DESCRIPTION":
                        $contenu = strip_tags($contenu);
                        $contenu = str_replace("\r\n","</br>",$contenu);
                        echo "$contenu|";                     
                    break;
                    
                    case "IMAGE":
                        echo "$contenu|None|";
                    break;
                    
                    default:
                        echo "$contenu|";
                }
                
                $i++;
            } 
            echo "\n"; 
        } 
    } 
}
?> 
