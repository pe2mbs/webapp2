import webapp2.api as API
from sqlalchemy.exc import IntegrityError, InternalError, ProgrammingError
from datetime import datetime, time, date
from sqlalchemy import text
import pymysql.err


class NotAnWebappSchema( Exception ):
    pass


def getCurrentSchema():
    return API.app.config[ 'DATABASE' ][ 'SCHEMA' ]


def listSchemas( schema = None, all = False, exclude = None, remote = None ):
    if remote is None:
        data = API.db.session.connection().execute( text( "SHOW DATABASES" ) )

    else:
        data = remote.session.connection().execute( text( "SHOW DATABASES" ) )

    if schema is None:
        current_schema = getCurrentSchema()

    else:
        current_schema = schema

    if not isinstance( exclude, ( tuple, list ) ):
        exclude = []

    result = []
    for rec, *args in data:
        if all or rec.startswith( current_schema ) or rec == current_schema:
            if rec in exclude:
                continue

            result.append( rec )

    return result


def listTables( schema = None, exclude = None, remote = None ):
    if schema is None:
        schema = getCurrentSchema()

    if exclude is None:
        exclude = []

    if remote is None:
        data = API.db.session.connection().execute( text( "SHOW TABLES FROM {}".format( schema ) ) )


    else:
        data = remote.session.connection().execute( text( "SHOW TABLES FROM {}".format( schema ) ) )

    result = []
    for rec,*args in data:
        if rec not in exclude:
            result.append( rec )

    return result


def getCurrentVersion( schema = None, remote = None):
    version_num = ''
    if schema is None:
        schema = getCurrentSchema()

    try:
        if remote is None:
            data = API.db.session.connection().execute( text( f"SELECT version_num FROM {schema}.alembic_version" ) )

        else:
            data = remote.session.connection().execute( text( f"SELECT version_num FROM {schema}.alembic_version" ) )

        if data.rowcount > 0:
            version_num = data.fetchone()[0]


    except pymysql.err.ProgrammingError as exc:
        API.logger.error( f"pymysql.err.ProgrammingError: {exc.args}")
        if 1146 == exc.args[0] and 'alembic_version' in exc.args[1]:
            raise NotAnWebappSchema( repr( exc.args ) )

        API.logger.exception(f"pymysql.err.ProgrammingErrorRetrieving version_num from {schema}.alembic_version: {repr(exc.args)}" )
        return None

    except ProgrammingError as exc:
        API.logger.error(f"ProgrammingError: {exc.args}")
        if 1146 == exc.orig.args[0] and 'alembic_version' in exc.orig.args[1]:
            raise NotAnWebappSchema( repr( exc.orig.args ) )

        API.logger.exception(f"ProgrammingError: Retrieving version_num from {schema}.alembic_version: {repr(exc.args)}")
        return None

    except Exception:
        API.logger.exception( f"MASTER: Retrieving version_num from {schema}.alembic_version" )
        return None

    return version_num


def copySchema( oSchema, nSchema ):
    connection = API.db.session.connection()
    connection.execute( text( "DROP DATABASE IF EXISTS {}".format( nSchema ) ) )
    connection.execute( text( "CREATE DATABASE {}".format( nSchema ) ) )

    for table in listTables( oSchema ):
        cmd = "CREATE TABLE {nSchema}.{table} SELECT * FROM {oSchema}.{table}".format( oSchema = oSchema,
                                                                                       nSchema = nSchema,
                                                                                       table = table )
        connection.execute( text( cmd ) )

    return

def mapFieldLists( connection, destination, source ):
    def Diff( li1, li2 ):
        return ( list( list( set( li1 ) - set( li2 ) ) + list( set( li2 ) - set( li1 ) ) ) )

    def Common( li1, li2 ):
        return list( set( li1 ).intersection( li2 ) )

    def GetFieldList( table_schema ):
        result = connection.execute( text( "SHOW FULL COLUMNS FROM {};".format( table_schema ) ) )
        fieldList = [ ]
        fieldData = {}
        for field, field_type, _, field_null, field_index, *field_options in result:
            fieldList.append( field )
            field_type, *field_type1 = field_type.split('(')
            field_len = 0
            if len( field_type1 ) > 0:
                field_len = int( field_type1[0].split(')')[0] )

            fieldData[ field ] = {
                'type': field_type,
                'length': field_len,
                'null': field_null,
                'index': field_index,
                'option': field_options
            }

        return fieldData, list( sorted( fieldList ) )

    destInfo, destFields = GetFieldList( destination )
    srcInfo, srcFields = GetFieldList( source )
    if len( Diff( destFields, srcFields ) ) > 0:
        srcAppendFields = [ ]
        destAppendFields = [ ]
        commonFields = Common( destFields,srcFields )
        # Get fields from destination not in common, therefor we need default values
        for field in Diff( commonFields, destFields ):
            fieldData = destInfo[ field ]
            if fieldData[ 'null' ].lower() == 'no':
                if fieldData[ 'type' ].lower() in ( 'char', 'varchar', 'text', 'longtext', 'blob' ):
                    srcAppendFields.append( '""' )
                    destAppendFields.append( field )

                elif fieldData[ 'type' ].lower() in ( 'int', 'long', 'tinyint' ):
                    srcAppendFields.append( '0' )
                    destAppendFields.append( field )

                elif fieldData[ 'type' ].lower() == 'datetime':
                    srcAppendFields.append( datetime.utcnow() )
                    destAppendFields.append( field )

                elif fieldData[ 'type' ].lower() == 'date':
                    srcAppendFields.append( datetime.utcnow().date() )
                    destAppendFields.append( field )

                elif fieldData[ 'type' ].lower() == 'time':
                    srcAppendFields.append( datetime.utcnow().time() )
                    destAppendFields.append( field )

        srcFields = commonFields + srcAppendFields
        destFields = commonFields + destAppendFields

    return ", ".join( destFields ), ", ".join( srcFields )


