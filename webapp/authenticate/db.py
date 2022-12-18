import traceback
import hashlib
import json
from sqlalchemy.orm.exc import NoResultFound
from backend.user.model import User
import webapp.api as API
from webapp.authenticate.base import Authenticate


class DbAuthenticate( Authenticate ):
    def __init__(self):
        super( DbAuthenticate, self ).__init__()
        return

    MAX_PASSWORD_TRIES = 5

    def Authenticate( self, username, password ) -> bool:
        try:
            userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
            data = json.loads( userRecord.U_PROFILE )
            cnt = data.get( 'pw-failed-count', 0 )
            if cnt >= self.MAX_PASSWORD_TRIES:
                API.app.logger.warning( f"User '{username}' exceeded password tries, user locked out" )
                return False

            hash = hashlib.sha3_512()
            if userRecord.U_HASH_PASSWORD.startswith( 'hash:' ):
                # Hashed password
                hash.update( username )
                hash.update( password )
                result = hash.hexdigest() == userRecord.U_HASH_PASSWORD[5:]
                if result:
                    cnt = 0

            else:
                # Plain text password
                result = userRecord.U_HASH_PASSWORD == password
                if result:
                    # Hash the password and store into the record
                    hash.update( username )
                    hash.update( password )
                    userRecord.U_HASH_PASSWORD = f"hash:{hash.hexdigest()}"
                    cnt = 0

            if not result:
                API.app.logger.warning( f"User '{username}' failed password (try: {cnt})" )
                cnt += 1

            # Update the user record with the failed count and optional the hashed password
            data[ 'pw-failed-count' ] = cnt
            userRecord.U_PROFILE = json.dumps( data )
            API.db.session.commit()
            return result

        except NoResultFound:
            API.app.logger.error( f"User '{username}' not found" )

        except Exception:
            API.app.logger.error( traceback.format_exc() )

        return False

