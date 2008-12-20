<?php

//Get the database and board information
require_once(dirname(__FILE__) . '/Settings.php');
global $db_server, $db_name, $db_user, $db_prefix, $db_passwd;


//nom de la table
$table_name="smf_tp_dlmanager";

//connection à la base de donnée 
 
$link = mysql_connect($db_server, $db_user, $db_passwd) or die("Connexion impossible.");
$db = mysql_select_db($db_name, $link);
  
      
$resQuery = mysql_query("select `id`, `name`, `description`, `icon`, `category`, `type`, `downloads`, `file`, `created`, `parent`, `screenshot` from " . $table_name); 

header("Content-Type: application/csv-tab-delimited-table"); 
header("Content-disposition: filename=table.csv"); 

if (mysql_num_rows($resQuery) != 0) { 
    // titre des colonnes 
    //$fields = mysql_num_fields($resQuery); 
    //$i = 0; 
    //while ($i < $fields) { 
    //    echo mysql_field_name($resQuery, $i)."|"; 
    //    $i++; 
    //} 
    //echo "\n"; 

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
                $contenu = str_replace("&nbsp;", " ",$contenu);
                $textsansbalise = strip_tags($contenu);
                $text = str_replace("\r\n","</br>",$textsansbalise);
                //$text = nl2br($contenu);
                echo "$text|"; 
            }
        } 
        echo "\n"; 
    } 
} 
?> 
