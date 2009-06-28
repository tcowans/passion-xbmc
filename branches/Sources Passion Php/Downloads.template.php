<?php
/*
Download System
Version 1.1
by:vbgamer45
Cool Layout AddOn by:  SoLoGHoST
http://www.smfhacks.com
Copyright 2009 SMFHacks.com

############################################
License Information:

Links to http://www.smfhacks.com must remain unless
branding free option is purchased.
#############################################
*/
function template_mainview()
{
    global $scripturl, $txt, $context, $modSettings, $subcats_linktree, $ID_MEMBER, $settings;

    echo '
<script language="JavaScript" type="text/javascript" src="' . $settings['default_theme_url'] . '/scripts/ratings.js"></script>';
    
echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';

    // Permissions
    $g_manage = allowedTo('downloads_manage');
    $g_add = allowedTo('downloads_add');

    
    if ($g_manage)
    {
        // Warn the user if they are managing the downloads that the path it is not writable
        if (!is_writable($modSettings['down_path']))
            echo '<font color="#FF0000"><b>', $txt['downloads_write_error'], $modSettings['down_path'], '</b></font>';
    }

    // Get the Category if present
    @$cat = (int) $_REQUEST['cat'];

    // Check if a category is selected
    if (!empty($cat))
    {
        // Show the items in the category
        
        // Permissions if they are allowed to edit or delete their own downloads.
        $g_edit_own = allowedTo('downloads_edit');
        $g_delete_own = allowedTo('downloads_delete');

    
    
    echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">',$context['downloads_cat_name'],'</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';                

        // Show sub catigories
        ShowSubCats($cat,$g_manage);
    
        
        if (!isset($context['downloads_cat_norate']))
            $context['downloads_cat_norate'] = 0;
            
    if (!isset($context['downloads_cat_layout']))
            $context['downloads_cat_layout'] = (int) $modSettings['down_set_cat_layout'];
    
        // $layout = (int) $modSettings['down_set_cat_layout'];
        $layout = $context['downloads_cat_layout'];
        // Show table header
        $count = 0;
        
        if ($context['downloads_orderby2'] == 'asc')
            $neworder = 'desc';
        else 
            $neworder = 'asc';
        
if ($layout == 0) {
        echo '<table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                        <tr class="catbg">';

            if (!empty($modSettings['down_set_t_title']))
            {   
                echo  '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=title;orderby=' . $neworder . '">',$txt['downloads_cat_title'], '</a></td>';
                $count++;
            }

            if (!empty($modSettings['down_set_t_rating']) && $context['downloads_cat_norate'] != 1)
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=ratings;orderby=' . $neworder . '">', $txt['downloads_cat_rating'], '</a></td>';
                $count++;
            }
            
            if (!empty($modSettings['down_set_t_views']))
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostview;orderby=' . $neworder . '">', $txt['downloads_cat_views'], '</a></td>';
                $count++;
            }
                
                
            if (!empty($modSettings['down_set_t_downloads']))
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostdowns;orderby=' . $neworder . '">', $txt['downloads_cat_downloads'] , '</a></td>';   
                $count++;
            }
                
            if (!empty($modSettings['down_set_t_filesize']))
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . 'sortby=filesize;orderby=' . $neworder . '">',$txt['downloads_cat_filesize'], '</a></td>';
                $count++;
            }
                
            if (!empty($modSettings['down_set_t_date']))
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=date;orderby=' . $neworder . '">',$txt['downloads_cat_date'], '</a></td>';
                $count++;
            }
                
            if (!empty($modSettings['down_set_t_comment']))
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostcom;orderby=' . $neworder . '">',$txt['downloads_cat_comments'],'</a></td>';
                $count++;
            }
            
            if (!empty($modSettings['down_set_t_username']))
            {
                echo '<td><a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=membername;orderby=' . $neworder . '">',$txt['downloads_cat_membername'],'</a></td>';
                $count++;
            }
            
            
            // Options
            if ($g_manage ||  ($g_delete_own) || ($g_edit_own) )
            {
                echo '<td>',$txt['downloads_cat_options'],'</td>';
                $count++;
            }

        echo '</tr>';
        

        
        foreach ($context['downloads_files'] as $i => $file)
        {
    
            echo '<tr>';
            
            if (!empty($modSettings['down_set_t_title']))   
                echo  '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '">', $file['title'], '</a></td>';
            

            if (!empty($modSettings['down_set_t_rating']) && $context['downloads_cat_norate'] != 1)
                echo '<td>', GetStarsByPrecent(($file['totalratings'] != 0) ? ($file['rating'] / ($file['totalratings']* 5) * 100) : 0), '</td>';
            
            if (!empty($modSettings['down_set_t_views']))
                echo '<td>', $file['views'], '</td>';
                
            if (!empty($modSettings['down_set_t_downloads']))
                echo '<td>', $file['totaldownloads'], '</td>';
                
            if (!empty($modSettings['down_set_t_filesize']))
                echo '<td>', format_size($file['filesize'], 2) . '</td>';
                
            if (!empty($modSettings['down_set_t_date']))    
                echo '<td>', timeformat($file['date']), '</td>';
                
            if (!empty($modSettings['down_set_t_comment'])) 
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '">', $file['commenttotal'], '</a></td>';
            if (!empty($modSettings['down_set_t_username']))
            {
                if ($file['realName'] != '')
                    echo '<td><a href="' . $scripturl . '?action=profile;u=' . $file['ID_MEMBER'] . '">'  . $file['realName'] . '</a></td>';
                else 
                    echo '<td>', $txt['downloads_guest'], '</td>';
            }
            
            
            // Options
            if ($g_manage ||  ($g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER) || ($g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER) )
            {
                echo '<td>';
                if ($g_manage)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=unapprove;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_unapprove'] . '</a>';
                if ($g_manage || $g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=edit;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_edit'] . '</a>';
                if ($g_manage || $g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_delete'] . '</a>';
    
                echo '</td>';
            }


            
            echo '</tr>';
            
        }

        // Display who is viewing the downloads.
        if (!empty($modSettings['down_who_viewing']))
        {
            echo '<tr>
            <td align="center" colspan="', $count, '"><span class="smalltext">';

            // Show just numbers...?
            // show the actual people viewing the topic?
            echo empty($context['view_members_list']) ? '0 ' . $txt['downloads_who_members'] : implode(', ', $context['view_members_list']) . (empty($context['view_num_hidden']) || $context['can_moderate_forum'] ? '' : ' (+ ' . $context['view_num_hidden'] . ' ' . $txt['downloads_who_hidden'] . ')');

            // Now show how many guests are here too.
            echo $txt['who_and'], @$context['view_num_guests'], ' ', @$context['view_num_guests'] == 1 ? $txt['guest'] : $txt['guests'], $txt['downloads_who_viewdownload'], '</span></td></tr>';
        }

        
            echo '<tr class="titlebg">
                    <td align="left" colspan="', $count, '">
                    ' . $txt['downloads_text_pages'];
            
                    echo $context['page_index'];
    
        
            echo '
                    </td>
                </tr>';
    
        
        // Show return to downloads link and Show add download if they can
        echo '
                <tr class="titlebg"><td align="center" colspan="', $count, '">';

}
else {
// We are viewing either Small Tables or FULL VIEW Layout NOW... Do some Very Cool STuFF :)
// If 1 or more downloads are available in this category...
if (count($context['downloads_files']) >= 1) {

        echo '<table cellspacing="0" cellpadding="0" border="0" align="center" width="90%" class="tborder">';
            echo '<tr class="titlebg" style="padding: 5px;">';

            echo '<td align="left" style="font-size: 10px;">';

if ($context['downloads_orderby2'] == 'asc')

echo '<a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=', $context['downloads_sortby'], ';orderby=' . $neworder . '"><div class="asc" title="Ascending"></div></a>';

else if ($context['downloads_orderby2'] == 'desc')

echo '<a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=', $context['downloads_sortby'], ';orderby=' . $neworder . '"><div class="desc" title="Descending"></div></a>';          

  echo 'Sort by: &nbsp;&nbsp;'; 

            if (!empty($modSettings['down_set_t_title']))
            {   
            if ($context['downloads_sortby'] == 'title')
                echo '[', $txt['downloads_cat_title'], '] &nbsp;';
            else
                echo  '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=title;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_title'], '</a> &nbsp;';
            }

            if (!empty($modSettings['down_set_t_rating']) && $context['downloads_cat_norate'] != 1)
            {
            if ($context['downloads_sortby'] == 'ratings')
                echo '[', $txt['downloads_cat_rating'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=ratings;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_rating'], '</a> &nbsp;';
            }
            
            if (!empty($modSettings['down_set_t_views']))
            {
            if ($context['downloads_sortby'] == 'mostview')
                echo '[', $txt['downloads_cat_views'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostview;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_views'], '</a> &nbsp;';
            }
                

            if (!empty($modSettings['down_set_t_downloads']))
            {
            if ($context['downloads_sortby'] == 'mostdowns')
                echo '[', $txt['downloads_cat_downloads'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostdowns;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_downloads'], '</a> &nbsp;';  
            }
                
            if (!empty($modSettings['down_set_t_filesize']))
            {
            if ($context['downloads_sortby'] == 'filesize')
                echo '[', $txt['downloads_cat_filesize'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=filesize;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_filesize'], '</a> &nbsp;';
            }
                
            if (!empty($modSettings['down_set_t_date']))
            {
            if ($context['downloads_sortby'] == 'date')
                echo '[', $txt['downloads_cat_date'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=date;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_date'], '</a> &nbsp;';
            }
                
            if (!empty($modSettings['down_set_t_comment']))
            {
            if ($context['downloads_sortby'] == 'mostcom')
                echo '[', $txt['downloads_cat_comments'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostcom;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_comments'], '</a> &nbsp;';
            }
            
            if (!empty($modSettings['down_set_t_username']))
            {
            if ($context['downloads_sortby'] == 'membername')
                echo '[', $txt['downloads_cat_membername'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=membername;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_membername'], '</a> &nbsp;';
            }
            
            
            echo '</td>';

    echo '<td align="right">
                    ' . $txt['downloads_text_pages'];
            
                    echo $context['page_index'];
    
        
            echo '
                </td>';
            
        // Display who is viewing the downloads.
        if (!empty($modSettings['down_who_viewing']))
        {
            echo '<tr>
            <td align="center" colspan="2"><span class="smalltext">';

            // Show just numbers...?
            // show the actual people viewing the topic?
            echo empty($context['view_members_list']) ? '0 ' . $txt['downloads_who_members'] : implode(', ', $context['view_members_list']) . (empty($context['view_num_hidden']) || $context['can_moderate_forum'] ? '' : ' (+ ' . $context['view_num_hidden'] . ' ' . $txt['downloads_who_hidden'] . ')');

            // Now show how many guests are here too.
            echo $txt['who_and'], @$context['view_num_guests'], ' ', @$context['view_num_guests'] == 1 ? $txt['guest'] : $txt['guests'], $txt['downloads_who_viewdownload'], '</span></td></tr>';
        }
                        
    echo '<tr><td>&nbsp;</td></tr><tr><td colspan="2" align="center">'; 
    
    if ($layout == 1) {
        $xFile = 0;
        $currRow = 0;
        $totalfiles = count($context['downloads_files']);
        // $numRows = $modSettings['down_set_rows_per_page_tables'];
        echo '<table border="0" align="center" width="90%" cellspacing="0" cellpadding="5">
                    <tr>';
                        
    
    }           
                
        foreach ($context['downloads_files'] as $i => $file)
        {       
        
        if ($layout == 1) { // We are viewing Tables, not Full View..
        // Update the file...
        echo '<td width="25%" align="center">';
        
            // Check to see if title it too long, and rename it a little using ...
            $tNum = strlen($file['title']);
            // No quotes before we do some checking...
            $downTitle = htmlspecialchars_decode($file['title'], ENT_QUOTES);
            if ($tNum > 20) {
                $downTitle = substr($downTitle, 0, 17);
                $downTitle = $downTitle . '...';
            }
            // strip problems after checking...
            $downTitle = htmlspecialchars_decode($downTitle, ENT_QUOTES);
        
        
            echo '<div align="center" width="100%" height="25%" class="tborder">
                    <div class="titlebg" width="100%" height="100%" align="center" style="vertical-align: center; font-size: 14px;">';
                                if ($modSettings['down_set_file_title'])    
                                    echo  '<strong><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '" style="font-size: 14px;" title="' . $file['title'] . '">', $downTitle, '</a></strong></span>
                    </div>                              
                    <div class="downBody1 smalltext" width="100%" height="183" align="center" style="position: relative; left: 0px; top: 0px; width: 100%; height: 183px; align: center; text-align: center; vertical-align: middle;"><table cellpadding="0" cellspacing="0" border="0" width="211" height="183" align="center"><tr><td width="100%" height="100%" align="center" valign="middle">';                    
                // Check if rating is allowed for these files in the Category...
    if ($modSettings['down_set_file_showrating']) {
            if ($modSettings['down_show_ratings'] == true && $context['downloads_cat_norate'] != 1)
                echo '' . GetStarsByPrecent($file['actualrating'] != 0 ? $file['actualrating'] : 0) . '<br/>';
                if ($modSettings['down_set_file_rating_count'] && empty($file['screenshotTables']))
                    if ($file['totalratings'] != 0)
                        echo 'Rated <b>', ($file['totalratings'] > 1 ? $file['totalratings'] . '</b> times' : $file['totalratings'] . '</b> time') . '<br/>';
    }


    if (!empty($file['screenshotTables'])) {
    
    $ssTables = $modSettings['down_url'] . 'screenshots/tables/' . $file['screenshotTables'];
    
        echo '<span style="align: center;" title="' . $file['title'] . '"><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '"><img src="' . $ssTables . '" /></a></span><br/>';

    }

    echo '<span style="font-size: 12px;">';
    // Sort the Posted By:  User and the Date...        
    if (!empty($modSettings['down_set_file_poster']))
    {
    echo $txt['downloads_text_by'] . ' ';
    
        if ($file['realName'] != '')
            echo '<a href="' . $scripturl . '?action=profile;u=' . $file['ID_MEMBER'] . '" style="font-size: 12px;"><strong>'  . $file['realName'] . '</strong></a>';
        else 
            echo $txt['downloads_guest'], '';
            
    }   
                    echo '</span>';


        if (empty($file['screenshotTables'])) { 
    
                if (!empty($modSettings['down_set_t_date']))    
                    echo '<br />', timeformat($file['date']), '';
                    
                if (!empty($modSettings['down_set_t_filesize']))
                    echo '<br />' . $txt['downloads_text_filesize'] . ' ', format_size($file['filesize'], 2), '';
            
                if (!empty($modSettings['down_set_t_views']))
                    echo '<br />' . $txt['downloads_text_views'] . ' ', $file['views'];
                    
                if (!empty($modSettings['down_set_t_downloads']))
                    echo '<br />' . $txt['downloads_cat_downloads'] . ': ', $file['totaldownloads'];
                    
                if (!empty($modSettings['down_set_t_comment'])) {
                    echo '<br />';
                    if ($file['commenttotal'] >= 1)
                        echo '<a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '">', $txt['downloads_text_comments'], ': ', $file['commenttotal'], '</a>';
                    else
                        if (allowedTo('downloads_comment'))
                        {
                            // Show Add Comment
                            echo '<a href="' . $scripturl . '?action=downloads;sa=comment;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_addcomment'] . '</a>';
                        }
                }
        }

                        echo '</td></tr></table></div>
                    <div class="titlebg downBody1" width="100%" height="100%" align="center" style="vertical-align: center;">';
                        // Let's add the download button now...
                        echo '<a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $file['ID_FILE'], '"><img src="' . $settings['images_url'] . '/downloads.png"  width="122" height="32" border="0" /></a>
                    </div>
                    </div>';        
        echo '</td>';

            $xFile++;
            if (fmod($xFile, 4) == 0) {
                $currRow++;
                if ($currRow == $modSettings['down_set_rows_per_page_tables'] || $xFile == $totalfiles)
                    echo '</tr></table></td>';
                else
                    echo '</tr><tr>';   
            } else {
                // We are somewhere in the row, find out where so we can create a colspan="#" to fill the rest and then </tr></table></td> it.
                if ($xFile == $totalfiles) {
                    $col = 0; 
                    $dumFiles = $totalfiles;
                    
                    while (fmod($dumFiles, 4) != 0)
                    {
                        $dumFiles++;
                        $col++;
                    }
                    if ($col <= 1)
                        echo '</tr></table></td>';
                    else 
                        echo '<td colspan="' . $col . '">&nbsp;</td></tr></table></td>';
            
                }
            }
                
        } else { // BEGIN FULL VIEW LAYOUT!
        // Create an anchor so we can scroll to this download, if needed, when reloading this page...
echo '<a href="javascript:void(0);" name="down' . $file['ID_FILE'] . '"></a><table border="0" align="center" width="90%" cellspacing="0" cellpadding="0" class="tborder">
                            <tr class="titlebg"><td width="25%" align="left" valign="middle"><span style="font-size: 10px;">';
            // Options
            if ($g_manage ||  ($g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER) || ($g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER) )
            {
            if ($g_manage)
            echo '<a href="' . $scripturl . '?action=downloads;sa=unapprove;id=' . $file['ID_FILE'] . '" style="font-size: 10px;">' . $txt['downloads_text_unapprove'] . '</a>';
            if ($g_manage || $g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER)
            echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=edit;id=' . $file['ID_FILE'] . '" style="font-size: 10px;">' . $txt['downloads_text_edit'] . '</a>';
            if ($g_manage || $g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER)
            echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $file['ID_FILE'] . '" style="font-size: 10px;">' . $txt['downloads_text_delete'] . '</a>';
            }           
            echo '</span></td><td width="50%" align="center" valign="middle" style="padding-bottom: 5px;">';
            
            echo '<span style="color: #000000; font-size: 16px;">';
            if ($modSettings['down_set_file_title'])
                
                echo  '<strong><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '" style="font-size: 18px;">', $file['title'], '</a></strong>';
            
            echo '</span><br/><span style="font-size: 10px; color: #CCCCCC;"><strong><a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $file['ID_FILE'], '" style="font-size: 12px;">', $file['orginalfilename'], '</a></strong> ';

// We are dealing with the Downloads $modSettings, not the Category $modSettings...
            if (!empty($modSettings['down_set_file_showfilesize']) || !empty($modSettings['down_set_file_downloads']))
            {
                    echo '(';
                    
                    if (!empty($modSettings['down_set_file_showfilesize']))
                        echo format_size($file['filesize'], 2);
                        
                    if (!empty($modSettings['down_set_file_downloads']) && !empty($modSettings['down_set_file_showfilesize']))
                        echo ' - Downloaded ', $file['totaldownloads'], ' times';
                    else if (!empty($modSettings['down_set_file_downloads']) && empty($modSettings['down_set_file_showfilesize']))
                        echo 'Downloaded ', $file['totaldownloads'], ' times';                      

                        echo ')';
            }
                echo'</span></td><td width="25%" align="right" valign="middle">';
                // Check if rating is allowed for these files in the Category...
    if ($modSettings['down_set_file_showrating']) {
            if ($modSettings['down_show_ratings'] == true && $context['downloads_cat_norate'] != 1)
                echo '' . GetStarsByPrecent($file['actualrating'] != 0 ? $file['actualrating'] : 0);
                if ($modSettings['down_set_file_rating_count'])
                    if ($file['totalratings'] != 0)
                    echo '<br/><b style="font-size: 10px; font-weight: normal;">Rated <b>', ($file['totalratings'] > 1 ? $file['totalratings'] . '</b> times</b>' : $file['totalratings'] . '</b> time');
    }
            echo '</td></tr><tr><td colspan="3" align="center" valign="middle" class="downBody1"><span style="font-size: 12px; color: #CCCCCC;">';

            // Sort the Posted By:  User and the Date...
            if ($modSettings['down_set_file_poster'] && $modSettings['down_set_file_date'])
            {
                if ($file['realName'] != '')
                    echo 'Posted by: <a href="' . $scripturl . '?action=profile;u=' . $file['ID_MEMBER'] . '"><strong>'  . $file['realName'] . '</strong></a> - ', timeformat($file['date']), '';
                else 
                    echo 'Posted by: ', $txt['downloads_guest'], ' - ', timeformat($file['date']), '';
                    
            } else if ($modSettings['down_set_file_poster'] && empty($modSettings['down_set_file_date'])) {
                if ($file['realName'] != '')
                    echo 'Posted by: <a href="' . $scripturl . '?action=profile;u=' . $file['ID_MEMBER'] . '"><strong>'  . $file['realName'] . '</strong></a>';
                else 
                    echo 'Posted by: ', $txt['downloads_guest'];
            } else if (empty($modSettings['down_set_file_poster']) && $modSettings['down_set_file_date']) {
                        
                echo '', timeformat($file['date']), '';
            }

        echo '</span></td></tr>';
        
        if ($modSettings['down_set_file_desc']) {
            
            echo '<tr><td colspan="3" align="center" valign="middle" class="downBody2">';
                    
            if (!empty($file['screenshot'])) {
                echo '<img src="' . $modSettings['down_url'] . 'screenshots/' . $file['screenshot'] . '" /><br/>';
            }
            
            echo parse_bbc($file['description']), '</td></tr>';
        
        }
        
        echo '<tr width="100%">';
                            
        echo '<td width="100%" colspan="3"><table width="100%" cellspacing="0" cellpadding="0" border="0"><tr class="titlebg"><td align="left" valign="middle" width="305">';               

            // Placing form in here allows us to get all of the hidden types at all permission levels...
            echo '<form name="backMain' . $file['ID_FILE'] . '" method="post" action="' . $scripturl . '?action=downloads;sa=rate2">';
        // Check if the files in this category are allowed to be rated...
        if ($modSettings['down_set_file_showrating'] && $modSettings['down_show_ratings'] == true && $context['downloads_cat_norate'] == 0)
        {

                    $max_num_stars = 5;
                    
                    if (allowedTo('downloads_ratefile'))
                    {
                        // If file belongs to the user, do not show Rating Info, since they can't rate their own downloads!
                        if ($file['ID_MEMBER'] == $ID_MEMBER)
                        {
                        // If the user can manage the downloads let them see who voted for what and option to delete rating
                        if ($g_manage)
                            echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=viewrating;id=' . $file['ID_FILE'] . '">[' . $txt['downloads_form_viewratings'] . ']</a>';
                        } 
                        else if ($file['alreadyrated'] != 0)
                        {
                        // User has already rated this file, and will not be able to rate it again!
                        // So show them their rating for this file...
                            echo '<b style="position: relative; top: -5px;">Your Rating: </b>';
                        
                        for($i=0; $i < $max_num_stars; $i++) {
                            if ($i < $file['yourrating'])
                                echo '<img src="', $settings['images_url'], '/starFull.png" alt="*" border="0" />';
                            else                        
                                echo '<img src="', $settings['images_url'], '/starEmpty.png" alt="*" border="0" />';
                        }
                        // If the user can manage the downloads let them see who voted for what and option to delete rating
                        if ($g_manage)
                            echo '<br/><a href="' . $scripturl . '?action=downloads;sa=viewrating;id=' . $file['ID_FILE'] . '">[' . $txt['downloads_form_viewratings'] . ']</a>';
                        } else {
    // If the user has gotten this far, they have not rated another users download, or they are a Guest, so allow them to rate it...
    // Note: While Guests will have an option to Rate the Download, they will be prompted to register if trying to do so ;)
                            echo '<b style="position: relative; top: -5px;">Rate It: </b>';
                            for($i = 1; $i <= $max_num_stars;$i++) {
                            // Set the alt text variable...
                            $alt = '';
                            if ($i == 1)
                                $alt = 'Hate it';
                            else if ($i == 2)
                                $alt = 'Don\'t like it';
                            else if ($i == 3)
                                $alt = 'It\'s okay';
                            else if ($i == 4)
                                $alt = 'Like it';
                            else
                                $alt = 'Love it';   
                                
                                $combo[$i-1] = 'img' . $file['ID_FILE'];

                                echo '<input type="image" name="rating" id="' . $combo[$i-1] . '' . $i . '" src="'. $settings['images_url'] . '/starEmpty.png" alt="' . $alt . '" value="' . $i . '" border="0" onMouseOver="submitVote(\''.$file['ID_FILE'].'\', \''. $i .'\'); doMover(\''. $settings['images_url'] . '\', \'' . $combo[$i-1] . '\',\'' . $i . '\');" onMouseout="desOut(\''.$file['ID_FILE'].'\'); doMout(\''. $settings['images_url'] . '\', \'' . $combo[$i-1] . '\');" onClick="javascript:document.backMain'. $file['ID_FILE'] . '.submit()" alt="' . $alt . '" style="border: none; background: transparent;" />';
                                
// input is hidden, but necessary so we can get the ratings form the user...
// When user mouses over the Stars, it automatically checks the appropriate radio button, even tho it is hidden...                              
echo '<input type="radio" id="rat'. $file['ID_FILE'], $i . '" name="rating" value="' . $i . '" style="display: none;" />';
                                
                            }
                            // This will hold the description of each rating as the user mouses over the Stars!
                            echo '<b id="dRate' . $file['ID_FILE'] . '" style="position:relative; top: -5px; left: 5px; font-weight: normal;"> </b>';

                        // If the user can manage the downloads let them see who voted for what and option to delete rating
                        if ($g_manage)
                            echo '<br/><a href="' . $scripturl . '?action=downloads;sa=viewrating;id=' . $file['ID_FILE'] . '">[' . $txt['downloads_form_viewratings'] . ']</a>';
                        }
                    }

}
    // Setting all of the hidden values so that we can get them if we need them...
     echo '<input type="hidden" name="sortby" value="', $context['downloads_sortby'], '" />
     <input type="hidden" name="orderby" value="', $context['downloads_orderby2'], '" />
     <input type="hidden" name="start" value="', $context['start'], '" />';
     
     // <input type="hidden" name="catlayout" value="' , $context['downloads_cat_layout'], '" />
     echo '<input type="hidden" name="cat" value="', $context['downloads_cat'], '" />
     <input type="hidden" name="id" value="', $file['ID_FILE'], '" />
     <input type="hidden" name="id', $file['ID_FILE'], '" value="' . $file['ID_FILE'] . '" />
                        </form>';

    echo '</td><td valign="middle" width="20%"><a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $file['ID_FILE'], '"><img src="' . $settings['images_url'] . '/downloads.png"  width="122" height="32" border="0" /></a></td><td align="right" valign="middle" width="40%">';
    
            if (!empty($file['allowcomments'])) {
                if ($file['commenttotal'] >= 1)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '" style="font-size: 10px;">Comments';
            if (!empty($modSettings['down_set_t_comment'])) 
            {   
                if ($file['commenttotal'] >= 1)
                    echo ' (', $file['commenttotal'], ')</a>';
            }

            echo (!empty($file['allowcomments']) && $file['commenttotal'] >= 1 ? '<br/>' : ''), '<a href="' . $scripturl . '?action=downloads;sa=comment;id=' . $file['ID_FILE'] . '"', ($file['commenttotal'] >= 1 ? ' style="font-size: 10px;"' : ''), '>' . $txt['downloads_text_addcomment'] . '</a>';
            }
    echo '</td>
                          </tr>
</table></td></tr></table><br/><br/>';
    } // End of $layout == 2 - FULL VIEW
    
}
    
    
    
    
    
    
    
                    echo '</td>
                </tr>';


        // Display who is viewing the downloads.
        if (!empty($modSettings['down_who_viewing']))
        {
            echo '<tr>
            <td align="center" colspan="2"><span class="smalltext">';

            // Show just numbers...?
            // show the actual people viewing the topic?
            echo empty($context['view_members_list']) ? '0 ' . $txt['downloads_who_members'] : implode(', ', $context['view_members_list']) . (empty($context['view_num_hidden']) || $context['can_moderate_forum'] ? '' : ' (+ ' . $context['view_num_hidden'] . ' ' . $txt['downloads_who_hidden'] . ')');

            // Now show how many guests are here too.
            echo $txt['who_and'], @$context['view_num_guests'], ' ', @$context['view_num_guests'] == 1 ? $txt['guest'] : $txt['guests'], $txt['downloads_who_viewdownload'], '</span></td></tr>';
        }

        
            echo '<tr class="titlebg">';

            echo '<td align="left" style="font-size: 10px;">';

if ($context['downloads_orderby2'] == 'asc')

echo '<a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=', $context['downloads_sortby'], ';orderby=' . $neworder . '"><div class="asc" title="Ascending"></div></a>';

else if ($context['downloads_orderby2'] == 'desc')

echo '<a href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=', $context['downloads_sortby'], ';orderby=' . $neworder . '"><div class="desc" title="Descending"></div></a>';  

            echo 'Sort by: &nbsp;&nbsp;';

            if (!empty($modSettings['down_set_t_title']))
            {   
            if ($context['downloads_sortby'] == 'title')
                echo '[', $txt['downloads_cat_title'], '] &nbsp;';
            else
                echo  '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=title;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_title'], '</a> &nbsp;';
            }

            if (!empty($modSettings['down_set_t_rating']) && $context['downloads_cat_norate'] != 1)
            {
            if ($context['downloads_sortby'] == 'ratings')
                echo '[', $txt['downloads_cat_rating'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=ratings;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_rating'], '</a> &nbsp;';
            }
            
            if (!empty($modSettings['down_set_t_views']))
            {
            if ($context['downloads_sortby'] == 'mostview')
                echo '[', $txt['downloads_cat_views'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostview;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_views'], '</a> &nbsp;';
            }
                

            if (!empty($modSettings['down_set_t_downloads']))
            {
            if ($context['downloads_sortby'] == 'mostdowns')
                echo '[', $txt['downloads_cat_downloads'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostdowns;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_downloads'], '</a> &nbsp;';  
            }
                
            if (!empty($modSettings['down_set_t_filesize']))
            {
            if ($context['downloads_sortby'] == 'filesize')
                echo '[', $txt['downloads_cat_filesize'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=filesize;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_filesize'], '</a> &nbsp;';
            }
                
            if (!empty($modSettings['down_set_t_date']))
            {
            if ($context['downloads_sortby'] == 'date')
                echo '[', $txt['downloads_cat_date'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=date;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_date'], '</a> &nbsp;';
            }
                
            if (!empty($modSettings['down_set_t_comment']))
            {
            if ($context['downloads_sortby'] == 'mostcom')
                echo '[', $txt['downloads_cat_comments'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=mostcom;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_comments'], '</a> &nbsp;';
            }
            
            if (!empty($modSettings['down_set_t_username']))
            {
            if ($context['downloads_sortby'] == 'membername')
                echo '[', $txt['downloads_cat_membername'], '] &nbsp;';
            else
                echo '<a style="font-size: 10px;" href="' . $scripturl . '?action=downloads;cat=' . $cat . ';start=' . $context['start'] . ';sortby=membername;orderby=', $context['downloads_orderby2'], '">', $txt['downloads_cat_membername'], '</a> &nbsp;';
            }
              
echo '</td>';

            // Do the Pages view at the bottom...
            echo '<td align="right">
                    ' . $txt['downloads_text_pages'];
            
                    echo $context['page_index'];
    
        
            echo '
                    </td>
                </tr>';
            
        // Show return to downloads link and Show add download if they can
        echo '
                <tr class="titlebg"><td align="center" colspan="2">';

} else {
    // There are no downloads in here...  Just show members that are here, options to add download, add subcategory, & return to downloads
    echo '<table cellspacing="0" cellpadding="0" border="0" align="center" width="90%" class="tborder">';
        // Display who is viewing the downloads.
        if (!empty($modSettings['down_who_viewing']))
        {
            echo '<tr>
            <td align="center"><span class="smalltext">';

            // Show just numbers...?
            // show the actual people viewing the topic?
            echo empty($context['view_members_list']) ? '0 ' . $txt['downloads_who_members'] : implode(', ', $context['view_members_list']) . (empty($context['view_num_hidden']) || $context['can_moderate_forum'] ? '' : ' (+ ' . $context['view_num_hidden'] . ' ' . $txt['downloads_who_hidden'] . ')');

            // Now show how many guests are here too.
            echo $txt['who_and'], @$context['view_num_guests'], ' ', @$context['view_num_guests'] == 1 ? $txt['guest'] : $txt['guests'], $txt['downloads_who_viewdownload'], '</span></td></tr>';
        }
            echo '<tr class="titlebg"><td align="center">';
    
}

}
// END OF COOL LAYOUT!!!!
                if ($g_manage)              
                    echo '<a href="', $scripturl, '?action=downloads;sa=addcat;cat=', $cat, '">', $txt['downloads_text_addsubcat'], '</a>&nbsp;&nbsp;';
            
                if ($g_add)
                    echo '<a href="', $scripturl, '?action=downloads;sa=add;cat=', $cat, '">', $txt['downloads_text_adddownload'], '</a><br />';
                
                
                echo '
                <a href="', $scripturl, '?action=downloads">', $txt['downloads_text_returndownload'], '</a></td>
            </tr>
            </table><br /><br /><br />';

    }
    else
    {
        // No Category is set then show the main category list

            echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">',$txt['downloads_text_title'],'</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';

        // Show the index page blocks
        if ($modSettings['down_index_showtop'])
        {
            for ($x = 1; $x < 6; $x++) {
                // Recent
                if (!empty($modSettings['down_index_recent']) && $modSettings['down_index_recent_order'] == $x)
                    MainPageBlock($txt['downloads_main_recent'], $x, 'recent');
                // Most Viewed
                if (!empty($modSettings['down_index_mostviewed']) && $modSettings['down_index_mostviewed_order'] == $x)
                    MainPageBlock($txt['downloads_main_viewed'], $x, 'viewed');
                // Most Downloaded
                if (!empty($modSettings['down_index_mostdownloaded']) && $modSettings['down_index_mostdownloaded_order'] == $x)
                    MainPageBlock('Top Downloads', $x, 'mostdownloaded');
                // Most commented
                if (!empty($modSettings['down_index_mostcomments']) && $modSettings['down_index_mostcomments_order'] == $x)
                    MainPageBlock($txt['downloads_main_mostcomments'], $x, 'mostcomments');
                // Top Rated
                if (!empty($modSettings['down_index_toprated']) && $modSettings['down_index_toprated_order'] == $x)
                    MainPageBlock($txt['downloads_main_toprated'], $x, 'toprated');
                    
            }
        }
    
        if ($modSettings['down_index_showleft']) {
            echo '<table width="90%" height="100%" border="0" align="center" cellpadding="0" cellspacing="0"><tr><td>';
            echo '<table width="150" border="0" align="left" cellpadding="0" cellspacing="0">';
            // echo '<table width="20%" border="0" align="left" cellpadding="0" cellspacing="0" class="tborder">';
        } else if ($modSettings['down_index_showright']) {
            echo '<table width="90%" height="100%" border="0" align="center" cellpadding="0" cellspacing="0"><tr><td>';
        }
        // Show the index page blocks
        if ($modSettings['down_index_showleft'])
        {
            for ($x = 1; $x < 6; $x++) {
                // Recent
                if (!empty($modSettings['down_index_recent']) && $modSettings['down_index_recent_order'] == $x)
                    MainPageBlock($txt['downloads_main_recent'], $x, 'recent');
                // Most Viewed
                if (!empty($modSettings['down_index_mostviewed']) && $modSettings['down_index_mostviewed_order'] == $x)
                    MainPageBlock($txt['downloads_main_viewed'], $x, 'viewed');
                // Most Downloaded
                if (!empty($modSettings['down_index_mostdownloaded']) && $modSettings['down_index_mostdownloaded_order'] == $x)
                    MainPageBlock('Top Downloads', $x, 'mostdownloaded');
                // Most commented
                if (!empty($modSettings['down_index_mostcomments']) && $modSettings['down_index_mostcomments_order'] == $x)
                    MainPageBlock($txt['downloads_main_mostcomments'], $x, 'mostcomments');
                // Top Rated
                if (!empty($modSettings['down_index_toprated']) && $modSettings['down_index_toprated_order'] == $x)
                    MainPageBlock($txt['downloads_main_toprated'], $x, 'toprated');
                    
            }
        }
            
        // List all the catagories
        
        if ($modSettings['down_index_showleft'] || $modSettings['down_index_showright'])
        {
echo '<table border="0" cellspacing="1" cellpadding="5" class="bordercolor" style="', ($modSettings['down_index_showleft'] ? 'float: right;' : 'float: left'), '" width="79%">';
        
        } else {
        
        echo '<table border="0" cellspacing="1" cellpadding="5" class="bordercolor" style="margin-top: 1px;" align="center" width="90%">';
        }
        
        
        
                echo '<tr class="titlebg">
                <td colspan="2">', $txt['downloads_text_categoryname'], '</td>
                <td align="center">', $txt['downloads_text_totalfiles'], '</td>
                ';
        if  ($g_manage)
            echo '
                <td>', $txt['downloads_text_reorder'], '</td>
                <td>', $txt['downloads_text_options'], '</td>';
                
        echo '</tr>';


        foreach ($context['downloads_cats'] as $i => $cat_info)
        {
            $cat_url = '';
            
            // Check permission to show this category
            if ($cat_info['view'] == '0')
                continue;
            

            $totalfiles  = GetFileTotals($cat_info['ID_CAT']);
            $cat_url = $scripturl . '?action=downloads;cat=' . $cat_info['ID_CAT'];
            
            echo '<tr>';
    
                if ($cat_info['image'] == '' && $cat_info['filename'] == '')
                    echo '<td ', ($subcats_linktree != '' ? 'rowspan="2"' : ''), 'class="windowbg"></td><td  class="windowbg2"><b><a href="' . $cat_url . '">' . parse_bbc($cat_info['title']) . '</a></b><br />' . parse_bbc($cat_info['description']) . '</td>';
                else
                {
                    if ($cat_info['filename'] == '')
                        echo '<td ', ($subcats_linktree != '' ? 'rowspan="2"' : ''), 'class="windowbg" width="10%"><a href="' . $cat_url . '"><img src="' . $cat_info['image'] . '" /></a></td>';
                    else 
                        echo '<td ', ($subcats_linktree != '' ? 'rowspan="2"' : ''), 'class="windowbg" width="10%"><a href="' . $cat_url . '"><img src="' . $modSettings['down_url'] . 'catimgs/' . $cat_info['filename'] . '" /></a></td>';

                        
                    echo '<td class="windowbg2"><b><a href="' . $cat_url . '">' . parse_bbc($cat_info['title']) . '</a></b><br />' . parse_bbc($cat_info['description']) . '</td>';
                }


    
            // Show total downloads in the category
            echo '<td align="center" valign="middle" class="windowbg">', $totalfiles, '</td>';

            // Show Edit Delete and Order category
            if ($g_manage)
            {
                echo '<td class="windowbg2"><a href="' . $scripturl . '?action=downloads;sa=catup;cat=' . $cat_info['ID_CAT'] . '">' . $txt['downloads_text_up'] . '</a>&nbsp;<a href="' . $scripturl . '?action=downloads;sa=catdown;cat=' . $cat_info['ID_CAT'] . '">' . $txt['downloads_text_down'] . '</a></td>
                <td class="windowbg"><a href="' . $scripturl . '?action=downloads;sa=editcat;cat=' . $cat_info['ID_CAT'] . '">' . $txt['downloads_text_edit'] . '</a>&nbsp;
                <a href="' . $scripturl . '?action=downloads;sa=deletecat;cat=' . $cat_info['ID_CAT'] . '">' . $txt['downloads_text_delete'] . '</a>
                <br /><br />
                    <a href="' . $scripturl . '?action=downloads;sa=catperm;cat=' . $cat_info['ID_CAT'] . '">[' . $txt['downloads_text_permissions'] . ']</a>&nbsp;';
                    // <a href="' . $scripturl . '?action=downloads;sa=catlayout;cat=' . $cat_info['ID_CAT'] . '">[' . $txt['downloads_text_layout'] . ']</a>
                echo '</td>';
                
            }


            echo '</tr>';
        
            // Show any subcategory links
            if ($subcats_linktree != '')
            echo '
            <tr class="windowbg3">
                <td colspan="', ($g_manage ? '4' : '2'),'">&nbsp;<span class="smalltext largepadding">',($subcats_linktree != '' ? '<b>' . $txt['downloads_sub_cats'] . '</b>' . $subcats_linktree : ''),'</span></td>
            </tr>';
    
            

        }
        echo '</td></tr></table>';
        
        
    // Show the index page blocks on the right
    if ($modSettings['down_index_showright'])
    {
    echo '<table width="150" border="0" align="right" cellpadding="0" cellspacing="0">';
    
    for ($x = 1; $x < 6; $x++) {
        // Recent
        if (!empty($modSettings['down_index_recent']) && $modSettings['down_index_recent_order'] == $x)
            MainPageBlock($txt['downloads_main_recent'], $x, 'recent');
        // Most Viewed
        if (!empty($modSettings['down_index_mostviewed']) && $modSettings['down_index_mostviewed_order'] == $x)
            MainPageBlock($txt['downloads_main_viewed'], $x, 'viewed');
        // Most Downloaded
        if (!empty($modSettings['down_index_mostdownloaded']) && $modSettings['down_index_mostdownloaded_order'] == $x)
            MainPageBlock('Top Downloads', $x, 'mostdownloaded');
        // Most commented
        if (!empty($modSettings['down_index_mostcomments']) && $modSettings['down_index_mostcomments_order'] == $x)
            MainPageBlock($txt['downloads_main_mostcomments'], $x, 'mostcomments');
        // Top Rated
        if (!empty($modSettings['down_index_toprated']) && $modSettings['down_index_toprated_order'] == $x)
            MainPageBlock($txt['downloads_main_toprated'], $x, 'toprated');
            
    }
    }
        echo '</td></tr></table><br /><br />';
            
    
    // Show the index page blocks
    if ($modSettings['down_index_showbottom'])
    {
        for ($x = 1; $x < 6; $x++) {
            // Recent
            if (!empty($modSettings['down_index_recent']) && $modSettings['down_index_recent_order'] == $x)
                MainPageBlock($txt['downloads_main_recent'], $x, 'recent');
            // Most Viewed
            if (!empty($modSettings['down_index_mostviewed']) && $modSettings['down_index_mostviewed_order'] == $x)
                MainPageBlock($txt['downloads_main_viewed'], $x, 'viewed');
            // Most Downloaded
            if (!empty($modSettings['down_index_mostdownloaded']) && $modSettings['down_index_mostdownloaded_order'] == $x)
                MainPageBlock('Top Downloads', $x, 'mostdownloaded');
            // Most commented
            if (!empty($modSettings['down_index_mostcomments']) && $modSettings['down_index_mostcomments_order'] == $x)
                MainPageBlock($txt['downloads_main_mostcomments'], $x, 'mostcomments');
            // Top Rated
            if (!empty($modSettings['down_index_toprated']) && $modSettings['down_index_toprated_order'] == $x)
                MainPageBlock($txt['downloads_main_toprated'], $x, 'toprated');
                
        }
    }
    
        // Show stats link  
            echo '<br /><table cellspacing="0" cellpadding="5" border="0" align="center" width="90%" class="tborder">
                    <tr class="titlebg">
                        <td align="center">' . $txt['downloads_stats_title'] . '</td>
                    </tr>
                    <tr class="windowbg2">
                        <td align="center"><a href="' . $scripturl . '?action=downloads;sa=stats">', $txt['downloads_stats_viewstats'] ,'</a></td>
                    </tr>
                </table><br />';            

        // See if they are allowed to add catagories Main Index only
        if ($g_manage)
        {
            echo '<table cellspacing="0" cellpadding="5" border="0" align="center" width="90%" class="tborder">
                <tr class="titlebg">
                    <td align="center">' . $txt['downloads_text_adminpanel'] . '</td>
                </tr>
                <tr class="windowbg2">
            <td align="center"><a href="' . $scripturl . '?action=downloads;sa=addcat">' . $txt['downloads_text_addcategory'] . '</a>&nbsp;
            <a href="' . $scripturl . '?action=downloads;sa=adminset">' . $txt['downloads_text_settings'] . '</a>&nbsp;';


            if (allowedTo('manage_permissions')) {
                echo '<a href="', $scripturl, '?action=permissions">', $txt['downloads_text_permissions'], '</a>';
            }
            // Downloads waiting for approval
            echo '<br />' . $txt['downloads_text_fileswaitapproval'] . '<b>',$context['downloads_waitapproval'],'</b>&nbsp;&nbsp;<a href="' . $scripturl . '?action=downloads;sa=approvelist">' . $txt['downloads_text_filecheckapproval'] . '</a>';
            // Reported Downloads
            echo '<br />' . $txt['downloads_text_filereported'] . '<b>',$context['downloads_totalreport'],'</b>&nbsp;&nbsp;<a href="' . $scripturl . '?action=downloads;sa=reportlist">' . $txt['downloads_text_filecheckreported'] . '</a>';
            // Total Comments Rating for Approval
            echo '<br />' . $txt['downloads_text_comwaitapproval'] . '<b>',$context['downloads_totalcom'], '</b>&nbsp;&nbsp;<a href="' . $scripturl . '?action=downloads;sa=commentlist">' . $txt['downloads_text_comcheckapproval'] . '</a>';
            // Total reported Comments
            echo '<br />' . $txt['downloads_text_comreported'] . '<b>' . $context['downloads_totalcreport'] . '</b>&nbsp;&nbsp;<a href="' . $scripturl . '?action=downloads;sa=commentlist">' . $txt['downloads_text_comcheckreported'] . '</a>';
            echo '</td></tr></table><br /><br />';
        }
    }


echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';

    downloads_copyright();


}
function template_add_category()
{
    global $scripturl, $txt, $context, $settings, $modSettings;
        
    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '
                                    <script language="JavaScript" type="text/javascript" src="', $settings['default_theme_url'], '/spellcheck.js"></script>';


    echo '
<form method="post" enctype="multipart/form-data" name="catform" id="catform" action="' . $scripturl . '?action=downloads;sa=addcat2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>', $txt['downloads_text_addcategory'], '</b></td>
  </tr>
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_text_parentcategory'] .'</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><select name="parent">
    <option value="0">',$txt['downloads_text_catnone'],'</option>
    ';
     
    foreach ($context['downloads_cat'] as $i => $category)
        echo '<option value="' . $category['ID_CAT']  . '" ' . (($context['cat_parent'] == $category['ID_CAT']) ? ' selected="selected"' : '') .'>' . $category['title'] . '</option>';
    
    echo '</select>
    </td>
  </tr>  
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_title'] .'</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><input type="text" name="title" size="64" maxlength="100" /></td>
  </tr>
  <tr>
    <td width="28%"  valign="top" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_description'] . '</b>&nbsp;</span><br />'. $txt['downloads_text_bbcsupport'] .'</td>
    <td width="72%"  class="windowbg2">
      <table>
   ';
   theme_postbox('');
   echo '</table>';

    if ($context['show_spellchecking'])
        echo '
                                    <br /><input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'catform\', \'description\');" />';
echo '</td>
  </tr>
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_icon'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><input type="text" name="image" size="64" maxlength="100" /></td>
  </tr>
   <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_uploadicon'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2">';
 
            
        // Warn the user if the category image path is not writable
        if (!is_writable($modSettings['down_path'] . 'catimgs'))
            echo '<font color="#FF0000"><b>' . $txt['downloads_write_catpatherror']  . $modSettings['down_path'] . 'catimgs' . '</b></font>';

    
echo '
    <input type="file" size="48" name="picture" /></td>
  </tr>
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_text_cat_disableratings'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><input type="checkbox" name="disablerating" /></td>
  </tr>
  
  <tr>
    <td width="28%" class="windowbg2" align="right">
        <span class="gen"><b>Layout:</b>&nbsp;</span>
    </td>
    <td width="72%" class="windowbg2">
        <select name="layout">
            <option value="0"', ($modSettings['down_set_cat_layout'] == 0 ? ' selected' : ''), '>' . $txt['downloads_text_layout_list'] . '</option>
            <option value="1"', ($modSettings['down_set_cat_layout'] == 1 ? ' selected' : ''), '>' . $txt['downloads_text_layout_tables'] . '</option>
            <option value="2"', ($modSettings['down_set_cat_layout'] == 2 ? ' selected' : ''), '>' . $txt['downloads_text_layout_full'] . '</option>
        </select>
    </td>
  </tr> 
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_txt_sortby']  . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><select name="sortby">
        <option value="date">',$txt['downloads_txt_sort_date'],'</option>
        <option value="title">',$txt['downloads_txt_sort_title'],'</option>
        <option value="mostview">',$txt['downloads_txt_sort_mostviewed'],'</option>
        <option value="mostcom">',$txt['downloads_txt_sort_mostcomments'],'</option>
        <option value="ratings">',$txt['downloads_txt_sort_mostrated'],'</option>
        <option value="mostdowns">',$txt['downloads_txt_sort_mostdowns'],'</option>
        <option value="filesize">',$txt['downloads_txt_sort_filesize'],'</option>
        <option value="membername">',$txt['downloads_txt_sort_membername'],'</option>
        </select></td>
  </tr>  
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_txt_orderby'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><select name="orderby">
        <option value="desc">',$txt['downloads_txt_sort_desc'],'</option>
        <option value="asc">',$txt['downloads_txt_sort_asc'],'</option>
        </select></td>
  </tr>  
    <tr class="windowbg2">
    <td align="right"><b>', $txt['category_type'], '</b>&nbsp;</td>
    <td><select name="cat_type" size="7" />
        <option value="PluginMusDir">', $txt['PluginMusDir'], '</option>
        <option value="PluginPictDir">', $txt['PluginPictDir'], '</option>
        <option value="PluginProgDir">', $txt['PluginProgDir'], '</option>
        <option value="PluginVidDir">', $txt['PluginVidDir'], '</option>
        <option value="ScriptsDir">', $txt['ScriptsDir'], '</option>
        <option value="ThemesDir">', $txt['ThemesDir'], '</option>
        <option value="Other">', $txt['Other'], '</option>
        </select>
  </tr>

  <tr>
    <td colspan="2" class="windowbg2" align="center">
    <b>' . $txt['downloads_text_postingoptions'] . '</b>
    <hr />
    ' . $txt['downloads_postingoptions_info'] . '
    </td>
  </tr>
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_text_boardname'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"> 
    <select name="boardselect" id="boardselect">
  ';

    foreach ($context['downloads_boards'] as $key => $option)
         echo '<option value="' . $key . '">' . $option . '</option>';

echo '</select>
    </td>
  </tr>
   <tr>
    <td colspan="2" height="22" class="windowbg2" align="center">
    <input type="checkbox" name="locktopic" /><span class="gen"><b>' . $txt['downloads_posting_locktopic'] . '</b>&nbsp;</span>
    </td>
  </tr>
   <tr>
    <td colspan="2" class="windowbg2"><hr /></td>
  </tr>
  <tr>
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    <input type="submit" value="', $txt['downloads_text_addcategory'], '" name="submit" /></td>

  </tr>
</table>
</form>';

    if ($context['show_spellchecking'])
            echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" name="spellstring" value="" /></form>';
    

    downloads_copyright();

}
function template_edit_category()
{
    global $scripturl, $txt, $context, $settings, $modSettings;

    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '<script language="JavaScript" type="text/javascript" src="', $settings['default_theme_url'], '/spellcheck.js"></script>';


    echo '
<form method="post" enctype="multipart/form-data" name="catform" id="catform" action="', $scripturl, '?action=downloads;sa=editcat2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>', $txt['downloads_text_editcategory'], '</b></td>
  </tr>
    <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>', $txt['downloads_text_parentcategory'], '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><select name="parent">
    <option value="0">', $txt['downloads_text_catnone'], '</option>
    ';
     
        foreach ($context['downloads_cat'] as $i => $category)
        {
            echo '<option value="' . $category['ID_CAT']  . '" ' . (($context['down_catinfo']['ID_PARENT'] == $category['ID_CAT']) ? ' selected="selected"' : '') .'>' . $category['title'] . '</option>';
        }

    echo '</select>
    </td>
  </tr>
<tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>', $txt['downloads_form_title'], '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><input type="text" name="title" size="64" maxlength="100" value="', $context['down_catinfo']['title'], '" /></td>
  </tr>
  <tr>
    <td width="28%"  valign="top" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_description'] . '</b>&nbsp;</span><br />' . $txt['downloads_text_bbcsupport'] . '</td>
    <td width="72%"  class="windowbg2">
      <table>
   ';
   theme_postbox($context['down_catinfo']['description'] );
   echo '</table>
    ';

    if ($context['show_spellchecking'])
        echo '
                                    <br /><input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'catform\', \'description\');" />';
echo '</td>
  </tr>
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_icon'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><input type="text" name="image" size="64" maxlength="100" value="' . $context['down_catinfo']['image'] . '" /></td>
  </tr>
   <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_uploadicon'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2">';
   

        // Warn the user if the category image path is not writable
    if (!is_writable($modSettings['down_path'] . 'catimgs'))
            echo '<font color="#FF0000"><b>' . $txt['downloads_write_catpatherror']  . $modSettings['down_path'] . 'catimgs' . '</b></font>';

    
echo '
    <input type="file" size="48" name="picture" /></td>
  </tr>';

if ($context['down_catinfo']['filename'] != '')
echo '
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_form_filenameicon'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2">' . $context['down_catinfo']['filename'] .  '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=catimgdel;id=' . $context['down_catinfo']['ID_CAT'] . '">' . $txt['downloads_rep_deletefile'] . '</a></td>
  </tr>'; 
 
        
        $sortselect = '';
        $orderselect = '';

            switch ($context['down_catinfo']['sortby'])
            {
                case 'p.ID_FILE':
                    $sortselect = '<option value="date">' . $txt['downloads_txt_sort_date'] . '</option>';
                    
                break;
                case 'p.title':
                    $sortselect = '<option value="title">' . $txt['downloads_txt_sort_title'] . '</option>';
                break;
                
                case 'p.views':
                    $sortselect = '<option value="mostview">' . $txt['downloads_txt_sort_mostviewed']  . '</option>';
                break;
                
                case 'p.commenttotal':
                    $sortselect = '<option value="mostcom">' . $txt['downloads_txt_sort_mostcomments'] . '</option>';
                break;

                case 'p.actual_rating':
                    $sortselect = '<option value="ratings">' . $txt['downloads_txt_sort_mostrated'] . '</option>';
                break;
                
                case 'p.rating':
                    $sortselect = '<option value="ratings">' . $txt['downloads_txt_sort_mostrated'] . '</option>';
                break;

                case 'p.totalratings':
                    $sortselect = '<option value="mostrated">' . $txt['downloads_txt_sort_mostrated'] . '</option>';
                break;
                
                case 'p.totaldownloads':
                    $sortselect = '<option value="mostdowns">' . $txt['downloads_txt_sort_mostdowns'] . '</option>';
                break;
                
                case 'p.filesize':
                    $sortselect = '<option value="filesize">' . $txt['downloads_txt_sort_filesize'] . '</option>';
                break;
                
                case 'm.realname':
                    $sortselect = '<option value="membername">' . $txt['downloads_txt_sort_membername'] . '</option>';
                break;          
                
                default:
                    $sortselect = '<option value="date">' . $txt['downloads_txt_sort_date'] . '</option>';
                break;
            }
            


            switch ($context['down_catinfo']['orderby'])
            {
                case 'ASC':
                    $orderselect = '<option value="asc">' .$txt['downloads_txt_sort_asc'] .'</option>';
                    
                break;
                case 'DESC':
                    $orderselect = '<option value="desc">' . $txt['downloads_txt_sort_desc'] . '</option>';
                break;
                
                default:
                    $orderselect = '<option value="DESC">' . $txt['downloads_txt_sort_desc'] .' </option>';
                break;
            }
            

    
    echo '
      <tr>
        <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_text_cat_disableratings'] . '</b>&nbsp;</span></td>
        <td width="72%" height="22" class="windowbg2"><input type="checkbox" name="disablerating" ' . ($context['down_catinfo']['disablerating'] ? ' checked="checked"' : '') . ' /></td>
      </tr> 
  <tr>
    <td width="28%" class="windowbg2" align="right">
        <span class="gen"><b>Layout:</b>&nbsp;</span>
    </td>
    <td width="72%" class="windowbg2">
        <select name="layout">
            <option value="0"', ($context['down_catinfo']['layout'] == 0 ? ' selected' : ''), '>' . $txt['downloads_text_layout_list'] . '</option>
            <option value="1"', ($context['down_catinfo']['layout'] == 1 ? ' selected' : ''), '>' . $txt['downloads_text_layout_tables'] . '</option>
            <option value="2"', ($context['down_catinfo']['layout'] == 2 ? ' selected' : ''), '>' . $txt['downloads_text_layout_full'] . '</option>
        </select>
    </td>
  </tr> 
<tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_txt_sortby']  . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><select name="sortby">
        ',$sortselect,'
        <option value="date">',$txt['downloads_txt_sort_date'],'</option>
        <option value="title">',$txt['downloads_txt_sort_title'],'</option>
        <option value="mostview">',$txt['downloads_txt_sort_mostviewed'],'</option>
        <option value="mostcom">',$txt['downloads_txt_sort_mostcomments'],'</option>
        <option value="ratings">',$txt['downloads_txt_sort_mostrated'],'</option>
        <option value="mostdowns">',$txt['downloads_cat_downloads'],'</option>
        <option value="filesize">',$txt['downloads_cat_filesize'],'</option>
        <option value="membername">',$txt['downloads_cat_membername'],'</option>
        </select></td>
  </tr>  
  <tr>
    <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' .   $txt['downloads_txt_orderby'] . '</b>&nbsp;</span></td>
    <td width="72%" height="22" class="windowbg2"><select name="orderby">
        ',$orderselect,'
        <option value="desc">',$txt['downloads_txt_sort_desc'],'</option>
        <option value="asc">',$txt['downloads_txt_sort_asc'],'</option>
        </select></td>
  </tr>  
    <tr class="windowbg2">
    <td align="right"><b>', $txt['category_type'], '</b>&nbsp;</td>
    <td><select name="cat_type" size="7" />
        <option value="PluginMusDir">', $txt['PluginMusDir'], '</option>
        <option value="PluginPictDir">', $txt['PluginPictDir'], '</option>
        <option value="PluginProgDir">', $txt['PluginProgDir'], '</option>
        <option value="PluginVidDir">', $txt['PluginVidDir'], '</option>
        <option value="ScriptsDir">', $txt['ScriptsDir'], '</option>
        <option value="ThemesDir">', $txt['ThemesDir'], '</option>
        <option value="Other">', $txt['Other'], '</option>
        </select>
  </tr>     
      <tr>
        <td colspan="2" class="windowbg2" align="center">
        <b>' . $txt['downloads_text_postingoptions'] . '</b>
        <hr />
        ' . $txt['downloads_postingoptions_info'] . '
        </td>
      </tr>
      <tr>
        <td width="28%" height="22" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_text_boardname'] . '</b>&nbsp;</span></td>
        <td width="72%" height="22" class="windowbg2"> 
        <select name="boardselect" id="boardselect">
      ';
    
        foreach ($context['downloads_boards'] as $key => $option)
             echo '<option value="' . $key . '"' . (($context['down_catinfo']['ID_BOARD']==$key) ? ' selected="selected"' : '') . '>' . $option . '</option>';
    
    echo '</select>
        </td>
      </tr>
       <tr>
        <td colspan="2" height="22" class="windowbg2" align="center">
    <input type="checkbox" name="locktopic" ' . ($context['down_catinfo']['locktopic'] ? ' checked="checked"' : '') . ' /><span class="gen"><b>' . $txt['downloads_posting_locktopic'] . '</b>&nbsp;</span>
        </td>
      </tr>
   <tr>
    <td colspan="2" class="windowbg2"><hr /></td>
  </tr>
  <tr>
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    <input type="hidden" value="' . $context['down_catinfo']['ID_CAT'] . '" name="catid" />
    <input type="submit" value="' . $txt['downloads_text_editcategory'] . '" name="submit" /></td>

  </tr>
</table>
</form><br />';



    echo'
    <hr />
  <div align="center">
  <b>',  $txt['downloads_custom_fields'],'</b><br />
    <form method="post" action="', $scripturl, '?action=downloads;sa=cusadd">
    ', $txt['downloads_custom_title'], '<input type="text" name="title" />
    ', $txt['downloads_custom_default_value'], '<input type="text" name="defaultvalue" />
    <input type="hidden" name="id" value="',$context['down_catinfo']['ID_CAT'],'" />
    <input type="checkbox" name="required" />', $txt['downloads_custom_required'], ' 
    <input type="submit" name="addfield" value="',$txt['downloads_custom_addfield'],'" />
    </form>
    </div><br />
    
     <table cellspacing="0" cellpadding="4" border="0" align="center" class="tborder">
        <tr>
            <td class="titlebg">', $txt['downloads_custom_title'], '</td>
            <td class="titlebg">', $txt['downloads_custom_default_value'], '</td>
            <td class="titlebg">', $txt['downloads_custom_required'], '</td>
            <td class="titlebg">', $txt['downloads_text_options'], '</td>
        </tr>
     ';
  
    
    // Get all the custom fields
    foreach ($context['down_custom'] as $i => $custom)
    {
        echo '<tr>
            <td class="windowbg2">', $custom['title'], '</td>
            <td class="windowbg2">', $custom['defaultvalue'], '</td>
            <td class="windowbg2">', ($custom['is_required'] ? 'TRUE' : 'FALSE'), '</td>
            <td class="windowbg2"><a href="' . $scripturl . '?action=downloads;sa=cusup;id=' . $custom['ID_CUSTOM'] . '">' . $txt['downloads_text_up'] . '</a>&nbsp;<a href="' . $scripturl . '?action=downloads;sa=cusdown;id=' . $custom['ID_CUSTOM'] . '">' . $txt['downloads_text_down'] . '</a>
            &nbsp;&nbsp;<a href="' . $scripturl . '?action=downloads;sa=cusdelete;id=' . $custom['ID_CUSTOM'] . '">' . $txt['downloads_text_delete'] . '</a>
            </td>
        </tr>
     ';
    }


  
echo '</table>
    <br />
    <br />
    <div align="center">
    <a href="', $scripturl, '?action=downloads">', $txt['downloads_text_returndownload'], '</a>
    </div>
';


    if ($context['show_spellchecking'])
            echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" name="spellstring" value="" /></form>';
    


    downloads_copyright();

}
function template_delete_category()
{
    global $context, $scripturl, $txt;

    echo '
    <form method="post" action="' . $scripturl . '?action=downloads&sa=deletecat2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>' . $txt['downloads_text_delcategory'] . '</b></td>
  </tr>
  <tr>
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    <b>' . $txt['downloads_warn_category'] . '</b>
    <br />
    <i>' . $txt['downloads_text_categoryname'] . '&nbsp;"' . $context['cat_title'] . '"&nbsp;' . $txt['downloads_text_totalfiles'] . '&nbsp;' . $context['totalfiles'] . '</i>
     <br />
    <input type="hidden" value="' . $context['catid'] . '" name="catid" />
    <input type="submit" value="' . $txt['downloads_text_delcategory'] . '" name="submit" /></td>
  </tr>
</table>
</form>';
    
    downloads_copyright();
}
function template_add_download()
{
    global $scripturl, $modSettings, $txt, $context, $settings;

    // Get the category
    $cat = $context['down_cat'];


    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '<script language="JavaScript" type="text/javascript" src="', $settings['default_theme_url'], '/spellcheck.js"></script>';

    echo '<script type="text/javascript" src="http://passion-xbmc.org/Themes/default/ts_picker.js">
    //Script by Denis Gritcyuk: tspicker@yahoo.com
    //Submitted to JavaScript Kit (http://javascriptkit.com)
    //Visit http://javascriptkit.com for this script
    </script>';
    
    echo '<form method="post" enctype="multipart/form-data" name="picform" id="picform" action="' . $scripturl . '?action=downloads&sa=add2">
<table border="0" cellpadding="3" cellspacing="0" width="100%">
  <tr class="catbg">
    <td width="50%" colspan="2"  align="center">
    <b>', $txt['downloads_form_adddownload'], '</b></td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_category'] . '</b>&nbsp;</td>
    <td><select name="cat">';

    foreach ($context['downloads_cat'] as $i => $category)
    {
        echo '<option value="' . $category['ID_CAT']  . '" ' . (($cat == $category['ID_CAT']) ? ' selected="selected"' : '') .'>' . $category['title'] . '</option>';
    }

 echo '</select>
    </td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_title'] . '</b>&nbsp;</td>
    <td><input type="text" name="title" size="50" /></td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_description'] . '</b>&nbsp;</td>
    <td>
   <tr>
   <td class="windowbg2" colspan="2" align="center">
   <table>
   ';
   theme_postbox('');
   echo '</table>';

        if ($context['show_spellchecking'])
            echo '
                                        <br /><input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'picform\', \'description\');" />';

echo '
    </td>
  </tr>


  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_form_keywords'], '</b>&nbsp;</td>
    <td><input type="text" name="keywords" maxlength="100" size="50" /></td>
  </tr>


   <tr class="windowbg2" align="left">
   <td class="windowbg2" align="right" valign="top" style="padding-top: 5px;">
                    <span class="gen"><b>Upload Screenshot:</b>&nbsp;</span>
   </td>
   <td class="windowbg2" align="left">
        <table cellspacing="0" cellpadding="0" border="0" align="left">
            <tr>
                <td align="left">';
                    // Warning if the Screenshots image path is not writable
                    if (!is_writable($modSettings['down_path'] . 'screenshots'))
                        echo '<font color="#FF0000"><b>Warning Screenshots Image Path is not writable! '  . $modSettings['down_path'] . 'screenshots' . '</b></font>';
 
                    echo '
                        <input type="file" size="48" name="picture" />
                </td>
            </tr>
            <tr>
                <td align="left" height="20" width="100%" class="smalltext" style="padding: 2px;">
                    <input type="checkbox" name="reflection" />&nbsp;<b style="font-size: 12px;">Add Reflection</b> <b style="font-size: 10px;">(Thumbnails do not get reflections)</b><br/>';

                    if (!empty($modSettings['down_set_file_ss_width']) || !empty($modSettings['down_set_file_ss_height'])) {
                        echo 'If image dimensions exceed '; 
                            if (!empty($modSettings['down_set_file_ss_width'])) {
                                echo 'a Width of <b>' . $modSettings['down_set_file_ss_width'] . '</b>px';
                                if (!empty($modSettings['down_set_file_ss_height']))
                                    echo ' and/or a Height of <b>' . $modSettings['down_set_file_ss_height'] . '</b>px';
                                // else
                                //  echo ' &amp; Height: Unlimited)';
                                    
                            } else if (!empty($modSettings['down_set_file_ss_height'])) {
                                // echo '(Width: Unlimited';
                                echo 'a Height of <b>' . $modSettings['down_set_file_ss_height'] . '</b>px';
                            } // else
                                // echo 'none';
                            echo ', it will be resized.<br/>';
                    }
                            
                            echo 'Supported Formats: (png, gif, jpg, jpeg, bmp, wbmp)
                </td>
            </tr>
        </table>    
    </td>
  </tr>

<tr class="windowbg2">
    <td class="windowbg2" align="right" valign="top" style="padding-top: 5px;">
        <b>', $txt['downloads_form_uploadfile'], '</b>&nbsp;
    </td>
    <td class="windowbg2" align="left">
        <table cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td align="left" width="100%">
                    <input type="file" size="48" name="download" />
                </td>
            </tr>
            <tr>
                <td align="left" height="20" width="100%" class="smalltext">
                    <b>Max Filesize</b>: ', format_size($modSettings['down_max_filesize'], 2), '
                </td>
            </tr>
        </table>
    </td>
</tr>


   <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_form_uploadurl'], '</b>&nbsp;</td>
    <td><input type="text" name="fileurl" size="50" />
  </tr>
  <tr>
    <td colspan="2" class="windowbg2"><hr /></td>
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_createdate'], '</b>&nbsp;</td>
    <td><input type="text" name="createdate" size="10" />  ', $txt['downloads_custom_createdate_com'], '</td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_version'], '</b>&nbsp;</td>
    <td><input type="text" name="version" size="15" />
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_author'], '</b>&nbsp;</td>
    <td><input type="text" name="author" size="50" />
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_script_language'], '</b>&nbsp;</td>
    <td><select name="script_language[]" multiple size="3" />
        <option value="fr">', $txt['downloads_custom_script_language_fr'], '</option>
        <option value="en">', $txt['downloads_custom_script_language_en'], '</option>
        <option value="de">', $txt['downloads_custom_script_language_de'], '</option>
        <option value="nl">', $txt['downloads_custom_script_language_nl'], '</option>
        </select>
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_description_en'], '</b>&nbsp;</td>
    <td><textarea name="description_en" rows="12" cols="60" /></textarea>
  </tr>


  <tr>
    <td colspan="2" class="windowbg2"><hr /></td>
  </tr>';

    
    foreach ($context['downloads_custom'] as $i => $custom)
    {
        echo '<tr>
            <td class="windowbg2" align="right"><b>', $custom['title'], ($custom['is_required'] ? '<font color="#FF0000">*</font>' : ''), '</b></td>
            <td class="windowbg2"><input type="text" name="cus_', $custom['ID_CUSTOM'],'" value="' , $custom['defaultvalue'], '" /></td>
    
        </tr>
     ';
    }
    
  
    echo '
       <tr class="windowbg2">
        <td align="right"><b>' . $txt['downloads_form_additionaloptions'] . '</b>&nbsp;</td>
        <td><input type="checkbox" name="sendemail" checked="checked" /><b>' . $txt['downloads_notify_title'] .'</b>
      </tr>
  ';
 
  if ($modSettings['down_commentchoice'])
  {
    echo '
       <tr class="windowbg2">
        <td align="right">&nbsp;</td>
        <td><input type="checkbox" name="allowcomments" checked="checked" /><b>' . $txt['downloads_form_allowcomments'] .'</b>
      </tr>';
  }
  
  // Display the file quota information
  if ($context['quotalimit'] != 0)
  {
    echo '
       <tr class="windowbg2">
        <td align="right">',$txt['downloads_quotagrouplimit'],'&nbsp;</td>
        <td>',format_size($context['quotalimit'], 2),'</td>
      </tr>
       <tr class="windowbg2">
        <td align="right">',$txt['downloads_quotagspaceused'],'&nbsp;</td>
        <td>',format_size($context['userspace'], 2),'</td>
      </tr>
       <tr class="windowbg2">
        <td align="right">',$txt['downloads_quotaspaceleft'],'&nbsp;</td>
        <td><b>' . format_size(($context['quotalimit']-$context['userspace']), 2) . '</b></td>
      </tr>   
      
      ';
  }

echo '
  <tr class="windowbg2">
    <td width="28%" colspan="2"  align="center" class="windowbg2">

    <input type="submit" value="', $txt['downloads_form_adddownload'], '" name="submit" /><br />';

    if (!allowedTo('downloads_autoapprove'))
        echo $txt['downloads_form_notapproved'];

echo '
    </td>
  </tr>
</table>

        </form>
';

    if ($context['show_spellchecking'])
            echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" name="spellstring" value="" /></form>';


}

function template_edit_download()
{
    global $scripturl, $modSettings, $txt, $context, $settings;

    $g_manage = allowedTo('downloads_manage');
    

    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '
                                    <script language="JavaScript" type="text/javascript" src="', $settings['default_theme_url'], '/spellcheck.js"></script>';


    echo '<form method="post" enctype="multipart/form-data" name="picform" id="picform" action="' . $scripturl . '?action=downloads&sa=edit2">
<table border="0" cellpadding="3" cellspacing="0" width="100%">
  <tr class="catbg">
    <td width="50%" colspan="2"  align="center">
    <b>', $txt['downloads_form_editdownload'], '</b></td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_category'] . '</b>&nbsp;</td>
    <td><select name="cat">';

    foreach ($context['downloads_cat'] as $i => $category)
    {
        echo '<option value="' . $category['ID_CAT']  . '" ' . (($context['downloads_file']['ID_CAT'] == $category['ID_CAT']) ? ' selected="selected"' : '') .'>' . $category['title'] . '</option>';
    }


 echo '</select>
    </td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_title'] . '</b>&nbsp;</td>
    <td><input type="text" name="title" size="50" value="' . $context['downloads_file']['title'] . '" /></td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_description'] . '</b>&nbsp;</td>
    <td>
    
   <tr>
   <td class="windowbg2" colspan="2" align="center">
   <table>
   ';
   theme_postbox($context['downloads_file']['description']);
   echo '</table>
  ';

        if ($context['show_spellchecking'])
            echo '
                                        <br /><input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'picform\', \'description\');" />';



echo '
    </td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>' . $txt['downloads_form_keywords'] . '</b>&nbsp;</td>
    <td><input type="text" name="keywords" size="50" maxlength="100" value="' . $context['downloads_file']['keywords'] . '" />
  </tr>
  <tr class="windowbg2">
       <td class="windowbg2" align="right" valign="top" style="padding-top: 5px;">
                    <span class="gen"><b>Upload Screenshot:</b>&nbsp;</span>
       </td>
       <td class="windowbg2" align="left">
            <table cellspacing="0" cellpadding="0" border="0" align="left">
                <tr>
                    <td align="left">';
                    // Warning if the Screenshots image path is not writable
                    if (!is_writable($modSettings['down_path'] . 'screenshots'))
                        echo '<font color="#FF0000"><b>Warning Screenshots Image Path is not writable! '  . $modSettings['down_path'] . 'screenshots' . '</b></font>';
                    if (!is_writable($modSettings['down_path'] . 'screenshots/thumbs'))
                        echo '<font color="#FF0000"><b>Warning Screenshots Thumbnail Image Path is not writable! '  . $modSettings['down_path'] . 'screenshots/thumbs' . '</b></font>';
 
                    echo '
                        <input type="file" size="48" name="picture" />
                    </td>
                </tr>
                <tr>
                <td align="left" height="20" class="smalltext" style="padding: 2px;">
                    <input type="checkbox" name="reflection" />&nbsp;<b style="font-size: 12px;">Add Reflection</b> <b style="font-size: 10px;">(Thumbnails do not get reflections)</b><br/>';

                    if (!empty($modSettings['down_set_file_ss_width']) || !empty($modSettings['down_set_file_ss_height'])) {
                        echo 'If image dimensions exceed '; 
                            if (!empty($modSettings['down_set_file_ss_width'])) {
                                echo 'a Width of <b>' . $modSettings['down_set_file_ss_width'] . '</b>px';
                                if (!empty($modSettings['down_set_file_ss_height']))
                                    echo ' and/or a Height of <b>' . $modSettings['down_set_file_ss_height'] . '</b>px';
                                // else
                                //  echo ' &amp; Height: Unlimited)';
                                    
                            } else if (!empty($modSettings['down_set_file_ss_height'])) {
                                // echo '(Width: Unlimited';
                                echo 'a Height of <b>' . $modSettings['down_set_file_ss_height'] . '</b>px';
                            } // else
                                // echo 'none';
                            echo ', it will be resized.<br/>';
                    }
                            
                            echo 'Supported Formats: (png, gif, jpg, jpeg, bmp, wbmp)
                </td>
                </tr>
            </table>    
        </td>
  </tr>

  <tr class="windowbg2">
    <td class="windowbg2" align="right" valign="top" style="padding-top: 5px;">
        <b>', $txt['downloads_form_uploadfile'], '</b>&nbsp;
    </td>
    <td class="windowbg2" align="left">
        <table cellspacing="0" cellpadding="0" border="0" align="left">
            <tr>
                <td align="left">
                    <input type="file" size="48" name="download" />
                </td>
            </tr>
            <tr>
                <td align="left" height="20" class="smalltext">
                    <b>Max Filesize</b>: ', format_size($modSettings['down_max_filesize'], 2), '
                </td>
            </tr>
        </table>
    </td>
  </tr> 
  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_createdate'], '</b>&nbsp;</td>
    <td><input type="text" name="createdate" size="10" />  ', $txt['downloads_custom_createdate_com'], '</td>
  </tr>
  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_version'], '</b>&nbsp;</td>
    <td><input type="text" name="version" size="15" />
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_author'], '</b>&nbsp;</td>
    <td><input type="text" name="author" size="50" />
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_script_language'], '</b>&nbsp;</td>
    <td><select name="script_language[]" multiple size="3" />
        <option value="fr">', $txt['downloads_custom_script_language_fr'], '</option>
        <option value="en">', $txt['downloads_custom_script_language_en'], '</option>
        <option value="de">', $txt['downloads_custom_script_language_de'], '</option>
        <option value="nl">', $txt['downloads_custom_script_language_nl'], '</option>
        </select>
  </tr>

  <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_custom_description_en'], '</b>&nbsp;</td>
    <td><textarea name="description_en" rows="12" cols="60" /></textarea>
  </tr>

   <tr class="windowbg2">
    <td align="right"><b>', $txt['downloads_form_uploadurl'], '</b>&nbsp;</td>
    <td><input type="text" name="fileurl" size="50" value="' . $context['downloads_file']['fileurl'] . '" />
  </tr>';


  if ($context['downloads_file']['screenshot'] != '') {
  echo '<tr>
           <td class="windowbg2" align="right"><span class="gen"><b>Current Screenshot:</b>&nbsp;</span></td>
           <td class="windowbg2"><a href="' . $scripturl . '?action=downloads;sa=filessdel;id=' . $context['downloads_file']['ID_FILE'] . '">[Remove Screenshot]</a></td>
         </tr>'; 
  }


   echo '<tr>
    <td colspan="2" class="windowbg2"><hr /></td>
  </tr>';

    foreach ($context['downloads_custom'] as $i => $custom)
    {
        echo '<tr>
            <td class="windowbg2" align="right"><b>', $custom['title'], ($custom['is_required'] ? '<font color="#FF0000">*</font>' : ''), '</b></td>
            <td class="windowbg2"><input type="text" name="cus_', $custom['ID_CUSTOM'],'" value="' , $custom['value'], '" /></td>
    
        </tr>';
    }

 
 echo '
       <tr class="windowbg2">
        <td align="right"><b>' . $txt['downloads_form_additionaloptions'] . '</b>&nbsp;</td>
        <td><input type="checkbox" name="sendemail" ' . ($context['downloads_file']['sendemail'] ? 'checked="checked"' : '' ) . ' /><b>' . $txt['downloads_notify_title'] .'</b>
      </tr>';

  if ($modSettings['down_commentchoice'])
  {
    echo '
       <tr class="windowbg2">
        <td align="right">&nbsp;</td>
        <td><input type="checkbox" name="allowcomments" ' . ($context['downloads_file']['allowcomments'] ? 'checked="checked"' : '' ) . ' /><b>',$txt['downloads_form_allowcomments'],'</b>
      </tr>';
  }
  
  // If the user can manage the downloads give them the option to change the download owner.
  if ($g_manage == true)
  {
      echo '<tr class="windowbg2">
      <td align="right">', $txt['downloads_text_changeowner'], '</td>
      <td><input type="text" name="pic_postername" id="pic_postername" value="" />
      <a href="', $scripturl, '?action=findmember;input=pic_postername;quote=1;sesc=', $context['session_id'], '" onclick="return reqWin(this.href, 350, 400);"><img src="', $settings['images_url'], '/icons/assist.gif" alt="', $txt['find_members'], '" /></a> 
      <a href="', $scripturl, '?action=findmember;input=pic_postername;quote=1;sesc=', $context['session_id'], '" onclick="return reqWin(this.href, 350, 400);">', $txt['find_members'], '</a>
      </td>
      </tr>
      ';
  }

  
  // Display the file quota information
  if ($context['quotalimit'] != 0)
  {
    echo '
       <tr class="windowbg2">
        <td align="right">',$txt['downloads_quotagrouplimit'],'&nbsp;</td>
        <td>',format_size($context['quotalimit'], 2),'</td>
      </tr>
       <tr class="windowbg2">
        <td align="right">',$txt['downloads_quotagspaceused'],'&nbsp;</td>
        <td>',format_size($context['userspace'], 2),'</td>
      </tr>
       <tr class="windowbg2">
        <td align="right">',$txt['downloads_quotaspaceleft'],'&nbsp;</td>
        <td><b>', format_size(($context['quotalimit']-$context['userspace']), 2), '</b></td>
      </tr>   
      
      ';
  }

echo '
  <tr class="windowbg2">
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    <input type="hidden" name="id" value="' . $context['downloads_file']['ID_FILE'] . '" />
    <input type="submit" value="' . $txt['downloads_form_editdownload'] . '" name="submit" /><br />';

    if (!allowedTo('downloads_autoapprove'))
        echo $txt['downloads_form_notapproved'];

echo '<div align="center"><br /><b>' . $txt['downloads_text_olddownload'] . '</b><br />
' . $context['downloads_file']['orginalfilename'] . '<br />
            <span class="smalltext">' . $txt['downloads_text_views']  . $context['downloads_file']['views'] . '<br />
            ' . $txt['downloads_text_filesize']  . format_size($context['downloads_file']['filesize'],2) . '<br />
            ' . $txt['downloads_text_date'] . $context['downloads_file']['date'] . '<br />
    </div>
    </td>
  </tr>
</table>

        </form>
';

    if ($context['show_spellchecking'])
            echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" name="spellstring" value="" /></form>';

}


function template_view_download()
{
    global $scripturl, $context, $txt, $modSettings, $settings, $memberContext, $ID_MEMBER;

    // Load permissions
    $g_manage = allowedTo('downloads_manage');
    $g_edit_own = allowedTo('downloads_edit');
    $g_delete_own = allowedTo('downloads_delete');
    $g_edit_comment = allowedTo('downloads_editcomment');
    $g_report = allowedTo('downloads_report');


    // Keywords
    $keywords = explode(' ',$context['downloads_file']['keywords']);
    $keywordscount = count($keywords);
    
 echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';


            echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">&nbsp;</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';

    echo '<br /><table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">';
    
        // Show the title of the download
        if ($modSettings['down_set_file_title'])
            echo '<tr class="catbg">
                <td align="center">', $context['downloads_file']['title'], '</td>
            </tr>';
            
        
        // Show the main download
        echo '
            <tr class="windowbg2">
                <td align="center">';
        
                    echo '<a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $context['downloads_file']['ID_FILE'], '"><img src="', $settings['images_url'], '/download-image.png"  /></a>';
            echo '
                </td>
            </tr>';
            
        echo '
            <tr class="windowbg2">
                <td align="center"><span class="smalltext"><b>';
        
            if ($modSettings['down_set_file_showfilesize'] && $context['downloads_file']['fileurl'] == '')
                echo $txt['downloads_text_filesize']  . format_size($context['downloads_file']['filesize'],2) . '&nbsp;&nbsp;';
            
        
            if ($modSettings['down_set_file_views'])
                echo $txt['downloads_text_views'] . ' (' . $context['downloads_file']['views'] . ')&nbsp;&nbsp;';
            
            if ($modSettings['down_set_file_downloads'])
                echo $txt['downloads_cat_downloads'] . ' (' . $context['downloads_file']['totaldownloads'] . ')&nbsp;&nbsp;';
        
            if ($modSettings['down_set_file_lastdownload']) 
                echo $txt['downloads_text_lastdownload'] . ' ' . ($context['downloads_file']['lastdownload'] != 0 ? timeformat($context['downloads_file']['lastdownload']) : $txt['downloads_text_lastdownload2'] ) . '&nbsp;';
                 
            echo '</b></span>
                </td>
            </tr>'; 
            
        // Show the previous and next links
        if ($modSettings['down_set_file_prevnext'])
            echo '<tr class="windowbg2">
            <td align="center"><b>
                <a href="', $scripturl, '?action=downloads;sa=prev;id=', $context['downloads_file']['ID_FILE'], '">', $txt['downloads_text_prev'], '</a> | 
                <a href="', $scripturl, '?action=downloads;sa=next;id=', $context['downloads_file']['ID_FILE'], '">', $txt['downloads_text_next'], '</a>
                </b>
                </div>  
            </td>
            </tr>';
            
            echo '
            <tr class="windowbg2">
                <td><center>';
            
            if (!empty($context['downloads_file']['screenshot'])) {
                echo '<img src="' . $modSettings['down_url'] . 'screenshots/' . $context['downloads_file']['screenshot'] . '" /><br/><br/>';
            }
            
            // Show description
            if ($modSettings['down_set_file_desc'])
                echo '' . parse_bbc($context['downloads_file']['description']);
                
            echo '</center>
                <hr />';
        
                
            if ($modSettings['down_set_file_keywords'])
                if ($context['downloads_file']['keywords'] != '')
                {
                    echo  $txt['downloads_form_keywords'] . ' ';
    
                    for($i = 0; $i < $keywordscount;$i++)
                    {
                        echo '<a href="' . $scripturl . '?action=downloads;sa=search2;key=' . $keywords[$i] . '">' . $keywords[$i] . '</a>&nbsp;';
    
                    }
                    echo '<br />';
                }
                
            echo '<b>';
            if ($modSettings['down_set_file_poster'])
            {
                
                if ($context['downloads_file']['realName'] != '')
                    echo $txt['downloads_text_postedby'] . '<a href="' . $scripturl . '?action=profile;u=' . $context['downloads_file']['ID_MEMBER'] . '">'  . $context['downloads_file']['realName'] . '</a>&nbsp;';
                else 
                    echo $txt['downloads_text_postedby'] . ' ' . $txt['downloads_guest'] . '&nbsp;';
            
            }
            if ($modSettings['down_set_file_date'])
                echo $context['downloads_file']['date'] . '<br />';
            
            echo '</b>';

                // Show Custom Fields
                foreach ($context['downloads_custom'] as $i => $custom)
                {
                    // No reason to show empty custom fields on the display page
                    if ($custom['value'] != '')
                        echo '<b>', $custom['title'], ':</b>&nbsp;',$custom['value'], '<br />';

                }
                    
            echo '<br />';

                // Show rating information
            if ($modSettings['down_set_file_showrating'])
                if ($modSettings['down_show_ratings'] == true && $context['downloads_file']['disablerating'] == 0)
                {
                    
                    $max_num_stars = 5;
                    
                    if ($context['downloads_file']['totalratings'] == 0)
                    {
                        // Display message that no ratings are in yet
                        echo $txt['downloads_form_rating'] . $txt['downloads_form_norating'];
                    }
                    else
                    {   
                        // Compute the rating in %
                        $rating =($context['downloads_file']['rating'] / ($context['downloads_file']['totalratings']* $max_num_stars) * 100);
                        
                        echo $txt['downloads_form_rating'] . GetStarsByPrecent($rating). '';
                        
                        if ($modSettings['down_set_file_rating_count'])
                        echo ' ' . $txt['downloads_form_ratingby'] .$context['downloads_file']['totalratings'] . $txt['downloads_form_ratingmembers'] . '';
                        
                        echo '<br />';
                    }

                    if (allowedTo('downloads_ratefile'))
                    {
                        echo '<form method="post" action="' . $scripturl . '?action=downloads;sa=rate">';
                            for($i = 1; $i <= $max_num_stars;$i++)
                                echo '<input type="radio" name="rating" value="' . $i .'" />' . str_repeat('<img src="' . $settings['images_url'] . '/starFull.png" alt="*" border="0" />', $i);

                             
                    echo '
                             <input type="hidden" name="id" value="' . $context['downloads_file']['ID_FILE'] . '" />
                             <input type="submit" name="submit" value="' . $txt['downloads_form_ratedownload'] . '" />
                        ';

                        // If the user can manage the downloads let them see who voted for what and option to delete rating
                        if ($g_manage)
                            echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=viewrating;id=' . $context['downloads_file']['ID_FILE'] . '">' . $txt['downloads_form_viewratings'] . '</a>';
                        echo '</form><br />';
                    }
                }

                // Show linking codes
                
                if ($modSettings['down_set_showcode_directlink'] || $modSettings['down_set_showcode_htmllink'])
                {
                    echo '<br /><b>',$txt['downloads_txt_download_linking'],'</b><br />
                    <table border="0">
                    ';
                    

                    if ($modSettings['down_set_showcode_directlink'])
                    {
                        echo '<tr><td width="30%">', $txt['downloads_txt_directlink'], '</td><td> <input type="text" value="' . $scripturl . '?action=downloads;sa=downfile;id=' . $context['downloads_file']['ID_FILE']  . '" size="50"></td></tr>';
                    }
                    if ($modSettings['down_set_showcode_htmllink'])
                    {
                        echo '<tr><td width="30%">', $txt['downloads_set_showcode_htmllink'], '</td><td> <input type="text" value="<a href=&#34;' . $scripturl . '?action=downloads;sa=downfile;id=' . $context['downloads_file']['ID_FILE']  . '&#34; />', ($context['downloads_file']['fileurl'] == '' ? $context['downloads_file']['orginalfilename'] : $txt['downloads_app_download']), '</a>" size="50"></td></tr>';
                    }
                    
                    echo '</table>';
                    
                }
                
                // Show edit download links if allowed
                if ($g_manage)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=unapprove;id=' . $context['downloads_file']['ID_FILE'] . '">' . $txt['downloads_text_unapprove'] . '</a>';
                if ($g_manage || $g_edit_own && $context['downloads_file']['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=edit;id=' . $context['downloads_file']['ID_FILE']. '">' . $txt['downloads_text_edit'] . '</a>';
                if ($g_manage || $g_delete_own && $context['downloads_file']['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $context['downloads_file']['ID_FILE'] . '">' . $txt['downloads_text_delete'] . '</a>';


                // Show report download link
                if ($g_report)
                {
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=report;id=' . $context['downloads_file']['ID_FILE'] . '">' . $txt['downloads_text_reportdownload'] . '</a>';
                }

                echo '
                </td>
            </tr>';

        // Display who is viewing the download.
        if (!empty($modSettings['down_who_viewing']))
        {
            echo '<tr>
            <td align="center" class="windowbg2"><span class="smalltext">';

            // Show just numbers...?
            // show the actual people viewing the topic?
            echo empty($context['view_members_list']) ? '0 ' . $txt['downloads_who_members'] : implode(', ', $context['view_members_list']) . (empty($context['view_num_hidden']) || $context['can_moderate_forum'] ? '' : ' (+ ' . $context['view_num_hidden'] . ' ' . $txt['downloads_who_hidden'] . ')');

            // Now show how many guests are here too.
            echo $txt['who_and'], $context['view_num_guests'], ' ', $context['view_num_guests'] == 1 ? $txt['guest'] : $txt['guests'], $txt['downloads_who_viewfile'], '</span></td></tr>';
        }

echo '
        </table><br />';
    // Check if allowed to display comments for this file
    if ($context['downloads_file']['allowcomments'])
    {
        // Show comments
        echo '<table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                    <td align="center" colspan="2">' . $txt['downloads_text_comments'] . '</td>
                </tr>';

        if (allowedTo('downloads_comment'))
        {
            // Show Add Comment
            echo '
                <tr class="titlebg"><td colspan="2">
                <a href="' . $scripturl . '?action=downloads;sa=comment;id=' . $context['downloads_file']['ID_FILE'] . '">' . $txt['downloads_text_addcomment']  . '</a></td>
                </tr>';
        }
        
        
        foreach ($context['downloads_comments'] as $i => $comment)
        {
            echo '<tr class="windowbg">';
            // Display member info
            echo '<td width="10%" valign="top"><a name="c' . $comment['ID_COMMENT'] . '"></a>';
            
            if ($comment['realName'] != '')
                echo '<a href="' . $scripturl . '?action=profile;u=' . $comment['ID_MEMBER'] . '">'  . $comment['realName'] . '</a><br />
                <span class="smalltext">Posts: ' . $comment['posts'] . '</span><br />';
            else 
                echo $txt['downloads_guest'] . '<br />';
                
            
            // Display the users avatar
            $memCommID = $comment['ID_MEMBER'];
            if ($comment['realName'])
            {
                $memCommID = $comment['ID_MEMBER'];
                loadMemberData($memCommID);
                loadMemberContext($memCommID);
                
                
                echo $memberContext[$memCommID]['avatar']['image'];
    
            }


            echo '
            </td>';
            // Display the comment
            echo '<td width="90%"><span class="smalltext">' . timeformat($comment['date']) . '</span><hr />';

            echo  parse_bbc($comment['comment']);

            if ($comment['modified_ID_MEMBER'] != 0)
            {

                echo '<br /><span class="smalltext"><i>' . $txt['downloads_text_commodifiedby']  . '<a href="' . $scripturl . '?action=profile;u=' . $comment['modified_ID_MEMBER'] . '">'  . $comment['modmember'] . '</a> ' . timeformat($comment['lastmodified']) .  ' </i></span>';
            

            }

            // Check if they can edit the comment
            if ($g_manage || $g_edit_comment && $comment['ID_MEMBER'] == $ID_MEMBER)
                echo '<br /><a href="' . $scripturl . '?action=downloads;sa=editcomment;id=' . $comment['ID_COMMENT'] . '">' . $txt['downloads_text_edcomment'] .'</a>';

            if ($g_manage || $g_report)
                echo '<br /><a href="' . $scripturl . '?action=downloads;sa=reportcomment;id=' . $comment['ID_COMMENT'] . '">' . $txt['downloads_text_repcomment'] .'</a>';


            // Check if the user is allowed to delete the comment.
            if ($g_manage)
                echo '<br /><a href="' . $scripturl . '?action=downloads;sa=delcomment;id=' . $comment['ID_COMMENT'] . '">' . $txt['downloads_text_delcomment'] .'</a>';


            echo '</td>';
            echo '</tr>';
        }



        if (allowedTo('downloads_comment') && $context['comment_count'] != 0)
        {
        // Show Add Comment
            echo '
                <tr class="titlebg"><td colspan="2">
                <a href="' . $scripturl . '?action=downloads;sa=comment;id=' . $context['downloads_file']['ID_FILE'] . '">' . $txt['downloads_text_addcomment'] . '</a></td>
                </tr>';
        }

        echo '</table><br />';
        
        
        // Quick Reply Option
        
        if ($modSettings['down_set_show_quickreply'])
        {
            
    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '
                                    <script language="JavaScript" type="text/javascript" src="' . $settings['default_theme_url'] . '/scripts/spellcheck.js"></script>';

                echo '<form method="post" action="' . $scripturl . '?action=downloads&sa=comment2" id="cprofile" name="cprofile">
                <table border="0" cellpadding="0" cellspacing="0" width="90%" class="tborder" align="center">
                  <tr>
                    <td width="50%" colspan="2"  align="center" class="catbg">
                    <b>' . $txt['downloads_text_addcomment'] . '</b></td>
                  </tr>
                  <tr>
                    <td width="28%"  valign="top" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_comment'] . '</b>&nbsp;</span></td>
                    <td width="72%"  class="windowbg2"><textarea rows="6" name="comment" cols="54"></textarea></td>
                  </tr>
                  <tr>
                    <td width="28%" colspan="2"  align="center" class="windowbg2">
                    <input type="hidden" name="id" value="' . $context['downloads_file']['ID_FILE'] . '" />';
                
                    if (allowedTo('downloads_autocomment') == false)
                        echo $txt['downloads_text_commentwait'] . '<br />';
                
                
                echo '
                    <input type="submit" value="', $txt['downloads_text_addcomment'], '" name="submit" />';
                
                    if ($context['show_spellchecking'])
            echo '
                                        <input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'cprofile\', \'comment\');" />';
    
                
                echo '</td>
                  </tr>
                </table>
                </form>';
            
            
            if ($context['show_spellchecking'])
                        echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" id="spellstring" name="spellstring" value="" /></form>';
                
        }
        
        
    }

    echo '<div align="center"><a href="' . $scripturl . '?action=downloads;cat=' . $context['downloads_file']['ID_CAT'] . '">' . $txt['downloads_text_returndownload'] . '</a></div><br />';

echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';

    downloads_copyright();
}

function template_delete_download()
{
    global $scripturl, $modSettings, $txt, $context, $settings;


    echo '
    <form method="post" action="', $scripturl, '?action=downloads;sa=delete2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr class="catbg">
    <td width="50%" colspan="2"  align="center">
    <b>' . $txt['downloads_form_deldownload'] . '</b></td>
  </tr>
  <tr class="windowbg2">
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    ' . $txt['downloads_warn_deletedownload'] . '
    <br />
<div align="center"><br /><b>' . $txt['downloads_text_deldownload'] . '</b><br />
<a href="' . $scripturl . '?action=downloads;sa=view;down=' . $context['downloads_file']['ID_FILE'] . '" target="blank">',$context['downloads_file']['title'],'</a><br />
            <span class="smalltext">Views: ' . $context['downloads_file']['views'] . '<br />
            ' . $txt['downloads_text_filesize']  . format_size($context['downloads_file']['filesize'],2) . '<br />
            ' . $txt['downloads_text_date'] . $context['downloads_file']['date'] . '<br />
            ' . $txt['downloads_text_comments'] . ' (<a href="' . $scripturl . '?action=downloads;sa=view;down=' .  $context['downloads_file']['ID_FILE'] . '" target="blank">' .  $context['downloads_file']['commenttotal'] . '</a>)<br />
    </div><br />
    <input type="hidden" name="id" value="' . $context['downloads_file']['ID_FILE'] . '" />
    <input type="hidden" name="cat" value="' . $context['downloads_file']['ID_CAT'] . '" />
    <input type="submit" value="' . $txt['downloads_form_deldownload'] . '" name="submit" /><br />
    </td>
  </tr>
</table>

        </form>
';

}

function template_add_comment()
{
    global $context, $scripturl, $txt, $settings, $modSettings;
    
    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '
                                    <script language="JavaScript" type="text/javascript" src="', $settings['default_theme_url'], '/spellcheck.js"></script>';


echo '
<form method="post" name="cprofile" id="cprofile" action="' . $scripturl . '?action=downloads&sa=comment2">
<table border="0" cellpadding="0" cellspacing="0" bordercolor="#FFFFFF" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>',$txt['downloads_text_addcomment'], '</b></td>
  </tr>

   <tr>
   <td class="windowbg2" colspan="2" align="center">
   <table>
   ';
   theme_postbox('');
   echo '</table></td>
   </tr>
  <tr>
    <td width="28%" colspan="2" align="center" class="windowbg2">
    <input type="hidden" name="id" value="' . $context['downloads_file_id'] . '" />';

    if (allowedTo('downloads_autocomment') == false)
        echo $txt['downloads_text_commentwait'] . '<br />';

    if ($context['show_spellchecking'])
        echo '
                                    <input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'cprofile\', \'comment\');" />';



echo '
    <input type="submit" value="', $txt['downloads_text_addcomment'], '" name="submit" /></td>

  </tr>
</table>
</form>';


    if ($context['show_spellchecking'])
            echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" name="spellstring" value="" /></form>';
    
    
    downloads_copyright();
}

function template_report_download()
{
    global $scripturl, $context, $txt;

    echo '
<form method="post" name="cprofile" id="cprofile" action="' . $scripturl . '?action=downloads;sa=report2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>' . $txt['downloads_form_reportdownload'] . '</b></td>
  </tr>
  <tr>
    <td width="28%"  valign="top" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_comment'] . '</b>&nbsp;</span></td>
    <td width="72%"  class="windowbg2"><textarea rows="6" name="comment" cols="54"></textarea></td>
  </tr>
  <tr>
    <td width="28%" colspan="2" align="center" class="windowbg2">
    <input type="hidden" name="id" value="' . $context['downloads_file_id'] . '" />
    <input type="submit" value="' . $txt['downloads_form_reportdownload'] . '" name="submit" /></td>

  </tr>
</table>
</form>';
    
    downloads_copyright();
}
function template_report_comment()
{
    global $scripturl, $context, $txt;

    echo '
<form method="post" name="cprofile" id="cprofile" action="' . $scripturl . '?action=downloads;sa=reportcomment2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>' . $txt['downloads_text_reportcomment'] . '</b></td>
  </tr>
  <tr>
    <td width="28%"  valign="top" class="windowbg2" align="right"><span class="gen"><b>' . $txt['downloads_form_comment'] . '</b>&nbsp;</span></td>
    <td width="72%" class="windowbg2"><textarea rows="6" name="comment" cols="54"></textarea></td>
  </tr>
  <tr>
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    <input type="hidden" name="id" value="' . $context['downloads_comment_id'] . '" />
    <input type="submit" value="' . $txt['downloads_text_reportcomment'] . '" name="submit" /></td>

  </tr>
</table>
</form>';
    
    downloads_copyright();
}


function template_settings()
{
    global $scripturl, $modSettings, $txt, $settings;

    echo '
<script language="JavaScript" type="text/javascript" src="' . $settings['default_theme_url'] . '/scripts/layout.js"></script>';

echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>', $txt['downloads_text_settings'], '</td>
        </tr>
        <tr class="windowbg">
            <td>
            <b>' . $txt['downloads_text_settings'] . '</b> - <span class="smalltext">' . $txt['downloads_set_description'] . '</span><br />
            <form method="post" name="AdminSettings" action="' . $scripturl . '?action=downloads;sa=adminset2">
                <table border="0" width="100%" cellspacing="0" align="center" cellpadding="4">
                    <tr><td width="30%">' . $txt['downloads_set_filesize'] . '</td><td><input type="text" name="down_max_filesize" value="' .  $modSettings['down_max_filesize'] . '" /> (bytes)</td></tr>
                <tr><td width="30%">' . $txt['downloads_set_path'] . '</td><td><input type="text" name="down_path" value="' .  $modSettings['down_path'] . '" size="50" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_set_url'] . '</td><td><input type="text" name="down_url" value="' .  $modSettings['down_url'] . '" size="50" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_set_files_per_page_list'] . '</td><td><input type="text" name="down_set_files_per_page_list" value="' .  $modSettings['down_set_files_per_page_list'] . '" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_set_rows_per_page_tables'] . '</td><td><input type="text" name="down_set_rows_per_page_tables" value="' . $modSettings['down_set_rows_per_page_tables'] . '" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_set_files_per_page_full'] . '</td><td><input type="text" name="down_set_files_per_page_full" value="' .  $modSettings['down_set_files_per_page_full'] . '" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_set_cat_width'] . '</td><td><input type="text" name="down_set_cat_width" value="' .  $modSettings['down_set_cat_width'] . '" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_set_cat_height'] . '</td><td><input type="text" name="down_set_cat_height" value="' .  $modSettings['down_set_cat_height'] . '" /></td></tr>
                <tr><td width="30%">Max Screenshot Width: </td><td><input type="text" name="down_set_file_ss_width" value="' . $modSettings['down_set_file_ss_width'] . '" />&nbsp;<b class="smalltext">Set to 0 for an unlimited width size</b></td></tr>
                <tr><td width="30%">Max Screenshot Height: </td><td><input type="text" name="down_set_file_ss_height" value="' . $modSettings['down_set_file_ss_height'] . '" />&nbsp;<b class="smalltext">Set to 0 for an unlimited height size</b></td></tr>
                </table>
                <input type="checkbox" name="down_who_viewing" ' . ($modSettings['down_who_viewing'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_whoonline'] . '<br />
                <input type="checkbox" name="down_set_count_child" ' . ($modSettings['down_set_count_child'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_count_child'] . '<br />
                <input type="checkbox" name="down_set_commentsnewest" ' . ($modSettings['down_set_commentsnewest'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_commentsnewest'] . '<br />
                <input type="checkbox" name="down_set_show_quickreply" ' . ($modSettings['down_set_show_quickreply'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_show_quickreply'] . '<br />
                <input type="checkbox" name="down_show_ratings" ' . ($modSettings['down_show_ratings'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_showratings'] . '<br />
                <input type="checkbox" name="down_set_enable_multifolder" ' . ($modSettings['down_set_enable_multifolder'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_enable_multifolder'] . '<hr>
                <b>Index Blocks</b><hr>';

            echo '<table width="100%" border="0" cellpadding="0" cellspacing="0">';
                
    for ($x = 1; $x < 6; $x++) {
        // Recent
        if ($modSettings['down_index_recent_order'] == $x) {
        
        echo '<tr><td><input type="checkbox" name="down_index_recent" ' . ($modSettings['down_index_recent'] ? ' checked="checked" ' : '') . ' /> ' . $txt['downloads_index_recent'] . '</td><td>Default Expanded? <input type="checkbox" name="down_index_recent_expand" ' . (!empty($modSettings['down_index_recent_expand']) ? ' checked="checked" ' : '') . ' /></td><td width="15%">' . ($x == 1 ? '' : ' <a href="' . $scripturl . '?action=downloads;sa=pageup;position=' . $x . '">[Up]</a>') . ' ' . ($x == 5 ? '' : '<a href="' . $scripturl . '?action=downloads;sa=pagedown;position=' . $x . '">[Down]</a>') . '<input type="hidden" name="down_index_recent_order" value="' . $x . '" /></td></tr>';
        }
        
        // Most Viewed
        if ($modSettings['down_index_mostviewed_order'] == $x) {
        
        echo '<tr><td><input type="checkbox" name="down_index_mostviewed" ' . ($modSettings['down_index_mostviewed'] ? ' checked="checked" ' : '') . ' /> ' . $txt['downloads_index_mostviewed'] . '</td><td>Default Expanded? <input type="checkbox" name="down_index_mostviewed_expand" ' . (!empty($modSettings['down_index_mostviewed_expand']) ? ' checked="checked" ' : '') . ' /></td><td width="15%">' . ($x == 1 ? '' : ' <a href="' . $scripturl . '?action=downloads;sa=pageup;position=' . $x . '">[Up]</a>') . ' ' . ($x == 5 ? '' : '<a href="' . $scripturl . '?action=downloads;sa=pagedown;position=' . $x . '">[Down]</a>') . '<input type="hidden" name="down_index_mostviewed_order" value="' . $x . '" /></td></tr>';
        }
        
        // Most Downloaded
        if ($modSettings['down_index_mostdownloaded_order'] == $x) {
        
        echo '<tr><td><input type="checkbox" name="down_index_mostdownloaded" ' . ($modSettings['down_index_mostdownloaded'] ? ' checked="checked" ' : '') . ' /> Show the most downloaded files on the main page</td><td>Default Expanded? <input type="checkbox" name="down_index_mostdownloaded_expand" ' . (!empty($modSettings['down_index_mostdownloaded_expand']) ? ' checked="checked" ' : '') . ' /></td><td width="15%">' . ($x == 1 ? '' : ' <a href="' . $scripturl . '?action=downloads;sa=pageup;position=' . $x . '">[Up]</a>') . ' ' . ($x == 5 ? '' : '<a href="' . $scripturl . '?action=downloads;sa=pagedown;position=' . $x . '">[Down]</a>') . '<input type="hidden" name="down_index_mostdownloaded_order" value="' . $x . '" /></td></tr>';
        }
        
        // Most commented
        if ($modSettings['down_index_mostcomments_order'] == $x) {
        
        echo '<tr><td><input type="checkbox" name="down_index_mostcomments" ' . ($modSettings['down_index_mostcomments'] ? ' checked="checked" ' : '') . ' /> ' . $txt['downloads_index_mostcomments'] . '</td><td>Default Expanded? <input type="checkbox" name="down_index_mostcomments_expand" ' . (!empty($modSettings['down_index_mostcomments_expand']) ? ' checked="checked" ' : '') . ' /></td><td width="15%">' . ($x == 1 ? '' : ' <a href="' . $scripturl . '?action=downloads;sa=pageup;position=' . $x . '">[Up]</a>') . ' ' . ($x == 5 ? '' : '<a href="' . $scripturl . '?action=downloads;sa=pagedown;position=' . $x . '">[Down]</a>') . '<input type="hidden" name="down_index_mostcomments_order" value="' . $x . '" /></td></tr>';
        
        }
        // Top Rated
        if ($modSettings['down_index_toprated_order'] == $x) {
        
        echo '<tr><td><input type="checkbox" name="down_index_toprated" ' . ($modSettings['down_index_toprated'] ? ' checked="checked" ' : '') . ' /> ' . $txt['downloads_index_toprated'] . '</td><td>Default Expanded? <input type="checkbox" name="down_index_toprated_expand" ' . (!empty($modSettings['down_index_toprated_expand']) ? ' checked="checked" ' : '') . ' /></td><td width="15%">' . ($x == 1 ? '' : '<a href="' . $scripturl . '?action=downloads;sa=pageup;position=' . $x . '">[Up]</a>') . ' ' . ($x == 5 ? '' : '<a href="' . $scripturl . '?action=downloads;sa=pagedown;position=' . $x . '">[Down]</a>') . '<input type="hidden" name="down_index_toprated_order" value="' . $x . '" /></td></tr>';
        }
        
    }

                echo '</table><hr><b>Index Blocks Position on Main Page</b><hr>
                <input type="checkbox" id="top" name="down_index_showtop" ' . ($modSettings['down_index_showtop'] ? ' checked="checked" ' : '') . ' onClick="doPageBlocks(\'down_index_showtop\');" onFocus="if(this.blur)this.blur();" /> Show Index Blocks on Top of the Categories<br />
                <input type="checkbox" id="bottom" name="down_index_showbottom" ' . ($modSettings['down_index_showbottom'] ? ' checked="checked" ' : '') . ' onClick="doPageBlocks(\'down_index_showbottom\');" onFocus="if(this.blur)this.blur();" /> Show Index Blocks Below the Categories<br />
                <input type="checkbox" id="left" name="down_index_showleft" ' . ($modSettings['down_index_showleft'] ? ' checked="checked" ' : '') . ' onClick="doPageBlocks(\'down_index_showleft\');" onFocus="if(this.blur)this.blur();" /> Show Index Blocks to the Left of the Categories<br />
                <input type="checkbox" id="right" name="down_index_showright" ' . ($modSettings['down_index_showright'] ? ' checked="checked" ' : '') . ' onClick="doPageBlocks(\'down_index_showright\');" onFocus="if(this.blur)this.blur();" /> Show Index Blocks to the Right of the Categories<hr>
                <input type="checkbox" name="down_commentchoice" ' . ($modSettings['down_commentchoice'] ? ' checked="checked" ' : '') . ' /> ' . $txt['downloads_set_commentschoice'] . '<hr />
                <b>' . $txt['downloads_catthumb_settings'] . '</b><hr />' . $txt['downloads_text_default_layout'] . '
                <select name="down_set_cat_layout">
                    <option value="0"', ($modSettings['down_set_cat_layout'] == 0 ? ' selected' : ''), '>' . $txt['downloads_text_layout_list'] . '</option>
                    <option value="1"', ($modSettings['down_set_cat_layout'] == 1 ? ' selected' : ''), '>' . $txt['downloads_text_layout_tables'] . '</option>
                    <option value="2"', ($modSettings['down_set_cat_layout'] == 2 ? ' selected' : ''), '>' . $txt['downloads_text_layout_full'] . '</option>
                </select> &nbsp; ' . $txt['downloads_text_overide_layout'] . ' <input type="checkbox" name="overide_cat_layout" /><br />
                <input type="checkbox" name="down_set_t_title" ' . ($modSettings['down_set_t_title'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_title'] . '<br />
                <input type="checkbox" name="down_set_t_downloads" ' . ($modSettings['down_set_t_downloads'] ? ' checked="checked" ' : '') . ' />' .$txt['downloads_set_t_downloads'] . '<br />
                <input type="checkbox" name="down_set_t_views" ' . ($modSettings['down_set_t_views'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_t_views'] . '<br />
                <input type="checkbox" name="down_set_t_filesize" ' . ($modSettings['down_set_t_filesize'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_t_filesize'] . '<br />
                <input type="checkbox" name="down_set_t_date" ' . ($modSettings['down_set_t_date'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_t_date'] . '<br />
                <input type="checkbox" name="down_set_t_comment" ' . ($modSettings['down_set_t_comment'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_t_comment'] . '<br />
                <input type="checkbox" name="down_set_t_username" ' . ($modSettings['down_set_t_username'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_t_username'] . '<br />
                <input type="checkbox" name="down_set_t_rating" ' . ($modSettings['down_set_t_rating'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_t_rating'] . '<hr />
                
                <b>' . $txt['downloads_files_settings'] . '</b><hr />
                
                <input type="checkbox" name="down_set_file_prevnext" ' . ($modSettings['down_set_file_prevnext'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_prevnext'] . '<br />
                <input type="checkbox" name="down_set_file_desc" ' . ($modSettings['down_set_file_desc'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_desc'] . '<br />
                <input type="checkbox" name="down_set_file_title" ' . ($modSettings['down_set_file_title'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_title'] . '<br />
                <input type="checkbox" name="down_set_file_views" ' . ($modSettings['down_set_file_views'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_views'] . '<br />
                <input type="checkbox" name="down_set_file_downloads" ' . ($modSettings['down_set_file_downloads'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_downloads'] . '<br />
                <input type="checkbox" name="down_set_file_lastdownload" ' . ($modSettings['down_set_file_lastdownload'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_lastdownload'] . '<br />
                <input type="checkbox" name="down_set_file_poster" ' . ($modSettings['down_set_file_poster'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_poster'] . '<br />
                <input type="checkbox" name="down_set_file_date" ' . ($modSettings['down_set_file_date'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_date'] . '<br />
                <input type="checkbox" name="down_set_file_showfilesize" ' . ($modSettings['down_set_file_showfilesize'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_showfilesize'] . '<br />
                <input type="checkbox" name="down_set_file_showrating" ' . ($modSettings['down_set_file_showrating'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_showrating'] . '<br />
                <input type="checkbox" name="down_set_file_rating_count" ' . ($modSettings['down_set_file_rating_count'] ? ' checked="checked" ' : '') . ' />Show rating count<br />
                <input type="checkbox" name="down_set_file_keywords" ' . ($modSettings['down_set_file_keywords'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_file_keywords'] . '<br />

                <br />' . $txt['downloads_shop_settings'] . '<br />
                <table border="0" width="100%" cellspacing="0" align="center" cellpadding="4">
                <tr><td width="30%">' . $txt['downloads_shop_fileadd'] . '</td><td><input type="text" name="down_shop_fileadd" value="' .  $modSettings['down_shop_fileadd'] . '" /></td></tr>
                <tr><td width="30%">' . $txt['downloads_shop_commentadd'] . '</td><td><input type="text" name="down_shop_commentadd" value="' .  $modSettings['down_shop_commentadd'] . '" /></td></tr>
                </table>
                <br /><b>' . $txt['downloads_txt_download_linking'] . '</b><br />
                <input type="checkbox" name="down_set_showcode_directlink" ' . ($modSettings['down_set_showcode_directlink'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_showcode_directlink'] . '<br />
                <input type="checkbox" name="down_set_showcode_htmllink" ' . ($modSettings['down_set_showcode_htmllink'] ? ' checked="checked" ' : '') . ' />' . $txt['downloads_set_showcode_htmllink'] . '<br />
                
                ';

                if (!is_writable($modSettings['down_path']))
                    echo '<font color="#FF0000"><b>' . $txt['downloads_write_error']  . $modSettings['down_path'] . '</b></font>';

                echo '
                
                <input type="submit" name="savesettings" value="' . $txt['downloads_save_settings'] . '" />
            </form>
            <br />
            <b>' . $txt['downloads_text_permissions'] . '</b><br/><span class="smalltext">' . $txt['downloads_set_permissionnotice'] . '</span>
            <br /><a href="' . $scripturl . '?action=permissions">' . $txt['downloads_set_editpermissions']  . '</a>

            </td>
        </tr>
        
