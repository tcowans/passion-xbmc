
import os
import re
import sys
import urllib
from urlparse import urljoin

from constants_scrapers import *


def get_pages_listed( html ):
    try:
        pages = re.compile( '<div class="PagingRow">(.*?)</div>', re.DOTALL ).findall( html )
        pages_listed = set( re.findall( '<a href="(.*?)"', pages[ 0 ] ) )
        #pages = re.findall( "~(\d{1,4})~", pages ) #expression for set thumbs and name label in script/plugin
        #if pages.count( pages[ -1 ] ) > 1: pages = pages[ :-1 ]
    except:
        pages_listed = []
    return pages_listed


def get_games_listed( url ):
    html = get_html_source( url )
    pages_listed = get_pages_listed( html )

    games_listed = []
    games = re.compile( '<tr class="visible" id="trlink" onclick=".*?">.*?</tr>', re.DOTALL ).findall( html )
    for count, item in enumerate( games ):
        try:
            uri, title = re.findall( '<a href="(.*?)">(.*?)</a>', item )[ 0 ]
            urlsource = urljoin( url, uri ).replace( "&amp;", "&" )
            ID = get_item_id( urlsource )
            title = set_pretty_formatting( title ).strip().replace( "&amp;", "&" )
            try: style = re.findall( '<td class=".*?" style=".*?">(.*?)</td>', item )[ 1 ].strip()
            except: style = ""
            try: year = int( re.findall( ">\n(\d{1,4})<", item )[ 0 ] )
            except: year = 0
            try: amg_rating = re.findall( 'st_r(\d{1,4})', item )[ 0 ]
            except: amg_rating = ""
            games_listed.append( { "ID": ID, "style": style, "title": title, "amg_rating": amg_rating, "year": year, "urlsource": urlsource } )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )
    return pages_listed, games_listed


def get_buttons_allowed( html ):
    try:
        buttons_listed = re.compile( '<td class="tab_.*?" nowrap=".*?><a HREF=".*?~(.*?)">.*?</a>' ).findall( html )
    except:
        buttons_listed = []
    return buttons_listed


def get_game_overview( url ):
    html = get_html_source( url )
    buttons_listed = get_buttons_allowed( html )
    try:
        tbn = re.findall( '<td valign="top"><img src="(.*?)".*?>', html )[ 0 ]
        tbn = ( "", urljoin( url, tbn ) )[ tbn != "" ]
    except:
        tbn = ""
    try:
        synopsis = set_pretty_formatting( re.findall( '<td align="left" class="title">Synopsis</td>.*?<p>(.*?)</p>', html )[ 0 ] )
    except:
        synopsis = ""#"No synopsis provided by studio."
    try:
        extra_credits = set_pretty_formatting( re.findall( '<td align="left" class="title">Extra Credits</td>.*?<p>(.*?)</p>', html )[ 0 ] )
    except:
        extra_credits = ""#"No extra credits provided by studio."

    # Reduce html source
    try: html = re.compile( '<span>Title</span>(.*?)<td align="left" class="title">Synopsis' ).findall( html )[ 0 ]
    except: pass

    try:
        platform = re.findall( '<span>Platform</span>.*?title="(.*?)" alt="(.*?)" class="logo_lg"/>', html )[ 0 ][ 0 ]
    except:
        platform = ""
    if not platform:
        try:
            platform = re.findall( '<span>Platform</span>.*?<a href=".*?">(.*?)</a>', html )[ 0 ]
        except:
            platform = ""
    try:
        esrb_rating_img = ESRB_IMG + re.findall( '<img src="/img/esrb/(.*?)" class="esrb"', html )[ 0 ]
    except:
        esrb_rating_img = ""
    try:
        esrb_rating = re.findall( '<span>ESRB Rating</span>.*?<ul>(.*?)</ul>', html )[ 0 ].replace( "<li>", "" ).replace( "</li>", " / " ).strip( " / " )
        if '<a href="' in esrb_rating:
            esrb_rating = ""
    except:
        esrb_rating = ""
    try:
        genre = strip_off( re.findall( '<ul>(.*?)</ul>', re.findall( '<span>Genre</span>(.*?)</table>', html )[ 0 ] )[ 0 ].replace( "<li>", "" ).replace( "</li>", " / " ).strip( " / " ) )
    except:
        genre = ""
    try:
        number_players = strip_off( re.findall( '<span>Number of Players</span>(.*?)</table>', html )[ 0 ] )
    except:
        number_players = ""
    try:
        developer = strip_off( re.findall( '<span>Developer</span>(.*?)</table>', html )[ 0 ] )
    except:
        developer = ""
    try:
        publisher = strip_off( re.findall( '<span>Publisher</span>(.*?)</table>', html )[ 0 ] )
    except:
        publisher = ""
    try:
        release_date = strip_off( re.findall( '<span>Release Date</span>(.*?)</table>', html )[ 0 ] )
    except:
        release_date = ""
    try:
        cabinet_style = strip_off( re.findall( '<span>Cabinet Style</span>(.*?)</table>', html )[ 0 ] )
    except:
        cabinet_style = ""
    try:
        controls = strip_off( re.findall( '<span>Controls</span>(.*?)</table>', html )[ 0 ] )
    except:
        controls = ""
    try:
        warnings = strip_off( re.findall( '<span>Warnings</span>(.*?)</table>', html )[ 0 ] )
    except:
        warnings = ""
    try:
        flags = strip_off( re.findall( '<span>Flags</span>(.*?)</table>', html )[ 0 ] )
    except:
        flags = ""
    try:
        supports = strip_off( re.findall( '<span>Supports</span>(.*?)</table>', html )[ 0 ] )
    except:
        supports = ""
    try:
        included_package = strip_off( re.findall( '<ul>(.*?)</ul>', re.findall( '<span>Included in Package</span>(.*?)</table>', html )[ 0 ] )[ 0 ].replace( "<li>", "" ).replace( "</li>", " / " ).strip( " / " ) )
    except:
        included_package = ""
    try:
        support_url = strip_off( re.findall( '<span>Tech Support URL</span>.*?<a href="(.*?)">', html )[ 0 ] )
    except:
        support_url = ""
    try:
        support_email = strip_off( re.findall( '<span>Tech Support E-mail</span>.*?<a href="mailto:(.*?)">', html )[ 0 ] )
    except:
        support_email = ""
    try:
        support_phone = strip_off( re.findall( '<span>Tech Support Phone</span>(.*?)</table>', html )[ 0 ] )
    except:
        support_phone = ""

    # Delete html and url sources in locals variables and return dict locals()
    del html, url
    return locals()


