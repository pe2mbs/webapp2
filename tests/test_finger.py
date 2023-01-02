import sys
import subprocess


class FingerException( Exception ): pass


class LinuxFinger( object ):
    __attributes = [
        ('Login: ', 'login'),
        ('Name: ', 'name'),
        ('Directory: ', 'home'),
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
    def Username( self ):
        return self.__values.get('login')

    @property
    def Fullname( self ):
        return self.__values.get('name')

    @property
    def HomeDirectory( self ):
        return self.__values.get('home')

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
        return self.__values

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


if __name__ == '__main__':
    # For testing, retrieving the current user
    finger = LinuxFinger()
    print( f"Username    : {finger.Username}" )
    print( f"Fullname    : {finger.Fullname}" )
    print( f"Home folder : {finger.HomeDirectory}" )
    print( f"Shell       : {finger.Shell}" )
    print( f"Home phone  : {finger.HomePhone}" )
    print( f"Office phone: {finger.OfficePhone}" )
    try:
        finger = LinuxFinger( 'root' )
        print( f"Username    : {finger.Username}" )
        print( f"Fullname    : {finger.Fullname}" )
        print( f"Home folder : {finger.HomeDirectory}" )
        print( f"Shell       : {finger.Shell}" )
        print( f"Home phone  : {finger.HomePhone}" )
        print( f"Office phone: {finger.OfficePhone}" )

    except FingerException as exc:
        print( f"ERROR: {exc}", file = sys.stderr )

