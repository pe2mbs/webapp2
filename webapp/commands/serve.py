import os
from flask.cli import AppGroup
import webapp.api as API
import click
from flask import current_app
import werkzeug.serving
from werkzeug.middleware.proxy_fix import ProxyFix
from flask.cli import ( pass_script_info,
                        CertParamType,
                        _validate_key,
                        get_debug_flag,
                        show_server_banner )

def get_env():
    return os.environ.get( 'FLASK_ENV', 'DEVELOPMENT' )


@click.group( cls = AppGroup )
def serve():
    """Serve commands"""


@serve.command( 'dev',
                short_help = 'Runs a development server.' )
@click.option( '--hostname', '-h',
               help = 'The interface to bind to.')
@click.option( '--port', '-p',
               help = 'The port to bind to.' )
@click.option( '--cert',
               type = CertParamType(),
               help = 'Specify a certificate file to use HTTPS.')
@click.option( '--key',
               type = click.Path( exists = True,
                                  dir_okay = False,
                                  resolve_path = True ),
               callback=_validate_key,
               expose_value = False,
               help = 'The key file to use when specifying a certificate.')
@click.option( '--use_reloader/--no-reload',
               default = None,
               help = 'Enable or disable the reloader. By default the reloader '
                      'is active if debug is enabled.')
@click.option( '--use_debugger/--no-debugger',
               default = None,
               help = 'Enable or disable the debugger. By default the debugger '
                      'is active if debug is enabled.')
@click.option( '--eager-loading/--lazy-loader',
               default = None,
               help = 'Enable or disable eager loading. By default eager '
                      'loading is enabled if the reloader is disabled.' )
@click.option( '--with-threads/--without-threads',
               default = True,
               help = 'Enable or disable multithreading.' )
