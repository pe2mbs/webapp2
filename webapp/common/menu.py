import hashlib
import webapp.api as API
from typing import Union
import copy
import json

class InvalidMenuObject( Exception ): pass
class CannotAddMenuObject( Exception ): pass
class InvalidAccessValue( Exception ): pass


def createMenuHash( data: str ):
    sha = hashlib.sha1()
    sha.update( data.encode('utf-8') )
    return sha.hexdigest()


class WebappMenu( object ):
    def __init__( self, debug = False ):
        self.__root = []
        self.__debug    = debug
        self.__sorted   = True
        return

    def _find( self, caption: str, children: Union[list,None] = None ) -> Union[ int, None ]:
        if children is None:
            children = self.__root

        for idx, menuitem in enumerate( children ):
            if menuitem.get( 'caption' ) == caption:
                return idx

        return None

    def _lookup( self, children: list, args: list ) -> dict:
        if len( args ) == 0:
            raise InvalidMenuObject()

        caption = args[ 0 ]
        del args[ 0 ]

        for child in children:
            if child[ 'caption' ] == caption:
                # found
                if len( args ) > 0:
                    if 'children' not in child:
                        # Need to add
                        children.append( { 'caption': caption, 'children': [] } )

                    return self._lookup( child[ 'children' ], args )

                else:
                    return child

        child = { 'caption': caption, 'children': [] }
        children.append( child )
        if len( args ) > 0:
            return self._lookup( child[ 'children' ], args )

        return child

    def _register( self, children: list, menu: Union[dict,list,tuple] ) -> None:
        if isinstance( menu, ( list, tuple ) ):
            for item in menu:
                self._register( children, item )

        elif isinstance( menu, dict ):
            # Check if the menu exists
            submenu = menu.get( 'children', None )
            if submenu:
                submenu = copy.deepcopy( submenu )
                del menu[ 'children' ]

            idx     = self._find( menu.get( 'caption', '' ), children )
            if idx is None:
                # New menu item
                before  = menu.get( 'before', None )
                after   = menu.get( 'after', None )
                if before is None and ( after is None or after == '*' ):
                    idx = len( children )
                    children.append( menu )

                elif before == '*' and ( after is None or after == '*' ):
                    idx = 0
                    children.insert( idx, menu )

                else:
                    after_idx   = self._find( menu.get( 'after', None ), children )
                    if after_idx is None:
                        before_idx  = self._find( menu.get( 'before', None ), children )
                        if before_idx is None:
                            # Just stick it at the back, menu doesn't seem to be complete yet
                            self.__sorted   = False
                            idx = len( children )
                            children.append( menu )

                        else:
                            idx = before_idx
                            children.insert( idx, menu )

                    else:
                        idx = after_idx + 1
                        children.insert( idx, menu )

            else:
                children[ idx ].update( menu )

            if submenu:
                sub = children[ idx ].get( 'children', [] )
                self._register( sub, submenu )
                children[ idx ][ 'children' ] = sub

        else:
            raise InvalidMenuObject()

        return

    def register( self, menu: Union[dict,list,tuple], *args ) -> None:
        if len( args ):
            item = self._lookup( self.__root, list( args ) )
            item.setdefault( 'children', [] )
            self._register( item[ 'children' ], menu )

        else:
            self._register( self.__root, menu )

        return

    def sortMenu( self ):
        self._sortMenu( self.__root )

    def _sortMenu( self, items: list ):
        result = []
        for child in items:
            self._register( result, child )

        self.__sorted = True
        self.__root = result
        return

    def _getMenu( self, children: list, roles: Union[str,list,tuple] ) -> list:
        result = []
        def copyItem( item ):
            result = { 'caption': item[ 'caption' ], 'id': item[ 'id' ] }
            if self.__debug:
                result[ 'access' ] = item[ 'access' ]

            if 'route' in item:
                result[ 'route' ] = item[ 'route' ]

            return result

        for child in children:
            item = None
            access = child.get( 'access', '*' )
            if access == '*' or roles == '*' or access in roles:
                item = copyItem( child )
                if self.__debug:
                    item[ 'roles' ] = roles

                if 'children' in child:
                    item[ 'children' ] = self._getMenu( child[ 'children' ], roles )

            if item is not None:
                result.append( item )

        return result

    def getMenu( self, roles: Union[str,list,tuple] ):
        if not self.__sorted:
            self._sortMenu( self.__root )

        if isinstance( roles, ( str,list,tuple ) ):
            return self._getMenu( self.__root, roles )

        raise InvalidAccessValue( roles )

    def dump( self, roles: Union[str,tuple,list] = '*' ):
        print( json.dumps( self.getMenu( roles ), indent = 4 ) )
        return

