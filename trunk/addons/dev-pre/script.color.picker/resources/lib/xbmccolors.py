"""
    Note:
     * argb() = tuple( alpha, red, green, blue )
     * rgba() = tuple( red, green, blue, alpha )
"""

import os
import re
import sys
import math

try: from xbmc import translatePath
except: pass


# Mappings of color names to normalized hexadecimal color values.
'''
# get default xbmc colors
try: strColors = open( translatePath( 'special://xbmc/system/colors.xml' ) ).read()
except: strColors = open( r'C:\Program Files\XBMC\system\colors.xml' ).read()
# temp fixe space in name.
strColors = strColors.lower().replace( ' "', '"' ).replace( ' "', '"' )
xbmc_names_to_hex = dict( re.compile( '<color name="(.*?)">(.*?)</color>' ).findall( strColors ) )
# get default skin colors
try: strColors = open( translatePath( 'special://skin/colors/defaults.xml' ) ).read()
except: strColors = open( r'C:\Program Files\XBMC\addons\skin.confluence\colors\defaults.xml' ).read()
skin_names_to_hex = dict( re.compile( '<color name="(.*?)">(.*?)</color>' ).findall( strColors.lower() ) )
# update default xbmc colors with skin colors
if skin_names_to_hex: xbmc_names_to_hex.update( skin_names_to_hex )
#
xbmc_hex_to_names = dict( zip( xbmc_names_to_hex.values(), xbmc_names_to_hex.keys() ) )
'''
def get_colors():
    names_to_hex = {}
    dpath = os.path.join( sys.path[ 0 ], "resources", "colors" )
    if not os.path.exists( dpath ): dpath = "../colors"
    for xml in os.listdir( dpath ):
        strColors = open( os.path.join( dpath, xml ) ).read().lower()
        d = dict( re.compile( '<color name="(.*?)">(.*?)</color>' ).findall( strColors ) )
        names_to_hex.update( d )
    return names_to_hex

xbmc_names_to_hex = get_colors()
xbmc_hex_to_names = dict( zip( xbmc_names_to_hex.values(), xbmc_names_to_hex.keys() ) )


def normalize_hex( hex_value ):
    """
    Normalize a hexadecimal color value to the following form and
    return the result:

        #[a-f0-9]{8}

    In other words, the following transformations are applied as
    needed:

    * If the value contains only four hexadecimal digits, it is
      expanded to eight.

    * The value is normalized to lower-case.

    If the supplied value cannot be interpreted as a hexadecimal color
    value, ``ValueError`` is raised.

    Examples:

    >>> normalize_hex('ff0099cc')
    'ff0099cc'
    >>> normalize_hex('ff0099CC')
    'ff0099cc'
    >>> normalize_hex('f09c')
    'ff0099cc'
    >>> normalize_hex('f09C')
    'ff0099cc'
    """
    try:
        hex_digits = re.compile( r'^#([a-fA-F0-9]{4}|[a-fA-F0-9]{8})$' ).match( '#' + hex_value )
        hex_digits = hex_digits.groups()[ 0 ]
    except AttributeError:
        raise ValueError( "'%s' is not a valid hexadecimal color value." % hex_value )

    if len( hex_digits ) == 4:
        hex_digits = ''.join ( map( lambda s: 2 * s, hex_digits ) )

    return hex_digits.lower()


def name_to_hex( name ):
    """
    Convert a color name to a normalized hexadecimal color value.

    The color name will be normalized to lower-case before being
    looked up, and when no color of that name exists in the given
    specification, ``ValueError`` is raised.

    Examples:

    >>> name_to_hex('white')
    'ffffffff'
    >>> name_to_hex('navy')
    'ff000080'
    >>> name_to_hex('goldenrod')
    'ffdaa520'
    >>> name_to_hex('goldenred')
    Traceback (most recent call last):
        ...
    ValueError: 'goldenrod' is not defined as a named color in xbmc.

    """

    normalized = name.lower()
    try:
        hex_value = xbmc_names_to_hex[ normalized ]
    except KeyError:
        raise ValueError( "'%s' is not defined as a named color in xbmc." % name )

    return hex_value


