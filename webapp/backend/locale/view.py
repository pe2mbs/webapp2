from flask import Blueprint, request, jsonify
import webapp.api as API
from webapp.common.crud import CrudInterface, RecordLock
import traceback
from webapp.backend.locale.model import Locale
from webapp.backend.locale.schema import LocaleSchema


localeApi = Blueprint( 'localeApi', __name__ )


# Args is for downwards compatibility !!!!!
def registerApi( *args ):
    # Set the logger for the users module
    API.app.logger.info( 'Register Locale routes' )
    API.app.register_blueprint( localeApi )
    return



class LocaleRecordLock( RecordLock ):
    def __init__(self):
        RecordLock.__init__( self, 'locale', 'L_ID' )
        return


class LocaleCurdInterface( CrudInterface ):
    _model_cls = Locale
    _lock_cls = LocaleRecordLock
    _schema_cls = LocaleSchema()
    _schema_list_cls = LocaleSchema( many = True )
    _uri = '/api/locale'
    _relations = []

    def __init__( self ):
        CrudInterface.__init__( self, localeApi )
        return

    def beforeUpdate( self, record ):
        if "L_ID" in record and record[ "L_ID" ] in ( None, 0 ):
            del record[ "L_ID" ]




        return record


locale = LocaleCurdInterface()
