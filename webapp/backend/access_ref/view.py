#
#   Python backend and Angular frontend code generation by gencrud
#   Copyright (C) 2018-2021 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
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
#   gencrud: 2023-01-07 16:14:56 version 2.3.707 by user W124574
#
from flask import Blueprint
import webapp.api as API
from webapp.common.crud import CrudInterface, RecordLock
import traceback
from webapp.backend.access_ref.model import AccessRef
from webapp.backend.access_ref.schema import AccessRefSchema


access_refApi = Blueprint( 'access_refApi', __name__ )


# Args is for downwards compatibility !!!!!
def registerApi( *args ):
    # Set the logger for the users module
    API.app.logger.info( 'Register AccessRef routes' )
    API.app.register_blueprint( access_refApi )
    return



class AccessRefRecordLock( RecordLock ):
    def __init__(self):
        RecordLock.__init__( self, 'access_ref', 'AR_ID' )
        return


class AccessRefCurdInterface( CrudInterface ):
    _model_cls = AccessRef
    _lock_cls = AccessRefRecordLock
    _schema_cls = AccessRefSchema()
    _schema_list_cls = AccessRefSchema( many = True )
    _uri = '/api/access_ref'
    _relations = []

    def __init__( self ):
        CrudInterface.__init__( self, access_refApi )
        return

    def beforeUpdate( self, record ):
        if "AR_ID" in record and record[ "AR_ID" ] in ( None, 0 ):
            del record[ "AR_ID" ]


        for field in ( "AR_A_ID", "AR_R_ID", ):
            if field in record and record[ field ] in ( None, 0 ):
                del record[ field ]


        return record


access_ref = AccessRefCurdInterface()
