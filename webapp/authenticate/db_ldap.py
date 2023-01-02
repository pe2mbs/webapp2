import traceback
import hashlib
import time
import json
from sqlalchemy.orm.exc import NoResultFound
from webapp.authenticate.ldap_srv import LdapAuthenticate
from webapp.backend.user.model import User
import webapp.api as API


class DbLdapAuthenticate( LdapAuthenticate ):
    def __init__( self ):
        super( DbLdapAuthenticate, self ).__init__( 'DB-LDAP' )
        self.MAX_PASSWORD_TRIES = API.app.config.get( 'MAX_PASSWORD_TRIES', 5 )
        self.MAX_WINDOW         = API.app.config.get( 'MAX_LOGGED_IN_WINDOW', 8 * 3600 )
        return

    def Authenticate( self, username, password ) -> bool:
        try:
            userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
            data = json.loads( userRecord.U_PROFILE )
            cnt = data.get( 'pw-failed-count', 0 )
            if cnt >= self.MAX_PASSWORD_TRIES:
                API.app.logger.warning( f"User '{username}' exceeded password tries, user locked out" )
                return False

            last_pam_auth = data.get( 'last-pam-auth', 0 )
            hash = hashlib.sha3_512()

            def doLdapAuthenticate() -> bool:
                result = LdapAuthenticate.Authenticate( self, username, password )
                if result:
                    # Set the new HASH and update the last time we used PAM
                    hash.update( username )
                    hash.update( password )
                    userRecord.U_HASH_PASSWORD = hash.hexdigest()
                    data[ 'last-pam-auth' ] = time.time()
                    data[ 'pw-failed-count' ] = 0

                else:
                    # Failed, update the count and clear the 'last-pam-auth'
                    data[ 'pw-failed-count' ] += 1
                    data[ 'last-pam-auth' ] = 0

                return result

            if last_pam_auth == 0 or userRecord.U_HASH_PASSWORD is ( None, "" ):
                # When 'last-pam-auth' is zero or when U_HASH_PASSWORD is not set, always authenticate via PAM
                result = doLdapAuthenticate()

            else:
                # We have a valid HASH, check the WINDOW
                if last_pam_auth >= (time.time() - self.MAX_WINDOW):
                    # Hashed password
                    hash.update( username )
                    hash.update( password )
                    result = hash.hexdigest() == userRecord.U_HASH_PASSWORD
                    if result:
                        data[ 'pw-failed-count' ] = 0

                    else:
                        # The password failed, so do the PAM authiricate
                        result = doLdapAuthenticate()

                else:
                    # Outside the WINDOW, so do the PAM authiricate
                    result = doLdapAuthenticate()

            if not result:
                data[ 'pw-failed-count' ] += 1
                cnt = data[ 'pw-failed-count' ]
                API.app.logger.warning( f"User '{username}' failed password (try: {cnt})" )

            # Update the user record with the failed count and optional the hashed password
            userRecord.U_PROFILE = json.dumps( data )
            API.db.session.commit()
            return result

        except NoResultFound:
            API.app.logger.error( f"User '{username}' not found" )

        except Exception:
            API.app.logger.error( traceback.format_exc() )

        return False
