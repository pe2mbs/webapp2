#webappwebappwebappwebapp
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
#   gencrud: 2022-12-22 14:32:53 version 2.3.704 by user w124574
#
import webapp.api as API
from webapp.common.dbmem import DbBaseMemory
from webapp.common.crudmixin import CrudModelMixin
import webapp.common as common
from webapp.backend.locale.schema import LocaleSchema
from sqlalchemy.orm import backref




class Locale( API.db.Model, CrudModelMixin ):
    __field_list__       = ['L_ID', 'L_NAME', 'L_COUNTRY_CODE', 'L_DESCRIPTION', 'L_REMARK']
    __tablename__        = 'gn_locale'
    __schema_cls__       = LocaleSchema()
    __secondary_key__    = 'L_NAME'
    L_ID                 = API.db.Column( "l_id", API.db.Integer, autoincrement = True, primary_key = True )
    L_NAME               = API.db.Column( "l_name", API.db.String( 10 ), nullable = False )
    L_COUNTRY_CODE       = API.db.Column( "l_country_code", API.db.Integer, nullable = False )
    L_DESCRIPTION        = API.db.Column( "l_description", API.db.String( 50 ), nullable = False )
    L_REMARK             = API.db.Column( "l_remark", API.db.LONGTEXT, nullable = True )


    def memoryInstance( self ):
        return LocaleMemory( self )

API.dbtables.register( Locale )

class LocaleMemory( DbBaseMemory ):
    __model_cls__       = Locale
    __tablename__       = 'gn_locale'


API.memorytables.register( LocaleMemory )
