import sqlite3


session = sqlite3.connect("file:mem1?cache=shared&mode=memory", uri=True, check_same_thread=False)


print( session )
print( session.execute( ".tables" ))

result = session.execute( "select * from user" )
print( result )
for row in result:
    print( row )




