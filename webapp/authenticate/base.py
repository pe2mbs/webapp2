
class Authenticate( object ):
    def __init__( self ):
        return

    def Authenticate( self, username, password ) -> bool:
        return True


class NotAuthenticate( Authenticate ):
    def Authenticate( self, username, password ) -> bool:
        return False
