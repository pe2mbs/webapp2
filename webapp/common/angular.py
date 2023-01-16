# -*- coding: utf-8 -*-
"""Main webapp application package."""
#
# Main webapp application package
# Copyright (C) 2018-2023 Marc Bertens-Nguyen <m.bertens@pe2mbs.nl>
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
import os
from flask import Blueprint, send_from_directory, current_app, request, jsonify
from mako.template import Template
from werkzeug.routing import BaseConverter
import webapp.api as API
from webapp.extensions.database import db
from webapp.version import version, author, copyright

__version__         = version
__copyright__       = copyright
__author__          = author
__docformat__       = 'epytext'


bluePrint   = Blueprint( 'angular', __name__ )


class RegexConverter( BaseConverter ):
    """This class provides the regular expression URL converter class

    """
    def __init__( self, url_map, *items ):
        super( RegexConverter, self ).__init__( url_map )
        self.regex = items[ 0 ]


def renderErrorPage( message, reason = '', explanation = '' ):
    """Provides an error page when something goes wrong in the configuration.

    The default content may be oberridden by setting the variable 'ANGULAR_ERROR_PAGE' in the Flask configuration.

    @param message:         Problem desciption of the problem.
    @param reason:          Details of the problem, may even be a traceback of the stack.
    @param explanation:     Corrective actions to be taken to resolve the problem.

    @rtype:                 string
    @return:                returns a rendered page for the browser.
    """
    angular_error_page = current_app.config.get( 'ANGULAR_ERROR_PAGE', './' )
    if not os.path.exists( angular_error_page ):
        if os.path.exists( os.path.join( os.path.dirname( __file__ ), angular_error_page ) ):
            angular_error_page = os.path.join( os.path.dirname( __file__ ), angular_error_page )

    return Template( filename = angular_error_page ).render( message = message, reason = reason, explanation = explanation )


def registerAngular():
    """Registers the 'angular' blueprint in the backend. And setup the regex URL converter.

    @return:            None
    """
    API.app.url_map.converters[ 'regex' ] = RegexConverter
    API.app.register_blueprint( bluePrint )
    return


@bluePrint.route( '/' )
def index():
    """Main entry point of the web server that provides the Angular application.

    in the Flask configuration 'ANGULAR_PATH' must be set to the location where the index.html of the anglar application is located.

    @rtype:             Flask Response object
    @return:            object the reponse of the server
    """
    angular_path = current_app.config[ 'ANGULAR_PATH' ]
    env = current_app.config[ 'ENV' ]
    current_app.logger.info( f"Angular dist ({env}) : {angular_path}" )
    try:
        # Test if the path exists.
        if os.path.isdir( angular_path ):
            # Test if the file 'index.html' exists.
            if os.path.isfile( os.path.join( angular_path, "index.html" ) ):
                # Deliver the file 'index.html' to the browser
                return send_from_directory( angular_path, "index.html" )

            # The file was not found, deliver a usefull page that the application clould not be loaded.
            # Normally this only apears during development of the Angular application.
            current_app.logger.info( f"Python says file not found for {angular_path}/index.html" )
            return renderErrorPage( "Angular application is missing",
                                    f"The frontend application was not found at {angular_path}",
                                    """Correct the ANGULAR_PATH in the configuration
                                     or perform the <pre># ng build</pre> in the frontend folder to
                                     (re-)create the Angular application.
                                     """ )
        else:
            # The path was not found, deliver a usefull page that the application clould not be loaded.
            # Normally this only apears during development of the Angular application.
            current_app.logger.info( f"ANGULAR_PATH incorrect {angular_path}." )
            return renderErrorPage( f"ANGULAR_PATH incorrect {angular_path}.",
                                    f"The frontend folder was not found {angular_path}.",
                                    "Correct the ANGULAR_PATH in the configuration." )

    except Exception as exc:
        # Log the error at this point
        current_app.logger.exception( exc )
        # re-raise the exception
        raise exc


@bluePrint.route( r"/<regex('\w\.(js|css|map|ico|jpg|eps|png|woff|woff2|svg|eot|ttf)'):path>" )
def angularSource( path ):
    """This entry point provides all the files that are retrieved by the Angular application.

    @type path:         string
    @param path:        path and filename of Angular application file to be retrieved.

    @rtype:             Flask Response object
    @return:            object the reponse of the server
    """
    angular_path = current_app.config[ 'ANGULAR_PATH' ]
    env = current_app.config[ 'ENV' ]
    current_app.logger.info( f"Angular dist ({env}) : {angular_path}" )
    return send_from_directory( angular_path, path )


@bluePrint.route( r"/assets/<regex('\w\.(ico|jpg|eps|png|woff|woff2|svg|eot|ttf)'):path>" )
def angularAsserts( path ):
    """This entry point provides all the files that are retrieved by the Angular application for the /assets/ path.

    @type path:         string
    @param path:        path and filename of Angular application file to be retrieved.

    @rtype:             Flask Response object
    @return:            object the reponse of the server
    """
    angular_path = current_app.config[ 'ANGULAR_PATH' ]
    env = current_app.config[ 'ENV' ]
    current_app.logger.info( "Angular assets ({}) : {}".format( env, angular_path ) )
    return send_from_directory( os.path.join( angular_path, 'assets' ), path )


@bluePrint.route( "/api/database", methods=[ 'GET' ] )
def getDatabaseConfig():
    """Returns a JSON object with the current database(s)

    @rtype:         string
    @return:        JSON object with database provider information
    """
    result = {}
    for key, value in current_app.config.get( 'DATABASE', {} ).items():
        if key == 'TNS':
            result[ 'database' ] = value

        else:
            result[ key.lower() ] = value

    # check for extra binds
    extraBinds = []
    for bind in current_app.config.get( 'DATABASE_BINDS', [] ):
        result_bind = {}
        for key, value in bind.get( 'DATABASE', {} ).items():
            if key == 'TNS':
                result_bind[ 'database' ] = value

            else:
                result_bind[ key.lower() ] = value

            extraBinds.append( result_bind )

    if len( extraBinds ):
        result[ 'binds' ] = extraBinds

    return jsonify( **result )


@bluePrint.route( "/api/webapp/version", methods=[ 'GET' ] )
def getVersionInfo():
    """Returns a JSON object with the current information of the webapp package.

    @rtype:         string
    @return:        JSON object with webapp information
    """
    return jsonify( version = __version__, copyright = __copyright__, author = __author__ )
