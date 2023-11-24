import typing as t
import yaml
import json
import os
import sys
import deepmerge
from yamlinclude import YamlIncludeConstructor
from flask import Config as BaseConfig
from mako.template import Template
from webapp2.common.exceptions import ConfigFolderNotFound, ConfigurationNotFound


class Config( BaseConfig ):
    class ConfigLoader(yaml.SafeLoader):
        def __init__( self, stream ):
            super().__init__( stream )
            return

    class MyMerger( deepmerge.Merger ):
        def __init__(self):
            super().__init__(  # pass in a list of tuple, with the
                # strategies you are looking to apply to each type.
                [ ( list, [ "append" ] ), ( dict, [ "merge" ] ), ( set, [ "union" ] ) ],
                # next, choose the fallback strategies, applied to all other types:
                [ "override" ],
                # finally, choose the strategies in the case where the types conflict:
                [ "override" ] )
            return

    def __init__( self, root_path: str,
                  defaults: t.Union[dict,None] = None ):
        super().__init__( root_path, defaults )
        self.__merge = Config.MyMerger()
        self.__merger = self.__merge.merge
        self.__extension = 'json'
        return

    def fromFolder( self, config_folder, extension: str = 'yaml' ):
        self.__extension = extension
        if not os.path.exists( config_folder ):
            configFolder = os.path.abspath( os.path.join( config_folder, '..' ) )

        else:
            configFolder = config_folder

        if not os.path.exists( configFolder ):
            raise ConfigFolderNotFound( config_folder )

        if not os.path.exists( os.path.join( configFolder, f"config.{ self.__extension }") ):
            raise ConfigurationNotFound( os.path.join( configFolder, f"config.{ self.__extension }" ) )

        YamlIncludeConstructor.add_to_loader_class( loader_class = Config.ConfigLoader,
                                                    base_dir = config_folder )  # or specify another dir relatively or absolutely
        # Load the default configuration, which is shared for every body.
        config  = self.loadConfiguration( config_folder, 'config' )
        # For the task we use the starter script name
        segment = os.path.splitext( os.path.basename( sys.argv[ 0 ] ) )[ 0 ]
        config  = self.loadConfiguration( config_folder, segment, 'tsk', config )
        # First check if the depricated FLASK_ENV is set, if not we check WEBAPP_ENV,
        # when is not set either we use the login name in uppercase.
        segment = os.environ.get( 'FLASK_ENV', os.environ.get( 'WEBAPP_ENV', os.getlogin().upper() ) )
        config  = self.loadConfiguration( config_folder, segment, 'env', config )
        config  = self.resolveSqlalchemy( config )
        self.update( self.resolver( config ) )
        return config

    def loadConfiguration( self,
                           config_folder: str,
                           segment: str,
                           section: t.Optional[str] = None,
                           config: t.Optional[t.Union[dict]] = None ):
        not_exists_ok   = False
        if config is None:
            config      = {}

        if section is None:
            config_file     = os.path.join( config_folder, f'{segment}.{self.__extension}' )

        else:
            # Only for the section config we allow for Not Exists
            config_file     = os.path.join( config_folder, section, f'{segment}.{self.__extension}' )
            not_exists_ok   = True

        if os.path.exists( config_file ):
            with open( config_file, 'r' ) as stream:
                config = self.__merger( config, Config._flatten( yaml.load(stream, Loader=Config.ConfigLoader ) ) )

            config.setdefault( 'WEBAPP', {} )[ segment.upper() ] = config_file

        elif not not_exists_ok:
            raise FileNotFoundError( f"{ config_file } not found" )

        if (section or '').lower() == 'env':
            config[ 'ENV' ] = segment.upper()

        return config

    def from_file( self, filename: str, load: t.Optional[t.Callable[[t.IO[t.Any]], t.Mapping]] = None,
                   silent: bool = False, text: bool = True ) -> bool:
        return super().from_file( filename, yaml.load, silent, True )

    def resolver( self, config: dict ):
        """ This resolver tries to resolve the ${ variable } in the configuration
            When it could not resolve it leaves the item as-is
        """
        for key in config.keys():
            value = config[ key ]
            if isinstance( value, str ):
                Config.tryToResolve( config, key, value )

            elif isinstance( value, dict ):
                config[ key ] = self.resolver( value )

            elif isinstance( value, list ):
                for idx, item in enumerate( value ):
                    if isinstance( item, str ):
                        Config.tryToResolve( config, key, value )

                    elif isinstance( item, dict ):
                        config[ key ][ idx ] = self.resolver( item )

        return config

    def resolveSqlalchemy( self, config: dict ):
        """ This resolved the segment DATABASE into SQLALCHEMY_DATABASE_URI
        """
        if 'SQLALCHEMY_DATABASE_URI' not in config and 'DATABASE' in config:
            #
            #   Setup SQLALCHEMY_DATABASE_URI parameter from the DATABASE segment
            #
            database = config[ 'DATABASE' ]
            config[ 'SQLALCHEMY_DATABASE_URI' ] = Config._buildSqlalchemyUrl( database )
            # If there are any binds
            for bind in database.get( 'BINDS', [] ):
                schema = bind.get( 'SCHEMA' )
                if schema is not None:
                    dbname = os.path.split( schema )[ -1 ]
                    config.setdefault( 'SQLALCHEMY_BINDS', {} )[ dbname ] = Config._buildSqlalchemyUrl( bind )

        return config

    def dump( self, dumper: t.Optional[ t.Callable ] = None ):
        if not callable( dumper ):
            dumper = print

        dumper( yaml.dump( self ) )
        return

    @staticmethod
    def tryToResolve( config, key, value ):
        """ This resolves values that contain ${ var }
        """
        try:
            if '${' in value:
                config[ key ] = Template( text = value ).render( **config )

        except Exception:
            # When an exception occurs we don't change it, we leave it as-is
            pass

        return

    @staticmethod
    def _buildSqlalchemyUrl( database ):
        """ This builds url for SQLALCHEMY_DATABASE_URI or BINDS for SqlAlchemy
        """
        engine = database.get( 'ENGINE', 'sqlite' )     # Some defaults for testing
        schema = database.get( 'SCHEMA', ':memory:' )
        username = database.get( 'USERNAME', '' )
        password = database.get( 'PASSWORD', '' )
        host = database.get( 'HOST' )
        port = database.get( 'PORT' )
        if isinstance( host, str ):
            hostname = f"{ host }:{ port }" if isinstance( port, int ) else host

        else:
            hostname = None

        if engine.startswith( 'sqlite' ):
            uri = f'{engine}:///{schema}'

        else:
            # All others are handled like this, mysql/mariadb is what we use currently
            if isinstance( hostname, str ):
                hostname += '/'

            else:
                hostname = ''

            uri = f"{engine}://{username}:{password}@{hostname}{schema}"

        return uri

    @staticmethod
    def _flatten( data: any ):
        """ This resolves __inherit__
        """
        if isinstance( data, dict ):
            result = {}
            for key, value in data.items():
                if key == '__inherit__':
                    for k1, v1 in value.items():
                        if k1 not in data:
                            result[ k1 ] = v1

                else:
                    if isinstance( value, dict ):
                        result[ key ] = Config._flatten( value )

                    elif isinstance( value, list ):
                        arr = []
                        for item in value:
                            if isinstance( item, dict ):
                                arr.append( Config._flatten( item ) )

                            else:
                                arr.append( item )

                        result[ key ] = arr

                    else:
                        result[ key ] = value

        elif isinstance( data, list ):
            result = []
            for item in data:
                result.append( Config._flatten( item ) )

        else:
            result = data

        return result
