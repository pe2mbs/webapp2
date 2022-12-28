import webapp.api as API
from marshmallow import fields, pre_load, post_dump
from webapp.common.convert import value2Label # , utcDateString2Local


class LocaleSchema( API.mm.SQLAlchemySchema ):
    L_ID    = fields.Integer()
    L_NAME    = fields.String()
    L_COUNTRY_CODE    = fields.Integer()
    L_DESCRIPTION    = fields.String()
    L_REMARK    = fields.String(missing=None)

    __field_set__ = {
        'L_ID': 0,
        'L_NAME': '',
        'L_COUNTRY_CODE': 0,
        'L_DESCRIPTION': '',
        'L_REMARK': None,
    }

    @post_dump
    def post_dump_process( self, in_data, **kwargs ):
        for field, default in self.__field_set__.items():
            if in_data[ field ] is None:
                in_data[ field ] = default

        return in_data


localeSchema   = LocaleSchema()
localesSchema  = LocaleSchema( many = True )
