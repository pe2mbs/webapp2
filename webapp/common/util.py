# -*- coding: utf-8 -*-
"""Main webapp application package."""
#
# Main webapp application package
# Copyright (C) 2018-2023 Marc Bertens-Nguyen <m.bertens@pe2mbs.nl>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License GPL-2.0-only
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import os
from itertools import tee, islice, zip_longest
from dateutil.parser import parse
from dateutil.tz import gettz

to_zone = gettz( 'Europe/Amsterdam' )


def keysToString( keys ):
    if len( keys ) > 1:
        return ', '.join( [ value for value in keys[ : -1 ] ] ) + ' and ' + keys[ -1 ]

    if len( keys ) == 1:
        return keys[ 0 ]

    return "?"


class DbExporterInporters( dict ):
    def __init__( self, d ):
        super( DbExporterInporters, self ).__init__()
        for key, value in d.items():
            self[ key ] = value

        return

    def hasClear2String( self ):
        result = [ ]
        for key,value in self.items():
            if value.CLEAR:
                result.append( key.upper() )

        return keysToString( result )

    def keysUpperCase( self ):
        return [ k.upper() for k in self.keys() ]

    def keysToString( self ):
        return keysToString( self.keysUpperCase() )


def CommandBanner( *args ):
    l = 76
    for line in args:
        if len( line ) > l:
            l = len( line )

    print( "+{}+".format( "-" * (l+2) ) )
    for line in args:
        print( "| {:{}} |".format( line, l ) )

    print( "+{}+".format( "-" * (l+2) ) )
    return


def ResolveRootPath( path ):
    if path == '':
        path = os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..', '..' ) )

    elif path == '.':
        path = os.path.abspath( path )

    return os.path.abspath( path )


def toggleInDict( d, key, value, recursive = False ):
    for k in d.keys():
        if k == key:
            d[ key ] = value

        elif recursive and type( d[ k ] ) is dict:
            d[ k ] = toggleInDict( d[ k ], key, value, recursive )

        elif recursive and type( d[ k ] ) is list:
            for idx, item in enumerate( d[ k ] ):
                if type( item ) is dict:
                    d[ k ][ idx ] = toggleInDict( d[ key ][ idx ], key, value, recursive )

    return d


class TableManager( object ):
    def __init__(self):
        self.__tables = {}

    def register( self, cls ):
        self.__tables[ cls.__tablename__ ] = cls
        return

    def get( self, name ):
        try:
            return self.__tables[ name ]

        except Exception:
            pass

        return None

    def instanciate( self, name ):
        try:
            return self.__tables[ name ]()

        except Exception:
            pass

        return None


def lookahead( iterable ):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False


def nextahead( some_iterable, window = 1):
    items, nexts = tee( some_iterable, 2 )
    nexts = islice( nexts, window, None )
    return zip_longest( items, nexts )


def value2Label( dictionary, value ):
    try:
        return dictionary[ value ]

    except Exception:
        return value


def utcDateString2Local( value, fmt = '%Y-%m-%d' ):
    return parse( value ).astimezone( to_zone ).date().strftime( fmt )