def get_game_review( url ):
    html = get_html_source( url )
    try:
        review = set_pretty_formatting( re.findall( '<td align="left" class="title">Review</td>.*?<p>(.*?)</p>', html )[ 0 ] )
    except:
        review = ""#"No review provided by studio."
    return review


def get_game_controls( url ):
    html = get_html_source( url )
    try:
        controls = re.compile( '<!--Begin Center Content-->(.*?)<!--End Center Content-->' ).findall( html )[ 0 ]
        ctrls = controls.split( '<td class="grid_heading"' )
        controls_listed = []
        for control in ctrls:
            try: head_ctrl = re.findall( ' colspan="2">(.*?)</td>', control )[ 0 ]
            except: head_ctrl = ""
            buttons = re.findall( '<td class="grid_row_title">(.*?)</td><td class="grid_row_body">(.*?)</td>', control )
            if buttons: controls_listed.append( ( head_ctrl, buttons ) )
    except:
        controls_listed = []
    return controls_listed


def get_game_credits( url ):
    html = get_html_source( url )
    try:
        credits = re.compile( '<!--Begin Center Content-->(.*?)<!--End Center Content-->' ).findall( html )[ 0 ]
        credits_listed = re.findall( '<td class="grid_row_title">(.*?)</td><td class="grid_row_body">(.*?)</td>', credits )
    except:
        credits_listed = []
    return credits_listed


def get_game_system_requirements( url ):
    html = get_html_source( url )
    try:
        system_requirements = re.compile( '<!--Begin Center Content-->(.*?)<!--End Center Content-->' ).findall( html )[ 0 ]
        lines = system_requirements.split( '<td class="grid_sysreqs"' )
        infos_listed = []
        for info in lines:
            try: head_info = re.findall( ' colspan="2">(.*?)</td>', info )[ 0 ]
            except: head_info = ""
            infos = re.findall( '<td class="grid_row_body">(.*?)</td>', info )
            if infos: infos_listed.append( ( head_info, infos ) )
    except:
        infos_listed = []
    return infos_listed


def get_game_screens( url ):
    html = get_html_source( url )
    try:
        screens = re.compile( '<div id="screens">(.*?)</div>' ).findall( html )[ 0 ]
        screens = re.findall( '<img src="(.*?)" alt="screen shot" />', screens )
    except:
        screens = []
    return screens


def get_game_buy( url ):
    #for moment not find infos about buy
    #pass
    return ""


def get_game_trailer( url ):
    #allgame.com indicate comming soon.
    #pass
    return []


def get_other_game_infos( iterable, url ):
    review = ""#"No review provided by studio."
    controls_listed = []
    credits_listed = []
    system_requirements = []
    screens = []
    base_url = url

    game_buy = ""
    trailers = []

    for button in iterable:
        url = base_url + "~" + button
        if button == "T1":
            review = get_game_review( url )
        elif button == "T2":
            controls_listed = get_game_controls( url )
        elif button == "T3":
            credits_listed = get_game_credits( url )
        elif button == "T4":
            system_requirements = get_game_system_requirements( url )
        elif button == "T5":
            screens = get_game_screens( url )

        del button

    # Delete unnecessary variables in locals and return dict locals()
    del iterable, url, base_url
    return locals()
