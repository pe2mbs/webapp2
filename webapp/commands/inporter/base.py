import os
import webapp.api as API
from webapp.common.util import DbExporterInporters
from webapp.common.exceptions import InvalidModel


class DbInporter( object ):
    CLEAR = True

    def __init__( self, filename = None ):
        self._filename = filename
        self._stream = None
        return

    def open( self, filename ):
        if self._stream is not None:
            return

        if not os.path.isfile( filename ):
            API.app.logger.error( "Filename {} doesn't exists".format( filename ) )
            raise FileNotFoundError( filename )

        self._stream = open( filename, 'r' )
        return

    def close( self ):
        if self._stream is not None:
            self._stream.close()

        self._stream = None
        return

    def loadTable( self, table, model, clear ):
        return


class DbInporters( DbExporterInporters ):
    pass

