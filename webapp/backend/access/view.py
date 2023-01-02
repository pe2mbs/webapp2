#
#   Python backend and Angular frontend code generation by gencrud
#   Copyright (C) 2018-2023 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
#   gencrud: 2021-04-04 08:26:10 version 2.1.680 by user mbertens
#
from flask import Blueprint
import webapp.api as API
from webapp.common import CrudInterface, RecordLock, createMenuHash
from webapp.backend.access.model import Access
from webapp.backend.access.schema import AccessSchema



webappAccessApi = Blueprint( 'webappAccessApi', __name__ )


# Args is for downwards compatibility !!!!!
def registerApi( *args ):
    # Set the logger for the users module
    API.app.logger.debug( 'Register Access routes' )
    API.app.register_blueprint( webappAccessApi )
    # Register at 'Administration' -> 'Users, Roles and Access'
    API.menu.register( {
        'caption':  'Access',
        'id':       createMenuHash( 'Access' ),
        'access':   'menu:user_role_access',
        'after':    'Roles',
        'before':   '*',
        'route':    '/access'
    }, 'Administration', 'Users, Roles and Access' )
    return


class AccessRecordLock( RecordLock ):
    def __init__(self):
        RecordLock.__init__( self, 'access', 'A_ID' )
        return


class AccessCurdInterface( CrudInterface ):
    _model_cls = Access
    _lock_cls = AccessRecordLock
    _schema_cls = AccessSchema()
    _schema_list_cls = AccessSchema( many = True )
    _uri = '/api/webapp/access'
    _relations = []

    def __init__( self ):
        CrudInterface.__init__( self, webappAccessApi )
        return

    def beforeUpdate( self, record ):
        for field in ( "A_ID", ):
            if field in record:
                del record[ field ]

        return record


user = AccessCurdInterface()
