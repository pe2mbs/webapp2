#
# serve commands webapp application package
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
from flask.cli import AppGroup
from deprecated import deprecated
import webapp.api as API
import click
from flask import current_app
import werkzeug.serving
try:
    # does not work on werkzeug 0.14.1
    from werkzeug.middleware.proxy_fix import ProxyFix
except Exception as exc:
    pass
from flask.cli import pass_script_info, CertParamType, _validate_key, get_debug_flag, show_server_banner
from threading import Thread, Lock


__docformat__ = 'epytext'


"""Serve commands webapp application package
"""


@deprecated( reason = "This should not be nessary" )
def get_env():
    return os.environ.get( 'FLASK_ENV', 'DEVELOPMENT' )


@click.group( cls = AppGroup )
def serve():
    """Serve commands"""


class DispatchingApp( object ):
    """This class was removed from the standard Flask version 2.x, the webapp startup depends on it

    Special application that dispatches to a Flask application which
    is imported by name in a background thread.  If an error happens
    it is recorded and shown as part of the WSGI handling which in case
    of the Werkzeug debugger means that it shows up in the browser.
    """

    def __init__( self, loader ):
        """Contructort of the class

        @param loader:
        """
        self.loader             = loader
        self._app               = None
        self._lock              = Lock()
        self._bg_loading_exc    = None
        self._load_unlocked()

    def _load_in_background( self ):
        # Store the Click context and push it in the loader thread so
        # script_info is still available.
        ctx = click.get_current_context( silent = True )

        def _load_app():
            __traceback_hide__ = True  # noqa: F841

            with self._lock:
                if ctx is not None:
                    click.globals.push_context(ctx)

                try:
                    self._load_unlocked()
                except Exception as e:
                    self._bg_loading_exc = e

        t = Thread(target=_load_app, args=())
        t.start()

    def _flush_bg_loading_exception( self ):
        # If __traceback_hide__ set and true, this indicates that the frame should be hidden from abbreviated tracebacks.
        # This way you can hide some of the complexity of the larger framework and let the user focus
        # on their own errors.
        __traceback_hide__ = True  # noqa: F841
        exc = self._bg_loading_exc
        if exc is not None:
            self._bg_loading_exc = None
            raise exc

        return

    def _load_unlocked(self):
        # If __traceback_hide__ set and true, this indicates that the frame should be hidden from abbreviated tracebacks.
        # This way you can hide some of the complexity of the larger framework and let the user focus
        # on their own errors.
        __traceback_hide__ = True  # noqa: F841
        self._app = rv = self.loader()
        self._bg_loading_exc = None
        return rv

    def __call__( self, environ, start_response ):
        # If __traceback_hide__ set and true, this indicates that the frame should be hidden from abbreviated tracebacks.
        # This way you can hide some of the complexity of the larger framework and let the user focus
        # on their own errors.
        __traceback_hide__ = True  # noqa: F841
        if self._app is not None:
            return self._app( environ, start_response )

        self._flush_bg_loading_exception()
        with self._lock:
            if self._app is not None:
                rv = self._app

            else:
                rv = self._load_unlocked()

            return rv( environ, start_response )


@serve.command( 'dev', short_help = 'Runs a development server.' )
@click.option( '--hostname', '-h', help = 'The interface to bind to.')
@click.option( '--port', '-p', help = 'The port to bind to.' )
@click.option( '--cert', type = CertParamType(), help = 'Specify a certificate file to use HTTPS.')
@click.option( '--key', type = click.Path( exists = True, dir_okay = False, resolve_path = True ),
               callback=_validate_key, expose_value = False, help = 'The key file to use when specifying a certificate.')
@click.option( '--use_reloader/--no-reload', default = None,
               help = 'Enable or disable the reloader. By default the reloader is active if debug is enabled.')
@click.option( '--use_debugger/--no-debugger', default = None,
               help = 'Enable or disable the debugger. By default the debugger  is active if debug is enabled.')
