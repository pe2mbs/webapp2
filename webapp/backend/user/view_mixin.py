import json
import traceback
from flask import jsonify, request
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
import webapp.api as API
from webapp.common.decorators import no_pre_processing, requires_access
from webapp.common.util import Right
from webapp.authenticate.init import initAuthenticator
from webapp.backend.user.model import User
from webapp.backend.role.model import Role
#from webapp.backend.access.util import getCurrentAccessProfile
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, decode_token
from webapp.backend.user.constant import JWT_EXPIRATION_DAYS


class UserViewMixin():
    def __init__( self ):
        self.__authentcatior = initAuthenticator()
        self.registerRoute( 'profile/<username>', self.restoreProfile, methods = [ 'GET' ] )
        self.registerRoute( 'profile', self.storeProfile, methods = [ 'POST' ] )
        self.registerRoute( 'authenticate', self.getUserAuthenticate, methods = [ 'POST' ] )
        self.registerRoute( 'signup', self.getUserSignup, methods = [ 'POST' ] )
        self.registerRoute( 'logout', self.userLogout, methods = [ 'POST' ] )
        self.registerRoute( 'pagesize', self.pageSize, methods = [ 'GET' ] )
        return

    @jwt_required
    @no_pre_processing(blueprint="webappUserApi")
    def userLogout( self ):
        return "", 200

    @jwt_required
    @requires_access("webappUserApi", [Right.READ])
    def pageSize( self ):
        self.checkAuthentication()
        username = get_jwt_identity()
        defaultPageSize = [ 5, 10, 25, 100 ]
        try:
            userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
            pageSize = userRecord.U_LISTITEMS

        except NoResultFound:
            pageSize = defaultPageSize
            pass

        return jsonify( pageSize = pageSize, pageSizeOptions = defaultPageSize )

    @jwt_required
    @requires_access("webappUserApi", [Right.READ])
    def restoreProfile( self, username ):
        self.checkAuthentication()
        profileData = { 'locale': 'en_GB',
                        'pageSize': 10,
                        'pageSizeOptions': [ 5, 10, 25, 100 ],
                        'user': 'guest',
                        'fullname': "Guest",
                        'role': 0,
                        'roleString': 'Guest',
                        'theme': 'light-theme', 'objects': { },
                        'profilePage': '', 'profileParameters': {} }
        if username not in ( '', None, 'undefined' ):
            API.logger.info( "Restore profile for user: {}".format( username ) )
            try:
                userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
                if userRecord.U_PROFILE is None:
                    userRecord.U_PROFILE = ''

                if userRecord.U_PROFILE.startswith( '{' ) and userRecord.U_PROFILE.endswith( '}' ):
                    # TODO: This needs to be moved to it own field U_PROFILE
                    data = json.loads( userRecord.U_PROFILE )

                else:
                    data = { }

                profileData = { 'locale': userRecord.U_LOCALE,
                                'pageSize': userRecord.U_LISTITEMS,
                                'pageSizeOptions': [ 5, 10, 25, 100 ],
                                'user': userRecord.U_NAME,
                                'fullname': "{} {}".format( userRecord.U_FIRST_NAME, userRecord.U_LAST_NAME ),
                                'role': userRecord.U_R_ID,
                                'roleString': userRecord.U_R_ID_FK.R_NAME,
                                'theme': data.get( 'theme', 'light-theme' ),
                                'objects': data.get( 'objects', { } ),
                                'profilePage': '/user/edit',
                                'profileParameters': { 'id': 'U_ID', 'mode': 'edit', 'value': userRecord.U_ID, } }
                API.logger.info( "RESTORE.PROFILE: {}".format( profileData ) )

            except NoResultFound:
                pass

        return jsonify( profileData )

    @jwt_required
    @requires_access("webappUserApi", [Right.READ, Right.UPDATE])
    def storeProfile( self ):
        self.checkAuthentication()
        profileData = request.json
        username = get_jwt_identity()
        if username not in ( '', None, 'undefined' ):
            API.logger.info( "Store profile for user: {}".format( username ) )
            try:
                userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
                data = { 'theme': profileData.get( 'theme', 'light-theme' ),
                         'objects': profileData.get( 'objects', { } ) }
                userRecord.U_PROFILE = json.dumps( data )
                API.logger.info( "STORE.PROFILE: {}".format( userRecord.U_PROFILE ) )
                API.db.session.commit()

            except NoResultFound:
                pass

        else:
            API.logger.error( "Missing username" )

        return jsonify( ok = True )

    def encodeToken( self, username, keepsignedin ):
        """
            “exp” (Expiration Time) Claim
            “nbf” (Not Before Time) Claim
            “iss” (Issuer) Claim
            “aud” (Audience) Claim
            “iat” (Issued At) Claim
        """
        if keepsignedin:
            expiration = timedelta( days = JWT_EXPIRATION_DAYS )

        else:
            expiration = timedelta( days = 1 )

        API.logger.info( "identity = {}".format( username ) )
        return create_access_token( identity = username, expires_delta = expiration )

    def decodeToken( self, token ):
        try:
            decoded = decode_token( token )
            API.logger.info( "Decoded TOKEN: {}".format( decoded ) )
            return decoded[ 'username' ], decoded[ 'userrole' ]

        except Exception:
            return None, None

        except Exception:
            raise

    @no_pre_processing(blueprint="webappUserApi")
    def getUserAuthenticate( self ):
        data = request.json
        print("#####", request.json, request.data, request.args)
        API.app.logger.info( data )
        if data is None:
            return "Invalid request, missing user data", 500

        username = data.get( 'userid', None )
        passwd = data.get( 'password', None )
        result = self.__authentcatior.Authenticate( username, passwd )
        if result:
            token = self.encodeToken( username, data.get( 'keepsignedin', False ) )

        else:
            token = None

        return jsonify( result = result, token = token )

    @no_pre_processing("webappUserApi")
    def getUserSignup( self ):
        """The user sign-up is used for registering an new user into the database,
        and for unlocking a locked account

        :return:
        """
        data = request.json
        API.app.logger.info( data )
        if data is None:
            return "Invalid request, missing user data", 500

        authMethod = API.app.config.get( 'AUTHENTICATE', '' )
        if authMethod in ( "PAM", "LDAP" ):
            return jsonify( result = False, message = f"Account must be pre-registered via {authMethod}" )

        username = data.get( 'username', None )
        passwd = data.get( 'password', None )
        email = data.get( 'email', None )
        firstname = data.get( 'firstname', None )
        middlename = data.get( 'middlename', None )
        lastname = data.get( 'lastname', None )
        try:
            # We use the sign-up also as "account locked" reset, therefore the account must be active
            userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
            # When the account is ACTIVE we allow the reset
            if userRecord.U_ACTIVE:
                # Save the retry count
                cnt = userRecord.U_PASSWD_TRIES
                userRecord.U_PASSWD_TRIES = 0
                API.db.session.commit()
                # Second the password musty be validated correctly
                if self.__authentcatior.Authenticate( username, passwd ):
                    # Third validate the user email, first, middle and last name
                    if ( userRecord.U_EMAIL == email and userRecord.U_FIRST_NAME == firstname and userRecord.U_LAST_NAME == lastname and userRecord.U_MIDDLE_NAME == middlename ):
                        return jsonify( result = True, message = "Password lock removed" )

                # Authentication or attribute verify failed, so restore the count and DISABLE the account
                userRecord: User = API.db.session.query( User ).filter( User.U_NAME == username ).one()
                userRecord.U_PASSWD_TRIES = cnt
                userRecord.U_ACTIVE = False
                # Now log some info from the request
                API.app.logger.error( f"User {username} locked and disabled\nHeaders: {request.headers}\nRemote address: {request.remote_addr}\nRemote User: {request.remote_user}" )
                return jsonify( result = False, message = "Account is disabled and locked." )

        except NoResultFound:
            # User was not found, so NEW user
            try:
                roleRecord: Role = API.db.session.query( Role ).filter( Role.R_NAME.in_( 'Guest', 'Viewer' ) ).one()
                # When the Guest role is present in the Role table, the account is set active direcly.
                # When the Viewer role is present in the role table, the account is set in-active.
                API.db.session.add( User( U_NAME        = username,
                                          U_FIRST_NAME  = firstname,
                                          U_LAST_NAME   = lastname,
                                          U_MIDDLE_NAME = middlename,
                                          U_PASSWD_TRIES = 0,
                                          U_EMAIL       = email,
                                          U_R_ID        = roleRecord.R_ID,
                                          U_ACTIVE      = True if roleRecord.R_NAME == 'Guest' else False,
                                          U_LISTITEMS   = 25,
                                          U_LOCALE      = 1 ) )  # Should be the default locale
                API.db.session.commit()
                if roleRecord.R_NAME == 'Viewer':
                    msg = f"contact application manager for activation of your account and assining the correct role"

                else:
                    msg = "You can not login"

                return jsonify( result = True, message = f"User was added with role {roleRecord.R_NAME}, {msg}." )

            except NoResultFound:
                API.app.logger.error( f"In the Role table 'Guest' nor 'Viewer' was found, couldn't add new user {username}" )

            except Exception:
                API.app.logger.error( traceback.format_exc() )

        except Exception:
            API.app.logger.error( traceback.format_exc() )

        return jsonify( result = False, message = "Couldn't add user, contact application manager" )

    def beforeUpdate( self, record ):
        #access = getCurrentAccessProfile( 'user' )
        #if not access.hasFullAccess():
            # Only Administrators should have FULL-ACCESS to chnages these attributes
        #    if 'U_LAST_LOGIN' in record:
        #        del record[ 'U_LAST_LOGIN' ]

        #    if 'U_PASSWD_TRIES' in record:
        #        del record[ 'U_PASSWD_TRIES' ]

        return record