@pass_script_info
def dev( info, hostname, port, use_reloader, use_debugger, eager_loading, with_threads, cert ):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    FLASK_ENV=development or FLASK_DEBUG=1.
    """
    # run_simple( hostname = host, port = port, use_reloader = reload, use_debugger = debugger )
    # # application: "WSGIApplication",
    # # use_evalex: bool = True,
    # # extra_files: t.Optional[t.Iterable[str]] = None,
    # # exclude_patterns: t.Optional[t.Iterable[str]] = None,
    # # reloader_interval: int = 1,
    # # reloader_type: str = "auto",
    # # threaded: bool = False,
    # # processes: int = 1,
    # # request_handler: t.Optional[t.Type[WSGIRequestHandler]] = None,
    # # static_files: t.Optional[t.Dict[str, t.Union[str, t.Tuple[str, str]]]] = None,
    # # passthrough_errors: bool = False,
    # # ssl_context: t.Optional[_TSSLContextArg] = None, )
    #
    # debug = get_debug_flag()
    #
    # if reload is None:
    #     reload = debug
    #
    # if debugger is None:
    #     debugger = debug
    #
    # if eager_loading is None:
    #     eager_loading = not reload
    #
    # show_server_banner( get_env(), debug )
    # # app = DispatchingApp( info.load_app, use_eager_loading = eager_loading )
    #
    # applic      = info.load_app()
    # if host is None:
    #     host        = applic.config.get( 'HOST', 'localhost' )
    #
    # if port is None:
    #     port        = applic.config.get( 'PORT', 5000 )
    #
    # else:
    #     port = int( port )
    #
    # API.logger.info( "Serving application on http://{}:{}".format( host, port ) )
    # # appPath     = applic.config.get( 'APP_PATH', os.curdir )
    # # appApiMod   = applic.config.get( 'API_MODULE', '' )
    # # As those files may change, but are only loaded when the application starts
    # # we monitor them, so that the application restart when they change
    # extra_files = applic.config.get( 'EXTRA_FILES', [] )
    # appPath     = applic.config.get( 'APP_PATH', os.curdir )
    # appApiMod   = applic.config.get( 'API_MODULE', '' )
    # extra_files.extend( [ os.path.join( appPath, appApiMod, 'menu.yaml' ),
    #                       os.path.join( appPath, appApiMod, 'release.yaml' ) ] )
    # if API.socketio is not None:
    #     app.debug = True
    #     API.socketio.run( app, host, port,
    #                       debug = debugger,
    #                       use_reloader = reload,
    #                       extra_files = extra_files
    #                     )
    # else:
    #     from werkzeug.serving import run_simple
    #     run_simple( host, port, app,
    #                 use_reloader = reload,
    #                 reloader_type = 'stat',
    #                 use_debugger = debugger,
    #                 threaded = with_threads,
    #                 ssl_context = cert,
    #                 extra_files = extra_files )
    #
    applic = current_app
    if hostname is None:
        hostname    = applic.config.get( 'HOST', 'localhost' )

    if port is None:
        port        = applic.config.get( 'PORT', 5000 )

    else:
        port        = int( port )

    appPath     = applic.config.get( 'APP_PATH', os.curdir )
    appApiMod   = applic.config.get( 'API_MODULE', '' )
    extra_files = applic.config.get( 'EXTRA_FILES', [] )
    extra_files.extend( [ os.path.join( appPath, appApiMod, 'menu.yaml' ),
                          os.path.join( appPath, appApiMod, 'release.yaml' ) ] )
    static_files    = applic.config.get( 'STATIC_FILES', [] )
    use_evalex = True
    if not isinstance(port, int):
        port        = applic.config.get( 'PORT', 5000 )

    if static_files:
        from werkzeug.middleware.shared_data import SharedDataMiddleware
        applic = SharedDataMiddleware(applic, static_files)

    if use_debugger:
        from werkzeug.debug import DebuggedApplication
        applic = DebuggedApplication(applic, evalex=use_evalex)

    if not werkzeug.serving.is_running_from_reloader():
        s = werkzeug.serving.prepare_socket( hostname, port )
        fd = s.fileno()
        # Silence a ResourceWarning about an unclosed socket. This object is no longer
        # used, the server will create another with fromfd.
        s.detach()
        os.environ["WERKZEUG_SERVER_FD"] = str(fd)

    else:
        fd = int(os.environ["WERKZEUG_SERVER_FD"])

    threaded = False
    processes = 1
    request_handler = None
    passthrough_errors = False
    ssl_context = None
    exclude_patterns = None
    reloader_interval = 1
    reloader_type = "auto"

    if applic.config.get( "BEHIND_PROXY", False ):
        applic = ProxyFix( applic, x_for=1, x_proto=1, x_host=1, x_prefix=1 )

    srv = werkzeug.serving.make_server(
        hostname,
        port,
        applic,
        threaded,
        processes,
        request_handler,
        passthrough_errors,
        ssl_context,
        fd=fd,
    )

    if not werkzeug.serving.is_running_from_reloader():
        srv.log_startup()
        werkzeug.serving._log("info", werkzeug.serving._ansi_style("Press CTRL+C to quit", "yellow"))

    if use_reloader:
        from werkzeug._reloader import run_with_reloader

        run_with_reloader(
            srv.serve_forever,
            extra_files=extra_files,
            exclude_patterns=exclude_patterns,
            interval=reloader_interval,
            reloader_type=reloader_type,
        )
    else:
        srv.serve_forever()

    return


@serve.command( 'production',
                short_help = 'Runs a production server.' )
@click.option( '--host', '-h',
               default = '127.0.0.1',
               help = 'The interface to bind to.' )
@click.option( '--port', '-p',
               default = 8000,
               help = 'The port to bind to.' )
@pass_script_info
def production( info, host, port, *args, **kwargs ):
    import waitress
    app = DispatchingApp( info.load_app, use_eager_loading = True )
    applic = info.load_app()
    host = applic.config.get( 'HOST', host )
    port = applic.config.get( 'PORT', port )
    API.logger.info( "Serving application on http://{}:{}".format( host, port ) )
    waitress.serve( app, host = host, port = port )
    return


@serve.command( 'staged',
                short_help = 'Runs a production server.' )
@click.option( '--host', '-h',
               default = '127.0.0.1',
               help = 'The interface to bind to.' )
@click.option( '--port', '-p',
               default = 8000,
               help = 'The port to bind to.' )
@pass_script_info
def staged( info, host, port, *args, **kwargs ):
    import waitress
    app = DispatchingApp( info.load_app, use_eager_loading = True )
    applic = info.load_app()
    host = applic.config.get( 'HOST', host )
    port = applic.config.get( 'PORT', port )
    API.logger.info( "Serving application on http://{}:{}".format( host, port ) )
    waitress.serve( app, host = host, port = port )
    return

@serve.command( 'ssl',
                short_help = 'Runs a SSL/TLS server.')
@click.option( '--host', '-h',
               default = '127.0.0.1',
               help = 'The interface to bind to.')
@click.option( '--port', '-p',
               default = 5000,
               help='The port to bind to.')
@click.option( '--cert',
               type = CertParamType(),
               help='Specify a certificate file to use HTTPS.')
@click.option( '--key',
               type = click.Path( exists = True,
                                  dir_okay = False,
                                  resolve_path = True ),
               callback=_validate_key,
               expose_value = False,
               help = 'The key file to use when specifying a certificate.' )
@click.option( '--reload/--no-reload',
               default = None,
               help = 'Enable or disable the reloader. By default the reloader '
                      'is active if debug is enabled.')
@click.option( '--debugger/--no-debugger',
               default = None,
               help = 'Enable or disable the debugger. By default the debugger '
                      'is active if debug is enabled.')
@click.option( '--eager-loading/--lazy-loader',
               default = None,
               help = 'Enable or disable eager loading. By default eager '
                      'loading is enabled if the reloader is disabled.')
@click.option( '--with-threads/--without-threads',
               default = True,
               help = 'Enable or disable multithreading.')
@pass_script_info
def ssl( info, host, port, reload, debugger, eager_loading, with_threads, cert, key ):
    """Run a local development server.

    This server is for development purposes only. It does not provide
    the stability, security, or performance of production WSGI servers.

    The reloader and debugger are enabled by default if
    FLASK_ENV=development or FLASK_DEBUG=1.
    """
    debug = get_debug_flag()
    if reload is None:
        reload = debug

    if debugger is None:
        debugger = debug

    if eager_loading is None:
        eager_loading = not reload

    show_server_banner( get_env(), debug, info.app_import_path, eager_loading )
    app = DispatchingApp( info.load_app, use_eager_loading = eager_loading )
    applic      = info.load_app()
    if cert is None:
        ssl = applic.config.get( 'SSL', {} )
        if ssl is {}:
            raise Exception( "'SSL' section in configuration is missing" )

        try:
            certificate = ssl[ 'CERTIFICATE' ]
            if not os.path.isfile( certificate ):
                raise Exception( "Certificate file '%s' not preset." )

            keyfile = ssl[ 'KEYFILE' ]
            if not os.path.isfile( keyfile ):
                raise Exception( "Certificate file '%s' not preset." )

            cert = ( certificate, keyfile )

        except AttributeError:
            pass

        except Exception as exc:
            raise

    appPath     = applic.config.get( 'APP_PATH', os.curdir )
    appApiMod   = applic.config.get( 'API_MODULE', '' )
    # As those files may change, but are only loaded when the application starts
    # we monitor them, so that the application restart when they change
    extra_files = [ os.path.join( appPath, appApiMod, 'menu.yaml' ),
                    os.path.join( appPath, appApiMod, 'release.yaml' ) ]
    from werkzeug.serving import run_simple
    API.logger.info( "Serving application on https://{}:{}".format( host, port ) )
    run_simple( host, port, app,
                use_reloader = reload,
                reloader_type = 'stat',
                use_debugger = debugger,
                threaded = with_threads,
                ssl_context = cert,
                extra_files = extra_files )
    return
