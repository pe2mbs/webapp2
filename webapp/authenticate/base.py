#
# base authentication webapp application package
# Copyright (C) 2018-2023 Marc Bertens-Nguyen <m.bertens@pe2mbs.nl>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License GPL-2.0-only
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from typing import Union
from datetime import datetime


class AuthenticateInfo( object ):
    """This object provides user information for all Authentication methods
    Some fields shall be set to None (null) as they are not available for an
    specific Authentication method.

    Its based on the standard LDAP attributes
    """

    def __init__( self ):
        """Constructor
        """
        return

    def _getUsername( self ) -> Union[str,None]:
        """Internal member function to get the username from the object, this needs to be over ridden
        by the actual implementation for the authentication method.

        The simplified username without any prefix or suffix

        :rtype:         string or None
        :return:        When the user information is correcly set the username must be returned as a string.
                        When no user information is present this returns None.
        """
        return None

    username                    = property( fget = _getUsername )
    """username property, the simplified username without any prefix or suffix
    """

    def _getDistinguishedName( self ) -> Union[str,None]:
        """Internal member function to get the distinguishedName/DN from the object, this needs to be over ridden
        by the actual implementation for the authentication method.

        Standnrd LDAP attributes
        DN – also distinguishedName	DN is simply the most important LDAP attribute.
        "CN=John Doe,OU= Users,DC=example,DC=com"

        :rtype:         string or None
        :return:        When the user information is correcly set the username must be returned as a string.
                        When no user information is present this returns None.
        """
        return None

    distinguishedName           = property( fget = _getDistinguishedName )
    """distinguishedName propery, Standnrd LDAP attribute
    DN – also distinguishedName	DN is simply the most important LDAP attribute.
    "CN=John Doe,OU= Users,DC=example,DC=com"
    """

    def _getGivenName( self ) -> Union[str,None]:
        return None

    givenName                   = property( fget = _getGivenName )
    """givenName property, Firstname also called Christian name
    """

    def _getHomeDrive( self ) -> Union[str,None]:
        return None

    homeDrive                   = property( fget = _getHomeDrive )
    """homeDrive property, Home Folder: connect.
    """

    def _getInitials( self ) -> Union[str,None]:
        return None

    initials                    = property( fget = _getInitials )
    """initials property, Initials of the names of the user.
    """

    def _getName( self ) -> Union[str,None]:
        return None
    name                        = property( fget = _getName )
    """ame property, the full name Christian name and Surname, Exactly the same as CN.
    This can be in two formats:
    1.  Surname, Christian name:    "Doe, John"
    2.  Christian name Surname:     "John Doe"
    """

    def _getObjectCategory( self ) -> Union[str,None]:
        return None

    objectCategory              = property( fget = _getObjectCategory )
    """objectCategory property, Defines the Active Directory Schema category. For example, objectCategory = Person
    """

    def _getObjectClass( self ) -> Union[str,None]:
        return None

    objectClass                 = property( fget = _getObjectClass )
    """objectClass property, objectClass = User. Also used for Computer, organizationalUnit, even container. Important top-level container.
    """

    def _getPhysicalDeliveryOfficeName( self ) -> Union[str,None]:
        return None

    physicalDeliveryOfficeName  = property( fget = _getPhysicalDeliveryOfficeName )
    """physicalDeliveryOfficeName property, Office! on the user’s General property sheet.
    """

    def _getPostOfficeBox( self ) -> Union[str,None]:
        return None

    postOfficeBox               = property( fget = _getPostOfficeBox )
    """property postOfficeBox, P.O. box for the user.
    """

    def _getProfilePath( self ) -> Union[str,None]:
        return None

    profilePath                 = property( fget = _getProfilePath )
    """profilePath property, Roaming profile path: connect.
    """

    def _getSAMAccountName( self ) -> Union[str,None]:
        return None

    sAMAccountName              = property( fget = _getSAMAccountName )
    """sAMAccountName property, This is a mandatory property,sAMAccountName = doej.  The old NT 4.0 logon name, must be unique in the domain.
    If you are using an LDAP provider ‘Name’ automatically maps to sAMAcountName and CN. The default value is same as CN, but can be given a different value.
    """

    def _getSN( self ) -> Union[str,None]:
        return None

    SN                          = property( fget = _getSN )
    """SN property, This would be referred to as last name or surname.
    SN = Doe
    """

    def _getTitle( self ) -> Union[str,None]:
        return None

    title                       = property( fget = _getTitle )
    """title property, Job title.  For example Manager.
    """

    def _getUserAccountControl( self ) -> Union[int,None]:
        return None

    userAccountControl          = property( fget = _getUserAccountControl )
    """userAccountControl property, Used to disable an account.  A value of 514 disables the account, while 512 makes the account ready for logon.
    """

    def _getUserPrincipalName( self ) -> Union[str,None]:
        return None

    userPrincipalName           = property( fget = _getUserPrincipalName )
    """userPrincipalName property, userPrincipalName = doej@example.com  Often abbreviated to UPN, and looks like an email address.  Very useful for logging on especially in a large Forest.  Note UPN must be unique in the forest.
    """

    def _getWWWHomePage( self ) -> Union[str,None]:
        return None

    wWWHomePage                 = property( fget = _getWWWHomePage )
    """wWWHomePage property, User’s home page.
    """

    # OTHER USEFUL LDAP ATTRIBUTES / PROPERTIES
    #
    def _getCountry( self ) -> Union[str,None]:
        return None

    c                           = property( fget = _getCountry )
    """c property (same as country), Country or Region
    """

    country                     = property( fget = _getCountry )
    """country property (same as c), Country or Region
    """

    def _getCompany( self ) -> Union[str,None]:
        return None

    company                     = property( fget = _getCompany )
    """company property, Company or organization name
    """

    def _getDepartment( self ) -> Union[str,None]:
        return None

    department                  = property( fget = _getDepartment )
    """department property, organization department useful category to fill in and use for filtering
    """

    def _getHomephone( self ) -> Union[str,None]:
        return None

    homephone                   = property( fget = _getHomephone )
    """homephone property, Home Phone number.
    """

    def _getLocation( self ) -> Union[str,None]:
        return None

    l                           = property( fget = _getLocation )
    """l property (same as location), Location / City (Maybe Office)
    """

    location                    = property( fget = _getLocation )
    """location property (same as l), Location / City (Maybe Office)
    """

    def _getManager( self ) -> Union[str,None]:
        return None

    manager                     = property( fget = _getManager )
    """manager property, Boss, manager name
    """

    def _getMobile( self ) -> Union[str,None]:
        return None

    mobile                      = property( fget = _getMobile )
    """mobile property, Mobile Phone number
    """

    def _getObjectClass( self ) -> Union[str,None]:
        return None

    ObjectClass                 = property( fget = _getObjectClass )
    """ObjectClass property, Usually, User, or Computer
    """

    def _getOU( self ) -> Union[str,None]:
        return None

    OU                          = property( fget = _getOU )
    """OU property, Organizational unit.  See also DN
    """

    def _getPwdLastSet( self ) -> Union[datetime,None]:
        return None

    pwdLastSet                  = property( fget = _getPwdLastSet )
    """pwdLastSet property, Force users to change their passwords at next logon
    """

    def _getPostalCode( self ) -> Union[str,None]:
        return None

    postalCode                  = property( fget = _getPostalCode )
    """postalCode property, Zip or post code
    """

    def _getSt( self ) -> Union[str,None]:
        return None

    st                          = property( fget = _getSt )
    """st property (same as state), State, Province or County
    """

    state                       = property( fget = _getSt )
    """state property (same as st), State, Province or County
    """

    def _getStreetAddress( self ) -> Union[str,None]:
        return None

    streetAddress               = property( fget = _getStreetAddress )
    """streetAddress property, First line of address
    """

    def _getTelephoneNumber( self ) -> Union[str,None]:
        return None

    telephoneNumber             = property( fget = _getTelephoneNumber )
    """telephoneNumber property, Office Phone
    """

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
