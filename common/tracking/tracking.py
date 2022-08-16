import json
from datetime import datetime

from numpy import record
from webapp2.common.jsonenc import JsonEncoder
import webapp2.api as API
from webapp2.common.tracking.model import Tracking
from sqlalchemy import text


class RecordTracking( object ):
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    CASCADE_DELETE = 4


    def __init__(self):
        return

    def action( self, action, table, rec_id, record, user ):
        API.logger.debug( "record action: {} => {}".format( action, record ) )
        if isinstance( record, dict ):
            data = json.dumps( record, cls = JsonEncoder )
        else:
            data = record.json

        version_num = ""
        for row in API.db.engine.execute( text( 'select version_num from alembic_version' ) ):
            version_num = row[ 0 ]
        API.db.session.add( Tracking( T_USER = user,
                                      T_TABLE = table,
                                      T_ACTION = action,
                                      T_RECORD_ID = int( rec_id ),
                                      T_CONTENTS = data,
                                      T_CHANGE_DATE_TIME = datetime.utcnow(),
                                      T_VERSION = version_num ) )
        API.db.session.commit()
        return

    def insert( self, table, rec_id, record_instance, user ):
        API.logger.debug( "record insert( {} )".format( record_instance ) )
        self.action( self.INSERT, table, rec_id, record_instance, user )
        return

    def update( self, table, rec_id, record_instance, user ):
        API.logger.debug( "record update( {} )".format( record_instance ) )
        self.action( self.UPDATE, table, rec_id, record_instance, user )
        return

    def delete( self, table, rec_id, record_instance, user ):
        API.logger.debug( "record delete( {} )".format( record_instance ) )
        self.action( self.DELETE, table, rec_id, record_instance, user )
        return

    def cascade_delete( self, tables, parent_rec_id, record_instances, user ):
        if len(record_instances) > 0:
            API.logger.debug( "cascade delete( {} with id {} )".format( tables[0], parent_rec_id ) )
            if isinstance( record_instances[0], dict ):
                data = json.dumps( record_instances, cls = JsonEncoder )
            else:
                data = json.dumps( [record.dictionary for record in record_instances], cls = JsonEncoder )

            version_num = ""
            for row in API.db.engine.execute( text( 'select version_num from alembic_version' ) ):
                version_num = row[ 0 ]
            API.db.session.add( Tracking( T_USER = user,
                                        T_TABLE = json.dumps( tables, cls = JsonEncoder ),
                                        T_ACTION = self.CASCADE_DELETE,
                                        T_RECORD_ID = int( parent_rec_id ),
                                        T_CONTENTS = data,
                                        T_CHANGE_DATE_TIME = datetime.utcnow(),
                                        T_VERSION = version_num ) )
            API.db.session.commit()
        return


# API.recordTracking = RecordTracking()