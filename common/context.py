import webapp2.api as API
from sqlalchemy import text


def dbContextPush():
    API.app.app_context().push()
    if "mysql" in API.db.session.get_bind().dialect.name:
        # This is nessary for the QUERY below to read the changes make by other processes.
        API.logger.info( "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED" )
        API.db.session.execute( text( "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED" ) )

    return
