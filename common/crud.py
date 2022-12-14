import time
from typing import Any, List, Optional, Union, ForwardRef
from flask import request, Response, Request
from pydantic import BaseModel
import traceback
from sqlalchemy import and_, not_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from flask.globals import LocalProxy
import posixpath
from testprocess.util.decorators import with_valid_input
import webapp2.api as API
from flask_jwt_extended import ( verify_jwt_in_request, get_jwt_identity )
from webapp2.common.error import BackendError
from webapp2.common.exceptions import *
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Query
from webapp2.common.util import getNestedAttr
from webapp2.api import cache


def render_query(statement, dialect=None):
    """
    Generate an SQL expression string with bound parameters rendered inline
    for the given SQLAlchemy statement.
    WARNING: This method of escaping is insecure, incomplete, and for debugging
    purposes only. Executing SQL statements with inline-rendered user values is
    extremely insecure.
    Based on http://stackoverflow.com/questions/5631078/sqlalchemy-print-the-actual-query
    """
    if isinstance(statement, Query):
        if dialect is None:
            dialect = statement.session.bind.dialect

        statement = statement.statement

    elif dialect is None:
        dialect = statement.bind.dialect

    class LiteralCompiler(dialect.statement_compiler):

        def visit_bindparam(self, bindparam, within_columns_clause=False,
                            literal_binds=False, **kwargs):
            return self.render_literal_value(bindparam.value, bindparam.type)

        def render_array_value(self, val, item_type):
            if isinstance(val, list):
                return "{%s}" % ",".join([self.render_array_value(x, item_type) for x in val])

            return self.render_literal_value(val, item_type)

        def render_literal_value(self, value, type_):
            if isinstance(value, int):
                return str(value)

            elif isinstance(value, (str, date, datetime, timedelta)):
                return "'%s'" % str(value).replace("'", "''")

            elif isinstance(value, list):
                return "'{%s}'" % (",".join([self.render_array_value(x, type_.item_type) for x in value]))

            return super(LiteralCompiler, self).render_literal_value(value, type_)

    return LiteralCompiler(dialect, statement).process(statement)


def getDictFromRequest( request ):
    try:
        data = request.json

    except Exception:
        data = None

    if data is None:
        data = dict( request.args )

    if data is None:
        raise InvalidRequestExecption()

    return data


class Sorting(BaseModel):
    column: str
    direction: str

class BaseFilter(BaseModel):
    operator: str
    column: str
    value: Union[tuple, list, str]


# required for self referencing models
TableFilter = ForwardRef('TableFilter')
class TableFilter(BaseModel):
    table: str
    foreignKey: str
    filters: List[BaseFilter]
    childFilters: List[TableFilter] = []

TableFilter.update_forward_refs()

