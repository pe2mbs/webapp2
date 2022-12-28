from flask import Blueprint
import webapp.api as API
from webapp.backend.access.model import Access
from webapp.common.crud import CrudInterface, RecordLock

webappAccessApi = Blueprint( 'webappAccessApi', __name__ )


# Args is for downwards compatibility !!!!!
def registerApi( *args ):
    # Set the logger for the access module
    API.app.logger.info( 'Register Access routes' )
    API.app.register_blueprint( webappAccessApi )
    return

class AccessRecordLock( RecordLock ):
    def __init__(self):
        RecordLock.__init__( self, 'access', 'A_ID' )
        return


class AccessCurdInterface( CrudInterface ):
    _model_cls = Access
    _lock_cls = AccessRecordLock
    #_schema_cls = AccessSchema()
    #_schema_list_cls = AccessSchema( many = True )
    _uri = '/api/webapp/access'
    _relations = []

    def __init__( self ):
        CrudInterface.__init__( self, webappAccessApi )
        return

    def beforeUpdate( self, record ):
        for field in ( "A_ID", ):
            if field in record:
                del record[ field ]

        return record


user = AccessCurdInterface()