#
# def verifyMenuStruct( menu ):
#     """Internal function to verify the menu structure, special for the function addMenu()
#
#     :param menu:    menu struct
#     :return:        None
#     """
#     if 'caption' not in menu:
#         raise Exception( "Menu has no caption!: {} ".format( json.dumps( menu ) ) )
#
#     if 'route' not in menu and 'children' not in menu and 'child' not in menu:
#         raise Exception( "Menu has no route, children or child!: {} ".format( json.dumps( menu ) ) )
#
#     if 'child' in menu:
#         verifyMenuStruct( menu.get( 'child', [] ) )
#
#     elif 'children' in menu:
#         for child in menu.get( 'children', [] ):
#             verifyMenuStruct( child )
#
#     elif 'menu' in menu:
#         for child in menu.get( 'menu', [] ):
#             verifyMenuStruct( child )
#
#     return
#
#
# def _registerMenu( root_menu, menu, before = None, after = None ):
#     if before is None:
#         before = menu.get( 'before', None )
#
#     if after is None:
#         after = menu.get( 'after', None )
#
#     if isinstance( root_menu, dict ):
#         root_menu = root_menu[ 'children' ]
#
#     if before is None and after is None:
#         # Just add it at the back
#         root_menu.append( menu )
#         return
#
#     for idx, item in enumerate( root_menu ):
#         if before is not None and item[ 'caption' ] == before:
#             # Found it
#             root_menu.insert( idx, menu )
#             return
#
#         elif after is not None and item[ 'caption' ] == after:
#             # Found it
#             root_menu.insert( idx + 1, menu )
#             return
#
#     if before is not None:
#         raise Exception( "Menu item '{}' not found".format( before ) )
#
#     raise Exception( "Menu item '{}' not found".format( after ) )
#
#
# def registerMenu( menu, before = None, after = None ):
#     verifyMenuStruct( menu )
#     _registerMenu( API.menuItems, menu, before, after )
#     return
#
#
# def registerSubMenu( menu, *args, before = None, after = None ):
#     verifyMenuStruct( menu )
#     subMenu = API.menuItems
#     found = False
#     for arg in args:
#         found = False
#         for idx, item in enumerate( API.menuItems ):
#             if item[ 'caption' ] == arg:
#                 subMenu = item
#                 found = True
#                 break
#
#     if not found:
#         if before is not None:
#             raise Exception( "Menu item '{}' not found".format( args ) )
#
#         raise Exception( "Menu item '{}' not found".format( args ) )
#
#     _registerMenu( subMenu, menu, before, after )
#     return
#
# def getMenu( role: int ):
#     def processMenu( source_menu ):
#         menu = []
#         for item in source_menu:
#             route = item.get( 'route', None )
#             API.logger.info( "Menu Item: {} => {}".format( item.get( 'caption' ), route ) )
#             if route is None:   # Sub menu
#                 result = processMenu( item.get( 'children', [] ) )
#                 if len( result ) > 0:
#                     tmp = copy.copy( item )
#                     tmp[ 'children' ] = copy.copy( result )
#                     menu.append( tmp )
#
#             else:               # Menu item
#                 menu.append( item )
#
#         return menu
#
#     if len( API.menuItems ) == 1 and 'children' in API.menuItems:
#         return processMenu( API.menuItems.get( 'children', [] ) )
#
#     return processMenu( API.menuItems )