@click.option( '--with-threads/--without-threads', default = True, help = 'Enable or disable multithreading.' )
@pass_script_info
def dev( info, hostname, port, use_reloader, use_debugger, with_threads, cert ):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    FLASK_ENV=development or FLASK_DEBUG=1.
    """
    debug = get_debug_flag()
    if use_reloader is None:
        use_reloader = debug

    if use_debugger is None:
        use_debugger = debug

    show_server_banner( get_env(), debug, "" , False )
    app = DispatchingApp( info.load_app )

    applic      = info.load_app()
    if hostname is None:
        hostname    = applic.config.get( 'HOST', 'localhost' )

    if port is None:
        port        = applic.config.get( 'PORT', 5000 )

    else:
        port = int( port )

    API.logger.info( "Serving application on http://{}:{}".format( hostname, port ) )
    # As those files may change, but are only loaded when the application starts
    # we monitor them, so that the application restart when they change
    extra_files = applic.config.get( 'EXTRA_FILES', [] )
    appPath     = applic.config.get( 'APP_PATH', os.curdir )
    appApiMod   = applic.config.get( 'API_MODULE', '' )
    extra_files.extend( [ os.path.join( appPath, appApiMod, 'menu.yaml' ),
                          os.path.join( appPath, appApiMod, 'release.yaml' ) ] )
    if API.app.config.get( 'USE_EXTENSIONS', {} ).get( "SOCKETIO", False ):
        app.debug = True
        API.socketio.run( app, hostname, port, debug = use_debugger, use_reloader = use_reloader, extra_files = extra_files )

    else:
        from werkzeug.serving import run_simple
        run_simple( hostname, port, app,
                    use_reloader = use_reloader,
                    reloader_type = 'stat',
                    use_debugger = use_debugger,
                    threaded = with_threads,
                    ssl_context = cert,
                    extra_files = extra_files )

    return


@serve.command( 'production', short_help = 'Runs a production server.' )
@click.option( '--host', '-h', default = '127.0.0.1', help = 'The interface to bind to.' )
@click.option( '--port', '-p', default = 8000, help = 'The port to bind to.' )
@pass_script_info
def production( info, host, port, *args, **kwargs ):
    """This is the command for starting the production server using the 'waitress' package.
    The 'waitress' package must be installed manually, its not part of the standard installation
    of webapp.

    @param info:
    @type host:         string
    @param host:        (FQFN) hostname or dotted IP address
    @type port:         integer
    @param port:        the TCP/IP port number
    @param args:        unused arguments
    @param kwargs:      unused keyword arguments

    @return:            None
    """
    import waitress
    app = DispatchingApp( info.load_app )
    applic = info.load_app()
    host = applic.config.get( 'HOST', host )
    port = applic.config.get( 'PORT', port )
    API.logger.info( "Serving application on http://{}:{}".format( host, port ) )
    waitress.serve( app, host = host, port = port )
    return


@serve.command( 'staged', short_help = 'Runs a production server.' )
@click.option( '--host', '-h', default = '127.0.0.1', help = 'The interface to bind to.' )
@click.option( '--port', '-p', default = 8000, help = 'The port to bind to.' )
@pass_script_info
def staged( info, host, port, *args, **kwargs ):
    """This is the command for starting the staged server using the 'waitress' package.
    The 'waitress' package must be installed manually, its not part of the standard installation
    of webapp.

    @param info:
    @type host:         string
    @param host:        (FQFN) hostname or dotted IP address
    @type port:         integer
    @param port:        the TCP/IP port number
    @param args:        unused arguments
    @param kwargs:      unused keyword arguments

    @return:            None
    """
    import waitress
    app = DispatchingApp( info.load_app )
    applic = info.load_app()
    host = applic.config.get( 'HOST', host )
    port = applic.config.get( 'PORT', port )
    API.logger.info( "Serving application on http://{}:{}".format( host, port ) )
    waitress.serve( app, host = host, port = port )
    return