<tr class="windowbg"><td><b>Has the Downloads System helped you?</b> Then support the developers:<br />
    <form action="https://www.paypal.com/cgi-bin/webscr" method="post">
    <input type="hidden" name="cmd" value="_xclick">
    <input type="hidden" name="business" value="sales@visualbasiczone.com">
    <input type="hidden" name="item_name" value="Downloads System">
    <input type="hidden" name="no_shipping" value="1">
    <input type="hidden" name="no_note" value="1">
    <input type="hidden" name="currency_code" value="USD">
    <input type="hidden" name="tax" value="0">
    <input type="hidden" name="bn" value="PP-DonationsBF">
    <input type="image" src="https://www.paypal.com/en_US/i/btn/x-click-butcc-donate.gif" border="0" name="submit" alt="Make payments with PayPal - it is fast, free and secure!" />
    <img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>
            <br />  
            <table>
                <tr>
                <td>
                <a href="http://www.adbrite.com/mb/?spid=11444&afb=120x60-1-blue">
<img src="http://files.adbrite.com/mb/images/120x60-1-blue.gif" border="0"></a>
                </td>
                <td>
                                <a href="http://www.kqzyfj.com/click-3289266-10408495" target="_top">
<img src="http://www.tqlkg.com/image-3289266-10408495" width="120" height="60" alt="" border="0"/></a>

                </td>
                </table>

