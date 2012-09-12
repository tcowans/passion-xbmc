#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# Notes :
#    -> Filtre Wireshark : 
#          http.host contains "ftvodhdsecz" or http.host contains "francetv" or http.host contains "pluzz"
#    -> 

#
# Modules
#

import base64
import binascii
import os
import re
import sys
import urllib2
import xml.etree.ElementTree
import xml.sax

from Navigateur import Navigateur

import logging
logger = logging.getLogger( "pluzzdl" )

#
# Classes
#

class PluzzDL( object ):
	
	def __init__( self, url, useFragments = False, proxy = None, progressbar = False ):
		self.url              = url
		self.useFragments     = useFragments
		self.proxy            = proxy
		self.progressbar      = progressbar
		self.navigateur       = Navigateur( self.proxy )
		
		self.lienMMS          = None
		self.lienRTMP         = None
		self.manifestURL      = None
		self.m3u8URL          = None
		self.drm              = None
		
		# Recupere l'ID de l'emission
		self.getID()
		# Recupere la page d'infos de l'emission
		self.pageInfos = self.navigateur.getFichier( "http://www.pluzz.fr/appftv/webservices/video/getInfosOeuvre.php?mode=zeri&id-diffusion=%s" %( self.id ) )
		# Parse la page d'infos
		self.parseInfos()
		# Petit message en cas de DRM
		if( self.drm == "oui" ):
			logger.warning( "La vidéo posséde un DRM ; elle sera sans doute illisible" )
		
	def getID( self ):
		try :
			page     = self.navigateur.getFichier( self.url )
			self.id  = re.findall( r"http://info.francetelevisions.fr/\?id-video=([^\"]+)", page )[ 0 ]
			logger.debug( "ID de l'émission : %s" %( self.id ) )
		except :
			logger.critical( "Impossible de récupérer l'ID de l'émission" )
			sys.exit( -1 )
		
	def parseInfos( self ):
		try : 
			xml.sax.parseString( self.pageInfos, PluzzDLInfosHandler( self ) )
			logger.debug( "Lien MMS : %s" %( self.lienMMS ) )
			logger.debug( "Lien RTMP : %s" %( self.lienRTMP ) )
			logger.debug( "URL manifest : %s" %( self.manifestURL ) )
			logger.debug( "Utilisation de DRM : %s" %( self.drm ) )
		except :
			logger.critical( "Impossible de parser le fichier XML de l'émission" )
			sys.exit( -1 )
	
	def parseManifest( self ):
		try :
			arbre          = xml.etree.ElementTree.fromstring( self.manifest )
			# Duree
			self.duree     = float( arbre.find( "{http://ns.adobe.com/f4m/1.0}duration" ).text )
			media          = arbre.findall( "{http://ns.adobe.com/f4m/1.0}media" )[ -1 ]
			# Bitrate
			self.bitrate   = int( media.attrib[ "bitrate" ] )
			# URL des fragments
			urlbootstrap   = media.attrib[ "url" ]
			self.urlFrag   = "%s%sSeg1-Frag" %( self.manifestURLToken[ : self.manifestURLToken.find( "manifest.f4m" ) ], urlbootstrap )
			# Header du fichier final
			self.flvHeader = base64.b64decode( media.find( "{http://ns.adobe.com/f4m/1.0}metadata" ).text )
		except :
			logger.critical( "Impossible de parser le manifest" )
			sys.exit( -1 )
		
class PluzzDLInfosHandler( xml.sax.handler.ContentHandler ):
	
	def __init__( self, pluzzdl ):
		self.pluzzdl = pluzzdl
		
		self.isUrl = False
		self.isDRM = False
		
	def startElement( self, name, attrs ):
		if( name == "url" ):
			self.isUrl = True
		elif( name == "drm" ):
			self.isDRM = True
	
	def characters( self, data ):
		if( self.isUrl ):
			if( data[ : 3 ] == "mms" ):
				self.pluzzdl.lienMMS = data
			elif( data[ : 4 ] == "rtmp" ):
				self.pluzzdl.lienRTMP = data
			elif( data[ -3 : ] == "f4m" ):
				self.pluzzdl.manifestURL = data
			elif( data[ -4 : ] == "m3u8" ):
				self.pluzzdl.m3u8URL = data
		elif( self.isDRM ):
			self.pluzzdl.drm = data
			
	def endElement( self, name ):
		if( name == "url" ):
			self.isUrl = False
		elif( name == "drm" ):
			self.isDRM = False

class ProgressionVide( object ):
	
	def __init__( self, nbMax ):
		self.nbMax  = nbMax
		self.indice = 1
		self.old    = 0
		self.new    = 0
	
	def afficher( self ):
		pass
		
	def afficherFin( self ):
		pass
	
class Progression( ProgressionVide ):
	
	def __init__( self, nbMax ):
		ProgressionVide.__init__( self, nbMax )
		
	def afficher( self ):
		self.new = min( int( ( self.indice / self.nbMax ) * 100 ), 100 )
		if( self.new != self.old ):
			logger.info( "Avancement : %3d %%" %( self.new ) )
			self.old = self.new
		self.indice += 1
	
	def afficherFin( self ):
		if( self.old < 100 ):
			logger.info( "Avancement : %3d %%" %( 100 ) )
