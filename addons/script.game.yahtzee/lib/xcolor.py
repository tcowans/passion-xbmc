# -*- coding: utf-8 -*-

#####################################################################################################
''' Infos: Data '''
#####################################################################################################
__author__ = '''FrostBox (frostbox@users.sourceforge.net)'''
__title__  = '''xcolor'''

#####################################################################################################
''' Module: import '''
#####################################################################################################
import random
import os , os.path
import xbmc , xbmcgui
from collections import deque

#####################################################################################################
''' Function: Global '''
#####################################################################################################
nameColor = [
	'indian red', 'crimson', 'lightpink', 'lightpink 1', 'lightpink 2', 'lightpink 3', 'lightpink 4',
	'pink', 'pink 1', 'pink 2', 'pink 3', 'pink 4', 'palevioletred', 'palevioletred 1', 'palevioletred 2',
	'palevioletred 3', 'palevioletred 4', 'lavenderblush 1 (lavenderblush)', 'lavenderblush 2', 'lavenderblush 3',
	'lavenderblush 4', 'violetred 1', 'violetred 2', 'violetred 3', 'violetred 4', 'hotpink', 'hotpink 1',
	'hotpink 2', 'hotpink 3', 'hotpink 4', 'raspberry', 'deeppink 1 (deeppink)', 'deeppink 2', 'deeppink 3',
	'deeppink 4', 'maroon 1', 'maroon 2', 'maroon 3', 'maroon 4', 'mediumvioletred', 'violetred', 'orchid',
	'orchid 1', 'orchid 2', 'orchid 3', 'orchid 4', 'thistle', 'thistle 1', 'thistle 2', 'thistle 3', 'thistle 4',
	'plum 1', 'plum 2', 'plum 3', 'plum 4', 'plum', 'violet', 'magenta (fuchsia*)', 'magenta 2', 'magenta 3',
	'magenta 4 (darkmagenta)', 'purple*', 'mediumorchid', 'mediumorchid 1', 'mediumorchid 2', 'mediumorchid 3',
	'mediumorchid 4', 'darkviolet', 'darkorchid', 'darkorchid 1', 'darkorchid 2', 'darkorchid 3', 'darkorchid 4',
	'indigo', 'blueviolet', 'purple 1', 'purple 2', 'purple 3', 'purple 4', 'mediumpurple', 'mediumpurple 1',
	'mediumpurple 2', 'mediumpurple 3', 'mediumpurple 4', 'darkslateblue', 'lightslateblue', 'mediumslateblue',
	'slateblue', 'slateblue 1', 'slateblue 2', 'slateblue 3', 'slateblue 4', 'ghostwhite', 'lavender', 'blue*',
	'blue 2', 'blue 3 (mediumblue)', 'blue 4 (darkblue)', 'navy*', 'midnightblue', 'cobalt', 'royalblue',
	'royalblue 1', 'royalblue 2', 'royalblue 3', 'royalblue 4', 'cornflowerblue', 'lightsteelblue', 'lightsteelblue 1',
	'lightsteelblue 2', 'lightsteelblue 3', 'lightsteelblue 4', 'lightslategray', 'slategray', 'slategray 1',
	'slategray 2', 'slategray 3', 'slategray 4', 'dodgerblue 1 (dodgerblue)', 'dodgerblue 2', 'dodgerblue 3',
	'dodgerblue 4', 'aliceblue', 'steelblue', 'steelblue 1', 'steelblue 2', 'steelblue 3', 'steelblue 4', 'lightskyblue',
	'lightskyblue 1', 'lightskyblue 2', 'lightskyblue 3', 'lightskyblue 4', 'skyblue 1', 'skyblue 2', 'skyblue 3',
	'skyblue 4', 'skyblue', 'deepskyblue 1 (deepskyblue)', 'deepskyblue 2', 'deepskyblue 3', 'deepskyblue 4', 'peacock',
	'lightblue', 'lightblue 1', 'lightblue 2', 'lightblue 3', 'lightblue 4', 'powderblue', 'cadetblue 1', 'cadetblue 2',
	'cadetblue 3', 'cadetblue 4', 'turquoise 1', 'turquoise 2', 'turquoise 3', 'turquoise 4', 'cadetblue',
	'darkturquoise', 'azure 1 (azure)', 'azure 2', 'azure 3', 'azure 4', 'lightcyan 1 (lightcyan)', 'lightcyan 2',
	'lightcyan 3', 'lightcyan 4', 'paleturquoise 1', 'paleturquoise 2 (paleturquoise)', 'paleturquoise 3',
	'paleturquoise 4', 'darkslategray', 'darkslategray 1', 'darkslategray 2', 'darkslategray 3', 'darkslategray 4',
	'cyan / aqua*', 'cyan 2', 'cyan 3', 'cyan 4 (darkcyan)', 'teal*', 'mediumturquoise', 'lightseagreen',
	'manganeseblue', 'turquoise', 'coldgrey', 'turquoiseblue', 'aquamarine 1 (aquamarine)', 'aquamarine 2',
	'aquamarine 3 (mediumaquamarine)', 'aquamarine 4', 'mediumspringgreen', 'mintcream', 'springgreen', 'springgreen 1',
	'springgreen 2', 'springgreen 3', 'mediumseagreen', 'seagreen 1', 'seagreen 2', 'seagreen 3', 'seagreen 4 (seagreen)',
	'emeraldgreen', 'mint', 'cobaltgreen', 'honeydew 1 (honeydew)', 'honeydew 2', 'honeydew 3', 'honeydew 4',
	'darkseagreen', 'darkseagreen 1', 'darkseagreen 2', 'darkseagreen 3', 'darkseagreen 4', 'palegreen',
	'palegreen 1', 'palegreen 2 (lightgreen)', 'palegreen 3', 'palegreen 4', 'limegreen', 'forestgreen',
	'green 1 (lime*)', 'green 2', 'green 3', 'green 4', 'green*', 'darkgreen', 'sapgreen', 'lawngreen',
	'chartreuse 1 (chartreuse)', 'chartreuse 2', 'chartreuse 3', 'chartreuse 4', 'greenyellow', 'darkolivegreen 1',
	'darkolivegreen 2', 'darkolivegreen 3', 'darkolivegreen 4', 'darkolivegreen', 'olivedrab', 'olivedrab 1',
	'olivedrab 2', 'olivedrab 3 (yellowgreen)', 'olivedrab 4', 'ivory 1 (ivory)', 'ivory 2', 'ivory 3', 'ivory 4',
	'beige', 'lightyellow 1 (lightyellow)', 'lightyellow 2', 'lightyellow 3', 'lightyellow 4', 'lightgoldenrodyellow',
	'yellow 1 (yellow*)', 'yellow 2', 'yellow 3', 'yellow 4', 'warmgrey', 'olive*', 'darkkhaki', 'khaki 1', 'khaki 2',
	'khaki 3', 'khaki 4', 'khaki', 'palegoldenrod', 'lemonchiffon 1 (lemonchiffon)', 'lemonchiffon 2', 'lemonchiffon 3',
	'lemonchiffon 4', 'lightgoldenrod 1', 'lightgoldenrod 2', 'lightgoldenrod 3', 'lightgoldenrod 4', 'banana',
	'gold 1 (gold)', 'gold 2', 'gold 3', 'gold 4', 'cornsilk 1 (cornsilk)', 'cornsilk 2', 'cornsilk 3', 'cornsilk 4',
	'goldenrod', 'goldenrod 1', 'goldenrod 2', 'goldenrod 3', 'goldenrod 4', 'darkgoldenrod', 'darkgoldenrod 1',
	'darkgoldenrod 2', 'darkgoldenrod 3', 'darkgoldenrod 4', 'orange 1 (orange)', 'orange 2', 'orange 3', 'orange 4',
	'floralwhite', 'oldlace', 'wheat', 'wheat 1', 'wheat 2', 'wheat 3', 'wheat 4', 'moccasin', 'papayawhip',
	'blanchedalmond', 'navajowhite 1 (navajowhite)', 'navajowhite 2', 'navajowhite 3', 'navajowhite 4', 'eggshell',
	'tan', 'brick', 'cadmiumyellow', 'antiquewhite', 'antiquewhite 1', 'antiquewhite 2', 'antiquewhite 3',
	'antiquewhite 4', 'burlywood', 'burlywood 1', 'burlywood 2', 'burlywood 3', 'burlywood 4', 'bisque 1 (bisque)',
	'bisque 2', 'bisque 3', 'bisque 4', 'melon', 'carrot', 'darkorange', 'darkorange 1', 'darkorange 2', 'darkorange 3',
	'darkorange 4', 'orange', 'tan 1', 'tan 2', 'tan 3 (peru)', 'tan 4', 'linen', 'peachpuff 1 (peachpuff)', 'peachpuff 2',
	'peachpuff 3', 'peachpuff 4', 'seashell 1 (seashell)', 'seashell 2', 'seashell 3', 'seashell 4', 'sandybrown',
	'rawsienna', 'chocolate', 'chocolate 1', 'chocolate 2', 'chocolate 3', 'chocolate 4 (saddlebrown)', 'ivoryblack',
	'flesh', 'cadmiumorange', 'burntsienna', 'sienna', 'sienna 1', 'sienna 2', 'sienna 3', 'sienna 4',
	'lightsalmon 1 (lightsalmon)', 'lightsalmon 2', 'lightsalmon 3', 'lightsalmon 4', 'coral', 'orangered 1 (orangered)',
	'orangered 2', 'orangered 3', 'orangered 4', 'sepia', 'darksalmon', 'salmon 1', 'salmon 2', 'salmon 3', 'salmon 4',
	'coral 1', 'coral 2', 'coral 3', 'coral 4', 'burntumber', 'tomato 1 (tomato)', 'tomato 2', 'tomato 3', 'tomato 4',
	'salmon', 'mistyrose 1 (mistyrose)', 'mistyrose 2', 'mistyrose 3', 'mistyrose 4', 'snow 1 (snow)', 'snow 2', 'snow 3',
	'snow 4', 'rosybrown', 'rosybrown 1', 'rosybrown 2', 'rosybrown 3', 'rosybrown 4', 'lightcoral', 'indianred', 'indianred 1',
	'indianred 2', 'indianred 4', 'indianred 3', 'brown', 'brown 1', 'brown 2', 'brown 3', 'brown 4', 'firebrick',
	'firebrick 1', 'firebrick 2', 'firebrick 3', 'firebrick 4', 'red 1 (red*)', 'red 2', 'red 3', 'red 4 (darkred)',
	'maroon*', 'sgi beet', 'sgi slateblue', 'sgi lightblue', 'sgi teal', 'sgi chartreuse', 'sgi olivedrab', 'sgi brightgray',
	'sgi salmon', 'sgi darkgray', 'sgi gray 12', 'sgi gray 16', 'sgi gray 32', 'sgi gray 36', 'sgi gray 52', 'sgi gray 56',
	'sgi lightgray', 'sgi gray 72', 'sgi gray 76', 'sgi gray 92', 'sgi gray 96', 'white*', 'white smoke (gray 96)',
	'gainsboro', 'lightgrey', 'silver*', 'darkgray', 'gray*', 'dimgray (gray 42)', 'gray 99', 'gray 98',
	'gray 97', 'white smoke (gray 96)', 'gray 95', 'gray 94', 'gray 93', 'gray 92', 'gray 91', 'gray 90', 'gray 89',
	'gray 88', 'gray 87', 'gray 86', 'gray 85', 'gray 84', 'gray 83', 'gray 82', 'gray 81', 'gray 80', 'gray 79',
	'gray 78', 'gray 77', 'gray 76', 'gray 75', 'gray 74', 'gray 73', 'gray 72', 'gray 71', 'gray 70', 'gray 69',
	'gray 68', 'gray 67', 'gray 66', 'gray 65', 'gray 64', 'gray 63', 'gray 62', 'gray 61', 'gray 60', 'gray 59',
	'gray 58', 'gray 57', 'gray 56', 'gray 55', 'gray 54', 'gray 53', 'gray 52', 'gray 51', 'gray 50', 'gray 49',
	'gray 48', 'gray 47', 'gray 46', 'gray 45', 'gray 44', 'gray 43', 'gray 42', 'dimgray (gray 42)', 'gray 40',
	'gray 39', 'gray 38', 'gray 37', 'gray 36', 'gray 35', 'gray 34', 'gray 33', 'gray 32', 'gray 31', 'gray 30',
	'gray 29', 'gray 28', 'gray 27', 'gray 26', 'gray 25', 'gray 24', 'gray 23', 'gray 22', 'gray 21', 'gray 20'#,
	#'gray 19', 'gray 18', 'gray 17', 'gray 16', 'gray 15', 'gray 14', 'gray 13', 'gray 12', 'gray 11', 'gray 10',
	#'gray 9', 'gray 8', 'gray 7', 'gray 6', 'gray 5', 'gray 4'
	]
