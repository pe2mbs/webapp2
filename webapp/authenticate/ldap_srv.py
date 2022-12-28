from webapp.authenticate.base import Authenticate, NotAuthenticate
import webapp.api as API
try:
    import ldap


    class InvalidConfiguration( Exception ): pass


    class LdapAuthenticate( object ):
        def __init__(self):
            super( LdapAuthenticate, self ).__init__()
            self.__config = API.app.config( 'LDAP_AUTHENTICATOR', { } )
            self.__userdata = None
            return

        def Authenticate( self, username, password ) -> bool:
            connect = ldap.initialize( self.__config.get( 'hostname', 'ldaps://localhost' ) )
            self.__userdata = None
            try:
                # if authentication successful, get the full user data
                base_dn = self.__config.get( 'BASE-DN', self.__config.get( 'BASE_DN', None ) )
                if base_dn is None:
                    raise InvalidConfiguration( 'BASE-DN is not present in configuration (LDAP_AUTHENTICATOR)')

                f_user_dn = self.__config.get( 'USER-DN', self.__config.get( 'USER_DN', None ) )
                if f_user_dn is None:
                    raise InvalidConfiguration( 'USER-DN is not present in configuration (LDAP_AUTHENTICATOR)')

                if not f_user_dn.startswith( 'uid={},' ):
                    raise InvalidConfiguration( 'USER-DN invalid must start with "uid={}," in configuration (LDAP_AUTHENTICATOR)')

                connect.bind_s( f_user_dn.format( username ), password )
                self.__userdata = connect.search_s( base_dn, ldap.SCOPE_SUBTREE, f"uid={username}" )
                # return all user data results
                connect.unbind_s()
                return True

            except ldap.LDAPError as exc:
                connect.unbind_s()
                API.app.logger.error( f"User '{username}' LDAP-error: {exc}" )

            except InvalidConfiguration:
                raise SystemExit

            return False

        @property
        def UserDetails( self ):
            return self.__userdata


except ModuleNotFoundError:
    LdapAuthenticate = NotAuthenticate