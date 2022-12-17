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
#   gencrud: 2021-04-04 08:26:09 version 2.1.680 by user mbertens
#
import webapp.api as API
from webapp.common.dbmem import DbBaseMemory
from webapp.common.crudmixin import CrudModelMixin




class RecordLocks( API.db.Model, CrudModelMixin ):
    """Model for the locking table, this is generated by the gencrud.py module
    When modifing the file make sure that you remove the table from the configuration.
    """
    __field_list__       = ['L_ID', 'L_USER', 'L_TABLE', 'L_RECORD_ID', 'L_START_DATE']
    __tablename__        = 'locking'
    L_ID                 = API.db.Column( "l_id", API.db.Integer, autoincrement = True, primary_key = True )
    L_USER               = API.db.Column( "l_user", API.db.LONGTEXT, nullable = False )
    L_TABLE              = API.db.Column( "l_table", API.db.LONGTEXT, nullable = False )
    L_RECORD_ID          = API.db.Column( "l_record_id", API.db.Integer, nullable = False )
    L_START_DATE         = API.db.Column( "l_start_date", API.db.DateTime, nullable = False )


    def memoryInstance( self ):
        return RecordLocksMemory( self )


# API.dbtables.register( RecordLocks )


class RecordLocksMemory( DbBaseMemory ):
    __model_cls__       = RecordLocks
    __tablename__       = 'locking'


# API.memorytables.register( RecordLocksMemory )
