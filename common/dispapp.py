import os
import sys
from threading import Lock, Thread


def reraise(tp, value, tb=None):
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value

def get_env():
    """Get the environment the app is running in, indicated by the
    :envvar:`FLASK_ENV` environment variable. The default is
    ``'production'``.
    """
    return os.environ.get('FLASK_ENV') or 'production'

class DispatchingApp(object):
    """Special application that dispatches to a Flask application which
    is imported by name in a background thread.  If an error happens
    it is recorded and shown as part of the WSGI handling which in case
    of the Werkzeug debugger means that it shows up in the browser.
    """

    def __init__(self, loader, use_eager_loading=False):
        self.loader = loader
        self._app = None
        self._lock = Lock()
        self._bg_loading_exc_info = None
        if use_eager_loading:
            self._load_unlocked()
        else:
            self._load_in_background()

    def _load_in_background(self):
        def _load_app():
            __traceback_hide__ = True
            with self._lock:
                try:
                    self._load_unlocked()
                except Exception:
                    self._bg_loading_exc_info = sys.exc_info()
        t = Thread(target=_load_app, args=())
        t.start()

    def _flush_bg_loading_exception(self):
        __traceback_hide__ = True
        exc_info = self._bg_loading_exc_info
        if exc_info is not None:
            self._bg_loading_exc_info = None
            reraise(*exc_info)

    def _load_unlocked(self):
        __traceback_hide__ = True
        self._app = rv = self.loader()
        self._bg_loading_exc_info = None
        return rv

    def __call__(self, environ, start_response):
        __traceback_hide__ = True
        if self._app is not None:
            return self._app(environ, start_response)
        self._flush_bg_loading_exception()
        with self._lock:
            if self._app is not None:
                rv = self._app
            else:
                rv = self._load_unlocked()
            return rv(environ, start_response)

