from webapp.authenticate.base import NotAuthenticate

try:
    from typing import Union
    import pam
    import socket
    import subprocess
    from webapp.authenticate.base import Authenticate, AuthenticateInfo


    class FingerException( Exception ): pass


    class LinuxFinger( object ):
        __attributes = [
            ('Login: ', 'username'),
            ('Name: ', 'fullname'),
            ('Directory: ', 'home-folder'),
            ('Shell: ', 'shell'),
            ('Office: ', 'office-phone'),
            ('Home Phone: ', 'home-phone')
        ]
        def __init__( self, username = "" ):
            self.__values = {}
            self.__process = subprocess.run( f'finger -l {username}', shell=True, check=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
            self.__stdout = self.__process.stdout.decode('utf-8')
            self.__stderr = self.__process.stderr.decode('utf-8')
            if self.__stderr != '':
                raise FingerException( self.__stderr )

            for ( label, attr ) in self.__attributes:
                self.__values[ attr ] = self._getAttrbute( self.__stdout, label )

            return

        @property
        def ResultCode( self ):
            return self.__process.returncode

        @property
        def StdOut( self ) -> str:
            return self.__stdout

        @property
        def StdErr( self ) -> str:
            return self.__stderr

        @property
        def SystemName( self ):
            return socket.getfqdn()

        @property
        def Username( self ):
            return self.__values.get('username')

        @property
        def Fullname( self ):
            return self.__values.get('fullname')

        @property
        def HomeDirectory( self ):
            return self.__values.get('home-folder')

        @property
        def Shell( self ):
            return self.__values.get('shell')

        @property
        def OfficePhone( self ):
            return self.__values.get('office-phone')

        @property
        def HomePhone( self ):
            return self.__values.get('home-phone')

        def json( self ):
            result = {
                'system': socket.getfqdn()
            }
            result.update( self.__values )
            return result

        def _getAttrbute( self, buffer, attribute ):
            position = buffer.find( attribute )
            if position < 0:
                return ''
            position += len( attribute )
            value = ''
            lastCh = ''
            while position < len( buffer ) and buffer[ position ] >= ' ' and not ( buffer[ position ] == ' ' and lastCh == ' ' ):
                lastCh = buffer[ position ]
                position += 1
                value += lastCh

            return value.strip()


    class PamAuthenticateInfo( AuthenticateInfo ):
        def __init__( self, username ):
            self.__finger = LinuxFinger( username )

        def _getUsername( self ) -> Union[str,None]:
            return self.__finger.Username

        def _getSAMAccountName( self ) -> Union[str,None]:
            return self.__finger.Username

        def _getName( self ) -> Union[str,None]:
            return self.__finger.Fullname

        def _getProfilePath( self ) -> Union[str,None]:
            return self.__finger.HomeDirectory

        def _getSN( self ) -> Union[str,None]:
            if ',' in self.__finger.Fullname:
                return self.__finger.Fullname.split( ',' )[ 0 ]

            return self.__finger.Fullname.split( ' ' )[ -1 ]

        def _getInitials( self ) -> Union[str,None]:
            names = self.__finger.Fullname.replace( self._getSN(), '' ).strip()
            return ".".join( [ ch[0].upper() for ch in names ] )

        def _getUserPrincipalName( self ) -> Union[str,None]:
            return "@".join( [ self.__finger.Username,
                               ".".join( self.__finger.SystemName.split('.')[1:] ) ] )

        def _getMail( self ) -> Union[str,None]:
            return self._getUserPrincipalName()

        def _getHomephone( self ) -> Union[str,None]:
            return self.__finger.HomePhone

        def _getTelephoneNumber( self ) -> Union[str,None]:
            return self.__finger.OfficePhone


    class PamAuthenticate( Authenticate ):
        def __init__( self, method = 'PAM' ):
            super( PamAuthenticate, self ).__init__( method )
            self.__userDetails: Union[PamAuthenticateInfo,None] = None
            return

        def Authenticate( self, username, password ) -> bool:
            result = pam.authenticate( username, password )
            if result:
                self.__userDetails = PamAuthenticateInfo( username )

            else:
                self.__userDetails = None

            return result

        def _getUserInfo( self ) -> Union[AuthenticateInfo,None]:
            return self.__userDetails


except ModuleNotFoundError:
    PamAuthenticate = NotAuthenticate
