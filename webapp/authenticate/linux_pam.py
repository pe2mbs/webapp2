from webapp.authenticate.base import Authenticate, NotAuthenticate

try:
    import pam

    class PamAuthenticate( Authenticate ):
        def __init__(self):
            super( PamAuthenticate, self ).__init__()
            return

        def Authenticate( self, username, password ) -> bool:
            return pam.authenticate( username, password )





except ModuleNotFoundError:
    PamAuthenticate = NotAuthenticate
