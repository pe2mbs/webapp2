import time
import traceback
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import os
import sys
import getopt
import logging
import webapp.api as API
from webapp.app import createApp
from webapp.extensions.database import getDataBase


class TableCopyMixing(object):
    def _getFields( self ):
        return [ f for f in dir( user ) if not f.startswith('_') and f not in ( 'classes', 'metadata', 'prepare', 'registry', 'role' ) ]

    def _cloneRecord( self, record ):
        for field in self._getFields():
            setattr( record, field, getattr( self, field ) )

        return


def usage():
    print()


def banner():
    print()


def main( **kwargs ):
    logLevels = [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ]
    API.rootPath    = kwargs.get( 'root_path', '/home/mbertens/src/python/iptv_m3u_server' )
    try:
        opts, args = getopt.getopt( sys.argv[1:], "hvc:", [ "help", "config=" ] )

    except getopt.GetoptError as err:
        API.logger.exception( "An exception during argument parsing" )
        # print help information and exit:
        print( err )  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    configFile = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            idx = logLevels.index( API.logger.level )
            verbose = True
            try:
                API.logger.setLevel( logLevels[ idx + 1 ] )

            except Exception:
                pass

        elif o in ( "-h", "--help" ):
            usage()
            sys.exit()

        elif o in ( "-c", "--config" ):
            configFile = os.path.abspath( a )

        else:
            assert False, "unhandled option"

    print( "Loading config {}".format( configFile ) )
    API.app = createApp( API.rootPath,
                         configFile,
                         full_start = False,
                         verbose = verbose,
                         process_name = os.environ.get( 'FLASK_TASK', 'memtablemanager' ) )

    API.logger = logging.getLogger( 'MemTableManager' )
    API.logger.info( 'MemTableManager starting' )
    # Initialize the main thread database connection
    getDataBase( API.app )
    API.app.app_context().push()
    try:
        from webapp.backend.user.model import User
        from webapp.backend.role.model import Role
        print( "Results from actual table" )
        t1 = time.time()
        records = API.db.session.query( User ).all()
        print( f"Elapsed: {time.time() - t1}")
        for user in records:
            print( user.U_NAME )



        metadata = MetaData()
        metadata.reflect( API.db.session.connection(), only=[ 'user', 'roles' ] )
        AutoBase = automap_base(metadata=metadata)
        memory_engine = create_engine( 'sqlite:///mem1?cache=shared&mode=memory", uri=True', echo=False, future=True )
        metadata.bind = memory_engine
        AutoBase.prepare()
        metadata.create_all()

        memory_session = Session( memory_engine )
        for user in API.db.session.query( User ).all():
            new_user = User()
            user.cloneRecord( new_user )
            memory_session.add( new_user )

        memory_session.commit()
        print( "Results from memory table" )
        t1 = time.time()
        records = memory_session.query( User ).all()
        print( f"Elapsed: {time.time() - t1}")
        for user in records:
            print( user.U_NAME )

        input("Wait")

    except Exception as exc:
        print( traceback.format_exc() )


    return

if __name__ == '__main__':
    main()
