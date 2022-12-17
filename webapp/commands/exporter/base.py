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
from webapp.common.util import DbExporterInporters
from webapp.common.exceptions import InvalidModel


class DbExporter( object ):
    CLEAR = False

    def __init__( self, filename = None ):
        self._filename = filename
        self._stream   = None
        return

    def open( self, filename ):
        if self._stream is None:
            self._stream = open( filename, 'w' )

        return

    def close( self ):
        if self._stream is not None:
            self._stream.close()

        self._stream = None
        return

    def writeTable( self, table, records, clear ):
        return

    def buildRecord( self, table, record ):
        if not hasattr( record, 'toDict' ):
            raise InvalidModel( table )

        return record.toDict()


class DbExporters( DbExporterInporters ): pass
