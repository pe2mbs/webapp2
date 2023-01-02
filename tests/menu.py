

TEST_ADD_START1 = {
    'caption': 'Start Menu item #1',
    'id': 0,
    'access': 'user',
    'before': '*',
    'after': '*',
    'route': '/route'
}

TEST_ADD_START2 = {
    'caption': 'Start Menu item #2',
    'id': 0,
    'access': 'role',
    'before': '*',
    'after': None,
    'route': '/route'
}

TEST_ADD_END1 = {
    'caption': 'End Menu item #1',
    'id': 0,
    'access': 'admin',
    'before': None,
    'after': None,
    'route': '/route'
}

TEST_ADD_END2 = {
    'caption': 'End Menu item #2',
    'id': 0,
    'access': '*',
    'before': None,
    'after': '*',
    'route': '/route'
}

TEST_INSERT1 = {
    'caption': 'Insert Menu item #1',
    'id': 0,
    'access': '*',
    'before': None,
    'after': 'Start Menu item #1',
    'route': '/route'
}

TEST_INSERT2 = {
    'caption': 'Insert Menu item #2',
    'id': 0,
    'access': 'user',
    'before': 'Insert Menu item #1',
    'after': None,
    'route': '/route'
}

TEST_INSERT3 = {
    'caption': 'Insert Menu item #3',
    'id': 0,
    'access': 'role',
    'before': 'Start Menu item #1',
    'after': '*',
    'route': '/route'
}

TEST_SUB_MENU_INSERT = {
    'caption': 'Sub Menu item #1',
    'id': 0,
    'access': '*',
    'before': 'Insert Menu item #2',
    'after': 'Start Menu item #1',
    'children': [
        {
            'caption': 'Test sub menu #1',
            'id': 0,
            'access': '*',
            'route': '/route'
        },
        {
            'caption': 'Test sub menu #2',
            'id': 0,
            'after': 'Test sub menu #1',
            'access': 'admin',
            'route': '/route'
        },
        {
            'caption': 'Test sub menu #3',
            'id': 0,
            'access': '*',
            'after': 'Test sub menu #2',
            'children': [
                TEST_ADD_START1,
                TEST_INSERT1,
                TEST_INSERT2,
                TEST_INSERT3
            ]
        },

    ]
}

NESTED_ITEM = ( {   'caption': 'Test menu #2',
                    'id': 0,
                    'access': 'admin',
                    'route': '/route' }, 'Sub Menu item #1', 'Test sub menu #3' )


#
#   before          |  after            | result
#   ----------------+-------------------+----------------------------------------
#   None            | None              | Add at the end
#   None            | '*'               | Add at the end
#   '*'             | None              | Add at the beginning
#   '*'             | '*'               | Add at the beginning
#



def test_first_and_last():
    root = WebappMenu()
    root.register( TEST_ADD_START1 )
    root.register( TEST_ADD_END1 )
    root.dump()
    return


def test_first_and_last_twice():
    root = WebappMenu()
    root.register( TEST_ADD_START1 )
    root.register( TEST_ADD_END1 )
    root.register( TEST_ADD_START2 )
    root.register( TEST_ADD_END2 )
    root.dump()
    return


def test_adding_list():
    root = WebappMenu()
    items = [
        TEST_ADD_END2,
        TEST_ADD_END1,
        TEST_ADD_START2,
        TEST_ADD_START1,
    ]
    root.register( items )
    root.dump()
    return


def test_insert():
    root = WebappMenu()
    items = [
        TEST_ADD_END1,
        TEST_ADD_START1,
    ]
    root.register( items )
    root.register( TEST_INSERT1 )
    root.register( TEST_INSERT2 )
    root.register( TEST_INSERT3 )
    # root.dump()
    root.register( TEST_SUB_MENU_INSERT )
    # root.dump()
    root.register( *NESTED_ITEM )
    # root.dump()
    root.sortMenu()
    root.dump( ( 'user', 'role', 'admin' ) )



    return


if __name__ == '__main__':
    # test_first_and_last()
    # test_first_and_last_twice()
    # test_adding_list()
    test_insert()
