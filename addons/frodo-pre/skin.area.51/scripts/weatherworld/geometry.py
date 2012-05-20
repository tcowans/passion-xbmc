"""
    based on pygame - Python Game Library
    for script.game.arkanoid
    by frost (passion-xbmc.org)
"""

#Modules general
import random
from math import *


class Error( Exception ):
    pass


try:
    triangular = random.triangular
except:
    def triangular( low=0.0, high=1.0, mode=None ):
        """random.triangular(...) not implanted in python 2.4
        Triangular distribution.

        Continuous distribution bounded by given lower and upper limits,
        and having a given mode value in-between.

        http://en.wikipedia.org/wiki/Triangular_distribution

        """
        u = random.random()
        #c = 0.5 if mode is None else (mode - low) / (high - low) # python 2.5 to 3.xx only
        if mode is None: c = 0.5 
        else: c = ( mode - low ) / ( high - low )
        if u > c:
            u = 1.0 - u
            c = 1.0 - c
            low, high = high, low
        return low + ( high - low ) * ( u * c ) ** 0.5


class Rectangle:
    def __init__( self, x, y, w, h ):
        self.x = x
        self.y = y
        self.w = w or 1
        self.h = h or 1
        self.width = self.w
        self.height = self.h

        self.top = self.y
        self.left = self.x
        self.bottom = self.top + self.height
        self.right = self.left + self.width

        self.centerx = self.left + int( self.width/2.0 )
        self.centery = self.top + int( self.height/2.0 )
        self.center = ( self.centerx, self.centery )
        self.size = ( self.width, self.height )

        self.topleft = ( self.left, self.top )
        self.topright = ( self.right, self.top )
        self.bottomleft = ( self.left, self.bottom )
        self.bottomright = ( self.right, self.bottom )

        self.midtop = ( self.centerx, self.top )
        self.midleft = ( self.left, self.centery )
        self.midbottom = ( self.centerx, self.bottom )
        self.midright = ( self.right, self.centery )

    def __repr__( self ):
        return "<rect(%d, %d, %d, %d)>" % ( self.x, self.y, self.w, self.h )


class Rect( Rectangle ):
    def __init__( self, x=0, y=0, w=0, h=0 ):
        Rectangle.__init__( self, x, y, w, h )

    def move( self, x, y ):
        Rectangle.__init__( self, x, y, self.w, self.h )

    def resize( self, w, h ):
        Rectangle.__init__( self, self.x, self.y, w, h )

    def collidepoint( self, *xy ):
        """Rect.collidepoint

            test if a point is inside a rectangle
            Rect.collidepoint(x, y): return bool
            Rect.collidepoint((x,y)): return bool

            Returns true if the given point is inside the rectangle.

            A point along the right or bottom edge is not considered to be inside the rectangle.
            inside = x >= self.left and x < self.right and y >= self.top and y < self.bottom
        """
        if len( xy ) == 1:
            try:
                x, y = xy[ 0 ]
            except:
                raise Error, "bad point argument: %r" % ( xy[ 0 ], )
        else:
            try:
                x, y = xy
            except:
                raise Error, "bad coordinates: %r" % ( xy[ 0 ], )
        #for arkanoid include "right and bottom edge"
        inside = x >= self.left and x <= self.right and y >= self.top and y <= self.bottom
        return inside

    def colliderect( self, rect ):
        """Rect.colliderect

              test if two rectangles overlap
              Rect.colliderect(Rect): return bool

              Returns true if any portion of either rectangle overlap.
        """
        rectpos = [ rect.center, rect.midtop, rect.midleft, rect.midbottom, rect.midright, 
            rect.topleft, rect.topright, rect.bottomleft, rect.bottomright ]
        ret = self.collidelist( rectpos )
        return ret

    def collidelist( self, liste ):
        """Rect.collidelist

              test if one point in a list intersects
              Rect.collidelist(list): return index

              Test whether the point collides with any in a sequence of rectangles.
              The index of the first collision found is returned. If no collisions are found None is returned.
        """
        ret = None
        for count, xy in enumerate( liste ):
            if self.collidepoint( xy ):
                ret = count
                break
        return ret

    def collidelistall( self, liste ):
        """Rect.collidelistall

              test if all rectangles in a list intersect
              Rect.collidelistall(list): return indices

              Returns a list of all the indices that contain rectangles that collide with the Rect.
              If no intersecting rectangles are found, an empty list is returned.
        """
        indices = []
        for count, xy in enumerate( liste ):
            if self.collidepoint( xy ):
                indices.append( count )
        return indices

    def collidedict( self, dico ):
        """Rect.collidedict

              test if one rectangle in a dictionary intersects
              Rect.collidedict(dict): return (key, value)

              Returns the key and value of the first dictionary value that collides with the Rect.
              If no collisions are found, None is returned.

              Rect objects are not hashable and cannot be used as keys in a dictionary, only as values.
        """
        ret = None
        for key, value in dico.items():
            if self.colliderect( value ) is not None:
                ret = key, value
                break
        return ret

    def collidedictall( self, dico ):
        """Rect.collidedictall

              test if all rectangles in a dictionary intersect
              Rect.collidedictall(dict): return [(key, value), ...]

              Returns a list of all the key and value pairs that intersect with the Rect.
              If no collisions are found an empty dictionary is returned.

              Rect objects are not hashable and cannot be used as keys in a dictionary, only as values.
        """
        indices = []
        for key, value in dico.items():
            if self.colliderect( value ) is not None:
                indices.append( ( key, value ) )
        return indices

    def collidedirection( self, rect ):
        """Rect.collidedirection
        """
        direction = [ "center", "midtop", "midleft", "midbottom", "midright", "topleft", "topright", "bottomleft", "bottomright" ]
        index = self.colliderect( rect )
        if index is not None:
            return direction[ index ]


