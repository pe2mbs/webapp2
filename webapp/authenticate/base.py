from typing import Union
from datetime import datetime


class AuthenticateInfo( object ):
    """ This object provides user information for all Authentication methods
    Some fields shall be set to None (null) as they are not available for an
    specific Authentication method.

    Its based on the standard LDAP attributes
    """
    def __init__( self ):
        return

    # The simplified username without any profix or suffix
    def _getUsername( self ) -> Union[str,None]:
        return None

    username                    = property( fget = _getUsername )

    # Standnrd LDAP attributes
    # DN – also distinguishedName	DN is simply the most important LDAP attribute.
    # CN=Jay Jamieson, OU= Newport, DC=cp, DC=com
    def _getDistinguishedName( self ) -> Union[str,None]:
        return None

    distinguishedName           = property( fget = _getDistinguishedName )

    # Firstname also called Christian name
    def _getGivenName( self ) -> Union[str,None]:
        return None
    givenName                   = property( fget = _getGivenName )

    # Home Folder: connect.  Tricky to configure
    def _getHomeDrive( self ) -> Union[str,None]:
        return None
    homeDrive                   = property( fget = _getHomeDrive )

    # Useful in some cultures.
    def _getInitials( self ) -> Union[str,None]:
        return None
    initials                    = property( fget = _getInitials )

    # name = Guy Thomas.  Exactly the same as CN.
    def _getName( self ) -> Union[str,None]:
        return None
    name                        = property( fget = _getName )

    # Defines the Active Directory Schema category. For example, objectCategory = Person
    def _getObjectCategory( self ) -> Union[str,None]:
        return None

    objectCategory              = property( fget = _getObjectCategory )

    # objectClass = User.  Also used for Computer, organizationalUnit, even container.  Important top-level container.
    def _getObjectClass( self ) -> Union[str,None]:
        return None

    objectClass                 = property( fget = _getObjectClass )

    # Office! on the user’s General property sheet
    def _getPhysicalDeliveryOfficeName( self ) -> Union[str,None]:
        return None

    physicalDeliveryOfficeName  = property( fget = _getPhysicalDeliveryOfficeName )

    # P.O. box.
    def _getPostOfficeBox( self ) -> Union[str,None]:
        return None

    postOfficeBox               = property( fget = _getPostOfficeBox )

    # Roaming profile path: connect.  Trick to set up
    def _getProfilePath( self ) -> Union[str,None]:
        return None

    profilePath                 = property( fget = _getProfilePath )

    # This is a mandatory property,sAMAccountName = guyt.  The old NT 4.0 logon name, must be unique in the domain.
    # If you are using an LDAP provider ‘Name’ automatically maps to sAMAcountName and CN. The default value is same as CN, but can be given a different value.
    def _getSAMAccountName( self ) -> Union[str,None]:
        return None

    sAMAccountName              = property( fget = _getSAMAccountName )

    # SN = Thomas. This would be referred to as last name or surname.
    def _getSN( self ) -> Union[str,None]:
        return None

    SN                          = property( fget = _getSN )

    # Job title.  For example Manager.
    def _getTitle( self ) -> Union[str,None]:
        return None

    title                       = property( fget = _getTitle )

    # Used to disable an account.  A value of 514 disables the account, while 512 makes the account ready for logon.
    def _getUserAccountControl( self ) -> Union[int,None]:
        return None

    userAccountControl          = property( fget = _getUserAccountControl )

    # userPrincipalName = guyt@CP.com  Often abbreviated to UPN, and looks like an email address.  Very useful for logging on especially in a large Forest.  Note UPN must be unique in the forest.
    def _getUserPrincipalName( self ) -> Union[str,None]:
        return None

    userPrincipalName           = property( fget = _getUserPrincipalName )

    # User’s home page.
    def _getWWWHomePage( self ) -> Union[str,None]:
        return None

    wWWHomePage                 = property( fget = _getWWWHomePage )

    # OTHER USEFUL LDAP ATTRIBUTES / PROPERTIES
    # Country or Region
    def _getCountry( self ) -> Union[str,None]:
        return None

    c                           = property( fget = _getCountry )
    country                     = property( fget = _getCountry )

    # Company or organization name
    def _getCompany( self ) -> Union[str,None]:
        return None

    company                     = property( fget = _getCompany )

    # Useful category to fill in and use for filtering
    def _getDepartment( self ) -> Union[str,None]:
        return None

    department                  = property( fget = _getDepartment )

    # Home Phone number, (Lots more phone LDAPs)
    def _getHomephone( self ) -> Union[str,None]:
        return None

    homephone                   = property( fget = _getHomephone )

    # (Lower case L)	L = Location.  City ( Maybe Office
    def _getLocation( self ) -> Union[str,None]:
        return None

    l                           = property( fget = _getLocation )
    # Important, particularly for printers and computers.
    location                    = property( fget = _getLocation )

    # Boss, manager
    def _getManager( self ) -> Union[str,None]:
        return None

    manager                     = property( fget = _getManager )

    # Mobile Phone number
    def _getMobile( self ) -> Union[str,None]:
        return None

    mobile                      = property( fget = _getMobile )

    # Usually, User, or Computer
    def _getObjectClass( self ) -> Union[str,None]:
        return None

    ObjectClass                 = property( fget = _getObjectClass )

    # Organizational unit.  See also DN
    def _getOU( self ) -> Union[str,None]:
        return None

    OU                          = property( fget = _getOU )

    # Force users to change their passwords at next logon
    def _getPwdLastSet( self ) -> Union[datetime,None]:
        return None

    pwdLastSet                  = property( fget = _getPwdLastSet )

    # Zip or post code
    def _getPostalCode( self ) -> Union[str,None]:
        return None

    postalCode                  = property( fget = _getPostalCode )

    # State, Province or County
    def _getSt( self ) -> Union[str,None]:
        return None

    st                          = property( fget = _getSt )
    state                       = property( fget = _getSt )

    # First line of address
    def _getStreetAddress( self ) -> Union[str,None]:
        return None

    streetAddress               = property( fget = _getStreetAddress )

    # Office Phone
    def _getTelephoneNumber( self ) -> Union[str,None]:
        return None

    telephoneNumber             = property( fget = _getTelephoneNumber )

    # Enable (512) / disable account (514)
    def _getUserAccountControl( self ) -> Union[int,None]:
        return None

    userAccountControl          = property( fget = _getUserAccountControl )

    # EXAMPLES OF EXCHANGE SPECIFIC LDAP ATTRIBUTES
    # Here is where you set the MailStore
    def _getHomeMDB( self ) -> Union[str,None]:
        return None

    homeMDB                     = property( fget = _getHomeMDB )

    # Legacy distinguished name for creating Contacts. In the following example,
    # Guy Thomas is a Contact in the first administrative group of GUYDOMAIN: /o=GUYDOMAIN/ou=first administrative group/cn=Recipients/cn=Guy Thomas
    def _getLegacyExchangeDN( self ) -> Union[str,None]:
        return None

    legacyExchangeDN            = property( fget = _getLegacyExchangeDN )

    # An easy, but important attribute.  A simple SMTP address is all that is required billyn@ourdom.com
    def _getMail( self ) -> Union[str,None]:
        return None

    mail                        = property( fget = _getMail )

    # FALSE	Indicates that a contact is not a domain user.
    def _getMAPIRecipient( self ) -> Union[str,None]:
        return None

    mAPIRecipient               = property( fget = _getMAPIRecipient )

    # Normally this is the same value as the sAMAccountName, but could be different if you wished.  Needed for mail enabled contacts.
    def _getMailNickname( self ) -> Union[str,None]:
        return self._getSAMAccountName()

    mailNickname                = property( fget = _getMailNickname )

    # Another straightforward field, just the value to: True
    def _getMDBUseDefaults( self ) -> bool:
        return False

    mDBUseDefaults              = property( fget = _getMDBUseDefaults )

    # Exchange needs to know which server to deliver the mail.  Example:
    #     /o=YourOrg/ou=First Administrative Group/cn=Configuration/cn=Servers/cn=MailSrv
    def _getMsExchHomeServerName( self ) -> Union[str,None]:
        return None

    msExchHomeServerName        = property( fget = _getMsExchHomeServerName )

    # As the name ‘proxy’ suggests, it is possible for one recipient to have more than one email address.  Note the plural spelling of proxyAddresses.
    def _getProxyAddresses( self ) -> Union[str,None]:
        return None

    proxyAddresses              = property( fget = _getProxyAddresses )

    # SMTP:@ e-mail address.  Note that SMTP is case sensitive.  All capitals means the default address.
    def _getTargetAddress( self ) -> Union[str,None]:
        return None

    targetAddress               = property( fget = _getTargetAddress )

    # Displays the contact in the Global Address List.
    def _getShowInAddressBook( self ) -> Union[str,None]:
        return None

    showInAddressBook           = property( fget = _getShowInAddressBook )



class Authenticate( object ):
    def __init__( self, method = 'NONE' ):
        self.__method = method
        return

    @property
    def Method( self ):
        return self.__method

    def Authenticate( self, username, password ) -> bool:
        return True

    def _getUserInfo( self ) -> Union[AuthenticateInfo,None]:
        return None

    UserInfo: AuthenticateInfo = property( fget=_getUserInfo, fset=None, fdel=None, doc=None)


class NotAuthenticate( Authenticate ):
    def Authenticate( self, username, password ) -> bool:
        return False
