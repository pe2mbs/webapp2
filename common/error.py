from typing import List, Optional, Any, Union
from flask import Response, abort
from pydantic import BaseModel, ValidationError


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

class ErrorDescription (BaseModel):
    code: int
    message: str
    category: str
    details: Optional[Any] # Schema depends on category.


def list_to_jsonpath ( parts: List[Union[str,int]] ) -> str :
    """
    Converts a list of parts into a simplified JSON Path expression.
    Example:  ('processes',2,'flag')  -->  "$['processes'][2]['flag']"
    """
    fullpath = "$"
    for p in parts:
        if type(p) == str :
            fullpath += "['" + p + "']"
        else :
            fullpath += "[" + str(p) + "]"
    return fullpath


def build_error (
    status_code:int, problem:str, solution:str, category:str, details:Optional[Any]=None
) :
    """
    Build a generic error that is not specialized for any case.
    """
    error_desc = ErrorDescription(
        code=status_code,
        message=( problem + " " + solution ),
        category=category,
        details=details
    )
    return Response(
        response=error_desc.json(by_alias=False),
        status=status_code,
        mimetype='application/json'
    )

def abort_with_input_error ( validation_error:ValidationError ) :
    """
    Validation errors that reference invalid input delivered to endpoints.
    """
    problem = "Invalid input structure was sent to the endpoint."
    solution = "Compare input with accepted JSON-Schemas."
    errorResponse = build_error(
        status_code=400, problem=problem, solution=solution, category="input",
        details=[
            "{} : {} ({})".format( list_to_jsonpath(entry["loc"]), entry["msg"], entry["type"] )
            for entry in validation_error.errors()
        ]
    )
    return abort(errorResponse)


def abort_with_output_error ( validation_error:ValidationError ) :
    """
    Validation errors that reference invalid output delivered from the endpoints.
    """
    problem = "Invalid output structure was sent from the endpoint."
    solution = "Notify the backend developers."
    errorResponse = build_error(
        status_code=401, problem=problem, solution=solution, category="output",
        details=[
            "{} : {} ({})".format( list_to_jsonpath(entry["loc"]), entry["msg"], entry["type"] )
            for entry in validation_error.errors()
        ]
    )
    return abort(errorResponse)


def abort_with_error ( error: Exception, problem: str, solution: str, status_code: int = 500 ) :
    """
    General errors
    """
    errorResponse = build_error(
        status_code=status_code, problem=problem, solution=solution, category="server",
        details=[str(error)]
    )
    return abort(errorResponse)