class RecordLock( object ):
    def __init__( self, table, record_id ):
        self._table = table
        self._record_id = record_id
        self._data = None
        self._id = None
        return

    @property
    def data( self ):
        return self._data

    @property
    def id( self ):
        if isinstance( self._data, dict ) and self._record_id in self._data:
            return self._data[ self._record_id ]

        else:
            API.logger.debug( "ID: {} => {}".format( self._id, self._data ) )

        return self._id

    def removeId( self ):
        if isinstance( self._data, dict ):
            if self._record_id in self._data:
                del self._data[ self._record_id ]

        return

    @property
    def user( self ):
        try:
            user_info = get_jwt_identity()
            if user_info in ( None, '', 0 ):
                user_info = 'single.user'

        except:
            user_info = 'single.user'

        return user_info

    @classmethod
    def locked( cls, request, user = None ):
        from webapp2.common.locking.model import RecordLocks
        obj = cls()
        if user is None:
            user = obj.user

        obj._data = request
        try:
            if isinstance( request, int ):
                obj._id = request

            elif isinstance( request, LocalProxy ):
                obj._data = getDictFromRequest( request )
                if obj._record_id in obj._data:
                    obj._id = obj._data[ obj._record_id ]

                else:   # new record ?
                    raise NoResultFound

            else:
                raise InvalidRequestExecption( "Unknown {} object to get record information".format( request ) )

            API.logger.debug( "Is record lockec {}:{} not for {}".format( obj._table, obj._id, user ) )
            rec = API.db.session.query( RecordLocks ). \
                                 filter( and_( RecordLocks.L_TABLE == obj._table,
                                               RecordLocks.L_RECORD_ID == obj._id,
                                               RecordLocks.L_USER != user ) ).one()
            API.logger.warning( "Record is locked by {}".format( rec.L_USER ) )
            raise RecordLockedException( user = rec.L_USER )

        except NoResultFound:
            API.logger.debug( "Record NOT locked" )
            pass

        return obj

    @classmethod
    def unlock( cls, request, user = None ):
        from webapp2.common.locking.model import RecordLocks
        data = getDictFromRequest( request )
        obj = cls()
        if user is None:
            user = obj.user

        if user is None:
            user = 'single.user'

        API.logger.info( "request: {}".format( request ) )
        if isinstance( request, dict ):
            obj._data = request

        elif isinstance( request, Request ):
            obj._data = request.json

        elif isinstance( request, LocalProxy ):
            obj._data = getDictFromRequest( request )

        API.logger.debug( "unlock: {}".format( obj._data ) )
        if isinstance( obj._data, dict ):
            obj._id = data.get( obj._record_id, None )
            if obj._id is None:
                API.logger.error( 'Could not retrieve {} from record'.format( obj._record_id ) )
                return { 'result': 'OK', 'table': obj._table, 'id': obj._id }

        else:
            API.logger.error( 'data not a record'.format( obj._record_id ) )
            return { 'result': 'OK', 'table': obj._table, 'id': obj._id }

        try:
            API.logger.debug( "Unlocking {}:{} for {}".format( obj._table, obj._id, user ) )
            API.db.session.query( RecordLocks ).filter( and_( RecordLocks.L_TABLE == obj._table,
                                                               RecordLocks.L_RECORD_ID == obj._id,
                                                               RecordLocks.L_USER == user ) ).delete()
            API.db.session.commit()
            API.logger.debug( "Unlocking done" )

        except NoResultFound:
            API.logger.debug( "lock record not found for {}:{} by {}".format( obj._table, obj._id, user ) )

        return { 'result': 'OK', 'table': obj._table, 'id': obj._id }

    @classmethod
    def lock( cls, request, user = None ):
        from webapp2.common.locking.model import RecordLocks
        data = getDictFromRequest( request )
        obj = cls()
        if user is None:
            user = obj.user

        if user is None:
            user = 'single.user'

        API.logger.debug( "lock: {}".format( data ) )
        obj._id = data[ obj._record_id ]
        API.logger.debug( "Locking {}:{} for {}".format( obj._table, obj._id, user ) )
        API.db.session.add( RecordLocks( L_USER = user,
                                         L_RECORD_ID = obj._id,
                                         L_TABLE = obj._table,
                                         L_START_DATE = datetime.utcnow() ) )
        API.db.session.commit()
        API.logger.debug( "Locking done" )
        return { 'result': 'OK', 'table': obj._table, 'id': obj._id }