# removed color of list not good for dice
# 'black*', '0xFF000000', 
# 'gray 3', 'gray 2', 'gray 1', '0xFF080808', '0xFF050505', '0xFF030303', 

hexColor = [
	'0xFFB0171F', '0xFFDC143C', '0xFFFFB6C1', '0xFFFFAEB9', '0xFFEEA2AD', '0xFFCD8C95', '0xFF8B5F65', '0xFFFFC0CB',
	'0xFFFFB5C5', '0xFFEEA9B8', '0xFFCD919E', '0xFF8B636C', '0xFFDB7093', '0xFFFF82AB', '0xFFEE799F', '0xFFCD6889',
	'0xFF8B475D', '0xFFFFF0F5', '0xFFEEE0E5', '0xFFCDC1C5', '0xFF8B8386', '0xFFFF3E96', '0xFFEE3A8C', '0xFFCD3278',
	'0xFF8B2252', '0xFFFF69B4', '0xFFFF6EB4', '0xFFEE6AA7', '0xFFCD6090', '0xFF8B3A62', '0xFF872657', '0xFFFF1493',
	'0xFFEE1289', '0xFFCD1076', '0xFF8B0A50', '0xFFFF34B3', '0xFFEE30A7', '0xFFCD2990', '0xFF8B1C62', '0xFFC71585',
	'0xFFD02090', '0xFFDA70D6', '0xFFFF83FA', '0xFFEE7AE9', '0xFFCD69C9', '0xFF8B4789', '0xFFD8BFD8', '0xFFFFE1FF',
	'0xFFEED2EE', '0xFFCDB5CD', '0xFF8B7B8B', '0xFFFFBBFF', '0xFFEEAEEE', '0xFFCD96CD', '0xFF8B668B', '0xFFDDA0DD',
	'0xFFEE82EE', '0xFFFF00FF', '0xFFEE00EE', '0xFFCD00CD', '0xFF8B008B', '0xFF800080', '0xFFBA55D3', '0xFFE066FF',
	'0xFFD15FEE', '0xFFB452CD', '0xFF7A378B', '0xFF9400D3', '0xFF9932CC', '0xFFBF3EFF', '0xFFB23AEE', '0xFF9A32CD',
	'0xFF68228B', '0xFF4B0082', '0xFF8A2BE2', '0xFF9B30FF', '0xFF912CEE', '0xFF7D26CD', '0xFF551A8B', '0xFF9370DB',
	'0xFFAB82FF', '0xFF9F79EE', '0xFF8968CD', '0xFF5D478B', '0xFF483D8B', '0xFF8470FF', '0xFF7B68EE', '0xFF6A5ACD',
	'0xFF836FFF', '0xFF7A67EE', '0xFF6959CD', '0xFF473C8B', '0xFFF8F8FF', '0xFFE6E6FA', '0xFF0000FF', '0xFF0000EE',
	'0xFF0000CD', '0xFF00008B', '0xFF000080', '0xFF191970', '0xFF3D59AB', '0xFF4169E1', '0xFF4876FF', '0xFF436EEE',
	'0xFF3A5FCD', '0xFF27408B', '0xFF6495ED', '0xFFB0C4DE', '0xFFCAE1FF', '0xFFBCD2EE', '0xFFA2B5CD', '0xFF6E7B8B',
	'0xFF778899', '0xFF708090', '0xFFC6E2FF', '0xFFB9D3EE', '0xFF9FB6CD', '0xFF6C7B8B', '0xFF1E90FF', '0xFF1C86EE',
	'0xFF1874CD', '0xFF104E8B', '0xFFF0F8FF', '0xFF4682B4', '0xFF63B8FF', '0xFF5CACEE', '0xFF4F94CD', '0xFF36648B',
	'0xFF87CEFA', '0xFFB0E2FF', '0xFFA4D3EE', '0xFF8DB6CD', '0xFF607B8B', '0xFF87CEFF', '0xFF7EC0EE', '0xFF6CA6CD',
	'0xFF4A708B', '0xFF87CEEB', '0xFF00BFFF', '0xFF00B2EE', '0xFF009ACD', '0xFF00688B', '0xFF33A1C9', '0xFFADD8E6',
	'0xFFBFEFFF', '0xFFB2DFEE', '0xFF9AC0CD', '0xFF68838B', '0xFFB0E0E6', '0xFF98F5FF', '0xFF8EE5EE', '0xFF7AC5CD',
	'0xFF53868B', '0xFF00F5FF', '0xFF00E5EE', '0xFF00C5CD', '0xFF00868B', '0xFF5F9EA0', '0xFF00CED1', '0xFFF0FFFF',
	'0xFFE0EEEE', '0xFFC1CDCD', '0xFF838B8B', '0xFFE0FFFF', '0xFFD1EEEE', '0xFFB4CDCD', '0xFF7A8B8B', '0xFFBBFFFF',
	'0xFFAEEEEE', '0xFF96CDCD', '0xFF668B8B', '0xFF2F4F4F', '0xFF97FFFF', '0xFF8DEEEE', '0xFF79CDCD', '0xFF528B8B',
	'0xFF00FFFF', '0xFF00EEEE', '0xFF00CDCD', '0xFF008B8B', '0xFF008080', '0xFF48D1CC', '0xFF20B2AA', '0xFF03A89E',
	'0xFF40E0D0', '0xFF808A87', '0xFF00C78C', '0xFF7FFFD4', '0xFF76EEC6', '0xFF66CDAA', '0xFF458B74', '0xFF00FA9A',
	'0xFFF5FFFA', '0xFF00FF7F', '0xFF00EE76', '0xFF00CD66', '0xFF008B45', '0xFF3CB371', '0xFF54FF9F', '0xFF4EEE94',
	'0xFF43CD80', '0xFF2E8B57', '0xFF00C957', '0xFFBDFCC9', '0xFF3D9140', '0xFFF0FFF0', '0xFFE0EEE0', '0xFFC1CDC1',
	'0xFF838B83', '0xFF8FBC8F', '0xFFC1FFC1', '0xFFB4EEB4', '0xFF9BCD9B', '0xFF698B69', '0xFF98FB98', '0xFF9AFF9A',
	'0xFF90EE90', '0xFF7CCD7C', '0xFF548B54', '0xFF32CD32', '0xFF228B22', '0xFF00FF00', '0xFF00EE00', '0xFF00CD00',
	'0xFF008B00', '0xFF008000', '0xFF006400', '0xFF308014', '0xFF7CFC00', '0xFF7FFF00', '0xFF76EE00', '0xFF66CD00',
	'0xFF458B00', '0xFFADFF2F', '0xFFCAFF70', '0xFFBCEE68', '0xFFA2CD5A', '0xFF6E8B3D', '0xFF556B2F', '0xFF6B8E23',
	'0xFFC0FF3E', '0xFFB3EE3A', '0xFF9ACD32', '0xFF698B22', '0xFFFFFFF0', '0xFFEEEEE0', '0xFFCDCDC1', '0xFF8B8B83',
	'0xFFF5F5DC', '0xFFFFFFE0', '0xFFEEEED1', '0xFFCDCDB4', '0xFF8B8B7A', '0xFFFAFAD2', '0xFFFFFF00', '0xFFEEEE00',
	'0xFFCDCD00', '0xFF8B8B00', '0xFF808069', '0xFF808000', '0xFFBDB76B', '0xFFFFF68F', '0xFFEEE685', '0xFFCDC673',
	'0xFF8B864E', '0xFFF0E68C', '0xFFEEE8AA', '0xFFFFFACD', '0xFFEEE9BF', '0xFFCDC9A5', '0xFF8B8970', '0xFFFFEC8B',
	'0xFFEEDC82', '0xFFCDBE70', '0xFF8B814C', '0xFFE3CF57', '0xFFFFD700', '0xFFEEC900', '0xFFCDAD00', '0xFF8B7500',
	'0xFFFFF8DC', '0xFFEEE8CD', '0xFFCDC8B1', '0xFF8B8878', '0xFFDAA520', '0xFFFFC125', '0xFFEEB422', '0xFFCD9B1D',
	'0xFF8B6914', '0xFFB8860B', '0xFFFFB90F', '0xFFEEAD0E', '0xFFCD950C', '0xFF8B6508', '0xFFFFA500', '0xFFEE9A00',
	'0xFFCD8500', '0xFF8B5A00', '0xFFFFFAF0', '0xFFFDF5E6', '0xFFF5DEB3', '0xFFFFE7BA', '0xFFEED8AE', '0xFFCDBA96',
	'0xFF8B7E66', '0xFFFFE4B5', '0xFFFFEFD5', '0xFFFFEBCD', '0xFFFFDEAD', '0xFFEECFA1', '0xFFCDB38B', '0xFF8B795E',
	'0xFFFCE6C9', '0xFFD2B48C', '0xFF9C661F', '0xFFFF9912', '0xFFFAEBD7', '0xFFFFEFDB', '0xFFEEDFCC', '0xFFCDC0B0',
	'0xFF8B8378', '0xFFDEB887', '0xFFFFD39B', '0xFFEEC591', '0xFFCDAA7D', '0xFF8B7355', '0xFFFFE4C4', '0xFFEED5B7',
	'0xFFCDB79E', '0xFF8B7D6B', '0xFFE3A869', '0xFFED9121', '0xFFFF8C00', '0xFFFF7F00', '0xFFEE7600', '0xFFCD6600',
	'0xFF8B4500', '0xFFFF8000', '0xFFFFA54F', '0xFFEE9A49', '0xFFCD853F', '0xFF8B5A2B', '0xFFFAF0E6', '0xFFFFDAB9',
	'0xFFEECBAD', '0xFFCDAF95', '0xFF8B7765', '0xFFFFF5EE', '0xFFEEE5DE', '0xFFCDC5BF', '0xFF8B8682', '0xFFF4A460',
	'0xFFC76114', '0xFFD2691E', '0xFFFF7F24', '0xFFEE7621', '0xFFCD661D', '0xFF8B4513', '0xFF292421', '0xFFFF7D40',
	'0xFFFF6103', '0xFF8A360F', '0xFFA0522D', '0xFFFF8247', '0xFFEE7942', '0xFFCD6839', '0xFF8B4726', '0xFFFFA07A',
	'0xFFEE9572', '0xFFCD8162', '0xFF8B5742', '0xFFFF7F50', '0xFFFF4500', '0xFFEE4000', '0xFFCD3700', '0xFF8B2500',
	'0xFF5E2612', '0xFFE9967A', '0xFFFF8C69', '0xFFEE8262', '0xFFCD7054', '0xFF8B4C39', '0xFFFF7256', '0xFFEE6A50',
	'0xFFCD5B45', '0xFF8B3E2F', '0xFF8A3324', '0xFFFF6347', '0xFFEE5C42', '0xFFCD4F39', '0xFF8B3626', '0xFFFA8072',
	'0xFFFFE4E1', '0xFFEED5D2', '0xFFCDB7B5', '0xFF8B7D7B', '0xFFFFFAFA', '0xFFEEE9E9', '0xFFCDC9C9', '0xFF8B8989',
	'0xFFBC8F8F', '0xFFFFC1C1', '0xFFEEB4B4', '0xFFCD9B9B', '0xFF8B6969', '0xFFF08080', '0xFFCD5C5C', '0xFFFF6A6A',
	'0xFFEE6363', '0xFF8B3A3A', '0xFFCD5555', '0xFFA52A2A', '0xFFFF4040', '0xFFEE3B3B', '0xFFCD3333', '0xFF8B2323',
	'0xFFB22222', '0xFFFF3030', '0xFFEE2C2C', '0xFFCD2626', '0xFF8B1A1A', '0xFFFF0000', '0xFFEE0000', '0xFFCD0000',
	'0xFF8B0000', '0xFF800000', '0xFF8E388E', '0xFF7171C6', '0xFF7D9EC0', '0xFF388E8E', '0xFF71C671', '0xFF8E8E38',
	'0xFFC5C1AA', '0xFFC67171', '0xFF555555', '0xFF1E1E1E', '0xFF282828', '0xFF515151', '0xFF5B5B5B', '0xFF848484',
	'0xFF8E8E8E', '0xFFAAAAAA', '0xFFB7B7B7', '0xFFC1C1C1', '0xFFEAEAEA', '0xFFF4F4F4', '0xFFFFFFFF', '0xFFF5F5F5',
	'0xFFDCDCDC', '0xFFD3D3D3', '0xFFC0C0C0', '0xFFA9A9A9', '0xFF808080', '0xFF696969', '0xFFFCFCFC',
	'0xFFFAFAFA', '0xFFF7F7F7', '0xFFF5F5F5', '0xFFF2F2F2', '0xFFF0F0F0', '0xFFEDEDED', '0xFFEBEBEB', '0xFFE8E8E8',
	'0xFFE5E5E5', '0xFFE3E3E3', '0xFFE0E0E0', '0xFFDEDEDE', '0xFFDBDBDB', '0xFFD9D9D9', '0xFFD6D6D6', '0xFFD4D4D4',
	'0xFFD1D1D1', '0xFFCFCFCF', '0xFFCCCCCC', '0xFFC9C9C9', '0xFFC7C7C7', '0xFFC4C4C4', '0xFFC2C2C2', '0xFFBFBFBF',
	'0xFFBDBDBD', '0xFFBABABA', '0xFFB8B8B8', '0xFFB5B5B5', '0xFFB3B3B3', '0xFFB0B0B0', '0xFFADADAD', '0xFFABABAB',
	'0xFFA8A8A8', '0xFFA6A6A6', '0xFFA3A3A3', '0xFFA1A1A1', '0xFF9E9E9E', '0xFF9C9C9C', '0xFF999999', '0xFF969696',
	'0xFF949494', '0xFF919191', '0xFF8F8F8F', '0xFF8C8C8C', '0xFF8A8A8A', '0xFF878787', '0xFF858585', '0xFF828282',
	'0xFF7F7F7F', '0xFF7D7D7D', '0xFF7A7A7A', '0xFF787878', '0xFF757575', '0xFF737373', '0xFF707070', '0xFF6E6E6E',
	'0xFF6B6B6B', '0xFF696969', '0xFF666666', '0xFF636363', '0xFF616161', '0xFF5E5E5E', '0xFF5C5C5C', '0xFF595959',
	'0xFF575757', '0xFF545454', '0xFF525252', '0xFF4F4F4F', '0xFF4D4D4D', '0xFF4A4A4A', '0xFF474747', '0xFF454545',
	'0xFF424242', '0xFF404040', '0xFF3D3D3D', '0xFF3B3B3B', '0xFF383838', '0xFF363636', '0xFF333333'#, '0xFF303030',
	#'0xFF2E2E2E', '0xFF2B2B2B', '0xFF292929', '0xFF262626', '0xFF242424', '0xFF212121', '0xFF1F1F1F', '0xFF1C1C1C',
	#'0xFF1A1A1A', '0xFF171717', '0xFF141414', '0xFF121212', '0xFF0F0F0F', '0xFF0D0D0D', '0xFF0A0A0A'
	]

