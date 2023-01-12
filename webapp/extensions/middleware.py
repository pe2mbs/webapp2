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
import webapp.api as API
from webapp.api import app
from webapp.common.util import Right
from webapp.backend.access_ref import AccessRef
from webapp.backend.access.model import Access
from webapp.backend.user.model import User
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import attributes as history_attributes
from flask_jwt_extended import verify_jwt_in_request, decode_token, get_current_user, get_jwt_identity
from flask import request
from typing import List
from datetime import datetime
import re


# uncomment for handling incoming requests before reaching the endpoint
@app.before_request
def before_request_func():
    funcName = request.endpoint #.split(".")[-1]
    apiName = request.endpoint.split(".")[0]
    print("### before_request executing: ", request.endpoint)
    #print(API.required_rights.keys())
    if funcName in API.no_pre_processing.keys():
        # ignore this endpoint
        print("##### no auth")
        pass
    else:
        print("########### jwt identity: ", get_jwt_identity())
        # 1. verify token itself
        verify_jwt_in_request()

        # 2. verify that expiration date is not exceeded
        token = None
        try:
            header_name = "Authorization"
            header_type = "JWT"

            # Verify we have the auth header
            jwt_header = request.headers.get(header_name, None)
    
            # Make sure the header is in a valid format that we are expecting, ie
            # <HeaderName>: <HeaderType(optional)> <JWT>
            parts = jwt_header.split()
            if not header_type:
                if len(parts) != 1:
                    msg = "Bad {} header. Expected value '<JWT>'".format(header_name)
                    raise Exception(msg)
                encoded_token = parts[0]
            else:
                if parts[0] != header_type or len(parts) != 2:
                    msg = "Bad {} header. Expected value '{} <JWT>'".format(
                        header_name,
                        header_type
                    )
                    raise Exception(msg)
                encoded_token = parts[1]

            token = decode_token(encoded_token)
            print("############", token)
        except Exception as e:
            print("Error: ", e)
        if token is not None and (token["exp"] < datetime.now().timestamp() or "exp" not in token):
            raise Exception("Token expired!")
        
        # 3. check roles of the user
        if token is not None and "identity" in token:
            userName = token["identity"]
            userObject =  API.db.session.query( User ).filter( User.U_NAME == userName).one()
            print(userObject)
            role = userObject.U_R_ID_FK
            print(role.R_NAME)
            # get access objects for the user's role 
            accessRights: List[Access] = API.db.session.query( Access ).join( AccessRef, AccessRef.AR_R_ID == userObject.U_R_ID ).all()
            print(accessRights)
            shouldGrantAccess = True # TODO: set to False later

            # search for access rights that correspond to the specific function to call
            accessRights = set([accessRight for accessRight in accessRights for component in \
                    accessRight.A_COMPONENT.replace(" ", "").split(",") if \
                    re.search(component.replace(".", "\.").replace("*", ".*"), funcName) ])


            # search for the access right that corresponds to the current endpoint (without specific function)
            if len(accessRights) == 0:
                accessRights = set([accessRight for accessRight in accessRights for component in \
                    accessRight.A_COMPONENT.replace(" ", "").split(",") if \
                    re.search(component.replace(".", "\.").replace("*", ".*"), apiName) ])
    
            print(accessRights)
            for accessRight in accessRights:
                # component can be te_test_planApi or more specific te_test_planApi.getId
                # check whether we can access whole component or only subfunction
                requiredRights = API.required_rights.get( funcName, set([Right.CREATE, Right.DELETE, Right.READ, Right.UPDATE]))
                if Right.ALL in requiredRights:
                    requiredRights = set([Right.CREATE, Right.DELETE, Right.READ, Right.UPDATE])
                givenRights = [Right[field[2:]] for field in Access.rightFields if getattr(accessRight, field) == True]
                print(requiredRights, givenRights)
                # check whether the required rights are a subset of the given rights
                shouldGrantAccess = requiredRights.issubset(givenRights)
                print(shouldGrantAccess)
            
            if not shouldGrantAccess:
                raise Exception("The user does not have the required role/rights to access the resource!")
            
            #for right in requiredRights:
            #    accessRight = getattr( accessRights, "A_".format(right.name) )




@app.after_request
def after_request_func(response):
    if response.status_code >= 400 or "application/json" not in request.headers:
        return response
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

        if API.db.session.dirty:
            modifiedRecords = [obj for obj in API.db.session.dirty if API.db.session.is_modified(obj)]
        if API.db.session.new:
            newRecords = API.db.session.new

        # commit or at least try to commit all changes
        # API.db.session.commit()

        if deletedRecords and not disableTracking:
            deletedRecords = list(deletedRecords)
            if len(deletedRecords) > 1:
                API.recordTracking.cascade_delete(
                            [record.__tablename__ for record in deletedRecords],
                            getattr(deletedRecords[0], deletedRecords[0].__field_list__[ 0 ]),
                            [record.dictionary for record in deletedRecords],
                            user )
            else:
                deletedObject = deletedRecords[0]
                API.recordTracking.delete( deletedObject.__tablename__,
                                getattr(deletedObject, deletedObject.__field_list__[ 0 ]),
                                deletedObject.dictionary,
                                user )
        if modifiedRecords:
            for modifiedRecord in modifiedRecords:
                if not disableTracking:
                    API.recordTracking.autoUpdate( modifiedRecord, user )
                response.data = modifiedRecord.schemaJson
                return response

        if newRecords:
            #print("###################", newRecords)
            # commmit so that there will be ids for the primary key on
            # insertion time
            API.db.session.commit()
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

        API.db.session.commit()
        return response

    except IntegrityError as error:

        API.db.session.rollback()
        raise error

    except DatabaseError as error:
        API.db.session.rollback()
        raise error
