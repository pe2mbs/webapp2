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
#      gencrud: 2021-04-04 08:26:09 version 2.1.680 by user mbertens
#
import traceback
from flask import Blueprint, request, jsonify, current_app
import webapp.api as API
from webapp.backend.feedback.model import Feedback
from webapp.common import createMenuHash
from webapp.common.decorators import no_pre_processing


feedbackApi = Blueprint( 'feedbackApi', __name__ )

def registerApi( *args ):
    # Set the logger for the users module
    API.app.logger.debug( 'Register RecordLocks routes' )
    API.app.register_blueprint( feedbackApi )
    # Register at TOP level
    API.menu.register( {
        'caption':  'Feedback',
        'id':       createMenuHash( 'Feedback' ),
        'after':    'Administration',
        'access':   '*',
        'befone':   None,
        'route':    '/feedback'
    } )
    return


@feedbackApi.route( '/api/feedback', methods = [ 'PUT' ] )
@no_pre_processing('feedbackApi')
def feedback():
    data    = request.json
    if data is None:
        return "Invalid request, missing Feedback data", 500

    current_app.logger.info( '/api/feedback PUT: {0}'.format( repr( data ) ) )
    record = Feedback()
    for key,value in request.json.items():
        setattr( record,key, value )

    API.db.session.add( record )
    API.db.session.commit()
    if hasattr( current_app, 'sendMail' ):
        current_app.sendMail( record )

    current_app.logger.debug( 'feedback() => ok' )
    return jsonify( status = 'ok' )