def name_to_argb( name ):
    """
    Convert a color name to a 4-tuple of integers suitable for use in
    an ``argb()`` quadruplet  specifying that color.

    The color name will be normalized to lower-case before being
    looked up, and when no color of that name exists in the given
    specification, ``ValueError`` is raised.

    Examples:

    >>> name_to_argb('white')
    (255, 255, 255, 255)
    >>> name_to_argb('navy')
    (255, 0, 0, 128)
    >>> name_to_argb('goldenrod')
    (255, 218, 165, 32)

    """
    return hex_to_argb( name_to_hex( name ) )


def name_to_argb_percent( name ):
    """
    Convert a color name to a 4-tuple of percentages suitable for use
    in an ``argb()`` quadruplet specifying that color.

    The color name will be normalized to lower-case before being
    looked up, and when no color of that name exists in the given
    specification, ``ValueError`` is raised.

    Examples:

    >>> name_to_argb_percent('white')
    ('100%', '100%', '100%', '100%')
    >>> name_to_argb_percent('navy')
    ('100%', '0%', '0%', '50%')
    >>> name_to_argb_percent('goldenrod')
    ('100.00%', '85.49%', '64.71%', '12.5%')

    """
    return argb_to_argb_percent( name_to_argb( name ) )


def hex_to_name( hex_value ):
    """
    Convert a hexadecimal color value to its corresponding normalized
    color name, if any such name exists.

    The hexadecimal value will be normalized before being looked up,
    and when no color name for the value is found in the given
    specification, ``ValueError`` is raised.

    Examples:

    >>> hex_to_name('ffffffff')
    'white'
    >>> hex_to_name('fffff')
    'white'
    >>> hex_to_name('ff000080')
    'navy'
    >>> hex_to_name('ffdaa520')
    'goldenrod'
    >>> hex_to_name('90daa520')
    Traceback (most recent call last):
        ...
    ValueError: '90daa520' has no defined color name in xbmc.

    """
    normalized = normalize_hex( hex_value )
    try:
        name = xbmc_hex_to_names[ normalized.strip( '#' ) ]
    except KeyError:
        raise ValueError( "'%s' has no defined color name in xbmc." % hex_value )
    return name


def hex_to_argb( hex_value ):
    """
    Convert a hexadecimal color value to a 4-tuple of integers
    suitable for use in an ``argb()`` quadruplet specifying that color.

    The hexadecimal value will be normalized before being converted.

    Examples:

    >>> hex_to_argb('ffff')
    (255, 255, 255, 255)
    >>> hex_to_argb('ff000080')
    (255, 0, 0, 128)

    """
    hex_digits = normalize_hex( hex_value )
    hex_digits = ( hex_digits[ 0:2 ], hex_digits[ 2:4 ], hex_digits[ 4:6 ], hex_digits[ 6:8 ] )
    return tuple( map( lambda s: int( s, 16 ), hex_digits ) )


def hex_to_argb_percent( hex_value ):
    """
    Convert a hexadecimal color value to a 4-tuple of percentages
    suitable for use in an ``argb()`` quadruplet representing that color.

    The hexadecimal value will be normalized before converting.

    Examples:

    >>> hex_to_argb_percent('ffffffff')
    ('100%', '100%', '100%', '100%')
    >>> hex_to_argb_percent('ff000080')
    ('100%', '0%', '0%', '50%')

    """
    return argb_to_argb_percent( hex_to_argb( hex_value ) )


def argb_to_name( argb_quadruplet ):
    """
    Convert a 4-tuple of integers, suitable for use in an ``argb()``
    color quadruplet, to its corresponding normalized color name, if any
    such name exists.

    If there is no matching name, ``ValueError`` is raised.

    Examples:

    >>> argb_to_name((255, 255, 255, 255))
    'white'
    >>> argb_to_name((255, 0, 0, 128))
    'navy'

    """
    return hex_to_name( argb_to_hex( argb_quadruplet ) )


def argb_to_hex( argb_quadruplet ):
    """
    Convert a 4-tuple of integers, suitable for use in an ``argb()``
    color quadruplet, to a normalized hexadecimal value for that color.

    Examples:

    >>> argb_to_hex((255, 255, 255, 255))
    'ffffffff'
    >>> argb_to_hex((255, 0, 0, 128))
    'ff000080'

    """
    return '%02x%02x%02x%02x' % argb_quadruplet


