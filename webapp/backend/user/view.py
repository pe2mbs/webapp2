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
from webapp.common import CrudInterface, RecordLock
from webapp.backend.user.model import User
from webapp.backend.user.schema import UserSchema
from webapp.backend.user.view_mixin import UserViewMixin


webappUserApi = Blueprint( 'webappUserApi', __name__ )


# Args is for downwards compatibility !!!!!
def registerApi( *args ):
    # Set the logger for the users module
    API.app.logger.info( 'Register User routes' )
    API.app.register_blueprint( webappUserApi )
    return


class UserRecordLock( RecordLock ):
    def __init__(self):
        RecordLock.__init__( self, 'user', 'U_ID' )
        return


class UserCurdInterface( CrudInterface, UserViewMixin ):
    _model_cls = User
    _lock_cls = UserRecordLock
    _schema_cls = UserSchema()
    _schema_list_cls = UserSchema( many = True )
    _uri = '/api/webapp/user'
    _relations = []

    def __init__( self ):
        CrudInterface.__init__( self, webappUserApi )
        UserViewMixin.__init__( self )
        return

    def beforeUpdate( self, record ):
        for field in ( "U_ID", "U_ACTIVE_LABEL", "U_ROLE_FK", "U_MUST_CHANGE_LABEL", "U_LISTITEMS_LABEL", ):
            if field in record:
                del record[ field ]

        if hasattr( UserViewMixin, 'beforeUpdate' ):
            record = UserViewMixin.beforeUpdate( self, record )


        return record


user = UserCurdInterface()

