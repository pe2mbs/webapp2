# -*- coding: utf-8 -*-
"""This middleware module provides methods that are invoked before or after each
 request sent to the webapp2 flask application. Ensure that this module is initialized
 AFTER the tracking module"""
#
# Main webapp application package
# Copyright (C) 2018-2020 Marc Bertens-Nguyen <m.bertens@pe2mbs.nl>
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
import webapp2.api as API
from sqlalchemy.exc import DatabaseError, IntegrityError
from flask import request


# uncomment for handling incoming requests before reaching the endpoint
#@(API.app).before_request
#def before_request_func():
#    print("before_request executing!")

@(API.app).after_request
def after_request_func(response):
    if response.status_code >= 400:
        return
    try:
        requestData = request.json
        if requestData is None:
            requestData = request.args
        # enable tracking by default, however, this can be set to false
        # either by request or from the request handler through the response
        disableTracking = False
        if requestData != None and "tracking" in requestData and requestData["tracking"] in (False, str(False)):
            disableTracking = True
        if response.json != None and "tracking" in response.json and response.json["tracking"] in (False, str(False)):
            disableTracking = True
        
        # TODO: sqlalchemy does not seem to be aware of cascade deletion before commits
        # so we will only track the item that is deleted by user and not the cascade
        # deleted items
        
        # apply tracking on changed records
        user = response.headers["USER"] if ("USER" in  response.headers and \
                response.headers["USER"] not in (None, "")) else "backend"

        deletedRecords, modifiedRecords, newRecords = None, None, None

        if API.db.session.deleted:
            deletedRecords = API.db.session.deleted

        #if API.db.session.dirty:
        #    modifiedRecords = [obj for obj in API.db.session.dirty if API.db.session.is_modified(obj)]            
            #for object in API.db.session.dirty:
            #    if API.db.session.is_modified(object):
            #        print("###################", API.db.session.dirty)
            #    else: 
            #        print("&&&&&&&&&&&&&&&&&&&&&&&&&&", API.db.session.dirty)

            #print("###################", API.db.session.deleted)
        if API.db.session.new:
            newRecords = API.db.session.new
        
        # commit or at least try to commit all changes
        API.db.session.commit()

        if deletedRecords and not disableTracking:
            for deletedObject in deletedRecords:
                # print("###############", deletedObject.dictionary)
                API.recordTracking.delete( deletedObject.__tablename__,
                                getattr(deletedObject, deletedObject.__field_list__[ 0 ]),
                                deletedObject.dictionary,
                                user )
        #if modifiedRecords:
            # for modifiedRecord in modifiedRecords:
            #     if not disableTracking:
            #         # print(getattr(addedObject, addedObject.__field_list__[ 0 ]))
            #         API.recordTracking.update( modifiedRecord.__tablename__,
            #                             getattr(modifiedRecord, modifiedRecord.__field_list__[ 0 ]),
            #                             modifiedRecord.dictionary,
            #                             user )
            #     response.data = modifiedRecord.schemaJson
            #     return response

        if newRecords:
            #print("###################", newRecords)
            for addedObject in newRecords:
                if not disableTracking:
                    # print(getattr(addedObject, addedObject.__field_list__[ 0 ]))
                    API.recordTracking.insert( addedObject.__tablename__,
                                        getattr(addedObject, addedObject.__field_list__[ 0 ]),
                                        addedObject.dictionary,
                                        user )
                # in case we add only one item as it is the case for a crudinterface call
                # we will only have one item created and return it in the response
                if addedObject.__field_list__[ 0 ] in response.json:
                    response.data = addedObject.schemaJson
                    return response

        return response

    except IntegrityError as error:

        API.db.session.rollback()
        raise error

    except DatabaseError as error:
        API.db.session.rollback()
        raise error
