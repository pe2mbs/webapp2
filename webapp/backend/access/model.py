import webapp.api as API
from webapp.common import DbBaseMemory, CrudModelMixin


class Access( API.db.Model, CrudModelMixin ):
    __field_list__      = [ 'A_ID', 'A_COMPONENT', 'A_OBJECT', 'A_R_ID', 'A_CREATE', 'A_READ', 'R_UPDATE', 'R_DELETE', 'A_REMARK' ]
    __tablename__       = 'access'
    #__schema_cls__       = AccessSchema()
    A_ID                = API.db.Column( "a_id", API.db.Integer, autoincrement = True, primary_key = True )
    A_COMPONENT         = API.db.Column( "a_component", API.db.String(50), default = False )
    A_OBJECT            = API.db.Column( "a_object", API.db.Integer, default = 0 )
    A_R_ID              = API.db.Column( "a_r_id", API.db.Integer, API.db.ForeignKey( "roles.r_id" ), nullable = True )
    A_CREATE            = API.db.Column( "a_create", API.db.Boolean, default = False )
    A_READ              = API.db.Column( "a_read", API.db.Boolean, default = True )
    A_UPDATE            = API.db.Column( "a_update", API.db.Boolean, default = False )
    A_DELETE            = API.db.Column( "a_delete", API.db.Boolean, default = False )
    A_REMARK            = API.db.Column( "a_remark", API.db.LONGTEXT, nullable = True )

    def memoryInstance( self ):
        return AccessMemory( self )

API.dbtables.register( Access )

class AccessMemory( DbBaseMemory ):
    __model_cls__       = Access
    __tablename__       = 'access'

API.memorytables.register( AccessMemory )