class BackendError( Exception ):
    def __init__(self, *args: object, error_code: int = 500, problem: str = None, solution: str = None) -> None:
        super().__init__(*args)
        self._problem = problem
        self._solution = solution
        self._error_code = error_code

    @property
    def problem( self ):
        return self._problem

    @property
    def solution( self ):
        return self._solution

    @property
    def error_code( self ):
        return self._error_code