def copySchema2( destSchema, srcSchema, clear, ignore_errors = False ):
    def reccount( connection, schema_table ):
        try:
            for rec in connection.execute( text( "select count(*) from {};".format( schema_table ) ) ):
                return rec[ 0 ]

        except Exception:
            pass

        return 0

    INSERT_INTO = "INSERT INTO {destSchema}.{table} ( {destFields} ) SELECT {srcFields} FROM {srcSchema}.{table};"
    resultTable = {}
    errorTable = {}
    connection = API.db.session.connection()
    API.app.logger.info( "Begin work" )
    connection.execute( text( "SET FOREIGN_KEY_CHECKS=0;" ) )
    connection.execute( text( "SET SESSION sql_mode='ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION'" ) )
    connection.execute( text( "BEGIN WORK;" ) )
    total = 0
    errors = 0
    table = ''
    skipped = []
    try:
        for table in listTables( destSchema, exclude = [ 'alembic_version' ] ):
            # Now map the two field lists
            try:
                destFieldList, srcFieldList = mapFieldLists( connection,
                                                             "{}.{};".format( destSchema, table ),
                                                             "{}.{};".format( srcSchema, table ) )
            except ProgrammingError as exc:
                if ignore_errors:
                    API.app.logger.error( "Skipping '{}' table".format( table ) )
                    skipped.append( (table, exc) )
                    continue

                raise

            except Exception as exc:
                print( exc )
                raise

            if clear:
                API.app.logger.info( "Clear '{}' table".format( table ) )
                connection.execute( text( "DELETE FROM {}.{};".format( destSchema, table ) ) )

            print( "Copying table '{}'".format( table ) )
            cmd = INSERT_INTO.format( destSchema = destSchema, destFields = destFieldList,
                                      srcSchema = srcSchema, srcFields = srcFieldList,
                                      table = table )

            count = 0
            try:
                connection.execute( text( cmd ) )
                count = reccount( connection, "{}.{};".format( destSchema, table ) )
                resultTable[ table ] = count
                API.app.logger.info( "{} Inserted into '{}' table".format( count, table ) )
                total += count

            except ProgrammingError as exc:
                API.app.logger.error( "Exception on table {}: {} ".format( table, exc ) )
                if ignore_errors:
                    if count == 0:
                        count = reccount( connection,"{}.{};".format( srcSchema,table ) )

                    errors += count
                    errorTable[ table ] = count
                    API.app.logger.error( "Skipping '{}' table".format( table ) )
                    skipped.append( (table, exc) )

                else:
                    raise

            except IntegrityError as exc:
                API.app.logger.error( "Exception on table {}: {} ".format( table,exc ) )
                if ignore_errors:
                    if count == 0:
                        count = reccount( connection,"{}.{};".format( srcSchema,table ) )

                    errors += count
                    API.app.logger.error( "InternalError {} not inserted into '{}' table".format( count,table ) )
                    errorTable[ table ] = count
                    skipped.append( (table, exc) )

                else:
                    raise

            except InternalError as exc:
                API.app.logger.error( "Exception on table {}: {} ".format( table,exc ) )
                if ignore_errors:
                    if count == 0:
                        count = reccount( connection,"{}.{};".format( srcSchema,table ) )

                    errors += count
                    API.app.logger.error( "InternalError {} not inserted into '{}' table".format( count,table ) )
                    errorTable[ table ] = count
                    skipped.append( (table, exc) )
                else:
                    raise

            except Exception as exc:
                API.app.logger.error( exc )
                API.app.logger.error( "{} {} not inserted into '{}' table".format( type(exc), count, table ) )
                skipped.append( (table, exc) )

        API.app.logger.info( "Commit work" )
        connection.execute( text( "COMMIT WORK;" ) )
        API.app.logger.info( "{} records copied".format( total ) )

    except ( IntegrityError, InternalError, ProgrammingError ) as exc:
        if exc.orig is not None:
            API.app.logger.error( "{} in table {}".format( exc.orig.args[ 1 ], table ) )

        else:
            API.app.logger.error( "{} in table {}".format( exc.args[ 0 ],table ) )

        API.app.logger.info( "Rollback work" )
        connection.execute( text( "ROLLBACK WORK;" ) )

    except Exception as exc:
        API.app.logger.info( "Rollback work" )
        API.app.logger.error( exc )
        connection.execute( "ROLLBACK WORK;" )

    connection.execute( text( "SET FOREIGN_KEY_CHECKS=1;" ) )
    return resultTable, errorTable, total, errors, skipped
