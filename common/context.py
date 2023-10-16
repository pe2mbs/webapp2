import webapp2.api as API
from sqlalchemy import text
import threading
import flask

registeredThreads = {}


def dbContextPush():
    global registeredThreads
    name = threading.currentThread().name
    if name in registeredThreads:
        return registeredThreads[ name ]

    if isinstance( flask.globals.app_ctx, flask.ctx.AppContext ):
        API.logger.debug( f"Context present for name {name}" )

    else:
        API.app.app_context().push()
        API.logger.info( f"Flask Context created for {name}" )

    if name.startswith('Thread-'):
        session = API.db._make_scoped_session( { } )
        API.logger.info( f"Using scoped database session for {name}" )

    elif name == 'MainThread':
        session = API.db.session
        API.logger.info( f"Using default database session for {name}" )

    else:
        session = API.db.session
        API.logger.info( f"Using default database session for {name}" )

    registeredThreads[ name ] = session
    if "mysql" in session.get_bind().dialect.name:
        # This is nessary for the QUERY below to read the changes make by other processes.
        API.logger.info( f"'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED' for {name} " )
        session.execute( text( "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED" ) )

    return session