CWD = os.getcwd().rstrip( ";" )
BG04     = os.path.join(CWD, "media", "logo.png")
ROLLDICE = os.path.join(CWD, "sounds", "roll.wav")

#####################################################################################################
''' Class: userColorDice '''
#####################################################################################################
class userColorDice(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(6)
        self.multiColor = None
        self.colorDice = None
        self.showColor = 0
        self.colored = deque(hexColor)
        self.nameCol = deque(nameColor)

        self.addControl(xbmcgui.ControlLabel(0,63,720,0, "Choose Color Dice", 'special13', alignment=0x00000002))
        
        self.logo = xbmcgui.ControlImage(240,173,240,230, BG04)
        self.addControl(self.logo)

        self.confirmed = xbmcgui.ControlButton(315,425,90,32, "", font = "font10", 
            focusTexture="keyboard-btn-backspace.png", noFocusTexture="keyboard-btn-backspace.png",
            alignment=0x00000002+0x00000004)
        self.addControl(self.confirmed)
        self.left = xbmcgui.ControlImage(299,425,16,32, "scroll-left.png")
        self.addControl(self.left)
        self.right = xbmcgui.ControlImage(405,425,16,32, "scroll-right.png")
        self.addControl(self.right)

        self.confirmedName = xbmcgui.ControlLabel(0,458,720,32, "", 'special12', alignment=0x00000002)
        self.addControl(self.confirmedName)

        self.addControl(xbmcgui.ControlLabel(0,490,720,0, "MultiColor Dice\nPress X Button", 'font13', alignment=0x00000002))

        self.setColorDice()
        self.setFocus(self.confirmed)

    def setColorDice(self):
        self.colorDice = self.colored[0]
        self.confirmed.setLabel(self.colored[0])
        self.logo.setColorDiffuse(self.colored[0])
        self.confirmedName.setLabel(self.nameCol[0])
        if os.path.exists(ROLLDICE): xbmc.playSFX(ROLLDICE)

    def onActionColor(self, action):
        if (action == 1)|(action.getButtonCode() == 262)|(action.getButtonCode() == 272)|(action.getButtonCode() == 278):
            self.right.setImage("scroll-right.png")
            self.left.setImage("scroll-left-focus.png")
            self.colored.rotate(1)
            self.nameCol.rotate(1)
            self.setColorDice()
        if (action == 2)|(action.getButtonCode() == 263)|(action.getButtonCode() == 273)|(action.getButtonCode() == 279):
            self.left.setImage("scroll-left.png")
            self.right.setImage("scroll-right-focus.png")
            self.colored.rotate(-1)
            self.nameCol.rotate(-1)
            self.setColorDice()

    def onAction(self, action):
        self.onActionColor(action)
        if action == 10:
            self.multiColor = None
            self.colorDice = None
            self.close()
        if action == 18:
            self.multiColor = hexColor
            self.colorDice = None
            self.close()

    def onControl(self, control):
        if control == self.confirmed: self.close()
