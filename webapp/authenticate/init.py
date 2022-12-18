import webapp.api as API
from webapp.authenticate.base import Authenticate
from webapp.authenticate.db import DbAuthenticate
from webapp.authenticate.linux_pam import PamAuthenticate
from webapp.authenticate.ldap_srv import LdapAuthenticate


class UnknownAuthenticator( Exception ): pass


__custom = {}


def registerCustomAuthenticator( name: str, auth: Authenticate ):
    global __custom
    __custom[ name ] = auth
    return


def initAuthenticator():
    global __custom
    mod = API.app.config.get( 'AUTHENTICATE' )
    if mod in ( None, '', 'OFF', 'off' ):
        # Use this class as dummy authenticator
        return Authenticate()

    elif mod.upper() == 'DB':
        return DbAuthenticate()

    elif mod.upper() == 'PAM':
        return PamAuthenticate()

    elif mod.upper() == 'LDAP':
        return LdapAuthenticate()

    elif mod in __custom:
        return __custom[ mod ]()

    else:
        raise UnknownAuthenticator( mod )