</td>
</tr>
        
</table>';

}
function template_approvelist()
{
    global $scripturl, $context, $modSettings, $txt;


echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>', $txt['downloads_form_approvedownloads'], '</td>
        </tr>
        <tr class="windowbg">
            <td>
            <form method="post" action="', $scripturl, '?action=downloads;sa=bulkactions">
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                <td>&nbsp;</td>
                <td>', $txt['downloads_app_download'], '</td>
                <td>', $txt['downloads_text_category'], '</td>
                <td>', $txt['downloads_app_title'], '</td>
                <td>', $txt['downloads_app_description'], '</td>
                <td>', $txt['downloads_app_date'], '</td>
                <td>', $txt['downloads_app_membername'], '</td>
                <td>', $txt['downloads_text_options'], '</td>
                </tr>';


            foreach ($context['downloads_file'] as $i => $file)
            {
                echo '<tr class="windowbg2">';
                echo '<td><input type="checkbox" name="files[]" value="',$file['ID_FILE'],'" /></td>';

                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=' . $file['ID_FILE'] . '">',$txt['downloads_rep_viewdownload'],'</a></td>';
                echo '<td>' . (empty($file['catname']) ? $file['catname2'] : $file['catname']) . '</td>';
                echo '<td>', $file['title'], '</td>';
                echo '<td>', $file['description'], '</td>';
                echo '<td>', timeformat($file['date']), '</td>';
                if ($file['realName'] != '')
                    echo '<td><a href="' . $scripturl . '?action=profile;u=' . $file['ID_MEMBER'] . '">'  . $file['realName'] . '</a></td>';
                else 
                    echo '<td>',$txt['downloads_guest'],'</td>';
                    
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=approve;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_approve']  . '</a><br /><a href="' . $scripturl . '?action=downloads;sa=edit;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_edit'] . '</a><br /><a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';

            }
            
            
            
        echo '<tr class="titlebg">
                <td align="left" colspan="8">
                ' . $txt['downloads_text_pages'];

                echo $context['page_index'];
                
            echo '<br /><br /><b>',$txt['downloads_text_withselected'],'</b>
            
            <select name="doaction">
            <option value="approve">',$txt['downloads_form_approvedownloads'],'</option>
            <option value="delete">',$txt['downloads_form_deldownload'],'</option>
            </select>
            <input type="submit" value="',$txt['downloads_text_performaction'],'" />
            </form>
            ';
        echo '
                </td>
            </tr>
            </table>
            </td>
        </tr>

</table>';

}
function template_reportlist()
{
    global $scripturl, $txt, $context;
echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>' . $txt['downloads_form_reportdownloads'] . '</td>
        </tr>

        <tr class="windowbg">
            <td>
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                <td>', $txt['downloads_rep_filelink'], '</td>
                <td>', $txt['downloads_rep_comment'], '</td>
                <td>', $txt['downloads_app_date'], '</td>
                <td>', $txt['downloads_rep_reportby'], '</td>
                <td>', $txt['downloads_text_options'], '</td>
                </tr>';

            // List all reported downloads
            foreach ($context['downloads_reports'] as $i => $report)
            {

                echo '<tr class="windowbg2">';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=' . $report['ID_FILE'] . '">' . $txt['downloads_rep_viewdownload'] .'</a></td>';
                echo '<td>', $report['comment'], '</td>';
                echo '<td>', timeformat($report['date']), '</td>';
                
                if ($report['realName'] != '')
                    echo '<td><a href="' . $scripturl . '?action=profile;u=' . $report['ID_MEMBER'] . '">'  . $report['realName'] . '</a></td>';
                else 
                    echo '<td>',$txt['downloads_guest'],'</td>';
                    
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $report['ID_FILE'] . '">' . $txt['downloads_form_deldownload2']  . '</a>';
                echo '<br /><br /><a href="' . $scripturl . '?action=downloads;sa=deletereport;id=' . $report['ID'] . '">' . $txt['downloads_rep_delete'] . '</a></td>';
                echo '</tr>';

            }
            

echo '
            </table>
            </td>
        </tr>
</table>';

}
function template_comment_list()
{
    global $scripturl, $context, $txt;
    
echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>', $txt['downloads_form_approvecomments'], '</td>
        </tr>

        <tr class="windowbg">
            <td>
            <b>', $txt['downloads_form_approvecomments'], '</b><br />
            <form method="post" action="', $scripturl, '?action=downloads;sa=apprcomall">
            <input type="submit" value="', $txt['downloads_form_approveallcomments'], '" />
            </form>
            <br />
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                <td>' . $txt['downloads_rep_filelink'] . '</td>
                <td>' . $txt['downloads_rep_comment']  . '</td>
                <td>' . $txt['downloads_app_date'] . '</td>
                <td>' . $txt['downloads_app_membername'] . '</td>
                <td>' . $txt['downloads_text_options'] . '</td>
                </tr>';

            // List all Comments waiting approval
            foreach ($context['downloads_comments'] as $i => $comment)
            {

                echo '<tr class="windowbg2">';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=' . $comment['ID_FILE'] . '">' . $txt['downloads_rep_viewdownload'] .'</a></td>';
                echo '<td>' . $comment['comment'] . '</td>';
                echo '<td>' . timeformat($comment['date']) . '</td>';
                if ($comment['realName'] != '')
                    echo '<td><a href="' . $scripturl . '?action=profile;u=' . $comment['ID_MEMBER'] . '">'  . $comment['realName'] . '</a></td>';
                else 
                    echo '<td>'  . $txt['downloads_guest']. '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=apprcomment;id=' . $comment['ID_COMMENT'] . '">' . $txt['downloads_text_approve']  . '</a>';
                echo '<br /><br /><a href="' . $scripturl . '?action=downloads;sa=delcomment;id=' . $comment['ID_COMMENT'] . '">' . $txt['downloads_text_delcomment'] . '</a></td>';
                echo '</tr>';

            }
            
            
        if ($context['downloads_total'] > 0)
        {   
            echo '<tr class="titlebg">
                    <td align="left" colspan="5">
                    ' . $txt['downloads_text_pages'];
    
    
                    
                    echo $context['page_index'] ;
    
            echo '
                    </td>
                </tr>';
        }
        
        echo '
            </table><br />';

            echo '<b>' . $txt['downloads_form_reportedcomments'] . '</b><br />
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                <td>' . $txt['downloads_rep_filelink'] . '</td>
                <td>' . $txt['downloads_rep_org_comment']  . '</td>
                <td>' . $txt['downloads_rep_comment']  . '</td>
                <td>' . $txt['downloads_app_date'] . '</td>
                <td>' . $txt['downloads_rep_reportby'] . '</td>
                <td>' . $txt['downloads_text_options'] . '</td>
                </tr>';

            // List all reported comments
            foreach ($context['downloads_reports'] as $i => $report)
            {

                echo '<tr class="windowbg2">';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=' . $report['ID_FILE'] . '#c' . $report['ID_COMMENT'] . '">' . $txt['downloads_rep_viewdownload'] .'</a></td>';
                echo '<td>' . $report['OringalComment'] . '</td>';
                echo '<td>' . $report['comment'] . '</td>';
                echo '<td>' . timeformat($report['date']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=profile;u=' . $report['ID_MEMBER'] . '">'  . $report['realName'] . '</a></td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=deletecomment;id=' . $report['ID_COMMENT'] . ';ret=admin">' . $txt['downloads_text_delcomment'] . '</a>
                <br /><a href="' . $scripturl . '?action=downloads;sa=delcomreport;id=' . $report['ID'] . '">' . $txt['downloads_rep_delete'] . '</a>
                </td>';
                echo '</tr>';

            }


echo '
            </table>
            </td>
        </tr>
</table>';

}


function template_search()
{
    global $scripturl, $txt, $context, $settings;
    
echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';


            echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">&nbsp;</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';

    echo '
<form method="post" action="', $scripturl, '?action=downloads;sa=search2">
<table border="0" cellpadding="2" cellspacing="0" width="90%" class="tborder" align="center">
  <tr>
    <td width="100%" colspan="2"  align="center" class="catbg">
    <b>' .$txt['downloads_search_download'] . '</b></td>
  </tr>
  <tr class="windowbg2">
    <td width="50%"   align="right"><b>' . $txt['downloads_search_for'] . '</b>&nbsp;</td>
    <td width="50%" ><input type="text" name="searchfor" size= "50" />
    </td>
  </tr>
  <tr class="windowbg2" align="center">
    <td colspan="2"><input type="checkbox" name="searchtitle" checked="checked" />' . $txt['downloads_search_title'] . '&nbsp;<input type="checkbox" name="searchdescription" checked="checked" />' . $txt['downloads_search_description'] . '&nbsp;
    <input type="checkbox" name="searchkeywords" />' . $txt['downloads_search_keyword'] . '</td>
  </tr>
  <tr class="windowbg2">
    <td colspan="2" align="center">
    <hr />
    <b>',$txt['downloads_search_advsearch'],'</b><br />
    <hr />
    
    </td>
  </tr>
    <tr class="windowbg2">
    <td width="30%"  align="right">' . $txt['downloads_text_category'] . '&nbsp;</td>
    <td width="70%">
        <select name="cat">
        <option value="0">' . $txt['downloads_text_catnone'] . '</option>
    ';
     
    foreach ($context['downloads_cat'] as $i => $category)
    {
        echo '<option value="' . $category['ID_CAT']  . '" >' . $category['title'] . '</option>';
    }
    
    echo '</select></td>
    </tr>
    <tr class="windowbg2">
     <td width="30%"  align="right">' . $txt['downloads_search_daterange']. '&nbsp;</td>
    <td width="70%">
        <select name="daterange">
        <option value="0">' . $txt['downloads_search_alltime']  . '</option>
        <option value="30">' . $txt['downloads_search_days30']  . '</option>
        <option value="60">' . $txt['downloads_search_days60']  . '</option>
        <option value="90">' . $txt['downloads_search_days90']  . '</option>
        <option value="180">' . $txt['downloads_search_days180']  . '</option>
        <option value="365">' . $txt['downloads_search_days365']  . '</option>
        
</select></td>
    </tr>
    
    <tr class="windowbg2">
     <td width="30%"  align="right">' . $txt['downloads_search_membername']. '&nbsp;</td>
    <td width="70%">
        <input type="text" name="pic_postername" id="pic_postername" value="" />
      <a href="', $scripturl, '?action=findmember;input=pic_postername;quote=1;sesc=', $context['session_id'], '" onclick="return reqWin(this.href, 350, 400);"><img src="', $settings['images_url'], '/icons/assist.gif" alt="', $txt['find_members'], '" /></a> 
      <a href="', $scripturl, '?action=findmember;input=pic_postername;quote=1;sesc=', $context['session_id'], '" onclick="return reqWin(this.href, 350, 400);">', $txt['find_members'], '</a>
      </td>
    </tr>
    
    
  <tr>
    <td width="100%" colspan="2"  align="center" class="windowbg2"><br />
    <input type="submit" value="' . $txt['downloads_search'] . '" name="submit" />
    
    <br /></td>

  </tr>
</table>
</form>
<p align="center"><a href="' . $scripturl . '?action=downloads">' . $txt['downloads_text_returndownload'] . '</a></p>
<br />

';
    downloads_copyright();
}
function template_search_results()
{
    global $context, $modSettings, $scripturl, $txt, $db_passwd, $ID_MEMBER;

    // Get the permissions for the user
    $g_add = allowedTo('downloads_add');
    $g_manage = allowedTo('downloads_manage');
    $g_edit_own = allowedTo('downloads_edit');
    $g_delete_own = allowedTo('downloads_delete');

    echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';
    
            echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">',$txt['downloads_searchresults'],'</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';

    
    // Show table header
    $count = 0;
        
        echo '<br /><table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                        <tr class="catbg">';

            if (!empty($modSettings['down_set_t_title']))
            {   
                echo  '<td>', $txt['downloads_cat_title'], '</td>';
                $count++;
            }

            if (!empty($modSettings['down_set_t_rating']))
            {
                echo '<td>', $txt['downloads_cat_rating'], '</td>';
                $count++;
            }
            
            if (!empty($modSettings['down_set_t_views']))
            {
                echo '<td>', $txt['downloads_cat_views'], '</td>';
                $count++;
            }
                
                
            if (!empty($modSettings['down_set_t_downloads']))
            {
                echo '<td>', $txt['downloads_cat_downloads'] , '</td>'; 
                $count++;
            }
                
            if (!empty($modSettings['down_set_t_filesize']))
            {
                echo '<td>',$txt['downloads_cat_filesize'], '</td>';
                $count++;
            }
                
            if (!empty($modSettings['down_set_t_date']))
            {
                echo '<td>',$txt['downloads_cat_date'], '</td>';
                $count++;
            }
                
            if (!empty($modSettings['down_set_t_comment']))
            {
                echo '<td>',$txt['downloads_cat_comments'],'</td>';
                $count++;
            }
            
            if (!empty($modSettings['down_set_t_username']))
            {
                echo '<td>',$txt['downloads_cat_membername'],'</td>';
                $count++;
            }
            
            
            // Options
            if ($g_manage ||  ($g_delete_own ) || ($g_edit_own) )
            {
                echo '<td>',$txt['downloads_cat_options'],'</td>';
                $count++;
            }

        echo '</tr>';
        

    foreach ($context['downloads_files'] as $i => $file)
    {

            echo '<tr>';
            
            if (!empty($modSettings['down_set_t_title']))   
                echo  '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '">', $file['title'], '</a></td>';
            
            if (!empty($modSettings['down_set_t_rating']))
                echo '<td>', GetStarsByPrecent(($file['totalratings'] != 0) ? ($file['rating'] / ($file['totalratings']* 5) * 100) : 0), '</td>';
            
            if (!empty($modSettings['down_set_t_views']))
                echo '<td>', $file['views'], '</td>';
                
            if (!empty($modSettings['down_set_t_downloads']))
                echo '<td>', $file['totaldownloads'], '</td>';          
                
            if (!empty($modSettings['down_set_t_filesize']))
                echo '<td>', format_size($file['filesize'], 2) . '</td>';
                
            if (!empty($modSettings['down_set_t_date']))    
                echo '<td>', timeformat($file['date']), '</td>';
                
            if (!empty($modSettings['down_set_t_comment'])) 
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '">', $file['commenttotal'], '</a></td>';
            if (!empty($modSettings['down_set_t_username']))
            {
                if ($file['realName'] != '')
                    echo '<td><a href="' . $scripturl . '?action=profile;u=' . $file['ID_MEMBER'] . '">'  . $file['realName'] . '</a></td>';
                else 
                    echo '<td>', $txt['downloads_guest'], '</td>';
            }
            
            // Options
            if ($g_manage ||  ($g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER) || ($g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER) )
            {
                echo '<td>';
                if ($g_manage)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=unapprove;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_unapprove'] . '</a>';
                if ($g_manage || $g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=edit;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_edit'] . '</a>';
                if ($g_manage || $g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_delete'] . '</a>';
    
                echo '</td>';
            }


            
            echo '</tr>';
        
    }

        

        if ($context['downloads_total'] > 0)
        {
            
            $q =  base64_encode($context['downloads_search_query']);
            $w = base64_encode($context['downloads_where']);
            
            // Security check to make sure it has not been altered
            // Uses the db password as the secert.
            $qs = sha1($q . $db_passwd);
            $ws = sha1($w . $db_passwd);
            
            echo '<tr class="titlebg">
                    <td align="left" colspan="' . $count . '">
                    ' . $txt['downloads_text_pages'];

                    
                    $context['page_index'] = constructPageIndex($scripturl . '?action=downloads;sa=search2;q=' .$q . ';w=' . $w . ';qs=' .$qs . ';ws=' . $ws, $_REQUEST['start'], $context['downloads_total'], 10);
                    
                    echo $context['page_index'];
    
            echo '
                    </td>
                </tr>';
        }
        
        
        // Show return to downloads link and Show add download if they can
        echo '
                <tr class="titlebg"><td align="center" colspan="' . $count . '">';
                if ($g_add)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=add">' . $txt['downloads_text_adddownload'] . '</a><br />';

                echo '
                <a href="' . $scripturl . '?action=downloads">' . $txt['downloads_text_returndownload'] . '</a></td>
            </tr>';


    echo '</table><br /><br /><br />';
    
echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';
    
    downloads_copyright();
}

function template_myfiles()
{
    global $context, $modSettings, $scripturl, $txt, $ID_MEMBER, $settings;

    // Get the permissions for the user
    $g_add = allowedTo('downloads_add');
    $g_manage = allowedTo('downloads_manage');
    $g_edit_own = allowedTo('downloads_edit');
    $g_delete_own = allowedTo('downloads_delete');

    echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';
    
    
            echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">', $context['downloads_userdownloads_name'],'</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';
    // Show table header
        // $count = 0;

        echo '<table cellspacing="0" cellpadding="0" border="0" align="center" width="90%" class="tborder">';
            echo '<tr class="titlebg" style="padding: 5px;">';


        // Show page listing
        // if ($context['downloads_total'] > 0) 
    echo '<td align="right">
                    ' . $txt['downloads_text_pages'];
            
                    echo $context['page_index'];
    
        
            echo '
                </td><tr><td>&nbsp;</td></tr><tr><td colspan="2" align="center">';

    foreach ($context['downloads_files'] as $i => $file)
    {

echo '<table border="0" align="center" width="90%" cellspacing="0" cellpadding="0" class="tborder">';

    if ($file['approved'] != 1)
        echo '<tr style="background-color: #f58c8c; padding: 5px;"><td colspan="3" width="100%" align="center" valign="middle" style="color: #e70202; border-bottom: 1px groove black;"><b>Download Awaiting Approval</b></td></tr>';

                    echo '<tr class="titlebg"><td width="25%" align="left" valign="middle"><span style="font-size: 10px;">';
            // Options
            if ($g_manage ||  ($g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER) || ($g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER) )
            {
                if ($g_manage)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=unapprove;id=' . $file['ID_FILE'] . '" style="font-size: 10px;">' . $txt['downloads_text_unapprove'] . '</a>';
                if ($g_manage || $g_edit_own && $file['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=edit;id=' . $file['ID_FILE'] . '" style="font-size: 10px;">' . $txt['downloads_text_edit'] . '</a>';
                if ($g_manage || $g_delete_own && $file['ID_MEMBER'] == $ID_MEMBER)
                    echo '&nbsp;<a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $file['ID_FILE'] . '" style="font-size: 10px;">' . $txt['downloads_text_delete'] . '</a>';
            }
            echo '</span></td><td width="50%" align="center" valign="middle" style="padding-bottom: 5px;">';
            
            echo '<span style="color: #000000; font-size: 16px;">';
            if ($modSettings['down_set_file_title'])
                
                echo  '<strong><a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $file['ID_FILE'], '" style="font-size: 18px;">', $file['title'], '</a></strong>';
            
            echo '</span><br/><span style="font-size: 10px; color: #CCCCCC;"><strong><a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $file['ID_FILE'], '" style="font-size: 12px;">', $file['orginalfilename'], '</a></strong> ';

// We are dealing with the Downloads $modSettings, not the Category $modSettings...
            if (!empty($modSettings['down_set_file_showfilesize']) || !empty($modSettings['down_set_file_downloads']))
            {
                    echo '(';
                    
                    if (!empty($modSettings['down_set_file_showfilesize']))
                        echo format_size($file['filesize'], 2);
                        
                    if (!empty($modSettings['down_set_file_downloads']) && !empty($modSettings['down_set_file_showfilesize']))
                        echo ' - Downloaded ', $file['totaldownloads'], ' times';
                    else if (!empty($modSettings['down_set_file_downloads']) && empty($modSettings['down_set_file_showfilesize']))
                        echo 'Downloaded ', $file['totaldownloads'], ' times';                      

                        echo ')';
            }
                echo '</span></td><td width="25%" align="right" valign="middle">';
                // Check if rating is allowed for these files in the Category...
    if ($modSettings['down_set_file_showrating']) {
            if ($modSettings['down_show_ratings'] == true && $context['downloads_cat_norate'] != 1)
                echo '' . GetStarsByPrecent($file['actualrating'] != 0 ? $file['actualrating'] : 0);
                if ($modSettings['down_set_file_rating_count'])
                    if ($file['totalratings'] != 0)
                    echo '<br/><b style="font-size: 10px; font-weight: normal;">Rated <b>', ($file['totalratings'] > 1 ? $file['totalratings'] . '</b> times</b>' : $file['totalratings'] . '</b> time');
    }
            echo '</td></tr><tr><td colspan="3" align="center" valign="middle" class="downBody1"><span style="font-size: 12px; color: #CCCCCC;">';
            
            
            // Get the Date that the user added their download
            if ($modSettings['down_set_file_date'])
                echo 'Download Added: ', timeformat($file['date']), '';

        echo '</span></td></tr>';

        if ($modSettings['down_set_file_desc']) {
            
            echo '<tr><td colspan="3" align="center" valign="middle" class="downBody2">';
                    
            if (!empty($file['screenshot']))
                echo '<img src="' . $modSettings['down_url'] . 'screenshots/' . $file['screenshot'] . '" /><br/>';
            
            echo parse_bbc($file['description']), '</td></tr>';
        
        }
                    
        echo '<tr class="titlebg">';
        
        echo '<td align="left" valign="middle">';
        
            if (!empty($file['allowcomments'])) {
                if ($file['commenttotal'] >= 1)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=view;down=', $file['ID_FILE'], '">Comments';
            if (!empty($modSettings['down_set_t_comment'])) 
            {   
                if ($file['commenttotal'] >= 1)
                    echo ' (', $file['commenttotal'], ')</a>';
            }
        }
        
        echo '</td><td align="center" valign="middle" width="20%"><a href="' . $scripturl . '?action=downloads;sa=downfile;id=', $file['ID_FILE'], '"><img src="' . $settings['images_url'] . '/downloads.png"  width="122" height="32" border="0" /></a></td><td align="right" valign="middle">';
        
            if (!empty($file['allowcomments'])) {
                echo '<a href="' . $scripturl . '?action=downloads;sa=comment;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_addcomment'] . '</a>';          
            }
        
        echo '</td></tr></table><br/><br/>';
}
// END OF COOL LAYOUT!

                    echo '</td>
                </tr><tr class="titlebg" style="padding: 5px;">';
                
            // Do the Pages view at the bottom...
            echo '<td align="right">
                    ' . $txt['downloads_text_pages'];
            
                    echo $context['page_index'];
    
        
            echo '
                    </td>
                </tr>';
    
        
        // Show return to downloads link and Show add download if they can
        echo '<tr class="titlebg"><td align="center">';
                
                if ($g_add)
                    echo '<a href="' . $scripturl . '?action=downloads;sa=add">' . $txt['downloads_text_adddownload'] . '</a><br />';

                echo '
                <a href="', $scripturl, '?action=downloads">', $txt['downloads_text_returndownload'], '</a></td>
            </tr>
            </table><br /><br /><br />';

        
echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';

    downloads_copyright();
}
function template_edit_comment()
{
    global $context, $scripturl, $txt, $settings, $modSettings;


    // Load the spell checker?
    if ($context['show_spellchecking'])
        echo '
                                    <script language="JavaScript" type="text/javascript" src="', $settings['default_theme_url'], '/spellcheck.js"></script>';


    echo '
<form method="post" name="cprofile" id="cprofile" action="', $scripturl, '?action=downloads&sa=editcomment2">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td width="50%" colspan="2"  align="center" class="catbg">
    <b>', $txt['downloads_text_editcomment'], '</b></td>
  </tr>

   <tr>
   <td class="windowbg2" colspan="2" align="center">
   <table>
   ';
   theme_postbox($context['downloads_comment']['comment']);
   echo '</table></td>
   </tr>

  <tr>
    <td width="28%" colspan="2"  align="center" class="windowbg2">
    <input type="hidden" name="id" value="' . $context['downloads_comment']['ID_COMMENT'] . '" />';

    // Check if comments are autoapproved
    if (allowedTo('downloads_autocomment') == false)
            echo $txt['downloads_text_commentwait'] . '<br />';

    if ($context['show_spellchecking'])
        echo '
                                    <input type="button" value="', $txt['spell_check'], '" onclick="spellCheck(\'cprofile\', \'comment\');" />';


echo '
    <input type="submit" value="' . $txt['downloads_text_editcomment'] . '" name="submit" /></td>

  </tr>
</table>
</form>';


    if ($context['show_spellchecking'])
            echo '<form action="', $scripturl, '?action=spellcheck" method="post" accept-charset="', $context['character_set'], '" name="spell_form" id="spell_form" target="spellWindow"><input type="hidden" name="spellstring" value="" /></form>';
    

    downloads_copyright();
}

function template_view_rating()
{
    global  $context, $settings, $scripturl, $txt;
    

    echo '<table cellspacing="0" cellpadding="5" border="0" align="center" width="50%" class="tborder">
                <tr class="titlebg">
                    <td align="center" colspan="3">' . $txt['downloads_form_viewratings'] . '</td>
                </tr>
                <tr class="titlebg">
                    <td align="center">' . $txt['downloads_app_membername'] . '</td>
                    <td align="center">' . $txt['downloads_text_rating'] . '</td>
                    <td align="center">' . $txt['downloads_text_options'] . '</td>
                </tr>';

    foreach ($context['downloads_rating'] as $i => $rating)
    {
        echo '<tr class="windowbg2">
                <td align="center"><a href="' . $scripturl . '?action=profile;u=' . $rating['ID_MEMBER'] . '">'  . $rating['realName'] . '</a></td>
                <td align="center">';
                $max_num_stars = 5;
        // Show the star images
        for($i=0; $i < $max_num_stars; $i++) {
            if ($i < $rating['value'])
                echo '<img src="', $settings['images_url'], '/starFull.png" alt="*" border="0" />';
            else                        
                echo '<img src="', $settings['images_url'], '/starEmpty.png" alt="*" border="0" />';
        }

        echo '</td>
              <td align="center"><a href="' . $scripturl . '?action=downloads;sa=delrating;id=' . $rating['ID'] . '">'  . $txt['downloads_text_delete'] . '</a></td>
              </tr>';
    }
    echo '
            <tr class="titlebg">
                <td align="center" colspan="3"><a href="' . $scripturl . '?action=downloads;sa=view;down=' . $context['downloads_id'] . '">' . $txt['downloads_text_returnfile'] . '</a></td>
            </tr>
    </table>';

    
}
function template_stats()
{
    global $settings, $context, $txt, $scripturl;
    
echo '
        <div style="padding: 3px;">', theme_linktree(), '</div>';

            echo '<table border="0" cellspacing="0" cellpadding="4" align="center" width="90%" class="tborder" >
                    <tr class="titlebg">
                        <td align="center">&nbsp;</td>
                    </tr>
                    </table>
                <table border="0" cellpadding="0" cellspacing="0" align="center" width="90%">
                        <tr>
                            <td style="padding-right: 1ex;" align="right" >
                        <table cellpadding="0" cellspacing="0" align="right">
                                    <tr>
                        ', DoToolBarStrip($context['downloads']['buttons'], 'top'), '
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                <br />';
    
echo '<table border="0" cellpadding="1" cellspacing="0" width="90%" align="center" class="tborder">
            <tr>
                <td class="titlebg" colspan="2" align="center">', $txt['downloads_stats_title'], '</td>
            </tr>
            <tr>
                <td class="catbg" colspan="2">&nbsp;</td>
            </tr>
            <tr>
                <td class="windowbg2" width="50%" valign="top">
                    <table border="0" cellpadding="1" cellspacing="0" width="100%">
                        <tr>
                            <td class="windowbg2" width="50%">', $txt['downloads_stats_totalfiles'] ,  '</td>
                            <td class="windowbg2" width="50%"  align="right">', comma_format($context['total_files']) , '</td>
                        </tr>
                        <tr>
                            <td class="windowbg2" width="50%">', $txt['downloads_stats_totalviews'] ,  '</td>
                            <td class="windowbg2" width="50%"  align="right">', comma_format($context['total_views']) , '</td>
                        </tr>

                    </table>
                </td>
                <td class="windowbg2" width="50%" valign="top">
                    <table border="0" cellpadding="1" cellspacing="0" width="100%">
                        <tr>
                            <td class="windowbg2" width="50%">', $txt['downloads_stats_totalcomments'] , '</td>
                            <td class="windowbg2" width="50%"  align="right">', comma_format($context['total_comments']), '</td>
                        </tr>
                        <tr>
                            <td class="windowbg2" width="50%">', $txt['downloads_stats_totalfize'] ,  '</td>
                            <td class="windowbg2" width="50%" align="right">', $context['total_filesize'] , '</td>
                        </tr>
                    </table>
                </td>

            </tr>
            <tr>
                <td class="catbg" width="50%"><b>', $txt['downloads_stats_viewed'], '</b></td>
                <td class="catbg" width="50%"><b>', $txt['downloads_stats_toprated'], '</b></td>
            </tr>
            <tr>
                <td class="windowbg2" width="50%" valign="top">
                    <table border="0" cellpadding="1" cellspacing="0" width="100%">';
                        foreach ($context['top_viewed'] as $file)
                        {
                            echo '<tr>
                                    <td width="60%" valign="top">', $file['link'], '</td>
                                    <td width="20%" align="left" valign="top">', $file['views'] > 0 ? '<img src="' . $settings['images_url'] . '/bar.gif" width="' . $file['percent'] . '" height="15" alt="" />' : '&nbsp;', '</td>
                                    <td width="20%" align="right" valign="top">', $file['views'], '</td>
                                </tr>';
                        }
    echo '
                    </table>
                </td>
                <td class="windowbg2" width="50%" valign="top">
                    <table border="0" cellpadding="1" cellspacing="0" width="100%">';
                        foreach ($context['top_rating'] as $file)
                        {
                            echo '<tr>
                                    <td width="60%" valign="top">', $file['link'], '</td>
                                    <td width="20%" align="left" valign="top">', $file['rating'] > 0 ? '<img src="' . $settings['images_url'] . '/bar.gif" width="' . $file['percent'] . '" height="15" alt="" />' : '&nbsp;', '</td>
                                    <td width="20%" align="right" valign="top">', $file['rating'], '</td>
                                </tr>';
                        }
    echo '
                    </table>
                </td>
            </tr>
            <tr>
                <td class="catbg" width="50%"><b>', $txt['downloads_stats_mostcomments'], '</b></td>
                <td class="catbg" width="50%"><b>',$txt['downloads_stats_last'], '</b></td>
            </tr>
            <tr>
                <td class="windowbg2" width="50%" valign="top">
                    <table border="0" cellpadding="1" cellspacing="0" width="100%">';
                        foreach ($context['most_comments'] as $file)
                        {
                            echo '<tr>
                                    <td width="60%" valign="top">', $file['link'], '</td>
                                    <td width="20%" align="left" valign="top">', $file['commenttotal'] > 0 ? '<img src="' . $settings['images_url'] . '/bar.gif" width="' . $file['percent'] . '" height="15" alt="" />' : '&nbsp;', '</td>
                                    <td width="20%" align="right" valign="top">', $file['commenttotal'], '</td>
                                </tr>';
                        }
                        
    echo '
                    </table>
                </td>
                <td class="windowbg2" width="50%" valign="top">
                    <table border="0" cellpadding="1" cellspacing="0" width="100%">';
                        foreach ($context['last_upload'] as $file)
                        {
                            echo '<tr>
                                    <td width="100%" colspan="3" valign="top">', $file['link'], '</td>
                                </tr>';
                        }
    echo '
                    </table>
                </td>
            </tr>
            
            <tr>
                <td class="titlebg" colspan="2" align="center"><a href="' . $scripturl . '?action=downloads">' . $txt['downloads_text_returndownload'] . '</a></td>
            </tr>
        </table>';
}


function template_filespace()
{
    global $scripturl, $txt, $context;
    
    echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>' . $txt['downloads_filespace'] . '</td>
        </tr>

        <tr class="windowbg">
            <td>
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="windowbg">
                    <td colspan="3" align="center"><b>' .$txt['downloads_filespace_groupquota_title'] . '</b></td>
                </tr>
            <tr class="catbg">
                <td>' . $txt['downloads_filespace_groupname'] . '</td>
                <td>' .$txt['downloads_filespace_limit']  . '</td>
                <td>' .  $txt['downloads_text_options']  . '</td>
                </tr>';
        
        // Show the member groups
            foreach ($context['downloads_membergroups'] as $i => $group)
            {

                echo '<tr class="windowbg2">';
                echo '<td>'  . $group['groupName'] . '</td>';
                echo '<td>' . format_size($group['totalfilesize'], 2) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=deletequota;id=' . $group['ID_GROUP'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';

            }
        
            // Show Regular members
            foreach ($context['downloads_reggroup'] as $i => $group)
            {
                echo '<tr class="windowbg2">';
                echo '<td>', $txt['membergroups_members'], '</td>';
                echo '<td>' . format_size($group['totalfilesize'], 2) . '</td>';
                echo '<td><a href="',$scripturl, '?action=downloads;sa=deletequota;id=' . $group['ID_GROUP'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';

            }
            
            
    
        echo '
                <tr class="windowbg">
                    <td colspan="3" align="center">
                        <form method="post" action="' . $scripturl . '?action=downloads;sa=addquota">
                        ' . $txt['downloads_filespace_groupname']  . '&nbsp;<select name="groupname">
                                <option value="0">', $txt['membergroups_members'], '</option>';
                                foreach ($context['groups'] as $group)
                                    echo '<option value="', $group['ID_GROUP'], '">', $group['groupName'], '</option>';
                            
                            echo '</select><br />' . $txt['downloads_filespace_limit'] . '&nbsp;&nbsp;&nbsp;&nbsp;<input type="text" name="filelimit" /> (bytes)
                            <br /><br />
                        <input type="submit" value="' . $txt['downloads_filespace_addquota'] . '" />
                        </form>
                    </td>
                </tr>
        
                </table>
            </td>
        </tr>
        <tr class="windowbg">
            <td>
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                <td>' . $txt['downloads_app_membername'] . '</td>
                <td>' . $txt['downloads_text_options'] . '</td>
                <td>' . $txt['downloads_filespace_filesize']  . '</td>
                </tr>';
    
    
    // List all members filespace usage
    foreach ($context['downloads_members'] as $i => $member)
    {

        echo '<tr class="windowbg2">';
        echo '<td><a href="' . $scripturl . '?action=profile;u=' . $member['ID_MEMBER'] . '">'  . $member['realName'] . '</a></td>';
        echo '<td><a href="' . $scripturl . '?action=downloads;sa=filelist;id=' . $member['ID_MEMBER'] . '">'  . $txt['downloads_filespace_list'] . '</a></td>';
        echo '<td>' . format_size($member['totalfilesize'], 2) . '</td>';
        echo '</tr>';

    }
    
    
            echo '<tr class="titlebg">
                    <td align="left" colspan="3">
                    ' . $txt['downloads_text_pages'];
    
                            
                    echo $context['page_index'];
    
            echo '
                    </td>
                </tr>
            <tr class="titlebg">
                    <td align="left" colspan="3">
                    <form method="post" action="' . $scripturl . '?action=downloads;sa=recountquota">
                    <input type="submit" value="' . $txt['downloads_filespace_recount'] . '" />
                    </form>
                    </td>
            </tr>
            </table>
            </td>
        </tr>
</table>';

}
function template_filelist()
{
    global $scripturl, $txt, $context, $modSettings;
        

    echo '

    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>' . $txt['downloads_filespace_list_title'] . ' - ' . $context['downloads_filelist_realName'] . '</td>
        </tr>
        <tr class="windowbg">
            <td>
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
                <tr class="catbg">
                <td>' . $txt['downloads_app_title'] . '</td>
                <td>' . $txt['downloads_filespace_filesize']  . '</td>
                <td>' . $txt['downloads_text_options'] . '</td>
                
                </tr>';

        // List all user's downloads
            foreach ($context['downloads_files'] as $i => $file)
            {

                echo '<tr class="windowbg2">';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=view;down=' . $file['ID_FILE'] . '">', $file['title'],'</a></td>';
                echo '<td>' . format_size($file['filesize'], 2) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=delete;id=' . $file['ID_FILE'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';

            }
            

        if ($context['downloads_total'] > 0)
        {       
            echo '<tr class="titlebg">
                    <td align="left" colspan="3">
                    ' . $txt['downloads_text_pages'];
    
        
                    
                    echo $context['page_index'];
    
            echo '
                    </td>
                </tr>';
        }
        
echo '<tr class="titlebg">
                    <td align="center" colspan="3">
                    <a href="' . $scripturl . '?action=downloads;sa=filespace">' . $txt['downloads_filespace'] . '</a>
                    </td>
        </tr>

            </table>
            </td>
        </tr>
</table>';
}

function template_catpermlist()
{
    global $scripturl, $txt, $context;
    
    echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>' . $txt['downloads_text_catpermlist']. '</td>
        </tr>

        <tr class="windowbg">
            <td>
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
            <tr class="catbg">
                <td>' . $txt['downloads_filespace_groupname'] . '</td>
                <td>' . $txt['downloads_text_category']  . '</td>
                <td>' .  $txt['downloads_perm_view']  . '</td>
                <td>' .  $txt['downloads_perm_add']  . '</td>
                <td>' .  $txt['downloads_perm_edit']  . '</td>
                <td>' .  $txt['downloads_perm_delete']  . '</td>
                <td>' .  $txt['downloads_perm_addcomment']  . '</td>
                <td>' .  $txt['downloads_text_options']  . '</td>
                </tr>';
        
        // Show the member groups
            foreach ($context['downloads_membergroups'] as $i => $row)
            {

                echo '<tr class="windowbg2">';
                echo '<td>'  . $row['groupName'] . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catperm;cat=' . $row['ID_CAT'] . '">'  . $row['catname'] . '</a></td>';
                echo '<td>' . ($row['view'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['editfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['delfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addcomment'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catpermdelete;id=' . $row['ID'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';

            }
            
            // Show Regular members
            foreach ($context['downloads_regmem'] as $i => $row)
            {

                echo '<tr class="windowbg2">';
                echo '<td>'  . $txt['membergroups_members'] . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catperm;cat=' . $row['ID_CAT'] . '">'  . $row['catname'] . '</a></td>';
                echo '<td>' . ($row['view'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['editfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['delfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addcomment'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catpermdelete;id=' . $row['ID'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';
            }
            
            // Show Guests
            foreach ($context['downloads_guestmem'] as $i => $row)
            {

                echo '<tr class="windowbg2">';
                echo '<td>'  . $txt['membergroups_guests'] . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catperm;cat=' . $row['ID_CAT'] . '">'  . $row['catname'] . '</a></td>';
                echo '<td>' . ($row['view'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['editfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['delfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addcomment'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catpermdelete;id=' . $row['ID'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';
            }
            
    
        echo '

        
                </table>
            </td>
        </tr>
    
</table>';  
}

function template_catperm()
{
    global $scripturl, $txt, $context;
    
    echo '
    <table border="0" width="80%" cellspacing="0" align="center" cellpadding="4" class="tborder">
        <tr class="titlebg">
            <td>' .$txt['downloads_text_catperm'] . ' - ' . $context['downloads_cat_name']  . '</td>
        </tr>
        <tr class="windowbg">
        <td>
        <form method="post" action="' . $scripturl . '?action=downloads;sa=catperm2">
        <table align="center" class="tborder">
        <tr class="titlebg">
            <td colspan="2">'  . $txt['downloads_text_addperm'] . '</td>
        </tr>

              <tr class="windowbg2">
                <td align="right"><b>' . $txt['downloads_filespace_groupname'] . '</b>&nbsp;</td>
                <td><select name="groupname">
                                <option value="-1">' . $txt['membergroups_guests'] . '</option>
                                <option value="0">' . $txt['membergroups_members'] . '</option>';
                                foreach ($context['groups'] as $group)
                                    echo '<option value="', $group['ID_GROUP'], '">', $group['groupName'], '</option>';
                            
                            echo '</select>
                </td>
              </tr>
              <tr class="windowbg2">
                <td align="right"><input type="checkbox" name="view" checked="checked" /></td>
                <td><b>' . $txt['downloads_perm_view'] .'</b></td>
              </tr>
              <tr class="windowbg2">
                <td align="right"><input type="checkbox" name="add" checked="checked" /></td>
                <td><b>' . $txt['downloads_perm_add'] .'</b></td>
              </tr>
              <tr class="windowbg2">
                <td align="right"><input type="checkbox" name="edit" checked="checked" /></td>
                <td><b>' . $txt['downloads_perm_edit'] .'</b></td>
              </tr>
              <tr class="windowbg2">
                <td align="right"><input type="checkbox" name="delete" checked="checked" /></td>
                <td><b>' . $txt['downloads_perm_delete'] .'</b></td>
              </tr>
              <tr class="windowbg2">
                <td align="right"><input type="checkbox" name="addcomment" checked="checked" /></td>
                <td><b>' . $txt['downloads_perm_addcomment'] .'</b></td>
              </tr>
              <tr class="windowbg2">
                <td align="center" colspan="2">
                <input type="hidden" name="cat" value="' . $context['downloads_cat'] . '" />
                <input type="submit" value="' . $txt['downloads_text_addperm'] . '" /></td>

              </tr>
        </table>
        </form>
        </td>
        </tr>
            <tr class="windowbg">
            <td>
            <table cellspacing="0" cellpadding="10" border="0" align="center" width="90%" class="tborder">
            <tr class="catbg">
                <td>' . $txt['downloads_filespace_groupname'] . '</td>
                <td>' .  $txt['downloads_perm_view']  . '</td>
                <td>' .  $txt['downloads_perm_add']  . '</td>
                <td>' .  $txt['downloads_perm_edit']  . '</td>
                <td>' .  $txt['downloads_perm_delete']  . '</td>
                <td>' .  $txt['downloads_perm_addcomment']  . '</td>
                <td>' .  $txt['downloads_text_options']  . '</td>
                </tr>';
        
        // Show the member groups
            foreach ($context['downloads_membergroups'] as $i => $row)
            {

                echo '<tr class="windowbg2">';
                echo '<td>', $row['groupName'], '</td>';
                echo '<td>' . ($row['view'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['editfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['delfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addcomment'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catpermdelete;id=' . $row['ID'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';

            }
            
            // Show Regular members 
            foreach ($context['downloads_reggroup'] as $i => $row)
            {

                echo '<tr class="windowbg2">';
                echo '<td>', $txt['membergroups_members'], '</td>';
                echo '<td>' . ($row['view'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['editfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['delfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addcomment'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catpermdelete;id=' . $row['ID'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';
            }
            
            // Show Guests
            foreach ($context['downloads_guestgroup'] as $i => $row)
            {

                echo '<tr class="windowbg2">';
                echo '<td>', $txt['membergroups_guests'], '</td>';
                echo '<td>' . ($row['view'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['editfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['delfile'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td>' . ($row['addcomment'] ? $txt['downloads_perm_allowed'] : $txt['downloads_perm_denied']) . '</td>';
                echo '<td><a href="' . $scripturl . '?action=downloads;sa=catpermdelete;id=' . $row['ID'] . '">' . $txt['downloads_text_delete'] . '</a></td>';
                echo '</tr>';
            }
            
    
        echo '

        
                </table>
            </td>
        </tr>
</table>';  
}

function GetStarsByPrecent($percent)
{
    global $settings, $txt, $context;
    
    $starStr = '';
    
    if ($percent == 0) {
        return $txt['downloads_text_notrated'];
    } else if ($percent <= 20) {
        $starStr = '<img src="' . $settings['images_url'] . '/starFull.png" alt="*" border="0" />';
        $starStr .= str_repeat('<img src="' . $settings['images_url'] . '/starEmpty.png" alt="*" border="0" />', 4);
        return $starStr;
    } else if ($percent <= 40) {
        $starStr = str_repeat('<img src="' . $settings['images_url'] . '/starFull.png" alt="*" border="0" />', 2);
        $starStr .= str_repeat('<img src="' . $settings['images_url'] . '/starEmpty.png" alt="*" border="0" />', 3);
        return $starStr;
    } else if ($percent <= 60) {
        $starStr = str_repeat('<img src="' . $settings['images_url'] . '/starFull.png" alt="*" border="0" />', 3);
        $starStr .= str_repeat('<img src="' . $settings['images_url'] . '/starEmpty.png" alt="*" border="0" />', 2);
        return $starStr;
    } else if ($percent <= 80) {
        $starStr = str_repeat('<img src="' . $settings['images_url'] . '/starFull.png" alt="*" border="0" />', 4);
        $starStr .= str_repeat('<img src="' . $settings['images_url'] . '/starEmpty.png" alt="*" border="0" />', 1);
        return $starStr;
    } else if ($percent <= 100) {
        return str_repeat('<img src="' . $settings['images_url'] . '/starFull.png" alt="*" border="0" />', 5);
    }
}
function downloads_copyright()
{

    // Do NOT CHANGE THIS CODE UNLESS you have COPYRIGHT Link Removal
    //http://www.smfhacks.com/downloads-linkremoval.php
    
    //Copyright link must remain. To remove you need to purchase link removal at smfhacks.com
    echo '<div align="center"><!--Link must remain or contact me to pay to remove.--><span class="smalltext">Powered by: <a href="http://www.smfhacks.com" target="_blank">Download System</a></span><!--End Copyright link--></div>';

}

?>
