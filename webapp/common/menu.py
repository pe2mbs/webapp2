import hashlib
from threading import Lock
import webapp.api as API
from typing import Union
import copy
import json


__docformat__ = 'epytext'


class InvalidMenuObject( Exception ):
    """This Exception class reports when a menu dictionary is invalid.

    @type message:      string
    @param message:     a text string with usefull infomration about the problem.
    """


class CannotAddMenuObject( Exception ):
    """This Exception class reports when a menu item cannot be added to the menu structure.

    @type message:      string
    @param message:     a text string with usefull infomration about why it cannot be added.
    """


class InvalidAccessValue( Exception ):
    """This Exception class reports an invalid parameter as access parameter to the menu.

    @type message:      string
    @param message:     a text string with usefull infomration.
    """


def createMenuHash( data: str ):
    """createMenuHash() creates a hash code based on the string provided.
    This is useful to generate unique ids for the menu item for testing purposes.

    @type data:         string.
    @param data:        A unique menu item string.

    @rtype              string hexadecimal encoded.
    @return:            hash string.
    """
    sha = hashlib.sha1()
    sha.update( data.encode('utf-8') )
    return sha.hexdigest()


class WebappMenu( object ):
    """This is the root menu for the web application, this object registers menu's and obtains the menu for an access level.

    @raise InvalidMenuObject:   When a menu dictionary is invalid.
    @raise InvalidAccessValue:  When an invalid role parameter is given.
    """
    def __init__( self, debug = False ):
        """This initializes the menu object.

        @type debug:            booloan.
        @param debug:           When set to True, the 'access' parameter of the menu and 'roles' parameter are also passed to frontend.
        """
        self.__debug        = debug
        # Contains the menu structure
        self.__root         = []
        # Indocates if the menu is correctly sorted.
        self.__sorted       = True
        # Lock for sorting at run time when the application is fully started
        self.__sortingLock  = Lock()
        return

    def _find( self, caption: str, children: Union[list,None] = None ) -> Union[ int, None ]:
        """Internal member function to find a specific menu item in the current level of the menu by the caption.

        @type caption:      string.
        @param caption:     The menu caption to find.
        @type children:     list or None.
        @param children:    When a list is passed this is used to search the menu item, When None is passed the class its root level is used the search.

        @rtype:             integer or None.
        @return:            positive integer as index of the found menu item, None when no item was found.
        """
        if children is None:
            children = self.__root

        for idx, menuitem in enumerate( children ):
            if menuitem.get( 'caption' ) == caption:
                return idx

        return None

    def _lookup( self, children: list, args: list ) -> dict:
        """Internal member function to lookup a speific menu item in the menu tree.

        if an item is not present at a menu level the level is automaticly added.

        @type children:     list of dictionries with menu items.
        @param children:    menu dictionary items.
        @type args:         list of strings.
        @param args:        list of menu captions to be looked up.

        @rtype:             dictionary or None.
        @return:            The final found menu dictionary item.
        """
        if len( args ) == 0:
            raise InvalidMenuObject( "Some internal error as 'args' is empty" )

        caption = args[ 0 ]
        del args[ 0 ]

        for child in children:
            if child[ 'caption' ] == caption:
                # found
                if len( args ) > 0:
                    if 'menu' not in child:
                        # Need to add
                        children.append( { 'caption': caption, 'menu': [] } )

                    return self._lookup( child[ 'menu' ], args )

                else:
                    return child

        child = { 'caption': caption, 'menu': [] }
        children.append( child )
        if len( args ) > 0:
            return self._lookup( child[ 'menu' ], args )

        return child

    def _validateMenuItem( self, menu, exception = False ) -> bool:
        """Internal member function to validate a menu dictionary item

        @type menu          dictionary
        @param menu:        menu menu item to be validated
        @type exception:    boolean
        @param exception:   When set to True an exception is raised when the item is invalid, otherwise the function shall return False on a invalid item.

        @rtype:             boolean
        @return:            False on a invalid item, True on a valid item
        """
        if not menu.get( 'caption' ):
            # This is a mandatory item
            if exception:
                raise InvalidMenuObject( f"Missing 'caption' in menu {menu}" )

            return False

        if not menu.get( 'id' ):
            # This is a mandatory item
            if exception:
                raise InvalidMenuObject( f"Missing 'id' in menu {menu}" )

            return False

        if not menu.get( 'access' ):
            # This is a mandatory item
            if exception:
                raise InvalidMenuObject( f"Missing 'access' in menu {menu}" )

            return False

        # TODO Marc: uncomment and check whether it works
        #if not menu.get( 'menu' ) and not menu.get( 'route' ):
        #    # One of these is a mandatory item
        #    if exception:
        #        raise InvalidMenuObject( "Missing 'route' or 'menu'" )
        #    return False

        elif menu.get( 'menu' ) and menu.get( 'route' ):
            # 'menu' and 'route' cannot be both precent
            if exception:
                raise InvalidMenuObject( "Missing 'route' or 'menu'" )

            return False

        if not menu.get( 'before' ) and not menu.get( 'after' ):
            # One of these is a mandatory item, bit both may be present
            if exception:
                raise InvalidMenuObject( "Missing 'before' and/or 'after'" )

            return False

        return True

    def _register( self, target: list, menu: Union[dict,list,tuple] ) -> None:
        """Internal member function to register a menu item to the menu structure.

        @type target:       list
        @param target:      the list where the new menu item shall be placed in.
        @type menu          dictionary
        @param menu:        The menu item to be placed in the menu list

        @return:            None
        """
        if not isinstance( target, list ):
            raise InvalidMenuObject( "target not a 'list'" )

        if isinstance( menu, ( list, tuple ) ):
            for item in menu:
                self._register( target, item )

        elif isinstance( menu, dict ):
            self._validateMenuItem( menu, True )
            # Check if the menu exists
            submenu = menu.get( 'menu', None )
            if submenu:
                submenu = copy.deepcopy( submenu )
                del menu[ 'menu' ]

            idx     = self._find( menu.get( 'caption', '' ), target )
            if idx is None:
                # New menu item
                before  = menu.get( 'before', None )
                after   = menu.get( 'after', None )
                if before is None and ( after is None or after == '*' ):
                    idx = len( target )
                    target.append( menu )

                elif before == '*' and ( after is None or after == '*' ):
                    idx = 0
                    target.insert( idx, menu )

                else:
                    after_idx   = self._find( menu.get( 'after', None ), target )
                    if after_idx is None:
                        before_idx  = self._find( menu.get( 'before', None ), target )
                        if before_idx is None:
                            # Just stick it at the back, menu doesn't seem to be complete yet
                            self.__sorted   = False
                            idx = len( target )
                            target.append( menu )

                        else:
                            idx = before_idx
                            target.insert( idx, menu )

                    else:
                        idx = after_idx + 1
                        target.insert( idx, menu )

            else:
                target[ idx ].update( menu )

            if submenu:
                sub = target[ idx ].get( 'menu', [] )
                self._register( sub, submenu )
                target[ idx ][ 'menu' ] = sub

        else:
            raise InvalidMenuObject( "Menu item is neither 'dict', 'list' or 'tuple'" )

        return

    def register( self, menu: Union[dict,list,tuple], *args ) -> None:
        """public member function to register a menu.

        The menu parameter may be a single menu item or a menu structure with sub menu's.

        @type menu:     dictionary
        @param menu:    the menu item to register
        @type args:     list
        @param args:    Optional arguments with menu captions where the menu must be placed.

        @return:        None
        """
        if len( args ):
            item = self._lookup( self.__root, list( args ) )
            item.setdefault( 'menu', [] )
            self._register( item[ 'menu' ], menu )

        else:
            self._register( self.__root, menu )

        return

    def sortMenu( self ):
        """public member function to sort the menu structure based on the 'after' and 'before' attributes in the menu items

        @return:        None
        """
        if self.__sortingLock.acquire( timeout = 5 ):
            self._sortMenu( self.__root )
            self.__sortingLock.release()

        return

    def _sortMenu( self, items: list ):
        """Internal member function to sort menu items.

        @type items:    list
        @param items    the menu items that need to be sorted.
        @return:        None
        """
        result = []
        for child in items:
            self._register( result, child )

        self.__sorted = True
        self.__root = result
        return

    def _getMenu( self, items: list, roles: Union[str,list,tuple] ) -> list:
        """Internal member function to retrieve the menu for specific role(s)

        When roles is a string it is used to verify against the menu access attribute.
        When roles is a list or tuple these items are used to verify against the menu access attribute.

        @type items:        list
        @param items:       the menu items which are considered to be obtained.
        @type roles:        list, tuple or string
        @param roles:       which menu items to be selected

        @rtype:             list
        @return:            the selected menu items
        """
        result = []
        def copyItem( item ):
            result = { 'caption': item[ 'caption' ], 'id': item[ 'id' ] }
            if self.__debug:
                result[ 'access' ] = item[ 'access' ]

            if 'route' in item:
                result[ 'route' ] = item[ 'route' ]

            return result

        for child in items:
            item = None
            access = child.get( 'access', '*' )
            if access == '*' or roles == '*' or access in roles:
                item = copyItem( child )
                if self.__debug:
                    item[ 'roles' ] = roles

                if 'menu' in child:
                    item[ 'menu' ] = self._getMenu( child[ 'menu' ], roles )

            if item is not None:
                result.append( item )

        return result

    def getMenu( self, roles: Union[str,list,tuple] ):
        """public member function to retrieve the menu for specific role(s)

        if the menu needs sorting this shall be done first.

        For more information see _getMenu() above

        @type roles:        list, tuple or string
        @param roles:       which menu items to be selected

        @raise InvalidAccessValue:  When the roles parameter if on incorrect type

        @rtype:             list
        @return:            the selected menu items
        """
        if not self.__sorted:
            if self.__sortingLock.acquire( timeout = 5 ):
                self._sortMenu( self.__root )
                self.__sortingLock.release()

        if isinstance( roles, ( str,list,tuple ) ):
            return self._getMenu( self.__root, roles )

        raise InvalidAccessValue( roles )

    def dump( self, roles: Union[str,tuple,list] = '*' ):
        """public member function to dump the menu structure for debug purposes.

        @type roles:        list, tuple or string
        @param roles:       which menu items to be selected for the dump

        @return:            None
        """
        if API.logger:
            API.logger.debug( json.dumps( self.getMenu( roles ), indent = 4 ) )

        else:
            print( json.dumps( self.getMenu( roles ), indent = 4 ) )

        return