class CrudInterface( object ):
    _model_cls = None
    _lock_cls = None
    _schema_cls = None
    _schema_list_cls = None
    _lock = True
    _uri = ''
    _relations = []
    _delayed = False

    def __init__( self, blue_print, use_jwt = False ):
        self._blue_print = blue_print
        self.registerRoute( 'list/<id>/<value>', self.filteredList, methods = [ 'GET' ] )
        self.registerRoute( 'pagedlist', self.pagedList, methods = [ 'POST' ] )
        self.registerRoute( 'list', self.recordList, methods = [ 'GET' ] )
        self.registerRoute( 'new', self.newRecord, methods = [ 'POST' ] )
        self.registerRoute( 'primarykey', self.primaryKey, methods = [ 'GET' ] )
        self.registerRoute( 'get', self.recordGet, methods = [ 'GET' ] )
        self.registerRoute( 'get/<int:id>', self.recordGetId, methods = [ 'GET' ] )
        self.registerRoute( 'getvalue', self.recordGetColValue, methods = [ 'POST' ] )
        self.registerRoute( '<int:id>', self.recordDelete, methods = [ 'DELETE' ] )
        self.registerRoute( 'put', self.recordPut, methods = [ 'POST' ] )
        self.registerRoute( 'update', self.recordPatch, methods = [ 'POST' ] )
        self.registerRoute( 'select', self.selectList, methods = [ 'POST' ] )
        self.registerRoute( 'lock', self.lock, methods = [ 'POST' ] )
        self.registerRoute( 'unlock', self.unlock, methods = [ 'POST' ] )
        self.registerRoute( 'count', self.recordCount, methods=['GET'])
        self.__useJWT   = use_jwt
        return
    
    def __repr__( self ):
        return str(self._model_cls)

    @property
    def useJWT( self ):
        return self.__useJWT

    @useJWT.setter
    def useJWT( self, value ):
        self.__useJWT = value
        return

    def registerRoute( self, rule, function, endpoint = None, **options ):
        if not rule.startswith( '/' ):
            rule = posixpath.join( self._uri, rule )

        self._blue_print.add_url_rule( rule,
                                       endpoint,
                                       function,
                                       **options )
        return

    def checkAuthentication( self ):
        if self.__useJWT:
            verify_jwt_in_request()

        return

    def makeFilter( self, query, filter: Union[List[BaseFilter], List[dict]], childFilters: List[TableFilter] = [], model_cls = None ):
        if model_cls is None:
            model_cls = self._model_cls
        for item in filter:
            # TODO: can be removed once the filter is passed as a BaseFilter class
            if isinstance(item, dict):
                item = BaseFilter.parse_obj(item)

            operator = getattr( item, 'operator', None )
            if operator is None:
                continue

            column  = getattr( item, 'column', None )
            if isinstance( getattr( item, 'value' ), ( list, tuple ) ):
                value1, value2   = getattr( item, 'value', [ None, None ] )

            else:
                value1, value2 = getattr( item, 'value' ), None

            API.app.logger.debug( "Filter {} {} {} / {}".format( column, operator, value1, value2 ) )

            # if we have a nested relationship attribute, we split the column and
            # access the attribute via joins
            attributes = column.split(".")
            relatedClass = model_cls
            if len(attributes) > 1:
                for i in range(0, len(attributes) - 1):
                    relationship = getattr( relatedClass, attributes[i])
                    query = query.join(relationship)
                    relatedClass = relationship.mapper.class_

            if operator == 'EQ':
                # apply filter
                query = query.filter( getattr( relatedClass, attributes[-1] ) == value1)

            elif operator == '!EQ':
                query = query.filter( getattr( relatedClass, attributes[-1] ) != value1 )

            elif operator == 'GT':
                query = query.filter( getattr( relatedClass, attributes[-1] ) > value1 )

            elif operator == 'LE':
                query = query.filter( getattr( relatedClass, attributes[-1] ) < value1 )

            elif operator == 'GT|EQ':
                query = query.filter( getattr( relatedClass, attributes[-1] ) >= value1 )

            elif operator == 'LE|EQ':
                query = query.filter( getattr( relatedClass, attributes[-1] ) <= value1 )

            elif operator == 'EM':
                query = query.filter( getattr( relatedClass, attributes[-1] ) == "" )

            elif operator == '!EM':
                query = query.filter( getattr( relatedClass, attributes[-1] ) != "" )

            elif operator == 'CO':
                query = query.filter( getattr( relatedClass, attributes[-1] ).like( "%{}%".format( value1 ) ) )

            elif operator == '!CO':
                query = query.filter( not_( getattr( relatedClass, attributes[-1] ).contains( value1 ) ) )

            elif operator == 'BT': # Between
                query = query.filter( getattr( relatedClass, attributes[-1] ).between( value1, value2 ) )

            elif operator == 'SW': # Startswith
                query = query.filter( getattr( relatedClass, attributes[-1] ).like( "{}%".format( value1 ) ) )

            elif operator == 'EW': # Endswith
                query = query.filter( getattr( relatedClass, attributes[-1] ).like( "%{}".format( value1 ) ) )

        # process the filter for child records
        if len(childFilters) > 0:
            tables_dict = {table.__tablename__: table for table in API.db.Model.__subclasses__()}
        for childFilter in childFilters:
            try:
                # join with child table based on foreign key
                childTableClass = tables_dict[childFilter.table]
                foreignKey = childFilter.foreignKey
                query = query.join( childTableClass, and_(getattr(model_cls, model_cls.__field_list__[0]) == getattr(childTableClass, foreignKey)) )
                # apply filters for child table
                query = self.makeFilter( query, childFilter.filters, childFilter.childFilters, model_cls=childTableClass )
            except Exception as e:
                traceback.print_exc()
                API.logger.error("Child filter not working, reason: " + str(e))
        return query

    class PagedListBodyInput(BaseModel):
        filters: Optional[Union[List[BaseFilter], List[dict]]] = []
        pageIndex: int = 0
        pageSize: int = 1
        sorting: Optional[Sorting]
        cacheDeactivator: Optional[int]

    @with_valid_input(body=PagedListBodyInput)
    @cache.memoize(timeout=150)
    def pagedList( self, body: PagedListBodyInput ):
        if body.cacheDeactivator != None:
            self.deleteCache()
        self.checkAuthentication()
        t1 = time.time()
        if self.__useJWT:
            user_info = get_jwt_identity()
            API.app.logger.debug( 'POST: {}/pagedlist by {}'.format( self._uri, user_info ) )
        filter = body.filters
        API.app.logger.debug( "Filter {}".format( filter ) )
        query = self.makeFilter( API.db.session.query( self._model_cls ), filter )
        API.app.logger.debug( "SQL-QUERY : {}".format( render_query( query ) ) )
        recCount = query.count()
        API.app.logger.debug( "SQL-QUERY count {}".format( recCount ) )
        sorting = body.sorting
        if isinstance( sorting, Sorting ):
            column = sorting.column
            if column is not None:
                if sorting.direction == 'asc':
                    query = query.order_by( getNestedAttr( self._model_cls, column ) )
                else:
                    query = query.order_by( getNestedAttr( self._model_cls, column ).desc() )

        pageIndex = body.pageIndex
        pageSize = body.pageSize
        API.app.logger.debug( "SQL-QUERY limit {} / {}".format( pageIndex, pageSize ) )
        if ( ( pageIndex * pageSize ) > recCount ):
            pageIndex = 0

        query = query.limit( pageSize ).offset( pageIndex * pageSize )
        result:Response = self._schema_list_cls.jsonify( query.all() )
        API.app.logger.debug( "RESULT count {} => {}".format( recCount, result.json ) )
        result = jsonify(
            records = result.json,
            pageSize = pageSize,
            page = pageIndex,
            recordCount = recCount
        )
        if self._delayed and t1 + 1 > time.time():
            API.app.logger.debug( 'filteredList waiting: {}'.format( ( t1 + 1 ) - time.time() ) )
            time.sleep( ( t1 + 1 ) - time.time() )

        API.app.logger.debug( 'filteredList => {}'.format( result ) )
        return result

    def filteredList( self, id, value ):
        t1 = time.time()
        self.checkAuthentication()
        filter = { id: value }
        API.app.logger.debug( 'GET: {}/list/{}/{} by {}'.format( self._uri, id, value, self._lock_cls().user ) )
        recordList = API.db.session.query( self._model_cls ).filter_by( **filter ).all()
        result = self._schema_list_cls.jsonify( recordList )
        API.app.logger.debug( 'filteredList => count: {}'.format( len( recordList ) ) )
        if self._delayed and t1 + 1 > time.time():
            API.app.logger.debug( 'filteredList waiting: {}'.format( ( t1 + 1 ) - time.time() ) )
            time.sleep( ( t1 + 1 ) - time.time() )

        return result

    def recordList( self ):
        self.checkAuthentication()
        API.app.logger.debug( 'GET: {}/list by {}'.format( self._uri, self._lock_cls().user ) )
        recordList = API.db.session.query( self._model_cls ).all()
        result = self._schema_list_cls.jsonify( recordList )
        API.app.logger.debug( 'recordList => count: {}'.format( len( recordList ) ) )
        return result

    def primaryKey( self, **kwargs ):
        self.checkAuthentication()
        # get primary key of class
        primary_key = self._model_cls.__field_list__[ 0 ]
        result = jsonify( { "primaryKey": primary_key } )
        return result

    def newRecord( self, **kwargs ):
        self.checkAuthentication()
        locker = kwargs.get( 'locker', self._lock_cls.locked( request ) )
        API.app.logger.debug( 'POST: {}/new {} by {}'.format( self._uri, repr( locker.data), locker.user ) )
        locker.removeId()
        record = self.updateRecord( locker.data, self._model_cls(), locker.user )
        API.db.session.add( record )
        #API.db.session.commit()
        result = self._schema_cls.jsonify( record )
        result.headers["USER"] = locker.user
        #rec_id = getattr( record, self._model_cls.__field_list__[ 0 ] )
        #API.recordTracking.insert( self._model_cls.__tablename__,
        #                           rec_id,
        #                           record.dictionary,
        #                           locker.user )
        API.app.logger.debug( 'newRecord() => {0}'.format( record ) )
        # delete cache
        self.deleteCache()
        return result

    def recordGet( self, **kwargs ):
        self.checkAuthentication()
        locker = kwargs.get( 'locker', self._lock_cls.locked( request ) )
        API.app.logger.debug( 'GET: {}/get {} by {}'.format( self._uri, repr( locker.data ), locker.user ) )
        #record = self._model_cls.query.get( locker.id )
        try:
            query = API.db.session.query( self._model_cls )
            for column, value in locker.data.items():
                query = query.filter(getattr(self._model_cls, column) == value)

            record = query.one()
            result = self._schema_cls.jsonify( record )
        except Exception as exc:
            raise BackendError(exc, problem="Requested {} record does not exist in the database".format(str(self._model_cls)),
            solution="Ensure that you request an existing item")

        API.app.logger.debug( 'recordGet() => {0}'.format( result ) )
        return result

    def recordGetId( self, id, **kwargs ):
        self.checkAuthentication()
        locker = kwargs.get( 'locker', self._lock_cls.locked( int( id ) ) )
        API.app.logger.debug( 'GET: {}/get/{} by {}'.format( self._uri, locker.id, locker.user ) )
        try:
            record = self._model_cls.query.get( locker.id )
            result = self._schema_cls.jsonify( record )
        except Exception as exc:
            raise BackendError(exc, problem="{} record with id {} does not exist in the database".format(str(self._model_cls), id),
            solution="Ensure that you request an existing item")
        API.app.logger.debug( 'recordGetId() => {0}'.format( record ) )
        return result


    class GetColValueBodyInput(BaseModel):
        id: int
        column: str

    @with_valid_input(body=GetColValueBodyInput)
    @cache.memoize(200)
    def recordGetColValue( self, body: GetColValueBodyInput ):
        record = self._model_cls.query.get( body.id )
        API.app.logger.debug( 'Get {} value for {} record with id: {}'.format( body.column, self._model_cls, body.id ) )
        value = getattr(record, body.column, "")
        result = jsonify({"value": value})
        return result

    def recordDelete( self, id, **kwargs ):
        self.checkAuthentication()
        locker = kwargs.get( 'locker', self._lock_cls.locked( int( id ) ) )
        API.app.logger.debug( 'DELETE: {} {} by {}'.format( self._uri, locker.data, locker.user ) )
        record = self._model_cls.query.get( locker.id )
        #if self._lock:
        #recordData = record.dictionary
        #for relation in self._relations:
            # Now
        #    if 'delete' in relation.get( 'cascade' ):
        #        cascadeRecords = []
        #        for relRecord in getattr( record, relation.get( 'table', '' ) + '_relation' ):
        #            cascadeRecords.append( relRecord.dictionary )
        #        recordData[ relation.get( 'class', '' ) ] = cascadeRecords

        #API.recordTracking.delete( self._model_cls.__tablename__,
        #                           locker.id,
        #                           recordData,
        #                           locker.user )

        API.app.logger.debug( 'Deleting record: {}'.format( record ) )
        API.db.session.delete( record )
        #API.app.logger.debug( 'Commit delete' )
        message = ''
        result = True
        #try:
        #    API.db.session.commit()
        #    result = True

        #except IntegrityError:
        #    message = 'Could not delete due relations still exists'
        #    result = False

        API.app.logger.debug( 'recordDelete() => {} {}'.format( result, record ) )
        response = jsonify( ok = result, reason = message )
        response.headers["USER"] = locker.user
        self.deleteCache()
        return response

    def updateRecord( self, data: dict, record: any, user = None ):
        self.checkAuthentication()
        if isinstance( record, int ):
            record = API.db.session.query( self._model_cls ).get( record )

        elif isinstance( record, self._model_cls ):
            pass

        else:
            Exception( "Missing record ref" )

        # the .data was added after the merge from github into gitlab since
        # unmarshalresult objects have a data attribute containing the result
        result = self._schema_cls.load( self.beforeUpdate( data ) )
        # workaround to consider different Marshmallow versions
        if not isinstance(result, dict):
            result = result.data

        API.app.logger.debug( "{}".format( result ) )
        if len( result ) > 1:
            for field, value in result.items():
                API.app.logger.debug( "{} := '{}'".format( field, value ) )
                setattr( record, field, value )

        else:
            raise Exception( result )

        self.deleteCache()
        return self.beforeCommit( record )

    def beforeUpdate( self, data ):
        """before update hook (insert, update), when we need to alter the dictionary before we update the
        record class

        :param data:    dictionary with record fields and values
        :return:        dictionary with record fields and values (altered)
        """
        return data

    def beforeCommit( self, record ):
        """before commit hook (insert, update), when we need to change fields before committing the record
        to the database.

        :param record:  record modal class
        :return:        record modal class
        """
        return record

    def recordPut( self, **kwargs ):
        self.checkAuthentication()
        locker = kwargs.get( 'locker', self._lock_cls.locked( request ) )

        API.app.logger.debug( 'POST: {}/put {} by {}'.format( self._uri, repr( locker.data ), locker.user ) )
        record = self.updateRecord( locker.data, locker.id, locker.user )

        with API.db.session.no_autoflush:
            result = self._schema_cls.jsonify( record )
            result.headers["USER"] = locker.user
            API.app.logger.debug( 'recordPut() => {0}'.format( record ) )
            self.deleteCache()
            return result

    def recordPatch( self, **kwargs ):
        self.checkAuthentication()
        locker = kwargs.get( 'locker', self._lock_cls.locked( request ) )

        API.app.logger.debug( 'POST: {}/update {} by {}'.format( self._uri, repr( locker.data ), locker.user ) )
        record = self.updateRecord( locker.data, locker.id, locker.user )

        # the jsonification changes the dirty set of sqlalchemy
        with API.db.session.no_autoflush:
            result = self._schema_cls.jsonify( record )
            result.headers["USER"] = locker.user
            API.app.logger.debug( 'recordPatch() => {}'.format( record ) )
            self.deleteCache()
            return result

    class SelectListBodyInput(BaseModel):
        value: Optional[str]
        label: Optional[str]
        filter: Optional[Union[List[BaseFilter], List[dict]]]
        initial: Optional[Any]
        final: Optional[Any]
        childFilters: Optional[List[TableFilter]]
        pageIndex: Optional[int] # optional for paged version
        pageSize: Optional[int] # optional for paged version
        firstItem: Optional[int] # optional list item to be at the top

        def __repr__(self):
            return f"<SelectListBodyInput {self.label} => {self.value} filter {self.filter} \
            | {self.initial}, {self.final} child-filters {self.childFilters} \
            pageIndex: {self.pageIndex} pageSize: {self.pageSize} firstItem: {self.firstItem}>"

    @with_valid_input(body=SelectListBodyInput)
    @cache.memoize(150)
    def selectList( self, body: SelectListBodyInput ):
        name_field = self._model_cls.__field_list__[ 1 ]
        for fld in self._model_cls.__field_list__:
            if fld.endswith( 'NAME' ):
                name_field = fld
                break

        self.checkAuthentication()
        # data = getDictFromRequest( request )
        API.app.logger.info( 'GET {}/select: {} by {}'.format( self._uri, str(body) , self._lock_cls().user ) )

        # TODO: here, we explicitly assume that a post request is sent with params and filter
        value = body.value if body.value != None else self._model_cls.__field_list__[ 0 ] # primary key
        label = body.label if body.label != None else name_field  # first field name
        if isinstance( body.filter, dict ):
            filter = body.filter

        elif isinstance( body.filter, list ):
            filter = body.filter

        else:
            filter = []

        childFilters = []
        if body.childFilters != None:
            # TODO: add decorator to all crud methods
            for childFilter in body.childFilters:
                childFilters.append(TableFilter.parse_obj(childFilter))

        # apply specified filter on the query
        query = self.makeFilter( API.db.session.query( self._model_cls ), filter, childFilters=childFilters )

        pivotItem = None
        if body.firstItem not in (None, 0) and body.pageIndex == 0:
            try:
                pivotItem = query.filter( getattr( self._model_cls, value ) == body.firstItem ).one()
            except Exception as e:
                pass

        # TODO if label contains comma, split --> list
        # ' '.join( [ getattr( record, l ) for l in labels ] )
        totalItems = query.count()
        labels = label.split(',')
        query = query.order_by( getattr( self._model_cls, labels[0] ) )
        if body.pageIndex is not None and body.pageSize is not None:
            query = query.limit( body.pageSize ).offset( body.pageIndex * body.pageSize )
        result = [ { 'value': getattr( record, value ),
                     'label': ' '.join( [ str(getattr( record, l )) for l in labels ] ) }
                                for record in query.all() if getattr( record, value ) != body.firstItem
        ]
        if pivotItem is not None:
            result = [{'value': getattr( pivotItem, value ), 'label': ' '.join( [ str(getattr( pivotItem, l )) for l in labels ] )}] + result

        API.app.logger.debug( 'selectList => count: {}'.format( len( result ) ) )
        # API.app.logger.debug( 'selectList => result: {}'.format( result ) )
        if body.pageIndex is not None and body.pageSize is not None:
            return jsonify(  { "itemList": result, "totalItems": totalItems } )
        return jsonify( result )
    
    def deleteCache( self ):
        cache.delete_memoized(self.recordGetColValue)
        cache.delete_memoized(self.pagedList)
        cache.delete_memoized(self.selectList)

    def recordCount( self ):
        return jsonify( recordCount = API.db.session.query( self._model_cls ).count() )

    def lock( self ):
        if self._lock:
            self.checkAuthentication()
            return jsonify( self._lock_cls.lock( request ) )

        return ""

    def unlock( self ):
        if self._lock:
            self.checkAuthentication()
            return jsonify( self._lock_cls.unlock( request ) )

        return ""
