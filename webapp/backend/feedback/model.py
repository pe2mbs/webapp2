import webapp.api as API
# from webapp.common.dbmem import DbBaseMemory
# from webapp.common.crudmixin import CrudModelMixin

#
#   This part contains the standard /api/ routes other then loading the Angular application
#   TODO: This needs to be moved
#
class Feedback( API.db.Model ):
    __tablename__       = 'feedback'
    F_ID                = API.db.Column( "f_id",        API.db.Integer, autoincrement = True, primary_key = True )
    F_NAME              = API.db.Column( "f_name",      API.db.String( 50 ), nullable = False )
    F_TYPE              = API.db.Column( "f_type",      API.db.Integer, nullable = False )
    F_VOTED             = API.db.Column( "f_voted",     API.db.Integer, nullable = False )
    F_SUBJECT           = API.db.Column( "f_subject",   API.db.String( 100 ), nullable = False )
    F_MESSAGE           = API.db.Column( "f_message",   API.db.Text, nullable = True )
    F_STATUS            = API.db.Column( "f_status",    API.db.Integer, nullable = True )
    F_DATETIME          = API.db.Column( "f_datetime",  API.db.DateTime, nullable = True )
