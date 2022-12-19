import os


def main():
    result = os.system( 'finger -l mbertens' )
    attributes = [
        'Login',
        'Name',
        'Directory',
        'Shell',
        'Office',
        'Home Phone'
    ]




    print( result )


    return

if __name__ == '__main__':
    main()