class Circle:
    def __init__( self, x, y, r, e=None ):
        self.coords = []
        self._origin = ( x, y, r, e )
        self.circle( x, y, r, e )

    def circle( self, posx, posy, radius, extent=None ):
        position = posx, posy
        angle = 0.0
        fullcircle = 360.0
        invradian = pi / ( fullcircle * 0.5 )
        if extent is None:
            extent = fullcircle
        frac = abs( extent ) / fullcircle
        steps = 1 + int( min( 11 + abs( radius ) / 6.0, 59.0 ) * frac )
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        distance = 2.0 * radius * sin( w2 * invradian )
        if radius < 0:
            distance, w, w2 = -distance, -w, -w2
        angle = ( angle + w2 ) % fullcircle
        for i in range( steps ):
            x0, y0 = start = position
            x1 = x0 + distance * cos( angle * invradian )
            y1 = y0 - distance * sin( angle * invradian )

            x0, y0 = position
            position = map( float, ( x1, y1 ) )
            dx = float( x1 - x0 )
            dy = float( y1 - y0 )
            distance2 = hypot( dx, dy )
            nhops = int( distance2 )
            try:
                for i in range( 1, 1+nhops ):
                    x, y = x0 + dx * i / nhops, y0 + dy * i / nhops
                    self.coords.append( ( x, y ) )
            except:
                pass
            angle = ( angle + w ) % fullcircle
        angle = ( angle + -w2 ) % fullcircle

    def __repr__( self ):
        return "<circle(%s,%s)>" % ( self._origin, self.coords )


if  __name__ == "__main__":
    #print Rect( 0, 0, 0, 0 )
    #circ = Circle( 680, 293, 6 )

    #print min( circ.coords ), max( circ.coords )

    rect = Rect( 600, 300, 80, 120 )
    print rect
    rect.move( 500, 360 )
    print rect
    rect.resize( 256, 256 )
    print rect
    #point = rect.collidelistall( circ.coords )
    #center = circ.coords[ int( len( point )/2 ) ]
    #print "centerpoint", center
    #for p in point:
    #    print circ.coords[ p ]

    #print rect
    #print rect.center

    #print rect.midtop
    #print rect.midleft
    #print rect.midbottom
    #print rect.midright

    #print triangular()
