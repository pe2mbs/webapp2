import webapp.api as API


__docformat__ = 'epytext'


class DbBaseMemory( object ):
    """This is the base class for the database models as a memory only object.
    After retrieving the record(s) the database session is released.

    The usage is as following, a class is defined with two static properties:

    class SomeTableModelMemory( DbBaseMemory ):
        __model_cls__       = SomeTableModel
        __tablename__       = 'sometable'

    __model_cls__ is the actual Sqlalchemy memory model.
    __tablename__ is the actial table name.

    @note: The actual database model must contain the attribute '__field_list__' with the fieldnames that are in the model.

    Example

    class User( Model ):
        __tablename__       = 'user'
        __field_list__      = [ 'U_NAME', ... , 'U_R_ID', ... ]
        ...

    class UserMemory( DbBaseMemory ):
        __tablename__       = 'user'
        __model_cls__       = User
        ...


    # Obtain the record for user 'johndoe'
    rec = UserMemory.fetch( User.U_NAME == 'johndoe' )

    # Obtain all records fro role 1
    recs = UserMemory.fetch_many( User.U_R_ID == 1 )

    """
    __model_cls__   = None

    def __init__( self, record = None, *args, **kwargs ):
        """Constructor for the memory model

        @type record:       Model
        @param record:      The object containing a Sqlalchemy record model
        @param args:        not used
        @type kwargs:       dict
        @param kwargs:      When the field names are passed as keyword arguments the memory model is initialized with those.
        """
        self.clear()
        self.set( record, **kwargs )
        return

    def clear( self ):
        """Clears the field varialbes of the memory model object

        @return:            None
        """
        for field in self.__model_cls__.__field_list__:
            setattr( self, field, None )

        return

    def set( self, record = None, **kwargs ):
        """Set the field varialbes of the memory model object from an actual Sqlalchemy Model object

        Via keyword arguments the field varialbes may be overridden, or extra attributes can be stored.

        @type record:       Model
        @param record:      The object containing a Sqlalchemy record model
        @type kwargs:       dict
        @param kwargs:      When the field names are passed as keyword arguments the memory model is initialized with those.

        @return:            None
        """
        if isinstance( record, self.__model_cls__ ):
            # Walk through all the fields of the actual Model
            for field in self.__model_cls__.__field_list__:
                if field not in kwargs.keys():
                    setattr( self, field, getattr( record, field ) )

        for key, value in kwargs.items():
            setattr( self, key, value )

        return

    @classmethod
    def fetch( cls, *args, **kwargs ):
        """This fetches one record from the actual database and returns the memory model of the record.

        @note: Sqlalchmy orm exceptions may be raised

        @param args:        Sqlalchemy filter conditions
        @param kwargs:      not used

        @rtype:             MemoryModel
        @return:            class instance with the record data.
        """
        query = API.db.session.query( cls.__model_cls__ )
        for condition in args:
            query = query.filter( condition )

        return cls( query.one() )

    @classmethod
    def fetch_many( cls, *args, **kwargs ):
        """This fetches record(s) from the actual database and returns a list of memory class models of the record.

        @note: The return list may be empty when no result is found.

        @param args:        Sqlalchemy filter conditions
        @keyword order_by:  When provided it must contain a valid field name, on this field sorting is perfromed.
                            default sorting order is 'asc'
        @keyword order_dir: optional order direction may be 'asc' or 'desc'

        @rtype:             list
        @return:            empty list or list with memory class models
        """
        query = API.db.session.query( cls.__model_cls__ )
        for condition in args:
            query = query.filter( condition )

        if 'order_by' in kwargs:
            query = query.order_by( kwargs[ 'order_by' ] + " " + kwargs.get( 'order_dir', 'asc' ) )

        return [ cls( record ) for record in query.all() ]

    def __repr__( self ):
        """Returns a string with the contents ob the memory object

        @rtype:             string
        @return:            the contents ob the memory object
        """
        return "<<{} {}>".format( self.__class__.__name__, ", ".join(
                [ "{} = {}".format( field, getattr( self, field ) ) for field in self.__model_cls__.__field_list__ ]
            ) )

    def __str__( self ):
        """Returns a string with the contents ob the memory object

        @rtype:             string
        @return:            the contents ob the memory object
        """
        return self.__repr__()

    @property
    def dictionary( self ):
        """Provides the fields with their values as a dictionary

        @rtype:             dictionary
        @return:            fields with their values
        """
        return { field: getattr( self, field ) for field in self.__model_cls__.__field_list__ }
