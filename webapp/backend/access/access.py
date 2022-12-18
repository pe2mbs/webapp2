import webapp.api as API
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
from webapp.backend.user.model import User
from webapp.backend.role.model import Role
from webapp.backend.access.model import Access


class AccessProfile( object ):
    def __init__( self, name, user, c = False, r = False, u = False, d = False ):
        self._name      = name
        self._user      = user
        self._create    = c
        self._read      = r
        self._update    = u
        self._delete    = d

    def hasFullAccess( self ):
        return self._read and self._update and self._delete and self._create

    def mayRead( self ):
        return self._read

    def mayUpdate( self ):
        return self._update

    def mayDelete( self ):
        return self._delete

    def mayCreate( self ):
        return self._create


def getCurrentAccessProfile( table_name: str ) -> AccessProfile:
    current_user = 'admin'
    if current_user == 'admin':
        return AccessProfile( table_name, current_user, True, True, True, True )

    else:
        try:
            userRecord: User = API.db.session.query( User ).filter( User.U_NAME == current_user ).one()
            roleRecord: Role = API.db.session.query( Role ).filter( Role.R_ID == userRecord.U_ROLE ).one()
            try:
                # Access based on ACCESS
                accessRecord: Access = API.db.session.query( Access ).filter( or_( Access.A_U_ID == userRecord.U_ID,
                                                                                   Access.A_R_ID == roleRecord.R_ID ) ).one()
                return AccessProfile( table_name,
                                      current_user,
                                      accessRecord.A_CREATE,
                                      accessRecord.A_READ,
                                      accessRecord.A_UPDATE,
                                      accessRecord.A_DELETE )

            except NoResultFound:
                # Access based on ROLE
                return AccessProfile( table_name,
                                      current_user,
                                      roleRecord.R_DEFAULT_CREATE,
                                      roleRecord.R_DEFAULT_READ,
                                      roleRecord.R_DEFAULT_UPDATE,
                                      roleRecord.R_DEFAULT_DELETE )

        except Exception:
            # Any aception must cause NO-ACCESS !!!!
            pass

    # No access to tablw
    return AccessProfile( table_name, current_user, False, False, False, False )