def argb_to_argb_percent( argb_quadruplet ):
    """
    Convert a 4-tuple of integers, suitable for use in an ``argb()``
    color quadruplet, to a 4-tuple of percentages suitable for use in
    representing that color.

    This function makes some trade-offs in terms of the accuracy of
    the final representation; for some common integer values,
    special-case logic is used to ensure a precise result (e.g.,
    integer 128 will always convert to '50%', integer 32 will always
    convert to '12.5%'), but for all other values a standard Python
    ``float`` is used and rounded to two decimal places, which may
    result in a loss of precision for some values.

    Examples:

    >>> argb_to_argb_percent((255, 255, 255, 255))
    ('100%', '100%', '100%', '100%')
    >>> argb_to_argb_percent((255, 0, 0, 128))
    ('100%', '0%', '0%', '50%')
    >>> argb_to_argb_percent((255, 218, 165, 32))
    ('100.00%', '85.49%', '64.71%', '12.5%')

    """
    # In order to maintain precision for common values,
    # 256 / 2**n is special-cased for values of n
    # from 0 through 4, as well as 0 itself.
    specials = { 255: '100%', 128: '50%', 64: '25%', 32: '12.5%', 16: '6.25%', 0: '0%' }
    return tuple( map( lambda d: specials.get( d, '%.02f%%' % ( ( d / 255.0 ) * 100 ) ), argb_quadruplet ) )


def argb_percent_to_name( argb_percent_quadruplet ):
    """
    Convert a 4-tuple of percentages, suitable for use in an ``argb()``
    color quadruplet, to its corresponding normalized color name, if any
    such name exists.

    If there is no matching name, ``ValueError`` is raised.

    Examples:

    >>> argb_percent_to_name(('100%', '100%', '100%'))
    'white'
    >>> argb_percent_to_name(('100%', '0%', '0%', '50%'))
    'navy'
    >>> argb_percent_to_name(('100.00%', '85.49%', '64.71%', '12.5%'))
    'goldenrod'

    """
    return argb_to_name( argb_percent_to_argb( argb_percent_quadruplet ) )


def argb_percent_to_hex( argb_percent_quadruplet ):
    """
    Convert a 4-tuple of percentages, suitable for use in an ``argb()``
    color quadruplet, to a normalized hexadecimal color value for that
    color.

    Examples:

    >>> argb_percent_to_hex(('100%', '100%', '100%', '0%'))
    'ffffff00'
    >>> argb_percent_to_hex(('100%', '0%', '0%', '50%'))
    'ff000080'
    >>> argb_percent_to_hex(('100.00%', '85.49%', '64.71%', '12.5%'))
    'ffdaa520'

    """
    return argb_to_hex( argb_percent_to_argb( argb_percent_quadruplet ) )


def _percent_to_integer( percent ):
    """
    Internal helper for converting a percentage value to an integer
    between 0 and 255 inclusive.

    """
    num = float( str( percent ).split( '%' )[ 0 ] ) / 100.0 * 255
    e = num - math.floor( num )
    return e < 0.5 and int( math.floor( num ) ) or int( math.ceil( num ) )


def argb_percent_to_argb( argb_percent_quadruplet ):
    """
    Convert a 4-tuple of percentages, suitable for use in an ``argb()``
    color quadruplet, to a 4-tuple of integers suitable for use in
    representing that color.

    Some precision may be lost in this conversion. See the note
    regarding precision for ``argb_to_argb_percent()`` for details;
    generally speaking, the following is true for any 4-tuple ``t`` of
    integers in the range 0...255 inclusive::

        t == argb_percent_to_argb(argb_to_argb_percent(t))

    Examples:

    >>> argb_percent_to_argb(('100%', '100%', '100%', '100%'))
    (255, 255, 255, 255)
    >>> argb_percent_to_argb(('100%', '0%', '0%', '50%'))
    (255, 255, 0, 0, 128)
    >>> argb_percent_to_argb(('100.00%', '85.49%', '64.71%', '12.5%'))
    (255, 255, 218, 165, 32)

    """
    return tuple( map( _percent_to_integer, argb_percent_quadruplet ) )


if __name__ == '__main__':
    #print normalize_hex( 'f09C' )
    #print argb_percent_to_argb( ( 56.47, 76.86, 71.76, 7.84 ) )
    #print hex_to_argb( '9cb1' )

    #print argb_percent_to_hex( ( '56.47%', '76.86%', '71.76%', '7.84%' ) )

    #print hex_to_argb_percent( '90c4b714' )
    ##print hex_to_name( 'ffffffff' )

    #print name_to_hex( 'white' )
    print name_to_argb( 'white' )
