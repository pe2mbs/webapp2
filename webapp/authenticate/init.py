import webapp.api as API
from webapp.authenticate.base import Authenticate
from webapp.authenticate.db import DbAuthenticate
from webapp.authenticate.linux_pam import PamAuthenticate
from webapp.authenticate.db_pam import DbPamAuthenticate
from webapp.authenticate.ldap_srv import LdapAuthenticate
from webapp.authenticate.db_ldap import DbLdapAuthenticate


class UnknownAuthenticator( Exception ): pass


__custom = {
    'DB':       DbAuthenticate,
    'PAM':      PamAuthenticate,
    'DB-PAM':   DbPamAuthenticate,
    'LDAP':     LdapAuthenticate,
    'DB-LDAP':  DbLdapAuthenticate,
}


def registerCustomAuthenticator( name: str, auth: Authenticate ):
    global __custom
    __custom[ name ] = auth
    return


def initAuthenticator() -> Authenticate:
    global __custom
    mod = API.app.config.get( 'AUTHENTICATE' )
    if mod in ( None, '', 'OFF', 'off' ):
        # Use this class as dummy authenticator
        return Authenticate()

    elif mod in __custom:
        return __custom[ mod ]()

    else:
        raise UnknownAuthenticator( mod )
