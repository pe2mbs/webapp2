import json
from datetime import datetime
from typing import Union

from numpy import record
from webapp2.common.jsonenc import JsonEncoder
import webapp2.api as API
from webapp2.common.tracking.model import Tracking
from sqlalchemy.orm import attributes as history_attributes
from sqlalchemy import text

class RecordTracking( object ):
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    CASCADE_DELETE = 4


    def __init__(self):
        return

    def _getAttr(self, record: Union[dict, object], field):
        return record.get(field, "") if isinstance( record, dict ) else getattr(record, field, "")

    def action( self, action, table, rec_id, record, user ):
        API.logger.debug( "record action: {} => {}".format( action, record ) )
        if isinstance( record, dict ):
            data = json.dumps( record, cls = JsonEncoder )
        else:
            data = record.json

        version_num = ""
        for row in API.db.engine.execute( text( 'select version_num from alembic_version' ) ):
            version_num = row[ 0 ]
        
        record_name_field = getattr( API.tables_dict[table], "__secondary_key__", "" )
        record_name = ""
        if record_name_field not in ("", None):
            record_name = self._getAttr(record, record_name_field)
        else:
            for field in API.tables_dict[table].__field_list__:
                if field.endswith( 'NAME' ):
                    record_name = self._getAttr(record, field)
                    break
        API.db.session.add( Tracking( T_USER = user,
                                      T_TABLE = table,
                                      T_ACTION = action,
                                      T_RECORD_ID = int( rec_id ),
                                      T_RECORD_NAME = record_name,
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

            record_name_field = getattr( API.tables_dict[tables[0]], "__secondary_key__", "" )
            record_name = ""
            if record_name_field not in ("", None):
                record_name = self._getAttr(record_instances[0], record_name_field)
            else:
                for field in API.tables_dict[tables[0]].__field_list__:
                    if field.endswith( 'NAME' ):
                        record_name = self._getAttr(record_instances[0], field)
                        break
            API.db.session.add( Tracking( T_USER = user,
                                        T_TABLE = json.dumps( tables, cls = JsonEncoder ),
                                        T_ACTION = self.CASCADE_DELETE,
                                        T_RECORD_ID = int( parent_rec_id ),
                                        T_RECORD_NAME = record_name,
                                        T_CONTENTS = data,
                                        T_CHANGE_DATE_TIME = datetime.utcnow(),
                                        T_VERSION = version_num ) )
            API.db.session.commit()
        return

    def autoUpdate( self, modifiedRecord, user ):
        oldRecord = modifiedRecord.dictionary
        for key in oldRecord:
            # get an history object that shows the changes for a given attribute
            # deleted specifies the old value for an attribute
            changedValues = history_attributes.get_history(modifiedRecord, key).deleted
            if len(changedValues) > 0:
                oldRecord[key] = changedValues[-1]
        self.update( modifiedRecord.__tablename__,
                            getattr(modifiedRecord, modifiedRecord.__field_list__[ 0 ]),
                            oldRecord,
                            user )

# API.recordTracking = RecordTracking()