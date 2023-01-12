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
import webapp.api as API
from marshmallow import fields, pre_load, post_dump
from webapp.common import value2Label, utcDateString2Local


class AccessSchema( API.mm.SQLAlchemySchema ):
    """Schema for the user table, this is generated by the gencrud.py module
    When modifing the file make sure that you remove the table from the configuration.
    """
    A_ID        = fields.Integer()
    A_TABLE     = fields.String()
    A_CREATE    = fields.Boolean()
    A_READ      = fields.Boolean()
    A_UPDATE    = fields.Boolean()
    A_DELETE    = fields.Boolean()
    A_REMARK    = fields.String()


accessSchema    = AccessSchema()
accessSchema    = AccessSchema( many = True )
